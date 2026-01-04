# Configuration Reference

Complete guide to all configurable settings in your Discord chatbot.

---

## Quick Reference

| Setting | Default | Range | Effect |
|---------|---------|-------|--------|
| `SHORT_TERM_WINDOW` | 20 | 10-50 | How many messages to remember per channel |
| `SHORT_TERM_MAX_CONTEXT` | 10 | 5-15 | Messages included in AI prompt |
| `MAX_NEW_TOKENS` | 150 | 50-300 | Response length |
| `TEMPERATURE` | 0.7 | 0.1-1.5 | Randomness/creativity |
| `REPETITION_PENALTY` | 1.1 | 1.0-1.5 | Avoid repeating words |
| `LONG_TERM_TOP_K` | 3 | 1-5 | Past memories to recall |

---

## Memory Settings

### Short-Term Memory

#### `SHORT_TERM_WINDOW`
**Purpose**: How many recent messages to store per channel  
**Default**: `20`  
**Recommended**: 10-50

- **10-15**: Minimal memory, faster, less context
- **20-30**: Balanced (recommended)
- **40-50**: Maximum context, slower lookups

**Example**:
```env
SHORT_TERM_WINDOW=20  # Remember last 20 messages per channel
```

**Impact**:
- Higher → More conversation history
- Higher → More RAM usage (~1KB per message)
- Doesn't affect prompt directly (see `SHORT_TERM_MAX_CONTEXT`)

---

#### `SHORT_TERM_MAX_CONTEXT`
**Purpose**: How many messages to include in the AI prompt  
**Default**: `10`  
**Recommended**: 5-15

- **5**: Faster, less context-aware
- **10**: Balanced (recommended)
- **15**: Maximum context, slower generation

**Example**:
```env
SHORT_TERM_MAX_CONTEXT=10  # Include last 10 messages in prompt
```

**Impact**:
- Higher → More context-aware responses
- Higher → Slower generation (~50ms per message)
- Cannot exceed `SHORT_TERM_WINDOW`

**Tip**: Keep this at 50% of `SHORT_TERM_WINDOW`
```env
SHORT_TERM_WINDOW=20
SHORT_TERM_MAX_CONTEXT=10  # 50% of window
```

---

### Long-Term Memory (RAG)

#### `ENABLE_LONG_TERM_MEMORY`
**Purpose**: Enable persistent memory across sessions  
**Default**: `false`  
**Options**: `true` or `false`

**Example**:
```env
ENABLE_LONG_TERM_MEMORY=true  # Enable persistent memory
```

**Benefits**:
- Remembers conversations from days/weeks ago
- Maintains personality consistency over time
- Recalls important facts about users

**Costs**:
- ~500MB disk space for vector database
- ~200ms extra latency per response
- Requires ChromaDB

---

#### `LONG_TERM_DB_PATH`
**Purpose**: Where to store the vector database  
**Default**: `./data/vector_db`

**Example**:
```env
LONG_TERM_DB_PATH=./data/vector_db
```

---

#### `LONG_TERM_TOP_K`
**Purpose**: How many past memories to retrieve per query  
**Default**: `3`  
**Recommended**: 1-5

- **1**: Single most relevant memory
- **3**: Balanced (recommended)
- **5**: Maximum context from past

**Example**:
```env
LONG_TERM_TOP_K=3  # Retrieve 3 relevant past conversations
```

**Impact**:
- Higher → More relevant past context
- Higher → Slightly slower retrieval (~50ms per memory)

---

#### `EMBEDDING_MODEL`
**Purpose**: Model used for semantic search  
**Default**: `sentence-transformers/all-MiniLM-L6-v2`

**Options**:
- `all-MiniLM-L6-v2` - Fast, small (80MB)
- `all-mpnet-base-v2` - Better quality (420MB)
- `multi-qa-MiniLM-L6-cos-v1` - Best for Q&A (80MB)

**Example**:
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## Response Generation

### `MAX_NEW_TOKENS`
**Purpose**: Maximum length of responses  
**Default**: `150`  
**Recommended**: 50-300

- **50-100**: Short, snappy responses (1 sentence)
- **150-200**: Balanced (1-3 sentences)
- **250-300**: Long, detailed responses (paragraph)

**Example**:
```env
MAX_NEW_TOKENS=150  # ~1-2 sentences
```

**Impact**:
- Higher → Longer responses
- Higher → Slower generation (~50ms per 10 tokens)

**Note**: Bot may stop before reaching max if it naturally ends the response.

---

### `TEMPERATURE`
**Purpose**: Controls randomness/creativity  
**Default**: `0.7`  
**Recommended**: 0.1-1.5

