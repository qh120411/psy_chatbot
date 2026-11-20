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
        raise RuntimeError(f"Thiếu biến {name} trong file .env (xem mẫu ở .env.example)")
    return value


class Config:
    LLM_BASE_URL: str = _require("LLM_BASE_URL")
    LLM_MODEL: str = _require("LLM_MODEL")

    DATA_DIR: Path = BASE_DIR / "data"                # chứa file .docx
    VECTORSTORE_DIR: Path = BASE_DIR / "vectorstore"  # Chroma lưu index ở đây

    # Domain web được phép gọi API (CORS), cách nhau bằng dấu phẩy.
    # LƯU Ý: không phải danh sách ai được dùng bot. Nó chỉ bảo trình duyệt cho phép
    # trang web ở domain đó gọi API này. Quên đổi thì web thật sẽ bị lỗi CORS.
    ALLOWED_ORIGINS: list = [
        o.strip()
        for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if o.strip()
    ]
