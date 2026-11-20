import sys

from config.settings import Config
from AI.loader import load_all
from AI.splitter import split_docs
from AI.embedder import embed_passages
from AI.vector_store import reset_collection, add_chunks


def main():
    docs = load_all(Config.DATA_DIR)
    print("Số file:", len(docs))

    chunks = split_docs(docs, size=500, overlap=50)
    print("Số chunk:", len(chunks))

    # Không có chunk thì dừng, KHÔNG xóa index cũ (Chroma cũng báo lỗi khó hiểu nếu thêm danh sách rỗng)
    if not chunks:
        sys.exit(f"Không có nội dung để lưu. Kiểm tra file .docx trong {Config.DATA_DIR}")

    vectors = embed_passages([c["text"] for c in chunks])

    reset_collection()
    add_chunks(chunks, vectors)
    print("Đã lưu vào vectorstore")


if __name__ == "__main__":
    main()
