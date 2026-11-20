from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import pngutil


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def load_classes(path: Path) -> dict[int, str]:
    classes: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        classes[int(parts[0])] = parts[1]
    return classes


def load_jobs(path: Path) -> dict[str, dict[str, str]]:
    jobs: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            jobs[row["job_id"]] = row
    return jobs


def box_iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ix1 = max(a[0], b[0])
    iy1 = max(a[1], b[1])
    ix2 = min(a[2], b[2])
    iy2 = min(a[3], b[3])
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0.0 else 0.0


def scan_mask_counts_and_overlap(
    mask_path: Path,
    yolo_boxes_px: list[tuple[int, float, float, float, float]],
    thing_seg_ids: set[int],
) -> tuple[int, int, dict[int, int], dict[tuple[int, int], int]]:
    width, height, pixels = pngutil.read_rgb(mask_path)
    counts: dict[int, int] = {}
    inside: dict[tuple[int, int], int] = {}
    stride = width * 3
    for y in range(height):
        row_off = y * stride
        y_boxes = [
            (bi, bx[1], bx[3])
            for bi, bx in enumerate(yolo_boxes_px)
            if bx[2] <= y < bx[4]
        ]
        for x in range(width):
            idx = row_off + x * 3
            sid = pixels[idx] + (pixels[idx + 1] << 8) + (pixels[idx + 2] << 16)
            if sid == 0:
                continue
            counts[sid] = counts.get(sid, 0) + 1
            if y_boxes and sid in thing_seg_ids:
                for bi, x1, x2 in y_boxes:
                    if x1 <= x < x2:
                        key = (bi, sid)
                        inside[key] = inside.get(key, 0) + 1
    return width, height, counts, inside