- **0.1-0.5**: Focused, consistent, predictable
- **0.6-0.8**: Balanced, natural (recommended)
- **0.9-1.2**: Creative, varied, sometimes wild
- **1.3+**: Very random, experimental

**Example**:
```env
TEMPERATURE=0.7  # Balanced creativity
```

**Personality Impact**:
```
0.5: "yeah that sounds good"
0.7: "yeah sure! that sounds pretty good"
0.9: "oh hell yeah! that sounds awesome lol"
1.2: "YESSS omg that sounds amazing!! 🔥"
```

---

### `TOP_P` (Nucleus Sampling)
**Purpose**: Limits token selection to top probability mass  
**Default**: `0.9`  
**Recommended**: 0.85-0.95

- **0.85**: More focused
- **0.9**: Balanced (recommended)
- **0.95**: More diverse

**Example**:
```env
TOP_P=0.9  # Consider top 90% probable tokens
```

**Rarely needs adjustment** - `TEMPERATURE` is usually sufficient.

---

### `TOP_K` (Top-K Sampling)
**Purpose**: Limits token selection to top K most likely  
**Default**: `40`  
**Recommended**: 20-60

- **20-30**: More focused vocabulary
- **40-50**: Balanced (recommended)
- **60+**: More varied vocabulary

**Example**:
```env
TOP_K=40  # Consider top 40 most likely tokens
```

**Rarely needs adjustment** - `TEMPERATURE` is usually sufficient.

---

### `REPETITION_PENALTY`
**Purpose**: Discourages repeating words  
**Default**: `1.1`  
**Recommended**: 1.0-1.5

- **1.0**: No penalty (may repeat)
- **1.1**: Light penalty (recommended)
- **1.2-1.3**: Medium penalty
- **1.4-1.5**: Strong penalty (less natural)

**Example**:
```env
REPETITION_PENALTY=1.1  # Slightly discourage repetition
```

**Use higher values if**:
- Bot repeats same phrases
- Responses feel stuck in loops
- Too much "yeah yeah yeah" or "lol lol lol"

---

## Model Settings

### `CONTEXT_TOKENS`
**Purpose**: Maximum context length for model  
**Default**: `384`  
**Recommended**: Don't change

**Why 384?**
- Optimized for RTX 2080 Ti (11GB VRAM)
- Balances context vs. memory usage
- Matches training configuration

**Only increase if**:
- You have more VRAM (16GB+)
- You need longer conversation history

---

### `LOAD_IN_4BIT`
**Purpose**: Enable 4-bit quantization  
**Default**: `true`  
**Required**: `true` for 11GB VRAM

**Example**:
```env
LOAD_IN_4BIT=true  # Required for RTX 2080 Ti
```

**Do not disable** unless you have 24GB+ VRAM.

---

### `DEVICE`
**Purpose**: Compute device  
**Default**: `cuda`  
**Options**: `cuda`, `cpu`, `mps` (Mac)

**Example**:
```env
DEVICE=cuda  # Use NVIDIA GPU
```

---

## Summarization (Optional)

### `ENABLE_SUMMARIZATION`
**Purpose**: Automatically summarize long conversations  
**Default**: `false`  
**Options**: `true` or `false`

**Example**:
```env
ENABLE_SUMMARIZATION=true  # Enable auto-summarization
```

**Benefits**:
- Compresses long conversations
- Maintains context without token limit
- Better long-term memory storage

**Costs**:
- Requires BART model (~1.6GB)
- Adds ~2-3 seconds per summary

---

### `SUMMARIZATION_MODEL`
**Purpose**: Model for summarization  
**Default**: `facebook/bart-large-cnn`

**Options**:
- `facebook/bart-large-cnn` - Best quality (1.6GB)
- `sshleifer/distilbart-cnn-12-6` - Faster, smaller (1.2GB)

---

### `SUMMARIZE_THRESHOLD`
**Purpose**: When to trigger summarization  
**Default**: `30`  
**Recommended**: 20-50

**Example**:
```env
SUMMARIZE_THRESHOLD=30  # Summarize when >30 messages
```

---

### `SUMMARY_MAX_LENGTH`
**Purpose**: Maximum summary length  
**Default**: `150`  
**Recommended**: 100-200

---

### `SUMMARY_MIN_LENGTH`
**Purpose**: Minimum summary length  
**Default**: `40`  
**Recommended**: 30-60

---

## System Settings

### `LOG_LEVEL`
**Purpose**: Logging verbosity  
**Default**: `INFO`  
**Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Example**:
```env
LOG_LEVEL=INFO  # Standard logging
```

**Use `DEBUG` for**:
- Troubleshooting issues
- Monitoring performance
- Development

