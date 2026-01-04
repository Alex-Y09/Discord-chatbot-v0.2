"""
Long-Term Memory - RAG-based persistent memory using ChromaDB
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LongTermMemory:
    """
    Persistent memory storage using vector database (RAG)
    Stores conversation history and personality-relevant information
    """
    
    def __init__(self, db_path: str = "data/vector_db"):
        """
        Initialize long-term memory
        
        Args:
            db_path: Path to ChromaDB database directory
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self.collection = None
        self.next_id = 0
        
        logger.info(f"Long-term memory initialized (db_path={db_path})")
    
    async def initialize(self):
        """Initialize ChromaDB client and collection"""
        
        try:
            # Create ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="discord_memories",
                metadata={"description": "Discord conversation memories"}
            )
            
            # Set next_id based on existing documents
            existing_docs = self.collection.count()
            self.next_id = existing_docs
            
            logger.info(f"Long-term memory ready ({existing_docs} existing memories)")
            
        except Exception as e:
            logger.error(f"Failed to initialize long-term memory: {e}", exc_info=True)
            raise
    
    async def add_memory(
        self,
        content: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add a memory to the database
        
        Args:
            content: Memory content (conversation snippet, important fact, etc.)
            metadata: Optional metadata (channel, timestamp, etc.)
        
        Returns:
            Memory ID
        """
        
        if self.collection is None:
            raise RuntimeError("Long-term memory not initialized! Call initialize() first")
        
        try:
            # Generate ID
            memory_id = f"mem_{self.next_id}"
            self.next_id += 1
            
            # Add timestamp to metadata
            if metadata is None:
                metadata = {}
            metadata['timestamp'] = datetime.now().isoformat()
            
            # Add to collection
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[memory_id]
            )
            
            logger.debug(f"Memory added: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to add memory: {e}", exc_info=True)
            raise
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> List[str]:
        """
        Retrieve relevant memories based on query
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of relevant memory contents
        """
        
        if self.collection is None:
            raise RuntimeError("Long-term memory not initialized! Call initialize() first")
        
        try:
            # Query collection
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filter_metadata
            )
            
            # Extract documents
            if results and results['documents']:
                memories = results['documents'][0]
                logger.debug(f"Retrieved {len(memories)} memories for query: {query[:50]}...")
                return memories
            else:
                return []
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}", exc_info=True)
            return []
    
    async def get_recent_memories(
        self,
        count: int = 10
    ) -> List[Dict]:
        """
        Get the most recent memories
        
        Args:
            count: Number of memories to retrieve
        
        Returns:
            List of memory dictionaries with content and metadata
        """
        
        if self.collection is None:
            raise RuntimeError("Long-term memory not initialized! Call initialize() first")
        
        try:
            # Get all memories (ChromaDB doesn't have native "recent" query)
            # This is a simplified implementation
            results = self.collection.get(
                limit=count
            )
            
            memories = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents']):
                    memory = {
                        'content': doc,
                        'metadata': results['metadatas'][i] if results['metadatas'] else {}
                    }
                    memories.append(memory)
            
            logger.debug(f"Retrieved {len(memories)} recent memories")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get recent memories: {e}", exc_info=True)
            return []
    
    def clear_all(self):
        """Clear all memories (use with caution!)"""
        
        if self.client is None:
            return
        
        try:
            self.client.reset()
            self.collection = self.client.get_or_create_collection(
                name="discord_memories",
                metadata={"description": "Discord conversation memories"}
            )
            self.next_id = 0
            
            logger.warning("All long-term memories cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear memories: {e}", exc_info=True)
    
    def get_stats(self) -> Dict:
        """
        Get memory statistics
        
        Returns:
            Dictionary with stats about memory database
        """
        
        if self.collection is None:
            return {'status': 'not_initialized'}
        
        try:
            count = self.collection.count()
            return {
                'status': 'active',
                'total_memories': count,
                'db_path': str(self.db_path)
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}", exc_info=True)
            return {'status': 'error', 'error': str(e)}
