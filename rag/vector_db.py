import chromadb
import json
import uuid
import os
from chromadb.utils import embedding_functions

chroma_path = os.getenv('CHROMA_PATH', 'data/chroma_db')
    
chroma_client = chromadb.PersistentClient(path=chroma_path)
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = chroma_client.get_or_create_collection(
    name="py_docs", 
    embedding_function=embedding_function,
    metadata={'description': "Python documentation embeddings"}
)

with open('data/docs/python_docs.json', 'r', encoding='utf-8') as f:
    documents = json.load(f)

def get_chunks(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk) > 100:
            chunks.append(chunk)
    
    return chunks

def test_retrieval(query: str, n_results: int = 3):
    print(f"Testing query: '{query}'")
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    print("\nTop results:")
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"\n{i+1}. {metadata['title']}")
        print(f"   URL: {metadata['url']}")
        print(f"   Content preview: {doc[:200]}...")

def process(documents, batch_size=100):
    all_chunks = []
    all_metadata = []
    all_ids = []
    
    print(f"Processing {len(documents)} documents...")
    
    for doc in documents:
        doc_chunks = get_chunks(doc['content']) 
        
        for i, chunk in enumerate(doc_chunks):
            all_chunks.append(chunk)
            all_ids.append(str(uuid.uuid4()))
            all_metadata.append({
                'title': doc['title'], 
                'url': doc['url'],
                'chunk_index': i
            })
    
    print(f"Created {len(all_chunks)} chunks. Adding to database...")
    
    for i in range(0, len(all_chunks), batch_size):
        batch_end = min(i + batch_size, len(all_chunks))
        
        collection.add(
            documents=all_chunks[i:batch_end],
            metadatas=all_metadata[i:batch_end],
            ids=all_ids[i:batch_end]
        )
            
    print(f"Vector database created! Total chunks: {collection.count()}")

def main():    
    process(documents)
    
    print("Testing retrieval system")
    
    test_retrieval("How do I open and read a file in Python?")
    test_retrieval("What is a list comprehension?")
    test_retrieval("How to use asyncio?")
    
if __name__ == "__main__":
    main()