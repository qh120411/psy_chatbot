# PsyBot

Chatbot hỗ trợ người dùng trên website làm thang đo tâm lý. Bot trả lời dựa trên bộ tài liệu Word (RAG), có hai việc chính:

1. Hỏi đáp thông thường: hướng dẫn dùng website, giải thích thang đo, thuật ngữ.
2. Hỏi đáp có kết quả thang đo: giải thích điểm và mức phân loại mà web đã tính sẵn.

Repo này chỉ là backend (API). Giao diện chat nằm ở web riêng.

## Luồng hoạt động

Chuẩn bị dữ liệu (chạy một lần, chạy lại khi sửa tài liệu):

```
data/*.docx
    |  AI/loader.py       đọc chữ và bảng, giữ đúng thứ tự
    v
 văn bản
    |  AI/splitter.py     cắt thành đoạn 500 ký tự, chồng nhau 50
    v
 các chunk
    |  AI/embedder.py     đổi mỗi chunk thành vector
    v
 vectorstore/ (Chroma)
```

Khi có người dùng chat:

```
Người dùng
    |
    v
Backend web   (kiểm tra đăng nhập, người dùng có đồng ý chia sẻ kết quả không)
    |  POST /chat  +  header X-API-Key
    v
app.py        (kiểm tra khóa, kiểm tra dữ liệu gửi lên)
    |
    v
handlers/chat_handler.py
    |
    |-- có dấu hiệu tự hại? --(có)--> trả câu an toàn soạn sẵn, KHÔNG gọi LLM
    |
    |  (không)
    v
AI/rag_pipeline.py
    |-- AI/retriever.py          câu hỏi -> vector -> Chroma lấy 3 đoạn gần nhất,
    |                            đoạn nào xa quá ngưỡng thì bỏ
    |-- AI/prompts.py            ghép: luật + tài liệu + kết quả thang đo + câu hỏi
    |-- services/llm_service.py  gọi LLM
    v
 câu trả lời + nguồn   --> backend web --> người dùng
```

## Cách chạy

Cần Python 3.10 trở lên và một LLM gọi được theo kiểu OpenAI (qua 9router hoặc gọi thẳng nhà cung cấp, xem phần cấu hình `.env`).

1. Cài thư viện:

```
pip install -r requirements.txt
```

2. Tạo file `.env` ở thư mục gốc (xem phần cấu hình `.env` bên dưới).

3. Bỏ file Word vào `data/`, rồi tạo index:

```
python build_index.py
```

Lần đầu chạy sẽ tải model embedding, mất vài phút. Sửa hoặc thêm tài liệu thì chạy lại lệnh này.

4. Chạy server:

```
run_bot.bat
```

hoặc

```
uvicorn app:app --port 8000
```

Mở `http://localhost:8000/docs` để thử. Bấm Authorize, nhập `API_KEY`, rồi gọi `/chat`.

Chạy thử từng phần (không cần bật server):

```
python -m AI.retriever       # tìm đoạn tài liệu cho một câu hỏi mẫu
python -m AI.rag_pipeline    # chạy cả chuỗi, cần gọi được LLM
```

## Cấu hình .env

File `.env` không đưa lên git. Có hai loại khóa, đừng nhầm:

