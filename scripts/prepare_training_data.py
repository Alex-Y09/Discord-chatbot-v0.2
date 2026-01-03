"""
Training Data Preparation Script
Filters and formats raw Discord messages into training-ready format

Filters:
- Bot commands (!, /, .)
- Emoji-only messages
- Single-word replies
- Duplicates
- System messages

Output Format: Mistral instruction format with conversation context
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/prep.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path("data")
RAW_MESSAGES_FILE = DATA_DIR / "raw_messages.jsonl"
TRAINING_DATA_FILE = DATA_DIR / "training_data.jsonl"

# System prompt
SYSTEM_PROMPT = "You are sususbot, a friendly Discord chatbot with a casual, playful personality. You chat naturally like a regular Discord user, using informal language, occasional slang, and emojis. You're helpful but keep things light and fun."

# Bot identification (update with your bot's actual user ID)
BOT_USER_ID = None  # Will be auto-detected


class DataPreparator:
    """Prepares Discord messages for LLM training"""
    
    def __init__(self):
        self.raw_messages = []
        self.filtered_messages = []
        self.training_examples = []
        self.bot_user_id = None
        self.bot_username = None
        
        # Statistics
        self.stats = {
            'total_raw': 0,
            'filtered_commands': 0,
            'filtered_emoji_only': 0,
            'filtered_single_word': 0,
            'filtered_duplicates': 0,
            'filtered_system': 0,
            'total_filtered': 0,
            'training_examples': 0,
        }
    
    def load_messages(self):
        """Load raw messages from file"""
        logger.info(f"Loading messages from: {RAW_MESSAGES_FILE}")
        
        try:
            with open(RAW_MESSAGES_FILE, 'r', encoding='utf-8') as f:
                self.raw_messages = [json.loads(line) for line in f]
            
            self.stats['total_raw'] = len(self.raw_messages)
            logger.info(f"Loaded {self.stats['total_raw']:,} messages")
            
            # Auto-detect bot user ID (most frequent author)
            author_counts = defaultdict(int)
            author_names = {}
            for msg in self.raw_messages:
                author_id = msg['author_id']
                author_counts[author_id] += 1
                author_names[author_id] = msg['author_name']
            
            # Assume bot is the most frequent author
            self.bot_user_id = max(author_counts, key=author_counts.get)
            self.bot_username = author_names[self.bot_user_id]
            
            logger.info(f"Detected bot: {self.bot_username} (ID: {self.bot_user_id})")
            logger.info(f"Bot message count: {author_counts[self.bot_user_id]:,} ({author_counts[self.bot_user_id]/self.stats['total_raw']*100:.1f}%)")
        
        except FileNotFoundError:
            logger.error(f"File not found: {RAW_MESSAGES_FILE}")
            logger.error("Run backfill_messages.py first!")
            raise
        except Exception as e:
            logger.error(f"Error loading messages: {e}")
            raise
    
    def _is_command(self, content: str) -> bool:
        """Check if message is a bot command"""
        if not content:
            return False
        return content.strip().startswith(('!', '/', '.', '$'))
    
    def _is_emoji_only(self, content: str) -> bool:
        """Check if message is only emojis/reactions"""
        if not content:
            return True
        
        # Remove emojis and whitespace
        text_only = re.sub(r'[^\w\s]', '', content).strip()
        return len(text_only) == 0
    
    def _is_single_word(self, content: str) -> bool:
        """Check if message is a single word"""
        if not content:
            return True
        
        words = content.strip().split()
        return len(words) <= 1
    
    def _is_system_message(self, msg: Dict) -> bool:
        """Check if message is a system message"""
        return msg['type'] != 'MessageType.default'
    
    def filter_messages(self):
        """Apply filters to raw messages"""
        logger.info("Applying filters...")
        
        seen_content = set()
        
        for msg in self.raw_messages:
            content = msg['content']
            
            # Filter: System messages
            if self._is_system_message(msg):
                self.stats['filtered_system'] += 1
                continue
            
            # Filter: Bot commands
            if self._is_command(content):
                self.stats['filtered_commands'] += 1
                continue
            
            # Filter: Emoji-only
            if self._is_emoji_only(content):
                self.stats['filtered_emoji_only'] += 1
                continue
            
            # Filter: Single word
            if self._is_single_word(content):
                self.stats['filtered_single_word'] += 1
                continue
            
            # Filter: Duplicates
            content_lower = content.lower().strip()
            if content_lower in seen_content:
                self.stats['filtered_duplicates'] += 1
                continue
            seen_content.add(content_lower)
            
            # Message passed all filters
            self.filtered_messages.append(msg)
        
        self.stats['total_filtered'] = len(self.filtered_messages)
        
        logger.info(f"Filtering complete:")
        logger.info(f"  Commands removed: {self.stats['filtered_commands']:,}")
        logger.info(f"  Emoji-only removed: {self.stats['filtered_emoji_only']:,}")
        logger.info(f"  Single-word removed: {self.stats['filtered_single_word']:,}")
        logger.info(f"  Duplicates removed: {self.stats['filtered_duplicates']:,}")
        logger.info(f"  System messages removed: {self.stats['filtered_system']:,}")
        logger.info(f"  Remaining: {self.stats['total_filtered']:,}")
    
    def _get_context_messages(self, bot_msg_idx: int, context_size: int = 5) -> List[Dict]:
        """Get conversation context before bot response"""
        start_idx = max(0, bot_msg_idx - context_size)
        return self.filtered_messages[start_idx:bot_msg_idx]
    
    def _format_context(self, context_messages: List[Dict]) -> str:
        """Format context messages into conversation string"""
        lines = []
        for msg in context_messages:
            author = msg['author_display_name']
            content = msg['content']
            lines.append(f"{author}: {content}")
        return "\n".join(lines)
    
    def create_training_examples(self):
        """Create training examples from filtered messages"""
        logger.info("Creating training examples...")
        
        # Find all bot responses
        for i, msg in enumerate(self.filtered_messages):
            if msg['author_id'] != self.bot_user_id:
                continue
            
            # Get context
            context_messages = self._get_context_messages(i, context_size=5)
            if not context_messages:
                continue  # Skip if no context
            
            # Format training example
            context_str = self._format_context(context_messages)
            response = msg['content']
            
            example = {
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": context_str
                    },
                    {
                        "role": "assistant",
                        "content": response
                    }
                ],
                "metadata": {
                    "message_id": msg['id'],
                    "timestamp": msg['timestamp'],
                    "context_length": len(context_messages)
                }
            }
            
            self.training_examples.append(example)
        
        self.stats['training_examples'] = len(self.training_examples)
        logger.info(f"Created {self.stats['training_examples']:,} training examples")
    
    def validate_examples(self):
        """Validate training examples"""
        logger.info("Validating training examples...")
        
        issues = 0
        for i, example in enumerate(self.training_examples):
            # Check structure
            if 'messages' not in example:
                logger.warning(f"Example {i}: Missing 'messages' field")
                issues += 1
                continue
            
            messages = example['messages']
            if len(messages) != 3:
                logger.warning(f"Example {i}: Expected 3 messages, got {len(messages)}")
                issues += 1
                continue
            
            # Check roles
            expected_roles = ['system', 'user', 'assistant']
            actual_roles = [m['role'] for m in messages]
            if actual_roles != expected_roles:
                logger.warning(f"Example {i}: Invalid roles: {actual_roles}")
                issues += 1
                continue
            
            # Check empty content
            for msg in messages:
                if not msg.get('content', '').strip():
                    logger.warning(f"Example {i}: Empty content in {msg['role']} message")
                    issues += 1
                    break
        
        if issues > 0:
            logger.warning(f"Found {issues} issues in training examples")
        else:
            logger.info("✅ All examples validated successfully")
    
    def save_training_data(self):
        """Save training examples to file"""
        logger.info(f"Saving training data to: {TRAINING_DATA_FILE}")
        
        try:
            with open(TRAINING_DATA_FILE, 'w', encoding='utf-8') as f:
                for example in self.training_examples:
                    f.write(json.dumps(example) + '\n')
            
            file_size = TRAINING_DATA_FILE.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Saved {len(self.training_examples):,} examples ({file_size:.1f} MB)")
        
        except Exception as e:
            logger.error(f"Error saving training data: {e}")
            raise
    
    def print_summary(self):
        """Print final summary"""
        logger.info("="*60)
        logger.info("DATA PREPARATION COMPLETE")
        logger.info("="*60)
        logger.info(f"Input messages: {self.stats['total_raw']:,}")
        logger.info(f"Filtered out: {self.stats['total_raw'] - self.stats['total_filtered']:,}")
        logger.info(f"Training examples: {self.stats['training_examples']:,}")
        logger.info(f"Output file: {TRAINING_DATA_FILE}")
        logger.info(f"File size: {TRAINING_DATA_FILE.stat().st_size / (1024*1024):.1f} MB")
        logger.info("="*60)
        logger.info("✅ Ready for Phase 2 (Training)!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Review training data sample:")
        logger.info(f"     Get-Content {TRAINING_DATA_FILE} -First 1 | ConvertFrom-Json | ConvertTo-Json -Depth 10")
        logger.info("  2. When ready: 'Start Phase 2'")
        logger.info("="*60)
    
    def show_sample(self, num_samples: int = 3):
        """Show sample training examples"""
        logger.info("\n" + "="*60)
        logger.info("SAMPLE TRAINING EXAMPLES")
        logger.info("="*60)
        
        for i, example in enumerate(self.training_examples[:num_samples], 1):
            logger.info(f"\nExample {i}:")
            logger.info("-" * 40)
            for msg in example['messages']:
                role = msg['role'].upper()
                content = msg['content'][:200]  # Truncate for display
                logger.info(f"{role}:")
                logger.info(f"  {content}")
                logger.info("")


def main():
    """Entry point"""
    logger.info("="*60)
    logger.info("Training Data Preparation Script")
    logger.info("="*60)
    
    prep = DataPreparator()
    
    try:
        # Pipeline
        prep.load_messages()
        prep.filter_messages()
        prep.create_training_examples()
        prep.validate_examples()
        prep.save_training_data()
        
        # Summary
        prep.print_summary()
        prep.show_sample(num_samples=2)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
