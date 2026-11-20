# Nhóm Day 10 — Dataset Release & Handover

- **Số nhóm:** Chưa xác định
- **Seed luyện tập:** `3007`
- **Số thành viên:** 5
- **Repository:** https://github.com/VanQuyen11/K5-L23-Day10-2A202603226-LuongVanQuyen-Dataset-Release-Handover

## 1. Danh sách thành viên và phân công

| Họ và tên | MSHV | Tài khoản GitHub | Phần chính |
|---|---|---|---|
| Nguyễn Thanh Phong | 2A202603119 | Tphong27  | P1: Validator lỗi luật |
| Phạm Anh Tuấn | 2A202603232 | AnhTuan2003ml | P2: Detection–Panoptic, review |
| Lương Văn Quyến | 2A202603226 | VanQuyen11 | P0, P3: Leader, Release/Hold, lineage |
| Huỳnh Ngọc Gia Hân | 2A202603128 | suadaunanh | P4: Bàn giao dataset v2 |
| Nguyễn Nhật Minh | 2A202603210 | nminnnnn| P5, P6: Truy vết, bảo mật, đề ẩn |

## 2. Kế hoạch triển khai

- **Pha 0:** Lương Văn Quyến chuẩn bị repository, thống nhất seed `3007` và phân công công việc.
- **Pha 1:** Nguyễn Thanh Phong xây dựng validator kiểm tra 9 loại lỗi luật.
- **Pha 2:** Phạm Anh Tuấn phụ trách đối chiếu detection–panoptic, tạo danh sách ứng viên; cả 5 thành viên tham gia kiểm tra ảnh và review.
- **Pha 3:** Lương Văn Quyến xác định Release/Hold, ghi lineage và đánh giá tác động tới training run.
- **Pha 4:** Huỳnh Ngọc Gia Hân thực hiện đóng gói dataset v2, kiểm tra manifest, checksum và rework queue.
- **Pha 5:** Nguyễn Nhật Minh xây dựng truy vết ticket với tier_a, tier_b và notify.
- **Pha 6:** Nguyễn Nhật Minh phụ trách nội dung bảo mật; cả nhóm phối hợp hoàn thành đề ẩn.

## 3. Quy tắc làm việc nhóm

- Tất cả sử dụng seed `3007` để tạo dữ liệu luyện tập.
- Không commit thư mục `runs/`, `data_source/` hoặc dữ liệu đề ẩn gốc.
- Mỗi thành viên phụ trách công việc đã phân công và phối hợp review ảnh ở Pha 2.
- Mỗi thành viên thực hiện ít nhất 2 commit có nội dung thực chất.
- Trước khi nộp, nhóm kiểm tra đầy đủ validator, báo cáo, lineage, handover, trace, security và đề ẩn.
- Lương Văn Quyến chịu trách nhiệm kiểm tra bản nộp cuối cùng.