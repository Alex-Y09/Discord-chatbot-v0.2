# Product Design Review (PDR)
## Discord Character Chatbot with RAG and Dynamic Memory

**Project Name:** Discord Character Chatbot v0.2  
**Date:** January 2, 2026  
**Author:** System Architect  
**Status:** Design Phase

---

## 1. Executive Summary

### 1.1 Project Overview
A sophisticated Discord chatbot that learns from server conversations and responds in-character using a fine-tuned Mistral-7B-v0.3 language model. The bot features advanced memory systems including RAG (Retrieval-Augmented Generation) for long-term memory and dynamic summarization for short-term context awareness.

### 1.2 Key Objectives
- Create an engaging, personality-driven chatbot that mimics specific communication styles
- Implement efficient memory systems for context-aware conversations
- Develop and stabilize consistent personality through RAG-based long-term memory
- Remember and reference server lore, inside jokes, events, and community culture
- Fine-tune LLM on server-specific conversation data
- Maintain low latency responses (<3 seconds average)
- Support continuous learning from new conversations

### 1.3 Success Metrics
- Response relevance score: >85% (user feedback)
- Average response time: <3 seconds
- Memory retrieval accuracy: >90%
- User engagement rate: 50% increase in bot interactions
- System uptime: >99.5%

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Discord Server                           │
│                    (Message Events Source)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Discord Bot Client                          │
│                    (Event Listener Layer)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴───────────┐
                │                        │
                ▼                        ▼
┌───────────────────────┐   ┌──────────────────────────┐
│   Message Processor   │   │   Command Handler        │
│   - Filtering         │   │   - Admin Commands       │
│   - Preprocessing     │   │   - Training Controls    │
│   - Token Counting    │   │   - Memory Management    │
└──────────┬────────────┘   └──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Memory Manager (Core)                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌──────────────────────────────────┐ │
│  │  Short-Term Memory  │  │     Long-Term Memory (RAG)       │ │
│  │  ----------------   │  │     ---------------------        │ │
│  │  • Sliding Window   │  │  • Vector DB (ChromaDB/FAISS)    │ │
│  │  • Last 20 msgs     │  │  • Semantic Search               │ │
│  │  • Summarization    │  │  • Embedding Model               │ │
│  │  • Re-summarize/5   │  │  • Persistent Storage            │ │
│  └─────────────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Context Assembler                             │
│  • Combines RAG results + Short-term summary                     │
│  • Token budget management                                       │
│  • Prompt engineering                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Inference Engine                              │
│  • Mistral-7B-v0.3 (Base Model)                                  │
│  • LoRA Fine-tuned Adapter                                       │
│  • 4-bit Quantization (bitsandbytes)                             │
│  • Response Generation                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Response Post-Processor                        │
│  • Length validation                                             │
│  • Content filtering                                             │
│  • Format correction                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Discord API (Send)                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Training Pipeline (Offline)                   │
│  • Data Collection                                               │
│  • Data Preprocessing & Formatting                               │
│  • LoRA Fine-tuning                                              │
│  • Adapter Merging & Validation                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Details

#### 2.2.1 Discord Bot Client
- **Technology:** discord.py (Python 3.10+)
- **Responsibilities:**
  - Listen to message events (on_message)
  - Handle bot mentions and triggers
  - Send responses back to Discord
  - Manage connection lifecycle
  - Rate limiting compliance
- **Key Features:**
  - Async event handling
  - Reconnection logic
  - Error handling and logging
- **Important:** Does NOT query Discord API for historical messages during inference - all context comes from RAG + Short-Term Memory

#### 2.2.2 Memory Manager
**Short-Term Memory:**
- Maintains sliding window of last 20 messages in-memory (no Discord API calls)
- Messages are captured as they arrive via discord.py event listener
- Generates summary every 5 messages using lightweight summarization of 1 to 3 paragraphs
- Stored in memory only (Python deque) - persisted to disk optionally for crash recovery
- Structure:
  ```python
  {
    "messages": [
      {"author": "username", "content": "...", "timestamp": "..."},
      # ... up to 20 messages
    ],
    "current_summary": "...",
    "last_summarized_at": 15  # message index
  }
  ```

**Long-Term Memory (RAG):**
- **Purpose:** 
  - Develop and stabilize consistent personality traits
  - Remember server lore, inside jokes, and recurring topics
  - Maintain context about users, events, and community culture
