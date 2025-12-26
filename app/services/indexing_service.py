import asyncio
import os
from typing import List
from pathlib import Path
from app.core.config import get_logger
from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as rest
from uuid import uuid4

logger = get_logger(__name__)

class IndexingService:
    def __init__(self):
        self.embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        print(f"QDRANT_URL from env: {os.getenv('QDRANT_URL')}")
        print(f"QDRANT_API_KEY from env: {os.getenv('QDRANT_API_KEY')}")
        print(f"QdrantClient params: url={os.getenv('QDRANT_URL')}, api_key={'*' * len(os.getenv('QDRANT_API_KEY', '')) if os.getenv('QDRANT_API_KEY') else 'None'}, prefer_grpc=False")
        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            prefer_grpc=False
        )
        logger.info("IndexingService initialized.")

    async def create_collection(self, collection_name: str = "book_content"):
        """Create a Qdrant collection for storing book content embeddings."""
        try:
            # Check if collection already exists
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if collection_name in collection_names:
                logger.info(f"Collection '{collection_name}' already exists.")
                return
            
            # Create collection with appropriate settings
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # Size of all-MiniLM-L6-v2 embeddings
                    distance=models.Distance.COSINE
                )
            )
            
            logger.info(f"Collection '{collection_name}' created successfully.")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise

    def extract_book_content(self) -> List[dict]:
        """
        Extract content from the book files (from Docusaurus docs directory).
        This method should read the MD/MDX files from the frontend/docs directory.
        """
        content_chunks = []
        
        # Look for book content in the frontend docs directory
        docs_path = Path("../../frontend/docs")
        
        if not docs_path.exists():
            # Try alternative path - relative to backend directory
            docs_path = Path("../frontend/docs")
            
        if not docs_path.exists():
            logger.error(f"Docs directory not found at {docs_path.absolute()}")
            return content_chunks

        # Process all MD/MDX files in the docs directory
        for file_path in docs_path.rglob("*"):
            if file_path.suffix.lower() in ['.md', '.mdx']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Simple chunking: split by paragraphs
                        paragraphs = content.split('\n\n')
                        
                        for i, paragraph in enumerate(paragraphs):
                            if len(paragraph.strip()) > 20:  # Only include substantial paragraphs
                                content_chunks.append({
                                    'id': str(uuid4()),
                                    'content': paragraph.strip(),
                                    'source_file': str(file_path.relative_to(docs_path)),
                                    'chunk_index': i
                                })
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
        
        logger.info(f"Extracted {len(content_chunks)} content chunks from book.")
        return content_chunks

    async def index_book_content(self, collection_name: str = "book_content"):
        """Index the book content into the Qdrant collection."""
        await self.create_collection(collection_name)
        
        content_chunks = self.extract_book_content()
        
        if not content_chunks:
            logger.warning("No content found to index.")
            return

        # Create embeddings for each content chunk
        points = []
        for chunk in content_chunks:
            try:
                # Generate embedding for the content
                embedding = self.embeddings_model.embed_query(chunk['content'])
                
                # Create a Qdrant point
                point = rest.PointStruct(
                    id=chunk['id'],
                    vector=embedding,
                    payload={
                        'content': chunk['content'],
                        'source_file': chunk['source_file'],
                        'chunk_index': chunk['chunk_index']
                    }
                )
                points.append(point)
            except Exception as e:
                logger.error(f"Error creating embedding for chunk {chunk['id']}: {e}")
        
        # Upload all points to Qdrant
        if points:
            try:
                self.qdrant_client.upload_points(
                    collection_name=collection_name,
                    points=points
                )
                logger.info(f"Successfully uploaded {len(points)} points to Qdrant.")
            except Exception as e:
                logger.error(f"Error uploading points to Qdrant: {e}")
                raise
        else:
            logger.warning("No valid points to upload to Qdrant.")

indexing_service = IndexingService()