- `API_KEY`: khóa riêng của hệ thống này, dùng chung giữa backend web và chatbot (backend web gửi trong header `X-API-Key`). Tự tạo bằng lệnh `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Bắt buộc.
- `LLM_API_KEY`: khóa của nhà cung cấp LLM (vd OpenAI). Chỉ cần khi gọi thẳng nhà cung cấp.

Chọn một trong hai cách.

### Cách 1: gọi qua 9router (không cần khóa LLM)

```
LLM_BASE_URL=http://<địa-chỉ-9router>:<cổng>/v1
LLM_MODEL=<tên-model>
API_KEY=<khóa-tự-tạo>
```

- `LLM_BASE_URL`: địa chỉ 9router, có `/v1` ở cuối.
- `LLM_MODEL`: tên model đúng như 9router trả về ở `<LLM_BASE_URL>/models`.
- Không điền `LLM_API_KEY`.

### Cách 2: gọi thẳng nhà cung cấp LLM (điền API key)

Ví dụ với OpenAI:

```
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=<tên-model>
LLM_API_KEY=<api-key-lấy-từ-nhà-cung-cấp>
API_KEY=<khóa-tự-tạo>
```

- `LLM_BASE_URL`: địa chỉ API của nhà cung cấp. Nhà cung cấp khác thì dùng địa chỉ họ công bố cho kiểu OpenAI (xem tài liệu của họ). Code dùng thư viện `openai`, nên nhà cung cấp phải hỗ trợ kiểu gọi này.
- `LLM_MODEL`: tên model theo nhà cung cấp.
- `LLM_API_KEY`: API key lấy trong trang quản lý của nhà cung cấp.
- Phải điền `LLM_BASE_URL`, kể cả khi dùng OpenAI. Để trống thì server không khởi động.

Thiếu `LLM_BASE_URL`, `LLM_MODEL` hoặc `API_KEY` thì server báo lỗi ngay khi khởi động.

Lưu ý khi dùng Cách 2: câu hỏi và kết quả thang đo của người dùng sẽ được gửi tới nhà cung cấp LLM đó.

## API

`GET /health` trả `{"status": "ok"}`, không cần khóa.

`POST /chat` cần header `X-API-Key`.

```json
{
  "conversation_id": "do backend web sinh cho mỗi người dùng",
  "message": "Kết quả của mình có ý nghĩa gì?",
  "result": {
    "scale": "PHQ-9",
    "score": 12,
    "level": "Vừa",
    "scale_version": "bản tiếng Việt",
    "completed_at": "2026-11-20",
    "max_score": 27,
    "subscores": [{"name": "Cảm xúc", "score": 7}]
  }
}
```

- Bắt buộc: `conversation_id`, `message`. Trong `result` thì `scale`, `score`, `level` bắt buộc, còn lại tùy chọn.
- `result` chỉ gửi khi người dùng đã đồng ý chia sẻ. Gửi ở mỗi request trong lúc đang chia sẻ.
- Trả về:

```json
{ "answer": "...", "sources": ["ten_file.docx"] }
```

`sources` chỉ gồm tài liệu mà bot thực sự dùng, có thể rỗng.

Lỗi: 401 là sai hoặc thiếu khóa, 422 là dữ liệu gửi lên không hợp lệ.

## Cây thư mục

```
psybot/
├── AI/
│   ├── loader.py          đọc file .docx (đoạn văn và bảng, đúng thứ tự)
│   ├── splitter.py        cắt văn bản thành chunk
│   ├── embedder.py        đổi chữ thành vector
│   ├── vector_store.py    lưu và tìm trong Chroma
│   ├── retriever.py       lấy đoạn liên quan, lọc theo ngưỡng
│   ├── prompts.py         luật cho LLM, câu trả lời soạn sẵn, ghép prompt
│   ├── safety.py          phát hiện dấu hiệu tự hại (từ khóa)
│   └── rag_pipeline.py    tìm đoạn -> ghép prompt -> hỏi LLM -> tách nguồn
├── config/
│   └── settings.py        đọc .env
├── handlers/
│   └── chat_handler.py    xử lý một lượt chat
├── services/
│   ├── llm_service.py     gọi LLM
│   └── session_service.py lịch sử hội thoại (lưu trong RAM)
├── data/                  tài liệu Word (có test.docx là file mẫu)
├── vectorstore/           index Chroma, tự sinh, không commit
├── app.py                 FastAPI: /chat, /health
├── build_index.py         tạo index từ data/
├── run_bot.bat            chạy server
├── test.py                tạo file mẫu data/test.docx
├── requirements.txt
└── .env                   cấu hình, không commit
```

## Lưu ý

- Danh sách từ khóa trong `AI/safety.py` và các câu soạn sẵn trong `AI/prompts.py` (`CRISIS_REPLY`, `FALLBACK_REPLY`) là bản nháp, cần chuyên gia tâm lý duyệt.
- `MAX_DISTANCE = 0.18` trong `AI/retriever.py` là giá trị tạm, đo trên file mẫu. Khi có tài liệu thật cần đo lại. Thấp quá thì bot hay nói "chưa có thông tin", cao quá thì bot lấy cả đoạn không liên quan.
- Tài liệu Word nên chia mỗi thang đo một mục, ghi tên thang và tên các mức giống với những gì web gửi (vd "Vừa" thì ghi "Vừa").
- Chatbot không bật CORS và không đăng nhập người dùng. Trình duyệt phải gọi qua backend web, backend web mới gọi chatbot kèm `X-API-Key`.
- Chatbot không lưu kết quả thang đo giữa các request. Người dùng ngừng chia sẻ thì web ngừng gửi `result`. Muốn bot quên luôn lịch sử cũ thì web đổi sang `conversation_id` mới.
- Lịch sử hội thoại lưu trong RAM, tắt server là mất.
- Bot chỉ trả lời từ tài liệu. Tài liệu không có thì bot nói chưa có thông tin, nên với tài liệu ít, bot sẽ hay trả lời như vậy.