- Vector database: ChromaDB
- Embedding model: sentence-transformers/all-MiniLM-L6-v2
- Storage structure:
  ```python
  {
    "id": "msg_{timestamp}_{hash}",  # Unique identifier
    "document": "original message text",  # ChromaDB stores this as 'documents'
    "metadata": {
      "author": "username",
      "author_id": "discord_user_id",  # For user-specific queries
      "timestamp": "ISO8601",
      "unix_time": 1234567890,  # For faster recency calculations
      "channel": "channel_name",
      "channel_id": "channel_id",  # For channel filtering
      "message_id": "original_discord_msg_id",  # For deduplication
      "context": "conversation_topic",
      "lore_type": "inside_joke|event|personality_trait|user_info|regular",
      "engagement_score": 0.8,  # Based on reactions/replies (0-1)
      "bot_response": false,  # Track if this was bot's own message
      "has_context": true  # Whether surrounding context was captured
    }
    # embedding is automatically handled by ChromaDB
  }
  ```
  
  **Rationale for Structure:**
  - `document` field: ChromaDB's native field for text content to embed
  - `author_id` + `channel_id`: Enable filtering by specific users/channels
  - `unix_time`: Faster numerical comparisons for recency scoring
  - `message_id`: Prevents duplicate indexing of edited messages
  - `engagement_score`: Pre-calculated metric for importance weighting
  - `bot_response`: Allows distinguishing bot's own responses for personality learning
  - `has_context`: Indicates if conversational context is included
- Retrieval: Top-K semantic search (K=5-10)

#### 2.2.3 Context Assembler
- **Token Budget Management:**
  - Total context: 512 tokens (from .env config)
  - Allocation:
    - System prompt: 50 tokens
    - Short-term summary: 150 tokens
    - RAG results: 200 tokens
    - Current query: 50 tokens
    - Buffer: 62 tokens

- **Prompt Template:**
  ```
  <System>
  You are sususbot, a casual, witty Discord regular who is member of a Discord server with friends. You respond naturally, conversationally, and with personality. You understand inside jokes, sarcasm, and informal language. You are here primarily for entertainment and banter, not formal assistance. You keep responses concise unless the conversation clearly calls for more. You may tease, joke, or riff, but never become mean-spirited or hostile. You are a human friend in a group chat, not like an assistant or moderator.

  <Long-term Context>
  Server lore and personality reference:
  {RAG_RESULTS}
  
  <Recent Conversation Summary>
  {SHORT_TERM_SUMMARY}
  
  <Recent Messages>
  {LAST_3_MESSAGES}
  
  <Current Message>
  {USER_MESSAGE}
  
  <Response>
  ```

#### 2.2.4 Inference Engine
- **Base Model:** mistralai/Mistral-7B-v0.3
- **Fine-tuning Method:** LoRA (Low-Rank Adaptation)
  - Rank (r): 8
  - Alpha: 16
  - Dropout: 0.05
  - Target modules: q_proj, v_proj, k_proj, o_proj
- **Quantization:** 4-bit (bitsandbytes) for memory efficiency
- **Inference Parameters:**
  - Temperature: 0.7 (configurable)
  - Top-p: 0.9
  - Top-k: 40
  - Max new tokens: 100
  - Do sample: True

---

## 3. Data Pipeline

### 3.0 Data Flow Architecture

**Important Design Decision: No Discord API Calls During Inference**

The bot operates in two distinct modes:

1. **Data Collection Mode (Background/Startup):**
   - Listens to discord.py `on_message` events
   - Captures messages as they arrive in real-time
   - Optionally: One-time backfill from Discord export or API (setup phase only)
   - Indexes messages into ChromaDB asynchronously
   - Updates short-term memory cache

2. **Inference Mode (Response Generation):**
   - **NO Discord API calls are made**
   - Uses ONLY pre-indexed data from ChromaDB (RAG)
   - Uses ONLY in-memory short-term message cache
   - Fast and efficient - no API rate limits or latency

