import os
from pathlib import Path
from dotenv import load_dotenv

# BASE_DIR = thư mục gốc psybot (settings.py nằm trong config/ nên phải lên 2 cấp)
BASE_DIR = Path(__file__).parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")  # đọc file .env vào biến môi trường


def _require(name):
    """Biến bắt buộc phải có trong .env. Thiếu thì dừng ngay với thông báo rõ ràng.

    LƯU Ý: nếu LLM_BASE_URL bị trống, thư viện openai sẽ TỰ gọi tới api.openai.com,
    tức là gửi câu hỏi và kết quả thang đo của người dùng tới nơi mình không định gửi.
    Vì vậy không để giá trị mặc định cho biến này."""
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Thiếu biến {name} trong file .env")
    return value


class Config:
    LLM_BASE_URL: str = _require("LLM_BASE_URL")
    LLM_MODEL: str = _require("LLM_MODEL")

    # API key của nhà cung cấp LLM (OpenAI...). KHÔNG bắt buộc: gọi qua 9router không cần key thì để trống.
    # Đây KHÁC với API_KEY bên dưới (khóa giữa backend web và chatbot).
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "").strip()

    # Khóa bí mật dùng chung giữa backend web và chatbot. Backend web gửi trong header X-API-Key.
    # Chỉ có 1 khóa cho cả hệ thống (không phải mỗi người dùng một khóa), không đưa xuống trình duyệt.
    API_KEY: str = _require("API_KEY")

    DATA_DIR: Path = BASE_DIR / "data"                # chứa file .docx
    VECTORSTORE_DIR: Path = BASE_DIR / "vectorstore"  # Chroma lưu index ở đây
