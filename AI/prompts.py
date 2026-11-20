# TODO (nhờ chuyên gia tâm lý của team điền): thông tin hỗ trợ khẩn cấp, chỉ hiển thị khi người dùng
# có dấu hiệu nguy cơ. Ví dụ: số đường dây nóng, cơ sở tư vấn của trường/đơn vị.
# Để trống thì bot chỉ khuyên liên hệ người thân hoặc chuyên gia, không đưa thông tin liên hệ cụ thể.
CRISIS_CONTACT = ""

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
    if result.get("score") is not None:
        lines.append(f"Điểm: {result['score']}")
    if result.get("level"):
        lines.append(f"Mức độ: {result['level']}")
    if result.get("report"):
        lines.append(f"Báo cáo của hệ thống:\n{result['report']}")
    return "\n".join(lines)


def build_user_message(question, chunks, result=None):
    """Tin nhắn gửi LLM = tài liệu tìm được + (kết quả của người dùng) + câu hỏi."""
    parts = [f"Tài liệu:\n{build_context(chunks)}"]
    if result:
        parts.append(f"Kết quả của người dùng:\n{format_result(result)}")
    parts.append(f"Câu hỏi: {question}")
    return "\n\n".join(parts)