**Flow Diagram:**
```
Discord Message Arrives
  ↓
discord.py on_message event
  ↓
  ├─→ Add to Short-Term Memory (in-memory)
  ├─→ Queue for ChromaDB indexing (async)
  └─→ Trigger bot response if mentioned
      ↓
      Retrieve from ChromaDB (local DB)
      ↓
      Get from Short-Term Memory (in-memory)
      ↓
      Generate response with LLM
      ↓
      Send via discord.py
```

### 3.1 Data Collection

**Sources:**
- Discord server messages (real-time via discord.py on_message event)
- Historical message archives (Discord export or initial backfill - one-time operation)

**Collection Strategy:**
```python
# Filtering Criteria
- Minimum message length: 1 token
- Maximum message length: 512 tokens
- Exclude bot messages: True
- Exclude system messages: True
- Exclude messages with attachments only: True
- Exclude Links in messages
- Exclude exessive Emote spam (more than 3 emotes in a row)
- Languages: English (can be expanded)
```

**Storage Format (JSONL):**
```json
{"text": "User1: Hey, how's it going?\nBot: I'm doing great! Just finished training on some new data.", "metadata": {"channel": "general", "timestamp": "2026-01-02T10:30:00Z"}}
```

---

### 7. Configuration and Bot Logic

### 7.2 Configuration Interface

**Environment Variables (.env file):**
```bash
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=867551208286060594
DISCORD_CHANNEL_ID=867551208738127882

# Data Collection Settings
REQUESTS_PER_SECOND=5
MIN_MESSAGE_TOKENS=1
MAX_MESSAGE_TOKENS=512
EXCLUDE_BOT_MESSAGES=true
EXCLUDE_SYSTEM_MESSAGES=true

# Model Configuration
MODEL_NAME=mistralai/Mistral-7B-v0.3
ADAPTER_PATH=./adapters/discord-lora
CONTEXT_TOKENS=512
MAX_NEW_TOKENS=100
TEMPERATURE=0.7
TOP_P=0.9
TOP_K=40
REPETITION_PENALTY=1.1

# Memory Settings
SHORT_TERM_WINDOW=20
SUMMARIZE_INTERVAL=5
RAG_TOP_K=5
SUMMARIZATION_MODEL=facebook/bart-large-cnn

# Vector Database
VECTOR_DB_PATH=./data/vector_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Training Settings
TRAINING_DATA_PATH=./data/training_data.jsonl
LEARNING_RATE=2e-4
EPOCHS=3
BATCH_SIZE=1
GRADIENT_ACCUMULATION_STEPS=16

# System Settings
LOG_LEVEL=INFO
LOG_FILE=./logs/bot.log
CHECKPOINT_PATH=./data/backfill_checkpoint.json

# Performance
ENABLE_QUANTIZATION=true
DEVICE=cuda  # Options: cuda, cpu, mps (for Mac)
```

**Note:** Copy `.env.example` to `.env` and fill in your actual values.

### 7.3 Bot Trigger Logic

**When the bot responds:**
- **Primary:** When mentioned with @sususbot
- **Excluded:** Does NOT respond to:
  - Its own messages
  - Other bot messages
  - System messages

**Implementation:**
```python
async def should_respond(message: discord.Message, bot_user_id: int) -> bool:
    """
    Determine if bot should respond to a message
    
    Args:
        message: Discord message object
        bot_user_id: Bot's user ID
    
    Returns:
        True if bot should respond, False otherwise
    """
    # Don't respond to self
    if message.author.id == bot_user_id:
        return False
    
    # Don't respond to other bots
    if message.author.bot:
        return False
    
    # Don't respond to system messages
    if message.type != discord.MessageType.default:
        return False
    
    # Respond when mentioned
    if bot_user_id in [m.id for m in message.mentions]:
        return True
    
    return False
```

### 7.4 Helper Function Implementations

