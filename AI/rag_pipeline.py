from AI.retriever import retrieve
from AI.prompts import SYSTEM_PROMPT, build_user_message
from services.llm_service import chat


def answer(question, history=None, result=None, k=3):
    """Toàn bộ RAG: tìm chunk -> ghép prompt -> hỏi LLM.
    Trả về (câu trả lời, danh sách nguồn).

    result: kết quả thang đo do web gửi (dict), có thể None.

    LƯU Ý: lịch sử (history) chỉ giúp LLM hiểu câu hỏi nối tiếp như "còn mức này nghĩa là sao?".
    Việc tìm chunk chỉ dựa vào câu hỏi hiện tại (cộng tên thang đo nếu có), nên câu hỏi quá mơ hồ
    có thể tìm sai chunk."""
    # Thêm tên thang vào câu tìm kiếm để ưu tiên chunk của đúng thang đó
    search_text = f"{result['scale']} {question}" if result else question
    chunks = retrieve(search_text, k=k)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history or []  # lịch sử hội thoại
    messages.append({"role": "user", "content": build_user_message(question, chunks, result)})

    reply = chat(messages)
    sources = sorted({c["source"] for c in chunks})
    return reply, sources


if __name__ == "__main__":
    demo = {"scale": "PHQ-9", "score": 12, "level": "Trung bình"}
    reply, sources = answer("Kết quả này có ý nghĩa gì?", result=demo)
    print(reply)
    print("Nguồn:", sources)
