import re

from AI.retriever import retrieve
from AI.prompts import SYSTEM_PROMPT, build_user_message
from services.llm_service import chat

# Dòng trích nguồn LLM ghi ở cuối câu trả lời, vd "[[NGUON: 1,3]]" (số thứ tự đoạn tài liệu đã dùng).
# Chấp nhận cả khi LLM viết "NGUỒN" có dấu hoặc thiếu một dấu ngoặc.
_SOURCE_TAG = re.compile(r"\[{1,2}\s*NGU[OÔỒ]N\s*:\s*([^\]\n]*)\]{1,2}", re.IGNORECASE)


def _split_sources(reply, chunks):
    """Tách dòng [[NGUON: ...]] ra khỏi câu trả lời, đổi số đoạn thành tên file nguồn.

    LƯU Ý: chỉ trả nguồn mà LLM ghi là ĐÃ DÙNG, và chỉ nhận số nằm trong danh sách đoạn thật.
    LLM không ghi dòng nguồn thì trả danh sách rỗng, thà thiếu nguồn còn hơn ghi nguồn không được dùng."""
    used = set()
    for match in _SOURCE_TAG.finditer(reply):
        for n in re.findall(r"\d+", match.group(1)):
            i = int(n)
            if 1 <= i <= len(chunks):
                used.add(chunks[i - 1]["source"])
    clean = _SOURCE_TAG.sub("", reply).strip()
    return clean, sorted(used)


def answer(question, history=None, result=None, k=3):
    """Toàn bộ RAG: tìm chunk -> ghép prompt -> hỏi LLM.
    Trả về (câu trả lời, danh sách nguồn thực sự được dùng).

    result: kết quả thang đo do web gửi (dict), có thể None.

    LƯU Ý: lịch sử (history) chỉ giúp LLM hiểu câu hỏi nối tiếp như "còn mức này nghĩa là sao?".
    Việc tìm chunk chỉ dựa vào câu hỏi hiện tại (cộng tên thang đo nếu có), nên câu hỏi quá mơ hồ
    có thể không tìm được chunk nào."""
    # Thêm tên thang vào câu tìm kiếm để ưu tiên chunk của đúng thang đó
    search_text = f"{result['scale']} {question}" if result else question
    chunks = retrieve(search_text, k=k)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history or []  # lịch sử hội thoại
    messages.append({"role": "user", "content": build_user_message(question, chunks, result)})

    reply = chat(messages)
    return _split_sources(reply, chunks) if reply else ("", [])


if __name__ == "__main__":
    demo = {"scale": "PHQ-9", "score": 12, "level": "Vừa"}
    reply, sources = answer("Kết quả này có ý nghĩa gì?", result=demo)
    print(reply)
    print("Nguồn:", sources)