**Use `WARNING` for**:
- Production (less noise)
- Performance (faster)

---

## Common Configurations

### Chatty Bot (Creative & Long)
```env
MAX_NEW_TOKENS=200
TEMPERATURE=0.9
REPETITION_PENALTY=1.0
SHORT_TERM_WINDOW=30
SHORT_TERM_MAX_CONTEXT=15
```

### Concise Bot (Short & Focused)
```env
MAX_NEW_TOKENS=100
TEMPERATURE=0.5
REPETITION_PENALTY=1.2
SHORT_TERM_WINDOW=15
SHORT_TERM_MAX_CONTEXT=8
```

### Balanced Bot (Recommended)
```env
MAX_NEW_TOKENS=150
TEMPERATURE=0.7
REPETITION_PENALTY=1.1
SHORT_TERM_WINDOW=20
SHORT_TERM_MAX_CONTEXT=10
```

### Memory-Heavy Bot (Maximum Context)
```env
SHORT_TERM_WINDOW=50
SHORT_TERM_MAX_CONTEXT=15
ENABLE_LONG_TERM_MEMORY=true
LONG_TERM_TOP_K=5
ENABLE_SUMMARIZATION=true
```

### Performance Bot (Fastest Responses)
```env
MAX_NEW_TOKENS=100
SHORT_TERM_WINDOW=10
SHORT_TERM_MAX_CONTEXT=5
ENABLE_LONG_TERM_MEMORY=false
ENABLE_SUMMARIZATION=false
```

---

## Performance Impact

| Setting | Speed Impact | Quality Impact |
|---------|--------------|----------------|
| `MAX_NEW_TOKENS` | High | Medium |
| `SHORT_TERM_MAX_CONTEXT` | Medium | High |
| `TEMPERATURE` | None | High |
| `ENABLE_LONG_TERM_MEMORY` | Medium | Medium |
| `LONG_TERM_TOP_K` | Low | Medium |
| `ENABLE_SUMMARIZATION` | High | Medium |

**Fastest Configuration**:
- `MAX_NEW_TOKENS=100`
- `SHORT_TERM_MAX_CONTEXT=5`
- `ENABLE_LONG_TERM_MEMORY=false`
- Result: ~500ms per response

**Balanced Configuration** (Recommended):
- `MAX_NEW_TOKENS=150`
- `SHORT_TERM_MAX_CONTEXT=10`
- `ENABLE_LONG_TERM_MEMORY=false`
- Result: ~800ms per response

**Quality Configuration**:
- `MAX_NEW_TOKENS=200`
- `SHORT_TERM_MAX_CONTEXT=15`
- `ENABLE_LONG_TERM_MEMORY=true`
- `LONG_TERM_TOP_K=5`
- Result: ~1200ms per response

---

## Troubleshooting Settings

### Bot is too random/chaotic
```env
TEMPERATURE=0.5  # Lower = more focused
REPETITION_PENALTY=1.2  # Higher = less repetition
```

### Bot is too repetitive
```env
TEMPERATURE=0.9  # Higher = more varied
REPETITION_PENALTY=1.3  # Higher = penalize more
TOP_K=60  # Higher = more vocabulary
```

### Bot responses too short
```env
MAX_NEW_TOKENS=200  # Increase max length
```

### Bot responses too long
```env
MAX_NEW_TOKENS=100  # Decrease max length
```

### Bot forgets context too quickly
```env
SHORT_TERM_WINDOW=30  # Remember more messages
SHORT_TERM_MAX_CONTEXT=15  # Use more in prompt
ENABLE_LONG_TERM_MEMORY=true  # Enable persistent memory
```

### Bot too slow
```env
MAX_NEW_TOKENS=100  # Shorter responses
SHORT_TERM_MAX_CONTEXT=5  # Less context
ENABLE_LONG_TERM_MEMORY=false  # Disable LTM
```

---

## Testing Your Configuration

After changing settings, test with:
```powershell
python scripts\test_model.py
```

Monitor response quality and speed, then adjust as needed.

---

## Summary

**Start with defaults**, then adjust based on:
1. **Personality**: Adjust `TEMPERATURE` (0.5-0.9)
2. **Length**: Adjust `MAX_NEW_TOKENS` (100-200)
3. **Memory**: Adjust `SHORT_TERM_WINDOW` (15-30)
4. **Quality vs Speed**: Enable/disable `ENABLE_LONG_TERM_MEMORY`

**Most Important Settings**:
1. `TEMPERATURE` - Controls personality
2. `MAX_NEW_TOKENS` - Controls length
3. `SHORT_TERM_WINDOW` - Controls memory
4. `REPETITION_PENALTY` - Controls repetition

Have fun customizing your bot! 🎉
