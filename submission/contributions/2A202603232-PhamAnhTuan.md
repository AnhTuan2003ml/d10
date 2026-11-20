# Phạm Anh Tuấn — 2A202603232

- GitHub: `AnhTuan2003ml`
- Phụ trách: P2 — đối chiếu Detection–Panoptic và review ảnh ứng viên.

## Công việc đã thực hiện

- Xây dựng phần đối chiếu box detection với segment panoptic trong `validator/validate.py`.
- Tính IoU, độ phủ box/segment và đếm pixel mask để phát hiện `class_swap`, `category_swap`, `bbox_drift`, `missing_box` và `instance_merge`.
- Tinh chỉnh ngưỡng bằng lô sạch 50 ảnh để giảm danh sách từ hơn 20 cảnh báo giả xuống 0 ứng viên.
- Chạy seed `3007`, tạo 10 ứng viên trên 10 ảnh và mở ảnh review thủ công.
- Xác nhận 10 lỗi, bác bỏ 1 cảnh báo `bbox_drift`, đồng thời phân biệt `class_swap` với `category_swap`.

## File và đầu ra

- `validator/validate.py`: logic Detection–Panoptic và xuất ứng viên.
- `submission/r3007/candidates.json`: 10 ứng viên cần review.
- `submission/r3007/review_log.csv`: 11 quyết định review có mô tả bằng chứng quan sát.
- `submission/r3007/errors.json`: kết quả cuối có các lỗi Detection–Panoptic đã xác nhận.
- `submission/REPORT.md`: số liệu, ngưỡng và giải thích ảnh hưởng của false positive tới F1.