#### Message Indexing
```python
import chromadb
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def index_message(message_data: Dict, collection: chromadb.Collection) -> None:
    """
    Index a message into ChromaDB for RAG retrieval
    
    Args:
        message_data: Message data dictionary
        collection: ChromaDB collection instance
    """
    try:
        # Check for duplicates
        existing = collection.get(
            where={"message_id": message_data['message_id']},
            include=[]
        )
        
        if existing['ids']:
            logger.debug(f"Message {message_data['message_id']} already indexed, skipping")
            return
        
        # Calculate engagement score
        reactions = message_data.get('reactions', [])
        reaction_count = sum(r.get('count', 0) for r in reactions)
        reply_count = message_data.get('reply_count', 0)
        is_pinned = message_data.get('pinned', False)
        
        engagement_score = calculate_engagement_score(
            reaction_count, reply_count, is_pinned
        )
        
        # Classify lore type
        lore_type = classify_lore_type(message_data)
        
        # Prepare metadata
        metadata = {
            "author": message_data['author_name'],
            "author_id": str(message_data['author_id']),
            "timestamp": message_data['timestamp'].isoformat(),
            "unix_time": int(message_data['timestamp'].timestamp()),
            "channel": message_data.get('channel_name', 'unknown'),
            "channel_id": str(message_data['channel_id']),
            "message_id": str(message_data['message_id']),
            "context": message_data.get('context', ''),
            "lore_type": lore_type,
            "engagement_score": engagement_score,
            "bot_response": message_data.get('is_bot', False),
            "has_context": message_data.get('has_context', False)
        }
        
        # Generate unique ID
        msg_id = f"msg_{metadata['unix_time']}_{hash(message_data['message_id'])}"
        
        # Add to collection
        collection.add(
            documents=[message_data['content']],
            metadatas=[metadata],
            ids=[msg_id]
        )
        
        logger.info(f"Indexed message {message_data['message_id']} as {lore_type}")
        
    except Exception as e:
        logger.error(f"Failed to index message {message_data.get('message_id', 'unknown')}: {e}")
        raise

def save_for_training(message_data: Dict, filepath: str = None) -> None:
    """
    Append message to JSONL training file
    
    Args:
        message_data: Message data dictionary
        filepath: Path to JSONL file (from .env if not provided)
    """
    import json
    import os
    from pathlib import Path
    
    if filepath is None:
        filepath = os.getenv('TRAINING_DATA_PATH', './data/training_data.jsonl')
    
    try:
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Format for training
        training_entry = {
            "text": f"{message_data['author_name']}: {message_data['content']}",
            "metadata": {
                "message_id": str(message_data['message_id']),
                "channel": message_data.get('channel_name', 'unknown'),
                "timestamp": message_data['timestamp'].isoformat(),
                "author_id": str(message_data['author_id'])
            }
        }
        
        # Append to file
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(training_entry) + '\n')
        
        logger.debug(f"Saved message {message_data['message_id']} to training data")
        
    except Exception as e:
        logger.error(f"Failed to save message for training: {e}")
        # Don't raise - training data is non-critical
```

#### Toxicity Filtering (Placeholder)
```python
def contains_explicit_content(text: str) -> bool:
    """
    Check if text contains explicit or inappropriate content
    
    TODO: Implement with a proper toxicity detection model
    For now, use basic keyword filtering
    
    Args:
        text: Message content
    
    Returns:
        True if content should be filtered
    """
    # Basic implementation - expand as needed
    explicit_keywords = [
        # Add keywords as needed, but keep minimal to avoid false positives
    ]
    
    text_lower = text.lower()
    
    # Check for explicit keywords
    for keyword in explicit_keywords:
        if keyword in text_lower:
            logger.warning(f"Filtered message containing: {keyword}")
            return True
    
    return False
```

### 7.5 Error Handling Strategy

**Error Categories & Responses:**

#### Critical Errors (Stop Execution)
```python
class BotCriticalError(Exception):
    """Critical errors that should stop the bot"""
    pass

# Example: Model loading failure
try:
    model = load_model()
except Exception as e:
    logger.critical(f"CRITICAL: Failed to load model: {e}")
    print(f"[CRITICAL ERROR] Cannot start bot - model loading failed: {e}")
    print("Please check:")
    print("  1. MODEL_NAME in .env is correct")
    print("  2. You have sufficient GPU memory (12GB+ required)")
    print("  3. CUDA is properly installed")
    sys.exit(1)
```

#### Recoverable Errors (Log & Continue)
```python
# Example: ChromaDB query failure
try:
    rag_results = retrieve_relevant_context(query)
except Exception as e:
    logger.error(f"RAG retrieval failed: {e}")
    print(f"[ERROR] Vector DB query failed, using STM only: {e}")
    rag_results = []  # Fall back to short-term memory only
```

