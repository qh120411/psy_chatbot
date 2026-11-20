from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-small"
_model = None   # nạp model 1 lần, dùng lại

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def embed_passages(texts):
    # texts: list các chunk. Thêm "passage: " vào đầu mỗi chunk
    texts = ["passage: " + t for t in texts]
    return get_model().encode(texts, normalize_embeddings=True).tolist()

def embed_query(question):
    vec = get_model().encode(["query: " + question], normalize_embeddings=True)
    return vec[0].tolist()

if __name__ == "__main__":
    vecs = embed_passages(["Bot hoạt động từ 8h đến 17h", "Hôm nay trời đẹp"])
    q = embed_query("Mấy giờ bot làm việc?")
    print("Số chiều:", len(q))   # model small ra 384

    # độ giống = tích vô hướng (vì đã normalize)
    for v in vecs:
        print(sum(a * b for a, b in zip(q, v)))
