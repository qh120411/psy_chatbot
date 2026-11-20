from openai import OpenAI
from config.settings import Config

# LƯU Ý: 9router chỉ cần link, không cần API key. Nhưng thư viện openai BẮT BUỘC
# có tham số api_key, nên điền chuỗi bất kỳ. Chuỗi này không được dùng để xác thực.
# Dùng thư viện "openai" không có nghĩa là gọi OpenAI: base_url mới quyết định gọi tới đâu.
client = OpenAI(base_url=Config.LLM_BASE_URL, api_key="not-needed")


def chat(messages):
    """Gửi danh sách messages cho LLM, trả về câu trả lời dạng chuỗi.
    messages có dạng: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    role: system = luật, user = người hỏi, assistant = bot đã trả lời trước đó."""
    res = client.chat.completions.create(
        model=Config.LLM_MODEL,
        messages=messages,
        temperature=0.3,  # thấp = ít sáng tạo, bám tài liệu hơn
    )
    return res.choices[0].message.content
