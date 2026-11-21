from AI.embedder import embed_query
from AI.vector_store import search

# Chunk có khoảng cách lớn hơn ngưỡng này bị coi là KHÔNG liên quan và bị bỏ.
# Không có chunk nào qua ngưỡng thì bot nhận "không có tài liệu liên quan" và phải nói chưa đủ thông tin,
# thay vì cố trả lời từ một đoạn không liên quan (hoặc từ kiến thức ngoài).
#
# LƯU Ý: 0.18 là giá trị TẠM, đo trên test.docx: câu liên quan 0.06-0.165, câu không liên quan 0.19-0.23.
# Khoảng cách giữa hai nhóm rất hẹp. Khi có file Word thật của team, phải đo lại và chỉnh ngưỡng này.
# Ngưỡng quá thấp: bot hay nói "chưa có thông tin" dù tài liệu có. Quá cao: bot lấy cả đoạn không liên quan.
MAX_DISTANCE = 0.18


def retrieve(question, k=3):
    """Lấy tối đa k chunk giống câu hỏi nhất, chỉ giữ chunk đủ liên quan.
    Luồng: câu hỏi -> vector -> Chroma tìm vector gần nhất -> lọc theo ngưỡng -> trả về chunk.

    LƯU Ý: câu hỏi chỉ được đổi thành vector để so sánh, KHÔNG được lưu vào Chroma.
    Chroma chỉ lưu các chunk của tài liệu (lúc chạy build_index.py)."""
    query_vector = embed_query(question)
    return [c for c in search(query_vector, k=k) if c["distance"] <= MAX_DISTANCE]


if __name__ == "__main__":
    for r in retrieve("Bot làm việc mấy giờ?"):
        print(round(r["distance"], 3), r["source"], "|", r["text"][:100])
