from pathlib import Path
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


def _table_to_lines(table):
    """Mỗi hàng của bảng thành 1 dòng, các ô nối bằng " | "."""
    lines = []
    for row in table.rows:
        cells = []
        for c in row.cells:
            text = c.text.strip()
            # Ô gộp (merge) được python-docx trả về nhiều lần, bỏ ô trùng liền kề
            if cells and cells[-1] == text:
                continue
            cells.append(text)
        if any(cells):  # bỏ hàng rỗng
            lines.append(" | ".join(cells))
    return lines


def load_docx(path):
    """Đọc file Word thành 1 chuỗi, giữ ĐÚNG THỨ TỰ đoạn văn và bảng như trong file.
    LƯU Ý: doc.paragraphs và doc.tables là 2 danh sách riêng. Nếu đọc hết đoạn văn rồi mới
    đọc bảng, bảng mức điểm của mỗi thang đo sẽ bị dồn xuống cuối và tách khỏi tên thang.
    Vì vậy phải duyệt thẳng phần thân (body) của file theo thứ tự."""
    doc = Document(path)
    parts = []

    for child in doc.element.body.iterchildren():
        tag = child.tag.split("}")[-1]  # bỏ phần namespace, còn "p" hoặc "tbl"
        if tag == "p":
            text = Paragraph(child, doc).text.strip()
            if text:
                parts.append(text)
        elif tag == "tbl":
            parts.extend(_table_to_lines(Table(child, doc)))

    return "\n".join(parts)

def load_all(data_dir):
    docs = []
    for file in sorted(Path(data_dir).glob("*.docx")):
        # Word tạo file tạm "~$ten.docx" khi đang mở file. File này không đọc được, bỏ qua.
        if file.name.startswith("~$"):
            continue
        docs.append({"source": file.name, "text": load_docx(file)})
    return docs

if __name__ == "__main__":
    from config.settings import Config
    for d in load_all(Config.DATA_DIR):
        print(d["source"], len(d["text"]))
        print(d["text"][:300])