#### Warning Messages (Terminal Output)
```python
# Example: Model inference timeout
import time

start_time = time.time()
try:
    response = generate_response(prompt, timeout=10)
    inference_time = time.time() - start_time
    
    if inference_time > 5:
        logger.warning(f"Slow inference detected: {inference_time:.2f}s")
        print(f"[WARNING] Response took {inference_time:.2f}s (target: <3s)")
        
except TimeoutError:
    logger.error("Inference timeout (>10s)")
    print("[ERROR] Model took too long to respond (>10s). Using fallback.")
    response = "Sorry, I'm having trouble thinking right now. Try again?"
```

**Error Handling Patterns:**
```python
import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for the bot"""
    
    @staticmethod
    def handle_discord_error(error: Exception, context: str = "") -> bool:
        """
        Handle Discord API errors
        
        Returns:
            True if recoverable, False if critical
        """
        if isinstance(error, discord.errors.HTTPException):
            if error.status == 429:  # Rate limited
                logger.warning(f"Rate limited: {error.retry_after}s")
                print(f"[WARNING] Discord rate limit hit, waiting {error.retry_after}s")
                return True
            elif error.status >= 500:  # Server error
                logger.error(f"Discord server error {error.status}")
                print(f"[ERROR] Discord servers having issues (HTTP {error.status})")
                return True
            else:
                logger.error(f"Discord API error: {error}")
                print(f"[ERROR] Discord API error: {error}")
                return False
        
        return False
    
    @staticmethod
    def handle_model_error(error: Exception, context: str = "") -> Optional[str]:
        """
        Handle model inference errors
        
        Returns:
            Fallback response or None if unrecoverable
        """
        logger.error(f"Model error in {context}: {error}")
        
        if "out of memory" in str(error).lower():
            print("[ERROR] GPU out of memory! Try:")
            print("  1. Reduce CONTEXT_TOKENS in .env")
            print("  2. Ensure ENABLE_QUANTIZATION=true")
            print("  3. Close other GPU programs")
            return "Ugh, my brain just crashed. Give me a sec..."
        
        elif "cuda" in str(error).lower():
            print("[ERROR] CUDA error detected")
            print("Falling back to CPU (will be slower)")
            return "Hold on, switching to backup brain..."
        
        else:
            print(f"[ERROR] Unknown model error: {error}")
            return "Sorry, I'm fucking broken right now. Try again in a bit?"
    
    @staticmethod
    def handle_database_error(error: Exception, context: str = "") -> bool:
        """
        Handle vector database errors
        
        Returns:
            True if can continue without DB, False if critical
        """
        logger.error(f"Database error in {context}: {error}")
        print(f"[ERROR] Vector DB issue: {error}")
        print("[INFO] Bot will continue with short-term memory only")
        return True  # Can operate without RAG temporarily

# Usage example
try:
    response = model.generate(**generation_config)
except Exception as e:
    fallback = ErrorHandler.handle_model_error(e, context="inference")
    if fallback:
        response = fallback
    else:
        raise
```

---

## 8. Performance Optimization

### 8.1 Inference Optimization
**Strategies:**
1. **Model Quantization:** 4-bit → 60% memory reduction
2. **KV Cache Reuse:** Cache attention keys/values
3. **Batched Processing:** Process multiple requests together
4. **Speculative Decoding:** Faster generation for common patterns

**Expected Performance:**
- Cold start: ~5 seconds (model loading)
- Warm inference: 1-2 seconds per response
- Memory usage: ~6GB GPU VRAM (with 4-bit quantization)

---

## 20. Conclusion

This PDR outlines a comprehensive, production-ready Discord chatbot with advanced memory systems and personalized responses through fine-tuned language models. The system balances performance, cost, and user experience while remaining extensible for future enhancements.

**Key Strengths:**
- ✅ Sophisticated memory architecture (RAG + dynamic summarization)
- ✅ Efficient training with LoRA (fast iterations, low cost)
- ✅ Scalable design (can handle multiple servers)
- ✅ Privacy-conscious (local deployment option)
- ✅ Well-defined testing and monitoring strategy

**Next Steps:**
1. Review and approve PDR
2. Begin Phase 1 development
3. Collect initial training data
4. Set up development environment

**Estimated Timeline:** 8-9 weeks to production-ready v1.0

---

**Document Version:** 1.0  
**Last Updated:** January 2, 2026  
**Status:** Approved / Pending Review / Draft
