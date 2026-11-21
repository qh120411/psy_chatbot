import hmac
import logging
from datetime import date
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from AI.prompts import CRISIS_CONTACT
from config.settings import Config
from handlers.chat_handler import handle_chat

app = FastAPI(title="PsyBot")

if not CRISIS_CONTACT:
    logging.getLogger("uvicorn.error").warning(
        "CRISIS_CONTACT trong AI/prompts.py đang trống. Cần điền thông tin hỗ trợ khẩn cấp trước khi cho người dùng thật dùng."
    )

# LƯU Ý: không bật CORS. Trình duyệt KHÔNG gọi thẳng API này. Người dùng gọi backend web,
# backend web (đã kiểm tra đăng nhập, quyền sở hữu báo cáo và việc đồng ý chia sẻ) mới gọi chatbot
# kèm khóa X-API-Key. Nhờ vậy chatbot không cần tự xác thực người dùng.
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: Annotated[Optional[str], Depends(api_key_header)]):
    # compare_digest so sánh có độ dài thời gian cố định, tránh lộ khóa qua thời gian phản hồi
    if not key or not hmac.compare_digest(key.encode(), Config.API_KEY.encode()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sai hoặc thiếu X-API-Key")


# Chuỗi do bên ngoài gửi vào prompt: không cho ký tự điều khiển (xuống dòng, tab...) để tránh chèn chỉ dẫn
SAFE_TEXT = r"^[^\x00-\x1f\x7f]+$"


class Subscore(BaseModel):
    name: str = Field(min_length=1, max_length=100, pattern=SAFE_TEXT)
    score: float = Field(allow_inf_nan=False)


class ScaleResult(BaseModel):
    """Kết quả thang đo do BACKEND WEB tính sẵn. Bot chỉ giải thích, không tính lại.
    Bắt buộc: scale, score, level. Còn lại tùy chọn, có thì dùng, không có thì bỏ qua."""
    scale: str = Field(min_length=1, max_length=100, pattern=SAFE_TEXT)   # tên thang, vd "PHQ-9"
    score: float = Field(allow_inf_nan=False)                             # tổng điểm
    level: str = Field(min_length=1, max_length=50, pattern=SAFE_TEXT)    # mức web đã xếp, vd "Vừa"
    scale_version: Optional[str] = Field(default=None, max_length=100, pattern=SAFE_TEXT)
    completed_at: Optional[date] = None                                   # ngày làm, dạng 2026-11-20
    max_score: Optional[float] = Field(default=None, allow_inf_nan=False)
    subscores: Optional[list[Subscore]] = Field(default=None, max_length=20)


class ChatRequest(BaseModel):
    # Do backend web sinh, gắn với người dùng đã đăng nhập. Người dùng đổi hoặc ngừng chia sẻ thì dùng id mới.
    conversation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9._-]+$")
    message: str = Field(min_length=1, max_length=2000)
    # Chỉ gửi khi người dùng đã đồng ý chia sẻ, và gửi ở MỖI request trong lúc đang chia sẻ.
    # Chatbot không lưu kết quả giữa các request. Ngừng chia sẻ thì ngừng gửi trường này.
    result: Optional[ScaleResult] = None


@app.get("/health")
def health():
    return {"status": "ok"}


# LƯU Ý: dùng "def" thường (không async) vì gọi LLM và embedding là code chạy đồng bộ.
# FastAPI tự đưa vào thread riêng nên không làm treo các request khác.
@app.post("/chat", dependencies=[Depends(require_api_key)])
def chat(req: ChatRequest):
    result = req.result.model_dump(mode="json", exclude_none=True) if req.result else None
    return handle_chat(req.conversation_id, req.message, result)
