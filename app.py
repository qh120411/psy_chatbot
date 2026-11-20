import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from AI.prompts import CRISIS_CONTACT
from config.settings import Config
from handlers.chat_handler import handle_chat

app = FastAPI(title="PsyBot")

if not CRISIS_CONTACT:
    logging.getLogger("uvicorn.error").warning(
        "CRISIS_CONTACT trong AI/prompts.py đang trống. Cần điền thông tin hỗ trợ khẩn cấp trước khi cho người dùng thật dùng."
    )

# CORS: cho phép web của bạn gọi API này từ trình duyệt.
# LƯU Ý: CORS chỉ là rào của trình duyệt, không phải bảo mật thật. Ai gọi thẳng bằng
# Postman hay curl vẫn gọi được. Nếu public ra internet, cần thêm giới hạn lượt gọi hoặc key.
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class ScaleResult(BaseModel):
    """Kết quả thang đo do WEB tính sẵn. Bot chỉ giải thích, không tính lại."""
    scale: str = Field(max_length=100)               # tên thang, vd "PHQ-9"
    score: Optional[float] = None                    # tổng điểm
    level: Optional[str] = Field(default=None, max_length=100)    # mức độ web đã xếp, vd "Trung bình"
    report: Optional[str] = Field(default=None, max_length=5000)  # báo cáo chữ của web (nếu có)


class ChatRequest(BaseModel):
    session_id: str = Field(max_length=100)  # web tự sinh cho mỗi người dùng (vd lưu trong localStorage)
    message: str = Field(max_length=2000)
    result: Optional[ScaleResult] = None     # gửi 1 lần khi vừa làm xong thang đo


@app.get("/health")
def health():
    return {"status": "ok"}


# LƯU Ý: dùng "def" thường (không async) vì gọi LLM và embedding là code chạy đồng bộ.
# FastAPI tự đưa vào thread riêng nên không làm treo các request khác.
@app.post("/chat")
def chat(req: ChatRequest):
    result = req.result.model_dump() if req.result else None
    return handle_chat(req.session_id, req.message, result)
