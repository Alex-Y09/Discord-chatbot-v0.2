"""
Conversation Summarizer - Creates summaries for long-term memory
"""

from transformers import pipeline
import logging
from typing import List

logger = logging.getLogger(__name__)

class ConversationSummarizer:
    """
    Summarizes conversations for compact long-term memory storage
    Uses BART-large-cnn for summarization
    """
    
    def __init__(self):
        self.summarizer = None
        logger.info("Conversation summarizer initialized")
    
    def load_model(self):
        """Load summarization model"""
        
        if self.summarizer is not None:
            logger.info("Summarizer already loaded")
            return
        
        try:
            logger.info("Loading BART summarization model...")
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if __import__('torch').cuda.is_available() else -1
            )
            logger.info("Summarizer loaded!")
            
        except Exception as e:
            logger.error(f"Failed to load summarizer: {e}", exc_info=True)
            raise
    
    def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 40
    ) -> str:
        """
        Summarize a conversation or text
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            min_length: Minimum length of summary
        
        Returns:
            Summary text
        """
        
        if self.summarizer is None:
            raise RuntimeError("Summarizer not loaded! Call load_model() first")
        
        try:
            # Clean input
            text = text.strip()
            
            # Skip if text is too short
            if len(text.split()) < min_length:
                logger.debug("Text too short to summarize, returning as-is")
                return text
            
            # Generate summary
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            summary_text = summary[0]['summary_text']
            
            logger.debug(f"Summarized {len(text)} chars to {len(summary_text)} chars")
            
            return summary_text
            
        except Exception as e:
            logger.error(f"Failed to summarize text: {e}", exc_info=True)
            # Return original text if summarization fails
            return text
    
    def summarize_conversation(
        self,
        messages: List[dict],
        max_length: int = 150
    ) -> str:
        """
        Summarize a list of conversation messages
        
        Args:
            messages: List of message dictionaries with 'author' and 'content'
            max_length: Maximum length of summary
        
        Returns:
            Summary of the conversation
        """
        
        # Format messages into text
        lines = []
        for msg in messages:
            author = msg.get('author', 'Unknown')
            content = msg.get('content', '')
            lines.append(f"{author}: {content}")
        
        text = "\n".join(lines)
        
        # Summarize
        return self.summarize(text, max_length=max_length)
    
    def unload_model(self):
        """Unload model from memory"""
        
        if self.summarizer is not None:
            del self.summarizer
            self.summarizer = None
            
            if __import__('torch').cuda.is_available():
                __import__('torch').cuda.empty_cache()
            
            logger.info("Summarizer unloaded from memory")
