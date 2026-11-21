"""Phát hiện tin nhắn có dấu hiệu nguy cơ tự hại, KHÔNG dùng LLM.

Dùng để bot luôn trả phản hồi an toàn, kể cả khi LLM lỗi, bị bộ lọc chặn, hay không có tài liệu.

LƯU Ý:
- Danh sách cụm từ dưới đây là bản NHÁP. Cần chuyên gia tâm lý của team duyệt và bổ sung.
- Ưu tiên bắt nhầm hơn bỏ sót: câu như "nóng muốn chết" hay "thang đo có hỏi về tự tử không?"
  cũng sẽ nhận phản hồi an toàn. Chấp nhận được vì bỏ sót người có nguy cơ thì nguy hiểm hơn.
- Từ khóa không bắt được cách nói gián tiếp. Vì vậy prompt vẫn giữ quy tắc an toàn cho LLM.
"""
import re
import unicodedata

# So khớp trên chữ có dấu (đã viết thường)
CRISIS_PHRASES = [
    "tự tử", "tự sát", "tự vẫn", "muốn chết", "không muốn sống", "chẳng muốn sống",
    "không thiết sống", "chán sống", "kết thúc cuộc đời", "kết thúc cuộc sống", "kết liễu",
    "tự làm hại", "tự hại", "làm hại bản thân", "làm đau bản thân", "rạch tay", "cắt tay",
    "nhảy lầu", "nhảy cầu", "uống thuốc quá liều", "không muốn tồn tại", "biến mất mãi mãi",
]

# So khớp trên chữ đã bỏ dấu, cho người gõ không dấu.
# Chỉ dùng cụm không trùng với từ thường. Ví dụ không dùng "tu tu" vì trùng "từ từ",
# "tu van" vì trùng "tư vấn", "chan song" vì trùng "chặn sóng".
CRISIS_PHRASES_NO_ACCENT = [
    "tu sat", "muon chet", "khong muon song", "chang muon song", "khong thiet song",
    "ket thuc cuoc doi", "ket lieu", "tu lam hai", "lam hai ban than", "rach tay",
    "uong thuoc qua lieu", "khong muon ton tai",
]


def _normalize(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text).lower()).strip()


def _strip_accents(text):
    text = text.replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def is_crisis(message):
    text = _normalize(message)
    if any(p in text for p in CRISIS_PHRASES):
        return True
    plain = _strip_accents(text) + " "
    return any(p in plain for p in CRISIS_PHRASES_NO_ACCENT)
