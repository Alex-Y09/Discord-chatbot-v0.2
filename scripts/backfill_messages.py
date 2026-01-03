"""
Discord Message Backfill Script
Collects historical messages from a Discord channel for training data

Features:
- Resume from checkpoint if interrupted
- Rate limiting to respect Discord API
- Progress tracking
- Error handling with retries
"""

import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "backfill.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", 65000))
REQUESTS_PER_SECOND = int(os.getenv("REQUESTS_PER_SECOND", 40))
ENABLE_CHECKPOINT = os.getenv("ENABLE_CHECKPOINT", "true").lower() == "true"
CHECKPOINT_INTERVAL = int(os.getenv("CHECKPOINT_INTERVAL", 1000))

# File paths
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
RAW_MESSAGES_FILE = DATA_DIR / "raw_messages.jsonl"
CHECKPOINT_FILE = DATA_DIR / "backfill_checkpoint.json"


class MessageCollector:
    """Collects messages from Discord channel with checkpointing"""
    
    def __init__(self):
        self.collected_messages = []
        self.last_message_id = None
        self.start_time = None
        self.message_count = 0
        
        # Setup Discord client
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        self.client = discord.Client(intents=intents)
        
        # Load checkpoint if exists
        if ENABLE_CHECKPOINT and CHECKPOINT_FILE.exists():
            self._load_checkpoint()
    
    def _load_checkpoint(self):
        """Load progress from checkpoint file"""
        try:
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            
            self.message_count = checkpoint.get('message_count', 0)
            self.last_message_id = checkpoint.get('last_message_id')
            
            logger.info(f"Checkpoint loaded: {self.message_count} messages collected")
            logger.info(f"Resuming from message ID: {self.last_message_id}")
            
            # Load existing messages
            if RAW_MESSAGES_FILE.exists():
                with open(RAW_MESSAGES_FILE, 'r', encoding='utf-8') as f:
                    self.collected_messages = [json.loads(line) for line in f]
                logger.info(f"Loaded {len(self.collected_messages)} existing messages")
        
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            logger.info("Starting fresh collection")
    
    def _save_checkpoint(self):
        """Save current progress to checkpoint file"""
        if not ENABLE_CHECKPOINT:
            return
        
        checkpoint = {
            'message_count': self.message_count,
            'last_message_id': self.last_message_id,
            'timestamp': datetime.now().isoformat(),
        }
        
        try:
            with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2)
            logger.info(f"Checkpoint saved: {self.message_count} messages")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
    
    def _save_messages(self):
        """Save collected messages to file"""
        try:
            with open(RAW_MESSAGES_FILE, 'w', encoding='utf-8') as f:
                for msg in self.collected_messages:
                    f.write(json.dumps(msg) + '\n')
            logger.info(f"Saved {len(self.collected_messages)} messages to {RAW_MESSAGES_FILE}")
        except Exception as e:
            logger.error(f"Failed to save messages: {e}")
    
    def _message_to_dict(self, message: discord.Message) -> Dict:
        """Convert Discord message to dictionary"""
        return {
            'id': str(message.id),
            'author_id': str(message.author.id),
            'author_name': message.author.name,
            'author_display_name': message.author.display_name,
            'content': message.content,
            'timestamp': message.created_at.isoformat(),
            'edited_timestamp': message.edited_at.isoformat() if message.edited_at else None,
            'attachments': [att.url for att in message.attachments],
            'embeds_count': len(message.embeds),
            'mentions': [str(m.id) for m in message.mentions],
            'reference_id': str(message.reference.message_id) if message.reference else None,
            'type': str(message.type),
        }
    
    async def collect_messages(self):
        """Main collection loop"""
        
        @self.client.event
        async def on_ready():
            logger.info(f"Logged in as {self.client.user}")
            logger.info(f"Target Guild ID: {GUILD_ID}")
            logger.info(f"Target Channel ID: {CHANNEL_ID}")
            logger.info(f"Max messages: {MAX_MESSAGES}")
            logger.info(f"Rate limit: {REQUESTS_PER_SECOND} requests/second")
            
            try:
                # Get channel
                guild = self.client.get_guild(GUILD_ID)
                if not guild:
                    logger.error(f"Guild {GUILD_ID} not found")
                    await self.client.close()
                    return
                
                channel = guild.get_channel(CHANNEL_ID)
                if not channel:
                    logger.error(f"Channel {CHANNEL_ID} not found")
                    await self.client.close()
                    return
                
                logger.info(f"Found channel: #{channel.name}")
                
                # Start collection
                self.start_time = datetime.now()
                logger.info("Starting message collection...")
                
                # Calculate delay between requests
                delay = 1.0 / REQUESTS_PER_SECOND
                
                # Determine starting point
                after_id = None
                if self.last_message_id:
                    # Resume from checkpoint
                    after_id = discord.Object(id=int(self.last_message_id))
                    logger.info(f"Resuming from message {self.last_message_id}")
                
                # Collect messages in batches
                batch_size = 100  # Discord API limit
                while self.message_count < MAX_MESSAGES:
                    try:
                        # Fetch batch
                        messages = []
                        async for message in channel.history(
                            limit=min(batch_size, MAX_MESSAGES - self.message_count),
                            after=after_id,
                            oldest_first=True
                        ):
                            messages.append(message)
                        
                        if not messages:
                            logger.info("No more messages to collect")
                            break
                        
                        # Process batch
                        for message in messages:
                            msg_dict = self._message_to_dict(message)
                            self.collected_messages.append(msg_dict)
                            self.message_count += 1
                            self.last_message_id = str(message.id)
                            
                            # Progress update
                            if self.message_count % 100 == 0:
                                progress = (self.message_count / MAX_MESSAGES) * 100
                                logger.info(f"Progress: {self.message_count}/{MAX_MESSAGES} ({progress:.1f}%)")
                            
                            # Checkpoint
                            if self.message_count % CHECKPOINT_INTERVAL == 0:
                                self._save_messages()
                                self._save_checkpoint()
                        
                        # Update after_id for next batch
                        after_id = discord.Object(id=messages[-1].id)
                        
                        # Rate limiting
                        await asyncio.sleep(delay)
                    
                    except discord.errors.HTTPException as e:
                        if e.status == 429:  # Rate limited
                            retry_after = e.retry_after if hasattr(e, 'retry_after') else 60
                            logger.warning(f"Rate limited! Waiting {retry_after} seconds...")
                            await asyncio.sleep(retry_after)
                        else:
                            logger.error(f"HTTP error: {e}")
                            await asyncio.sleep(5)
                    
                    except Exception as e:
                        logger.error(f"Error collecting messages: {e}")
                        await asyncio.sleep(5)
                
                # Final save
                self._save_messages()
                if ENABLE_CHECKPOINT:
                    self._save_checkpoint()
                
                # Summary
                elapsed = (datetime.now() - self.start_time).total_seconds()
                logger.info("="*60)
                logger.info("Collection complete!")
                logger.info(f"Total messages collected: {self.message_count:,}")
                logger.info(f"Time taken: {elapsed/60:.1f} minutes")
                logger.info(f"Average rate: {self.message_count/elapsed:.1f} messages/second")
                logger.info(f"Saved to: {RAW_MESSAGES_FILE}")
                logger.info("="*60)
                logger.info("Next step: python scripts/analyze_training_data.py")
                
            except Exception as e:
                logger.error(f"Fatal error: {e}", exc_info=True)
            
            finally:
                await self.client.close()
        
        # Run client
        await self.client.start(DISCORD_TOKEN)


def main():
    """Entry point"""
    logger.info("="*60)
    logger.info("Discord Message Backfill Script")
    logger.info("="*60)
    
    # Validate configuration
    if not DISCORD_TOKEN:
        logger.error("DISCORD_BOT_TOKEN not set in .env")
        return
    
    if not GUILD_ID or not CHANNEL_ID:
        logger.error("DISCORD_GUILD_ID or DISCORD_CHANNEL_ID not set in .env")
        return
    
    # Start collection
    collector = MessageCollector()
    
    try:
        asyncio.run(collector.collect_messages())
    except KeyboardInterrupt:
        logger.info("\nCollection interrupted by user")
        logger.info(f"Progress saved: {collector.message_count} messages")
        logger.info("Run script again to resume from checkpoint")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
