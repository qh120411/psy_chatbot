import os
from pathlib import Path
from dotenv import load_dotenv

# BASE_DIR = thư mục gốc psybot (settings.py nằm trong config/ nên phải lên 2 cấp)
BASE_DIR = Path(__file__).parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")  # đọc file .env vào biến môi trường


class Config:
    # Giá trị thật nên đặt trong .env.
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL")
    LLM_MODEL: str = os.getenv("LLM_MODEL")
    DATA_DIR: Path = BASE_DIR / "data"                # chứa file .docx
    VECTORSTORE_DIR: Path = BASE_DIR / "vectorstore"  # Chroma lưu index ở đây

    # Domain web được phép gọi API (CORS), cách nhau bằng dấu phẩy.
    # LƯU Ý: không phải danh sách ai được dùng bot. Nó chỉ bảo trình duyệt cho phép
    # trang web ở domain đó gọi API này. Quên đổi thì web thật sẽ bị lỗi CORS.
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
