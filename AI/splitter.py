from AI.loader import load_all
from config.settings import Config

def split_text(text, size= 500, overlap=50) :
    chunks = []
    start = 0
    while start < len(text):
        end = start+size
        chunk = text[start:end] # cắt từ start đến end
        chunks.append(chunk)
        start = end - overlap  # nhích tới chunk kế tiếp
    return chunks

def split_docs(docs, size = 500, overlap = 50):
    result = []
    for doc in docs:
        for i, chunk in enumerate(split_text(doc["text"], size, overlap)):
          result.append({"source": doc["source"], "chunk_id": i, "text": chunk})
    return result  

if __name__ == "__main__":
    from AI.loader import load_all
    from config.settings import Config
    chunks = split_docs(load_all(Config.DATA_DIR), size=100, overlap=20)
    print("Số chunk:", len(chunks))
    for c in chunks[:3]:
        print(c)
