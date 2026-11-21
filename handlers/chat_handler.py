from AI.prompts import CRISIS_REPLY, FALLBACK_REPLY, LLM_DOWN_REPLY
from AI.rag_pipeline import answer
from AI.safety import is_crisis
from services.llm_service import LLMError
from services.session_service import get_history, add_turn


def handle_chat(conversation_id, message, result=None):
    """Nhận câu hỏi từ backend web, lấy lịch sử, gọi RAG, lưu lại lượt này.

    LƯU Ý: `result` chỉ có trong request mà backend web gửi khi người dùng đang chia sẻ kết quả.
    Chatbot KHÔNG lưu kết quả giữa các request. Request không có `result` thì bot không biết kết quả,
    và các lượt trước có kèm kết quả cũng bị ẩn khỏi lịch sử. Ngừng chia sẻ = ngừng gửi `result`."""
    shared = result is not None

    # Nguy cơ tự hại: trả phản hồi an toàn soạn sẵn, KHÔNG qua RAG hay LLM,
    # để không phụ thuộc vào việc tìm được tài liệu hay LLM có hoạt động không.
    if is_crisis(message):
        add_turn(conversation_id, message, CRISIS_REPLY, shared=False)
        return {"answer": CRISIS_REPLY, "sources": []}

    history = get_history(conversation_id, include_shared=shared)
    try:
        reply, sources = answer(message, history=history, result=result)
    except LLMError:
        # Không gọi được LLM: báo cho người dùng, không lưu lượt này vào lịch sử
        return {"answer": LLM_DOWN_REPLY, "sources": []}

    if not reply:
        # LLM trả rỗng, thường do bộ lọc an toàn chặn (hay gặp với tin nhắn về tự hại).
        # Không để người dùng nhận câu trả lời trống, và không lưu chuỗi rỗng vào lịch sử.
        return {"answer": FALLBACK_REPLY, "sources": []}

    add_turn(conversation_id, message, reply, shared=shared)
    return {"answer": reply, "sources": sources}
