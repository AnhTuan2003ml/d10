# Bảo mật khi làm việc

## 1. Ca USB: hết giờ, muốn chép lô về nhà làm tiếp
Không được chép dữ liệu ra USB, không gửi qua email cá nhân và cũng không nhờ người khác làm hộ. Dữ liệu dự án (kể cả ảnh và nhãn) mang theo ràng buộc bảo mật và quyền sử dụng nội bộ; việc mang ra ngoài thiết bị công ty hoặc gửi qua kênh cá nhân làm mất kiểm soát sao chép, rò rỉ dữ liệu khách hàng/nội bộ và vi phạm quyền truy cập theo tài khoản. Nếu chưa xong việc khi hết giờ, cần lưu tiến độ trên máy trạm/hệ thống được cấp phép của công ty, bàn giao lại trạng thái cho ca sau hoặc đăng nhập qua kênh làm việc từ xa (VPN/VDI) được phê duyệt vào ngày hôm sau.

## 2. Năm việc: được hay không
- **Mở job được giao trên máy công ty:** **Được**, vì đây là đúng phạm vi công việc, đúng thiết bị và tài khoản được cấp quyền.
- **Chụp màn hình gửi người quen:** **Không được**, vì làm lộ dữ liệu nội bộ ra ngoài phạm vi dự án và không kiểm soát được nơi ảnh được lưu trữ/phát tán.
- **Chép lô ra USB:** **Không được**, vì thiết bị lưu trữ cá nhân dễ thất lạc, nhiễm mã độc và đưa dữ liệu ra khỏi vùng kiểm soát của công ty.
- **Dán nhãn thật lên chatbot:** **Không được**, vì dữ liệu/nhãn thật của dự án có thể bị lưu lại hoặc dùng để huấn luyện trên dịch vụ bên thứ ba ngoài thỏa thuận bảo mật.
- **Đưa tài khoản CVAT cho đồng nghiệp:** **Không được**, vì làm sai lệch nhật ký truy vết (audit log ai là người gán/kiểm thật sự) và vi phạm nguyên tắc cấp quyền cá nhân.

## 3. Ca khuôn mặt: thấy mặt người rõ trong lô, guideline yêu cầu làm mờ
Khi phát hiện trong lô có ảnh lộ rõ khuôn mặt người thật chưa được làm mờ (ví dụ ngay trong lô `lab250_95697c6d4612` có ảnh `000000009483` thấy rõ mặt người đàn ông mặc vest đứng cạnh bàn máy tính, hay `000000013291` thấy rõ mặt bốn người cầm đĩa ném), trạng thái lô phải đặt là **Hold** và **báo ngay cho người phụ trách / quản lý dữ liệu**. Tuyệt đối không tự ý dùng công cụ ngoài làm mờ hay tự xóa ảnh khỏi lô vì làm thay đổi dữ liệu gốc, sai lệch hash/manifest và phá vỡ tính truy vết (lineage) của phiên bản bàn giao; mọi xử lý che mờ hoặc loại bỏ phải do quy trình/người có thẩm quyền thực hiện và ghi nhận thành phiên bản mới.
