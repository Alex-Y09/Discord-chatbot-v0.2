"""
Short-Term Memory - Sliding window conversation history
"""

from collections import deque
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ShortTermMemory:
    """
    Maintains recent conversation history per channel
    Uses sliding window to keep last N messages
    """
    
    def __init__(self, window_size: int = 20):
        """
        Initialize short-term memory
        
        Args:
            window_size: Number of recent messages to keep per channel
        """
        self.window_size = window_size
        
        # Store messages per channel
        # Format: {channel_id: deque([{author, content, timestamp}, ...])}
        self.channels = {}
        
        logger.info(f"Short-term memory initialized (window_size={window_size})")
    
    def add_message(self, author: str, content: str, channel_id: int):
        """
        Add a message to channel history
        
        Args:
            author: Message author's display name
            content: Message content
            channel_id: Discord channel ID
        """
        
        # Initialize channel if needed
        if channel_id not in self.channels:
            self.channels[channel_id] = deque(maxlen=self.window_size)
        
        # Add message
        message = {
            'author': author,
            'content': content,
            'timestamp': datetime.now()
        }
        
        self.channels[channel_id].append(message)
        
        logger.debug(f"Message added to channel {channel_id} (size: {len(self.channels[channel_id])})")
    
    def get_context(
        self,
        channel_id: int,
        max_messages: Optional[int] = None
    ) -> str:
        """
        Get recent conversation context for a channel
        
        Args:
            channel_id: Discord channel ID
            max_messages: Max messages to include (default: all in window)
        
        Returns:
            Formatted conversation context string
        """
        
        if channel_id not in self.channels:
            return ""
        
        messages = self.channels[channel_id]
        
        # Limit messages if requested
        if max_messages:
            messages = list(messages)[-max_messages:]
        
        # Format as conversation
        lines = []
        for msg in messages:
            lines.append(f"{msg['author']}: {msg['content']}")
        
        context = "\n".join(lines)
        
        logger.debug(f"Retrieved context for channel {channel_id}: {len(messages)} messages")
        
        return context
    
    def get_recent_messages(
        self,
        channel_id: int,
        count: int = 5
    ) -> List[Dict]:
        """
        Get the N most recent messages as structured data
        
        Args:
            channel_id: Discord channel ID
            count: Number of messages to retrieve
        
        Returns:
            List of message dictionaries
        """
        
        if channel_id not in self.channels:
            return []
        
        messages = list(self.channels[channel_id])[-count:]
        return messages
    
    def clear_channel(self, channel_id: int):
        """
        Clear all messages for a channel
        
        Args:
            channel_id: Discord channel ID
        """
        
        if channel_id in self.channels:
            self.channels[channel_id].clear()
            logger.info(f"Cleared memory for channel {channel_id}")
    
    def clear_all(self):
        """Clear all channel memories"""
        self.channels.clear()
        logger.info("Cleared all short-term memory")
    
    def get_stats(self) -> Dict:
        """
        Get memory statistics
        
        Returns:
            Dictionary with stats about memory usage
        """
        
        return {
            'total_channels': len(self.channels),
            'window_size': self.window_size,
            'channels': {
                channel_id: len(messages)
                for channel_id, messages in self.channels.items()
            }
        }
