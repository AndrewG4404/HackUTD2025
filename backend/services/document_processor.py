"""
Simple document processing for RAG
Reads PDFs and extracts text for agent context
"""
import PyPDF2
from pathlib import Path
from typing import List, Dict


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Extracted text content
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""


def extract_texts_from_files(file_infos: List[Dict]) -> str:
    """
    Extract and concatenate text from multiple files.
    
    Args:
        file_infos: List of file info dicts with 'path' and 'name'
    
    Returns:
        Concatenated text from all files
    """
    all_text = ""
    
    for file_info in file_infos:
        file_path = file_info.get("path", "")
        if not file_path or not Path(file_path).exists():
            continue
        
        if file_path.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
            all_text += f"\n\n=== Document: {file_info.get('name', 'Unknown')} ===\n{text}"
    
    return all_text


def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.
    Simple sliding window approach for MVP.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks


def retrieve_relevant_context(query: str, documents: str, max_context: int = 4000) -> str:
    """
    Simple context retrieval for MVP.
    For hackathon speed, just return first N characters.
    
    In production, you would:
    1. Chunk documents
    2. Embed query and chunks
    3. Find top-k similar chunks
    4. Return concatenated relevant context
    
    Args:
        query: Search query
        documents: Full document text
        max_context: Maximum context length
    
    Returns:
        Relevant context
    """
    # MVP: Simple truncation
    # This is intentionally simple for hackathon speed
    if len(documents) <= max_context:
        return documents
    
    # Try to find query terms in document and return surrounding context
    query_lower = query.lower()
    doc_lower = documents.lower()
    
    # Find first occurrence of query terms
    for word in query_lower.split():
        if len(word) > 3:  # Skip short words
            idx = doc_lower.find(word)
            if idx != -1:
                # Return context around the match
                start = max(0, idx - max_context // 2)
                end = min(len(documents), idx + max_context // 2)
                return documents[start:end]
    
    # Fallback: return first chunk
    return documents[:max_context]

