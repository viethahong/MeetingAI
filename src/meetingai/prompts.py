def get_meeting_minutes_prompt(transcript: str) -> str:
    return f"""Dưới đây là nội dung cuộc họp (transcript):

{transcript}

Dựa vào nội dung trên, hãy lập một biên bản cuộc họp chuyên nghiệp bằng tiếng Việt và định dạng thành Markdown với cấu trúc như sau:

## Biên bản họp
- **Chủ đề chính**: (Đoán từ nội dung, tóm tắt trong 1 câu)
- **Các điểm thảo luận chính**: (Sử dụng bullet points để liệt kê các thông tin quan trọng)
- **Quyết định**: (Những gì đã được thống nhất hoặc đưa ra quyết định)
- **Hành động tiếp theo**: (Trình bày dưới dạng Bảng với 3 cột: Người thực hiện - Công việc - Thời hạn. Nếu không rõ tên, hãy dùng "Thành viên A, B...")
- **Tóm tắt**: (Tóm tắt toàn bộ cuộc họp ngắn gọn trong 3-5 câu)

Lưu ý: Chỉ trả về nội dung Markdown chuẩn, không thêm bất kỳ văn bản giải thích nào khác.
"""
