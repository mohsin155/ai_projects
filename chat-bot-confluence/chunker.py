from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from pathlib import Path
import json

def load_and_chunk_docs():
    all_chunks = []

    with open('scraped_data.json', 'r', encoding='utf8') as f:
        scraped_data = json.load(f)

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100, length_function=len)

    for doc in scraped_data:
        full_text = f"Title: {doc.get('title', '')}\n\n{doc.get('full_text', '')}"
        chunks = splitter.split_text(full_text)
        for i, chunk in enumerate(chunks):
            chunk_doc = {
                'content': chunk,
                'source_url': doc.get('url', ''),
                'title': doc.get('title', ''),
                'chunk_id': f"{doc.get('title', '')}_{i}"
            }
            all_chunks.append(chunk_doc)
    with open('all_chunks.json', 'w', encoding='utf8') as f:
        json.dump(all_chunks, f)
    return all_chunks
