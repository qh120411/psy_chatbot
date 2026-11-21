MAX_TURNS = 5  # chỉ nhớ 5 lượt hỏi-đáp gần nhất để prompt không quá dài

# LƯU Ý: lưu trong RAM của tiến trình. Tắt server hoặc reload là mất hết lịch sử.
# Chạy nhiều worker thì mỗi worker có lịch sử riêng. Đủ dùng khi học và thử nghiệm.
# Kết quả thang đo KHÔNG được lưu ở đây: backend web gửi lại ở mỗi request khi người dùng đang chia sẻ.
#
# Mỗi lượt có cờ "shared" = lượt đó có kèm kết quả thang đo hay không.
# Khi người dùng ngừng chia sẻ (request không có result), các lượt "shared" bị ẩn khỏi lịch sử,
# vì câu trả lời trong đó có nhắc điểm số. Nhờ vậy bot không còn nhắc lại kết quả cũ.
_conversations = {}   # conversation_id -> list {"question", "answer", "shared"}


def get_history(conversation_id, include_shared):
    messages = []
    for turn in _conversations.get(conversation_id, []):
        if turn["shared"] and not include_shared:
            continue
        messages.append({"role": "user", "content": turn["question"]})
        messages.append({"role": "assistant", "content": turn["answer"]})
    return messages


def add_turn(conversation_id, question, answer, shared):
    turns = _conversations.setdefault(conversation_id, [])
    turns.append({"question": question, "answer": answer, "shared": shared})
    _conversations[conversation_id] = turns[-MAX_TURNS:]
