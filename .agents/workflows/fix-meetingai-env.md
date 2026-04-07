---
description: Khắc phục lỗi ModuleNotFoundError khi chạy ứng dụng MeetingAI
---

Lưu ý quan trọng: Mỗi khi thực hiện `uv sync` hoặc có sự thay đổi lớn về mã nguồn/phiên bản, đôi khi môi trường ảo của `uv` bỏ qua việc liên kết lại project chính ở dạng chỉnh sửa (editable mode), dẫn đến việc không tìm thấy module khi chạy lệnh (lỗi `ModuleNotFoundError: No module named 'meetingai'`).

Mỗi khi hệ thống báo lỗi này, AI/Agent sẽ tự động áp dụng Workflow dưới đây để khắc phục thay vì loay hoay sửa code hoặc thư mục.

// turbo-all
1. Chạy lệnh ép cài đặt lại gói mã nguồn (editable mode) vào môi trường ảo:
`uv pip install -e .`

2. Kiểm tra xem lệnh lỗi đã được giải quyết chưa:
`uv run meetingai-ui --help`
