import faiss
import pickle
from embeddings import get_model
from llm_service import get_llm_response

def query_index(query, chunks, index_path="vectorstore/faiss_index.index", meta_path="vectorstore/metadata.pkl", top_k=3):
    model = get_model()
    q_vector = model.encode([query])
    faiss.normalize_L2(q_vector.astype('float32'))
    index = faiss.read_index(index_path)
    scores, indices = index.search(q_vector.astype('float32'), top_k)
    relevant_docs = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(chunks) :
            doc = chunks[idx].copy()
            doc['similarity'] = float(score)
            relevant_docs.append(doc)
        # If nothing relevant, skip context
        if not relevant_docs:
            return f"User: {query}\nAssistant: [No context found, respond naturally to the question.]"

        # Build context
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"Source: {doc['title']}\nContent: {doc['content']}\n")

        context = "\n---\n".join(context_parts)
        user_prompt = (
            f"Based on the following context, answer the question:\n"
            f"Context:\n{context}\n"
            f"Question: {query}\n"
        )

    #llm_response = get_llm_response(link_system_prompt, user_prompt)
    #print(f"Response from llm : {llm_response}")
    return user_prompt
