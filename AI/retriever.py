from AI.embedder import embed_query
from AI.vector_store import search


def retrieve(question, k=3):
    """Lấy k chunk giống câu hỏi nhất.
    Luồng: câu hỏi -> vector -> Chroma tìm vector gần nhất -> trả về chunk (chữ).

    LƯU Ý: câu hỏi chỉ được đổi thành vector để so sánh, KHÔNG được lưu vào Chroma.
    Chroma chỉ lưu các chunk của tài liệu (lúc chạy build_index.py)."""
    query_vector = embed_query(question)
    return search(query_vector, k=k)


if __name__ == "__main__":
    for r in retrieve("Bot làm việc mấy giờ?"):
        print(r["source"], "|", r["text"][:100])
