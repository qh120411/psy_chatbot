from pathlib import Path
from docx import Document

def load_docx(path):
    doc = Document(path)
    parts = []

    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            parts.append(text)
    
    for table in doc.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells]  # chữ của từng ô
            parts.append(" | ".join(cells))  
    return "\n".join(parts) 

def load_all(data_dir):
    docs = []
    for file in Path(data_dir).glob("*.docx"):
        docs.append({"source": file.name, "text": load_docx(file)})
    return docs

# if __name__ == "__main__":
#     from config.settings import Config
#     for d in load_all(Config.DATA_DIR):
#         print(d["source"], len(d["text"]))
#         print(d["text"][:300])
