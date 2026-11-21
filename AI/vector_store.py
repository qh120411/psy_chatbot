import chromadb
from config.settings import Config

COLLECTION_NAME = "psybot"

def get_collection():
    # PersistentClient: lưu xuống ổ đĩa, tắt chương trình vẫn còn dữ liệu
    client = chromadb.PersistentClient(path=str(Config.VECTORSTORE_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},   # đo độ giống bằng cosine
    )

def reset_collection():
    # Xóa collection cũ để build lại từ đầu, tránh bị trùng dữ liệu
    client = chromadb.PersistentClient(path=str(Config.VECTORSTORE_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass   # chưa có collection thì bỏ qua
    return get_collection()

def add_chunks(chunks, vectors):
    # chunks: list dict {"source", "chunk_id", "text"}
    # vectors: list vector, cùng thứ tự với chunks
    col = get_collection()
    col.add(
        ids=[f'{c["source"]}-{c["chunk_id"]}' for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=vectors,
        metadatas=[{"source": c["source"]} for c in chunks],
    )

def search(query_vector, k=3):
    col = get_collection()
    res = col.query(query_embeddings=[query_vector], n_results=k)
    # res là dict, mỗi key là list lồng list (do có thể hỏi nhiều câu cùng lúc)
    # distance: khoảng cách cosine, càng NHỎ càng giống (0 = giống hệt)
    return [
        {"text": doc, "source": meta["source"], "distance": dist}
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]
