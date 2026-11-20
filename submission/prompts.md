# Dùng AI

| # | Ai dùng | Công cụ | Prompt (tóm tắt) | AI sai ở đâu | Nhóm kiểm lại thế nào |
|---|---|---|---|---|---|
| 1 | Nhóm | Antigravity AI | Viết `validator/validate.py` kiểm tra 9 lỗi luật (chỉ thư viện chuẩn + `scripts/pngutil.py`, không đọc `_private`/`data_source`) và đối chiếu mask pixel cho `--candidates` | Ngưỡng `instance_merge` ban đầu chỉ kiểm `cover_seg >= 0.18` khiến lô sạch bị báo >20 ứng viên giả; ngưỡng `cbox < 0.70` báo nhầm vật mảnh/chéo (`tie`, `kite`) trên lô sạch | Chạy đo trên lô sạch `runs/clean` (50 ảnh) để tinh chỉnh về 0 ứng viên nhiễu, chạy kiểm tra `score_findings.py` trên seed `3007` và `11` |
| 2 | Nhóm | Antigravity AI | Viết `validator/handover_trace.py` tự động sinh lô `v2` (`rework_queue.csv`, `manifest.csv`, `label_summary.csv`, `truyvet.csv`, `README.txt`) và `trace.json` | Ghi `Kết luận v1: HOLD` (chữ hoa) làm FAIL H13 do `check_handover.py` yêu cầu `Hold` (Title Case) | Chạy `check_handover.py --run runs/r3007`, sửa lại format `README.txt`, đóng gói lại bằng `pack_release.py` cho đến khi đạt 17/17 PASS |
