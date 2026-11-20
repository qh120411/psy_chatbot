MAX_TURNS = 5  # chỉ nhớ 5 lượt hỏi-đáp gần nhất để prompt không quá dài

# LƯU Ý: lưu trong RAM của tiến trình. Tắt server hoặc reload là mất hết lịch sử.
# Chạy nhiều worker thì mỗi worker có lịch sử riêng. Đủ dùng khi học và thử nghiệm.
# Dữ liệu này gồm cả kết quả thang đo của người dùng, không ghi ra log hay file.
_sessions = {}   # session_id -> list message
_results = {}    # session_id -> kết quả thang đo gần nhất web gửi lên


def get_history(session_id):
    return _sessions.get(session_id, [])


def add_turn(session_id, question, answer):
    history = _sessions.setdefault(session_id, [])
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    # mỗi lượt gồm 2 message nên giữ MAX_TURNS * 2
    _sessions[session_id] = history[-MAX_TURNS * 2:]


def get_result(session_id):
    return _results.get(session_id)


def set_result(session_id, result):
    _results[session_id] = result
