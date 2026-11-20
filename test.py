from docx import Document

doc = Document()
doc.add_heading("Giới thiệu PsyBot", level=1)
doc.add_paragraph("PsyBot là chatbot hỗ trợ giải đáp thông tin tâm lý học đường cho sinh viên.")
doc.add_paragraph("Bot hoạt động từ 8h đến 17h các ngày trong tuần.")

doc.add_heading("Lịch tư vấn", level=1)
table = doc.add_table(rows=3, cols=2)
table.rows[0].cells[0].text = "Ngày"
table.rows[0].cells[1].text = "Giờ"
table.rows[1].cells[0].text = "Thứ 2"
table.rows[1].cells[1].text = "9h - 11h"
table.rows[2].cells[0].text = "Thứ 4"
table.rows[2].cells[1].text = "14h - 16h"

doc.save("data/test.docx")
print("Đã tạo data/test.docx")
