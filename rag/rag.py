import chromadb
import httpx
import os
import asyncio
from chromadb.utils import embedding_functions
chroma_path = os.getenv('CHROMA_PATH', 'data/chroma_db')
    
client = chromadb.PersistentClient(path=chroma_path)
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_collection(
    name='py_docs',
    embedding_function=embedding_function
)

ollama_url = 'http://host.docker.internal:11434'
ollama_model = 'llama3.2'

def retrieve(query, n_top_results):
    results = collection.query(query_texts=[query], n_results=n_top_results)
    context = []
    
    for doc, metadata, distance in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
        context.append({
            'content': doc,
            'title': metadata['title'],
            'url': metadata['url'],
            'distance': distance
        })
    
    return context

def check_relevance(query, context, threshold=0.5):
    if not context:
        return False, "Not found"
    best_distance = context[0]['distance']
    if best_distance > threshold:
        return False, f"Best relevance too low (distance: {best_distance:.3f})"
    return True, "Relevant context found"

def system_prompt(query, context):
    context_text = "\n\n".join([f"[Source: {i['title']}]\n{i['content']}" for i in context])
    
    prompt = f"""You are a helpful Python programming assistant. Answer the user's question based on the provided Python documentation context.

Context from Python Documentation:
{context_text}

User Question: {query}

INSTRUCTIONS:
1. Base your answer STRICTLY on the provided sources
2. Cite sources using [SOURCE N] format when making specific claims
3. If you use code examples, ensure they're from or consistent with the sources
4. If the sources don't contain sufficient information, explicitly state: "The provided documentation doesn't contain enough information about X"
5. Be concise but complete (aim for 300-400 words)
6. Structure your answer with clear sections if appropriate
7. DO NOT add information not present in the sources

Answer:"""
    
    return prompt

async def generate_answer(query):
    context = retrieve(query, 5)
    prompt = system_prompt(query, context)
    is_relevant, relevance_msg = check_relevance(query, context)
    if not is_relevant:
        return {
            'answer': f"⚠️ I cannot answer this question. Reason: {relevance_msg}\n\n"
                     f"I can only answer questions about Python programming based on the official Python documentation. "
                     f"Your question appears to be about a topic not covered in my knowledge base.",
            'sources': [],
            'context_chunks': context,
            'validation_issues': [relevance_msg]
        }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 500
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            answer = result.get('response', 'No response generated')
        
        sources = list({chunk['url'] for chunk in context[:3]})
        
        return {
            'answer': answer,
            'sources': sources,
            'context_chunks': context
        }
        
    except httpx.ConnectError:
        return {
            'answer': "Cannot connect to Ollama. Make sure Ollama is running (ollama serve)",
            'sources': [],
            'context_chunks': []
        }
    except Exception as e:
        return {
            'answer': f"Encountered an error: {str(e)}",
            'sources': [],
            'context_chunks': []
        }

async def answer(query):
    result = await generate_answer(query)
    ans = result['answer']
    sources = result['sources']
    
    print(f"Query: {query}")
    print(f"Retrieved {len(result['context_chunks'])} chunks")
    print(f"Answer length: {len(ans)} chars")
    
    if sources:
        ans += "\n\nSources:\n" + "\n".join(f"- {url}" for url in sources[:3])
    
    return ans

async def test_rag():
    test_questions = [
        "How do I open and read a file in Python?",  # Valid
        "How pytorch works?",  # Invalid - not in docs
        "What is a list comprehension?",  # Valid
        "How to use React hooks?",  # Invalid - not Python
        "Explain Python decorators"  # Valid (if in docs)
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        print(f"{'='*60}")
        ans = await answer(question)
        print(f"A: {ans}")

if __name__ == "__main__":
    asyncio.run(test_rag())