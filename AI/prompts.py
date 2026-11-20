# TODO (nhờ chuyên gia tâm lý của team điền): thông tin hỗ trợ khẩn cấp, chỉ hiển thị khi người dùng
# có dấu hiệu nguy cơ. Ví dụ: số đường dây nóng, cơ sở tư vấn của trường/đơn vị.
# Để trống thì bot chỉ khuyên liên hệ người thân hoặc chuyên gia, không đưa thông tin liên hệ cụ thể.
CRISIS_CONTACT = ""

# Câu trả lời soạn sẵn, KHÔNG qua LLM.
# FALLBACK_REPLY: dùng khi LLM trả rỗng (thường do bộ lọc an toàn chặn, hay gặp với tin nhắn về tự hại),
# nên phải luôn an toàn cho người đang khủng hoảng. Nhờ chuyên gia của team duyệt nội dung này.
FALLBACK_REPLY = (
    "Mình chưa thể trả lời câu này lúc này. Nếu bạn đang cảm thấy quá sức hoặc nghĩ đến việc làm hại bản thân, "
    "hãy liên hệ ngay người thân bạn tin tưởng hoặc chuyên gia tâm lý."
    + (f" {CRISIS_CONTACT}" if CRISIS_CONTACT else "")
)
# LLM_DOWN_REPLY: dùng khi không kết nối được LLM.
LLM_DOWN_REPLY = "Hệ thống đang bận hoặc gặp sự cố, bạn vui lòng thử lại sau ít phút."

_crisis_info = (
    f"và cung cấp đúng thông tin liên hệ sau: {CRISIS_CONTACT}"
    if CRISIS_CONTACT
    else "(không bịa số điện thoại hay địa chỉ liên hệ)"
)

# LƯU Ý: đây là "luật" gửi cho LLM ở mỗi lần hỏi. LLM không tự nhớ tài liệu của bạn,
# nó chỉ biết những gì nằm trong prompt. Các dòng "chỉ dựa trên tài liệu", "không chẩn đoán"
# làm giảm rủi ro nhưng không đảm bảo 100%. Cần thử kỹ với câu hỏi thật trước khi dùng.
SYSTEM_PROMPT = f"""Bạn là PsyBot, trợ lý tâm lý học trả lời bằng tiếng Việt. Bạn làm hai việc:
(1) Giải thích kết quả thang đo mà người dùng vừa hoàn thành.
(2) Gợi ý người dùng nên chọn thang đo nào.

Quy tắc về nội dung:
- Chỉ dựa trên phần "Tài liệu". Không dùng kiến thức bên ngoài để giải thích thang đo, mức điểm hay ý nghĩa kết quả.
- Nếu tài liệu không có thông tin về thang đo hoặc mức điểm người dùng hỏi: nói rõ bạn chưa có tài liệu hướng dẫn
  giải thích kết quả này, chỉ nhắc lại điểm và mức độ do hệ thống cung cấp, rồi gợi ý họ hỏi chuyên gia.
  Không suy đoán ý nghĩa.
- Khi có phần "Kết quả của người dùng", điểm số và mức độ đó do hệ thống tính sẵn. Hãy dùng đúng như vậy,
  không tự tính lại, không đổi mức độ.
- Gợi ý thang đo: nếu chưa rõ nhu cầu, hỏi lại người dùng (họ quan tâm vấn đề gì, dành cho ai) rồi mới gợi ý.
  Chỉ gợi ý các thang có trong tài liệu.
- Giải thích dễ hiểu, ngắn gọn, giọng nhẹ nhàng, không phán xét.
- Người dùng không gửi và không nhìn thấy phần "Tài liệu". Không cảm ơn họ vì đã cung cấp tài liệu,
  không nói "tài liệu bạn gửi".

Quy tắc về an toàn:
- Không chẩn đoán và không kê đơn. Nhắc rõ kết quả thang đo chỉ mang tính tham khảo, không thay thế
  đánh giá của chuyên gia. Với kết quả ở mức cao, khuyến khích người dùng gặp chuyên gia.
- CHỈ khi người dùng nhắc đến ý định tự làm hại bản thân, tự tử, hoặc đang ở trong tình huống nguy hiểm:
  thể hiện sự quan tâm, khuyên họ liên hệ người thân tin cậy hoặc chuyên gia ngay {_crisis_info}.
  Trong trường hợp này, ưu tiên hỗ trợ người dùng hơn là giải thích điểm số.
- Trong mọi trường hợp khác, không nhắc đến thông tin hỗ trợ khẩn cấp."""


def build_context(chunks):
    """Ghép các chunk tìm được thành một khối văn bản, kèm tên file nguồn."""
    return "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in chunks)


def format_result(result):
    """Đổi kết quả từ web (dict) thành đoạn chữ để đưa vào prompt."""
    if not result:
        return ""
    lines = [f"Thang đo: {result['scale']}"]
    score = result.get("score")
    if score is not None:
        # Điểm nhận về dạng số thực (12.0). Bỏ ".0" để bot không ghi "12.0 điểm".
        lines.append(f"Điểm: {int(score) if float(score).is_integer() else score}")
    if result.get("level"):
        lines.append(f"Mức độ: {result['level']}")
    if result.get("report"):
        lines.append(f"Báo cáo của hệ thống:\n{result['report']}")
    return "\n".join(lines)


def build_user_message(question, chunks, result=None):
    """Tin nhắn gửi LLM = tài liệu tìm được + (kết quả của người dùng) + câu hỏi."""
    # LƯU Ý: phần tài liệu nằm trong tin nhắn "user" nên LLM dễ tưởng người dùng gửi nó
    # (vd "cảm ơn bạn đã cung cấp tài liệu"). Ghi rõ đây là tài liệu của hệ thống.
    parts = [f"Tài liệu (do hệ thống tự tìm, người dùng KHÔNG gửi và không nhìn thấy phần này):\n{build_context(chunks)}"]
    if result:
        parts.append(f"Kết quả của người dùng:\n{format_result(result)}")
    parts.append(f"Câu hỏi: {question}")
    return "\n\n".join(parts)
