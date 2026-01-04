"""
Discord Bot Main Entry Point
Responds when mentioned (@sususbot) in any accessible channel
"""

import discord
from discord.ext import commands
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from model.inference import InferenceEngine
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Response generation settings
MAX_RESPONSE_LENGTH = int(os.getenv("MAX_NEW_TOKENS", "150"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_P = float(os.getenv("TOP_P", "0.9"))
TOP_K = int(os.getenv("TOP_K", "40"))
REPETITION_PENALTY = float(os.getenv("REPETITION_PENALTY", "1.1"))

# Memory settings
SHORT_TERM_WINDOW = int(os.getenv("SHORT_TERM_WINDOW", "20"))
SHORT_TERM_MAX_CONTEXT = int(os.getenv("SHORT_TERM_MAX_CONTEXT", "10"))
ENABLE_LONG_TERM_MEMORY = os.getenv("ENABLE_LONG_TERM_MEMORY", "false").lower() == "true"
LONG_TERM_DB_PATH = os.getenv("LONG_TERM_DB_PATH", "data/vector_db")
LONG_TERM_TOP_K = int(os.getenv("LONG_TERM_TOP_K", "3"))

class DiscordChatbot(commands.Bot):
    """Discord chatbot with trained personality"""
    
    def __init__(self):
        # Setup intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.messages = True
        
        super().__init__(command_prefix="!", intents=intents)
        
        # Initialize components
        self.inference_engine = None
        self.short_term_memory = ShortTermMemory(window_size=SHORT_TERM_WINDOW)
        self.long_term_memory = None
        
        logger.info("Bot initialized")
    
    async def setup_hook(self):
        """Called when bot is starting up"""
        logger.info("Setting up bot components...")
        
        # Initialize inference engine
        logger.info("Loading inference engine (this takes 2-3 minutes)...")
        self.inference_engine = InferenceEngine()
        await asyncio.to_thread(self.inference_engine.load_model)
        logger.info("Inference engine ready!")
        
        # Initialize long-term memory (if enabled)
        if ENABLE_LONG_TERM_MEMORY:
            logger.info("Initializing long-term memory...")
            self.long_term_memory = LongTermMemory(db_path=LONG_TERM_DB_PATH)
            await self.long_term_memory.initialize()
            logger.info("Long-term memory ready!")
        
        logger.info("Bot setup complete!")
    
    async def on_ready(self):
        """Called when bot is fully connected"""
        logger.info("="*60)
        logger.info(f"Bot connected as {self.user}")
        logger.info(f"Bot ID: {self.user.id}")
        logger.info(f"Servers: {len(self.guilds)}")
        logger.info("="*60)
        
        # List accessible channels
        logger.info("Accessible channels:")
        for guild in self.guilds:
            text_channels = [c for c in guild.text_channels if c.permissions_for(guild.me).read_messages]
            logger.info(f"  {guild.name}: {len(text_channels)} channels")
        
        logger.info("="*60)
        logger.info("Bot is ready! Mention me (@sususbot) to chat!")
        logger.info("="*60)
    
    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        
        # Ignore own messages
        if message.author == self.user:
            return
        
        # Ignore DMs (optional - remove this if you want DM support)
        if not message.guild:
            return
        
        # Check if bot was mentioned
        if self.user not in message.mentions:
            # Store in short-term memory even if not mentioned (for context)
            self.short_term_memory.add_message(
                author=message.author.display_name,
                content=message.content,
                channel_id=message.channel.id
            )
            return
        
        # Bot was mentioned!
        logger.info(f"Mentioned in #{message.channel.name} by {message.author.display_name}")
        
        try:
            # Show typing indicator
            async with message.channel.typing():
                # Get conversation context from short-term memory
                context = self.short_term_memory.get_context(
                    channel_id=message.channel.id,
                    max_messages=SHORT_TERM_MAX_CONTEXT
                )
                
                # Get long-term memory context (if enabled)
                long_term_context = ""
                if self.long_term_memory:
                    relevant_memories = await self.long_term_memory.retrieve(
                        query=message.content,
                        top_k=LONG_TERM_TOP_K
                    )
                    if relevant_memories:
                        long_term_context = "\n".join(relevant_memories)
                
                # Generate response
                response = await asyncio.to_thread(
                    self.inference_engine.generate_response,
                    context=context,
                    long_term_context=long_term_context,
                    max_length=MAX_RESPONSE_LENGTH,
                    temperature=TEMPERATURE,
                    top_p=TOP_P,
                    top_k=TOP_K,
                    repetition_penalty=REPETITION_PENALTY
                )
                
                # Clean up response (remove mention from response if present)
                response = response.strip()
                if not response:
                    response = "..."
                
                # Send response
                await message.channel.send(response)
                
                # Store interaction in memory
                self.short_term_memory.add_message(
                    author=message.author.display_name,
                    content=message.content,
                    channel_id=message.channel.id
                )
                self.short_term_memory.add_message(
                    author=self.user.display_name,
                    content=response,
                    channel_id=message.channel.id
                )
                
                # Store in long-term memory (if enabled)
                if self.long_term_memory:
                    await self.long_term_memory.add_memory(
                        content=f"{message.author.display_name}: {message.content}\n{self.user.display_name}: {response}",
                        metadata={
                            'channel': message.channel.name,
                            'guild': message.guild.name,
                            'timestamp': message.created_at.isoformat()
                        }
                    )
                
                logger.info(f"Response sent in #{message.channel.name}")
        
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            await message.channel.send("sorry, something went wrong lol")
    
    async def on_error(self, event, *args, **kwargs):
        """Handle errors"""
        logger.error(f"Error in {event}", exc_info=True)


def main():
    """Main entry point"""
    
    # Validate configuration
    if not DISCORD_TOKEN:
        logger.error("DISCORD_BOT_TOKEN not set in .env!")
        logger.error("Please add your bot token to .env file")
        sys.exit(1)
    
    # Check if model exists
    adapter_path = Path("adapters/discord-lora")
    if not adapter_path.exists():
        logger.error("Trained model not found!")
        logger.error(f"Expected location: {adapter_path}")
        logger.error("Please complete Phase 2 (training) first")
        sys.exit(1)
    
    logger.info("="*60)
    logger.info("Discord Chatbot v0.2 - Starting")
    logger.info("="*60)
    
    # Create and run bot
    bot = DiscordChatbot()
    
    try:
        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
