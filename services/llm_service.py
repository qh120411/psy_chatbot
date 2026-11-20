import logging

from openai import OpenAI
from config.settings import Config

logger = logging.getLogger(__name__)

# LƯU Ý: 9router chỉ cần link, không cần API key. Nhưng thư viện openai BẮT BUỘC
# có tham số api_key, nên điền chuỗi bất kỳ. Chuỗi này không được dùng để xác thực.
# Dùng thư viện "openai" không có nghĩa là gọi OpenAI: base_url mới quyết định gọi tới đâu.
#
# timeout / max_retries: mặc định của thư viện là chờ 600 giây và thử lại 2 lần,
# nên khi 9router chết một request có thể treo ~30 phút. Đặt ngắn lại để web nhận lỗi sớm.
client = OpenAI(
    base_url=Config.LLM_BASE_URL,
    api_key="not-needed",
    timeout=30,
    max_retries=1,
)


class LLMError(Exception):
    """Gọi LLM thất bại (mất kết nối, quá thời gian, 9router báo lỗi...)."""


def chat(messages):
    """Gửi danh sách messages cho LLM, trả về câu trả lời dạng chuỗi.
    messages có dạng: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    role: system = luật, user = người hỏi, assistant = bot đã trả lời trước đó.

    Trả về "" nếu LLM không trả nội dung (vd bộ lọc an toàn của Gemini chặn câu trả lời).
    Ném LLMError nếu không gọi được LLM."""
    try:
        res = client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=messages,
            temperature=0.3,  # thấp = ít sáng tạo, bám tài liệu hơn
        )
    except Exception as e:
        # Chỉ ghi loại lỗi, KHÔNG ghi messages vì chứa câu hỏi và kết quả thang đo của người dùng
        logger.error("Gọi LLM thất bại: %s", type(e).__name__)
        raise LLMError from e

    if not res.choices:
        return ""
    return (res.choices[0].message.content or "").strip()
