from AI.prompts import FALLBACK_REPLY, LLM_DOWN_REPLY
from AI.rag_pipeline import answer
from services.llm_service import LLMError
from services.session_service import get_history, add_turn, get_result, set_result


def handle_chat(session_id, message, result=None):
    """Nhận câu hỏi từ web, lấy lịch sử, gọi RAG, lưu lại lượt này.
    LƯU Ý: web chỉ cần gửi `result` một lần (lúc người dùng vừa làm xong thang đo).
    Các câu hỏi sau trong cùng session_id, bot dùng lại kết quả đã lưu.
    Gửi `result` mới thì sẽ thay kết quả cũ."""
    if result:
        set_result(session_id, result)
    else:
        result = get_result(session_id)

    history = get_history(session_id)
    try:
        reply, sources = answer(message, history=history, result=result)
    except LLMError:
        # Không gọi được LLM: báo cho người dùng, không lưu lượt này vào lịch sử
        return {"answer": LLM_DOWN_REPLY, "sources": []}

    if not reply:
        # LLM trả rỗng, thường do bộ lọc an toàn chặn (hay gặp với tin nhắn về tự hại).
        # Không để người dùng nhận câu trả lời trống, và không lưu chuỗi rỗng vào lịch sử.
        return {"answer": FALLBACK_REPLY, "sources": []}

    add_turn(session_id, message, reply)
    return {"answer": reply, "sources": sources}
