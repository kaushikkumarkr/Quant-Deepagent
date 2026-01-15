import pytest
from unittest.mock import MagicMock, patch
from src.rag.embeddings import LocalEmbeddings
from src.rag.chunking import RecursiveChunker, SECChunker
from src.rag.vectorstore import QuantChroma
from src.rag.retriever import HybridRetriever

# --- Embeddings Tests ---
@pytest.fixture
def mock_sentence_transformer():
    with patch('src.rag.embeddings.SentenceTransformer') as mock:
        yield mock

def test_embeddings_singleton(mock_sentence_transformer):
    e1 = LocalEmbeddings()
    e2 = LocalEmbeddings()
    assert e1 is e2

def test_embed_query(mock_sentence_transformer):
    embedder = LocalEmbeddings()
    # Mock encode output
    embedder.model.encode.return_value = MagicMock(tolist=lambda: [0.1, 0.2])
    
    vec = embedder.embed_query("test")
    assert vec == [0.1, 0.2]

# --- Chunking Tests ---
def test_recursive_chunker():
    chunker = RecursiveChunker(chunk_size=10, chunk_overlap=0)
    text = "Hello World"
    chunks = chunker.chunk(text, {"id": 1})
    # 'Hello World' is 11 chars, limit 10. Split depends on logic but should yield something.
    # Actually Recursive splitter tries to respect separators.
    # With default separators it might keep "Hello World" if it can't split better or split at space.
    assert len(chunks) >= 1
    assert chunks[0]['metadata']['id'] == 1

def test_sec_chunker_section_detection():
    chunker = SECChunker()
    text = "Item 1A. Risk Factors\nThis is risky business."
    chunks = chunker.chunk(text, {})
    assert len(chunks) > 0
    # It should detect RISK_FACTORS in the first chunk
    assert chunks[0]['metadata']['section'] == 'RISK_FACTORS'

# --- Vector Store Tests ---
@pytest.fixture
def mock_chroma():
    with patch('chromadb.PersistentClient') as mock:
        yield mock

@pytest.fixture
def mock_embedder_cls():
    with patch('src.rag.vectorstore.LocalEmbeddings') as mock:
        yield mock

def test_vectorstore_add(mock_chroma, mock_embedder_cls):
    # Mock embedding function
    mock_embedder_cls.return_value.embed_documents.return_value = [[0.1], [0.2]]
    
    vs = QuantChroma()
    chunks = [{'text': 'A', 'metadata': {}}, {'text': 'B', 'metadata': {}}]
    
    vs.add_documents(chunks)
    
    # Verify upsert called
    vs.collection.upsert.assert_called_once()
    args, kwargs = vs.collection.upsert.call_args
    assert len(kwargs['documents']) == 2
    assert len(kwargs['embeddings']) == 2

# --- Retriever Tests ---
def test_retriever(mock_chroma, mock_embedder_cls):
    retriever = HybridRetriever()
    
    # Mock query result
    retriever.vectorstore.collection.query.return_value = {
        'ids': [['1']],
        'documents': [['Doc 1']],
        'metadatas': [[{'ticker': 'AAPL'}]],
        'distances': [[0.1]]
    }
    
    results = retriever.retrieve("query", ticker="AAPL")
    assert len(results) == 1
    assert results[0]['text'] == 'Doc 1'