def validate_delivery(delivery_dir: Path, need_candidates: bool) -> tuple[list[dict], list[dict]]:
    manifest = json.loads((delivery_dir / "manifest.json").read_text(encoding="utf-8"))
    metadata = json.loads((delivery_dir / "metadata.json").read_text(encoding="utf-8"))
    panoptic = json.loads((delivery_dir / "panoptic.json").read_text(encoding="utf-8"))
    classes = load_classes(delivery_dir / "classes.txt")
    jobs = load_jobs(delivery_dir / "jobs.csv")

    categories = {cat["id"]: cat for cat in panoptic["categories"]}
    img_info_by_stem = {Path(img["file_name"]).stem: img for img in panoptic["images"]}
    ann_by_stem = {Path(ann["file_name"]).stem: ann for ann in panoptic["annotations"]}
    meta_by_stem = {item["image"]: item for item in metadata["items"]}

    errors: list[dict] = []
    candidates: list[dict] = []
    seen_targets: set[str] = set()

    scene_splits: dict[str, set[str]] = {}
    for item in metadata["items"]:
        scene_splits.setdefault(item["scene_id"], set()).add(item["split"])
    for scene_id, splits in sorted(scene_splits.items()):
        if "train" in splits and "val" in splits:
            errors.append({"type": "scene_leak", "target": scene_id})

    for stem, item in sorted(manifest["items"].items()):
        img_path = delivery_dir / item["image"]
        lbl_path = delivery_dir / item["label"]
        msk_path = delivery_dir / item["mask"]

        if not img_path.is_file():
            errors.append({"type": "missing_image", "target": stem})
            seen_targets.add(stem)
            continue

        hash_mismatch = False
        if sha256_file(img_path) != item["image_sha256"]:
            hash_mismatch = True
        elif lbl_path.is_file() and sha256_file(lbl_path) != item["label_sha256"]:
            hash_mismatch = True
        elif msk_path.is_file() and sha256_file(msk_path) != item["mask_sha256"]:
            hash_mismatch = True

        if hash_mismatch:
            errors.append({"type": "wrong_hash", "target": stem})
            seen_targets.add(stem)
            continue

        meta = meta_by_stem.get(stem)
        if meta is not None:
            job = jobs.get(meta["job_id"])
            if job is not None and meta["guideline_version"] != job["guideline"]:
                errors.append({"type": "guideline_mismatch", "target": stem})
                seen_targets.add(stem)
                continue

        img_meta = img_info_by_stem.get(stem, {})
        img_w = int(img_meta.get("width", 1))
        img_h = int(img_meta.get("height", 1))

        parsed_boxes: list[tuple[int, float, float, float, float, float, float, float, float]] = []
        rule_found = False

        if lbl_path.is_file():
            for raw_line in lbl_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 5:
                    errors.append({"type": "invalid_class", "target": stem})
                    seen_targets.add(stem)
                    rule_found = True
                    break
                try:
                    cls_id = int(parts[0])
                    cx, cy, bw, bh = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                except ValueError:
                    errors.append({"type": "invalid_class", "target": stem})
                    seen_targets.add(stem)
                    rule_found = True
                    break

                if cls_id not in classes:
                    errors.append({"type": "invalid_class", "target": stem})
                    seen_targets.add(stem)
                    rule_found = True
                    break

                x1 = cx - bw / 2.0
                y1 = cy - bh / 2.0
                x2 = cx + bw / 2.0
                y2 = cy + bh / 2.0
                if bw <= 0.0 or bh <= 0.0 or x1 < -1e-5 or y1 < -1e-5 or x2 > 1.0 + 1e-5 or y2 > 1.0 + 1e-5:
                    errors.append({"type": "bbox_out_of_bounds", "target": stem})
                    seen_targets.add(stem)
                    rule_found = True
                    break

                parsed_boxes.append((
                    cls_id,
                    cx,
                    cy,
                    bw,
                    bh,
                    max(0.0, x1 * img_w),
                    max(0.0, y1 * img_h),
                    min(float(img_w), x2 * img_w),
                    min(float(img_h), y2 * img_h),
                ))

        if rule_found:
            continue

        for i in range(len(parsed_boxes)):
            if rule_found:
                break
            c1, cx1, cy1, w1, h1, *_ = parsed_boxes[i]
            for j in range(i + 1, len(parsed_boxes)):
                c2, cx2, cy2, w2, h2, *_ = parsed_boxes[j]
                if c1 != c2:
                    continue
                if (
                    abs(w1 - w2) * img_w <= 2.5
                    and abs(h1 - h2) * img_h <= 2.5
                    and abs(cx1 - cx2) * img_w <= 3.0
                    and abs(cy1 - cy2) * img_h <= 3.0
                ):
                    errors.append({"type": "duplicate_box", "target": stem})
                    seen_targets.add(stem)
                    rule_found = True
                    break

        if rule_found:
            continue

        ann = ann_by_stem.get(stem)
        if ann is not None:
            for seg in ann["segments_info"]:
                if seg["category_id"] not in categories:
                    errors.append({"type": "invalid_category_id", "target": stem})
                    seen_targets.add(stem)
                    rule_found = True
                    break

        if rule_found:
            continue

        if ann is not None and msk_path.is_file():
            thing_segs = [
                seg for seg in ann["segments_info"]
                if categories.get(seg["category_id"], {}).get("isthing") == 1 and seg.get("iscrowd", 0) == 0
            ]
            thing_seg_ids = {seg["id"] for seg in thing_segs}
            yolo_px = [(b[0], b[5], b[6], b[7], b[8]) for b in parsed_boxes]
            _, _, counts, inside = scan_mask_counts_and_overlap(
                msk_path,
                yolo_px if need_candidates else [],
                thing_seg_ids if need_candidates else set(),
            )

            for seg in ann["segments_info"]:
                actual = counts.get(seg["id"], 0)
                if actual < seg["area"]:
                    errors.append({"type": "thing_overlap", "target": stem})
                    seen_targets.add(stem)
                    rule_found = True
                    break

            if rule_found or not need_candidates:
                continue

            box_to_seg_best: dict[int, tuple[int, float, float, float]] = {}
            seg_to_boxes: dict[int, list[tuple[int, float, float, float]]] = {}

            for bi, (cls_id, bx1, by1, bx2, by2) in enumerate(yolo_px):
                b_area = max(1.0, (bx2 - bx1) * (by2 - by1))
                for seg in thing_segs:
                    sid = seg["id"]
                    s_area = max(1, counts.get(sid, seg["area"]))
                    sx, sy, sw, sh = seg["bbox"]
                    s_box = (float(sx), float(sy), float(sx + sw), float(sy + sh))
                    iou = box_iou((bx1, by1, bx2, by2), s_box)
                    in_px = inside.get((bi, sid), 0)
                    cover_seg = in_px / s_area
                    cover_box = in_px / b_area
                    if iou > 0.05 or cover_seg > 0.1:
                        seg_to_boxes.setdefault(sid, []).append((bi, iou, cover_seg, cover_box))
                        prev = box_to_seg_best.get(bi)
                        score = cover_seg + iou
                        if prev is None or score > prev[1] + prev[2]:
                            box_to_seg_best[bi] = (sid, iou, cover_seg, cover_box)

            seg_by_id = {seg["id"]: seg for seg in thing_segs}
            img_area = max(1, img_w * img_h)

            for sid, matches in seg_to_boxes.items():
                seg = seg_by_id[sid]
                seg_name = categories[seg["category_id"]]["name"]
                s_area = counts.get(sid, seg["area"])
                if s_area < 300:
                    continue
                same_cls_boxes = [
                    (bi, iou, cov, cbox)
                    for bi, iou, cov, cbox in matches
                    if classes[yolo_px[bi][0]] == seg_name and cov >= 0.15 and cbox >= 0.45
                ]
                merged_pair = False
                for i in range(len(same_cls_boxes)):
                    for j in range(i + 1, len(same_cls_boxes)):
                        bi1, _, cov1, _ = same_cls_boxes[i]
                        bi2, _, cov2, _ = same_cls_boxes[j]
                        b1 = yolo_px[bi1][1:5]
                        b2 = yolo_px[bi2][1:5]
                        if box_iou(b1, b2) < 0.35 and (cov1 + cov2) >= 0.55:
                            merged_pair = True
                            break
                    if merged_pair:
                        break
                if merged_pair:
                    candidates.append({
                        "image": stem,
                        "type": "instance_merge",
                        "detail": f"segment {sid} ({seg_name}) covers multiple boxes",
                    })

            for bi, (cls_id, bx1, by1, bx2, by2) in enumerate(yolo_px):
                box_name = classes[cls_id]
                best = box_to_seg_best.get(bi)
                if best is None:
                    continue
                sid, iou, cov, cbox = best
                seg = seg_by_id[sid]
                seg_name = categories[seg["category_id"]]["name"]
                if box_name != seg_name:
                    has_same_cls_match = any(
                        classes[yolo_px[obi][0]] == seg_name and ocov >= 0.4
                        for obi, oiou, ocov, _ in seg_to_boxes.get(sid, [])
                    )
                    if not has_same_cls_match and iou >= 0.45 and cov >= 0.45:
                        candidates.append({
                            "image": stem,
                            "type": "class_swap",
                            "detail": f"det={box_name} vs pan={seg_name} (iou={iou:.2f}, cov={cov:.2f})",
                        })
                else:
                    same_cls_on_seg = [
                        obi for obi, oiou, ocov, _ in seg_to_boxes.get(sid, [])
                        if classes[yolo_px[obi][0]] == seg_name and (oiou >= 0.1 or ocov >= 0.15)
                    ]
                    if len(same_cls_on_seg) == 1 and 0.15 <= iou < 0.72 and cov < 0.80:
                        candidates.append({
                            "image": stem,
                            "type": "bbox_drift",
                            "detail": f"cls={box_name} (iou={iou:.2f}, cov={cov:.2f}, cbox={cbox:.2f})",
                        })

            for seg in thing_segs:
                sid = seg["id"]
                s_area = counts.get(sid, seg["area"])
                if s_area < 250 and s_area / img_area < 0.002:
                    continue
                seg_name = categories[seg["category_id"]]["name"]
                matches = seg_to_boxes.get(sid, [])
                has_same = any(
                    classes[yolo_px[bi][0]] == seg_name and (cov >= 0.25 or iou >= 0.2)
                    for bi, iou, cov, _ in matches
                )
                has_other_strong = any(
                    cov >= 0.45 and iou >= 0.45
                    for bi, iou, cov, _ in matches
                )
                if not has_same and not has_other_strong:
                    candidates.append({
                        "image": stem,
                        "type": "missing_box",
                        "detail": f"pan={seg_name} area={s_area}",
                    })

    return errors, candidates


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a delivery batch")
    parser.add_argument("delivery", help="Path to delivery directory")
    parser.add_argument("--out", required=True, help="Output errors.json path")
    parser.add_argument("--candidates", help="Optional output candidates.json path")
    args = parser.parse_args()

    delivery_dir = Path(args.delivery)
    need_candidates = args.candidates is not None
    errors, candidates = validate_delivery(delivery_dir, need_candidates)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"errors": errors}, indent=2) + "\n", encoding="utf-8")

    if args.candidates is not None:
        cand_path = Path(args.candidates)
        cand_path.parent.mkdir(parents=True, exist_ok=True)
        cand_path.write_text(json.dumps({"candidates": candidates}, indent=2) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
