# 🚀 Phase 1 Start Guide - Data Collection & Preparation

**Goal:** Collect 63,000 Discord messages and prepare them for LLM training  
**Time Estimate:** 2-3 hours (mostly automated)  
**What You'll Get:** Ready-to-train dataset in `data/training_data.jsonl`

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- [ ] Discord Server (Guild) ID
- [ ] Target Channel ID (where 63k messages are)
- [ ] Python 3.10+ installed
- [ ] CUDA-capable GPU (for later training)

---

## 🎯 Phase 1 Overview

```
Step 1: Setup Environment (5 mins)
   ↓
Step 2: Configure Bot (3 mins)
   ↓
Step 3: Run Message Scraper (30-90 mins automated)
   ↓
Step 4: Analyze Dataset (5 mins)
   ↓
Step 5: Prepare Training Data (10 mins)
   ↓
✅ Ready for Phase 2 (Training)!
```

---

## 📝 Step-by-Step Instructions

### Step 1: Setup Environment (5 minutes)

```powershell
# Navigate to project directory
cd "c:\Users\abyia\iCloudDrive\Documents\python scripts\Discord Chatbot v0.2"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed discord.py-2.x.x transformers-4.x.x ...
✅ Environment ready!
```

---

### Step 2: Configure Bot (3 minutes)

#### 2.1 Create .env file
```powershell
# Copy template
Copy-Item .env.example .env

# Open in notepad
notepad .env
```

#### 2.2 Fill in Discord credentials

**Find your Bot Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application → Bot → Copy Token

**Find your Server ID:**
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click your server → Copy Server ID

**Find your Channel ID:**
1. Right-click the channel with 63k messages → Copy Channel ID

**Edit .env:**
```bash
# ============================================
# PHASE 1: DATA COLLECTION
# ============================================

# Discord Bot Credentials
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE          # Paste bot token
DISCORD_GUILD_ID=YOUR_SERVER_ID_HERE           # Paste server ID
DISCORD_CHANNEL_ID=YOUR_CHANNEL_ID_HERE        # Paste channel ID

# Scraper Settings
REQUESTS_PER_SECOND=40        # Fast collection (within Discord limits)
MAX_MESSAGES=65000            # Collect 65k (we expect 63k after filtering)
ENABLE_CHECKPOINT=true        # Resume if interrupted
CHECKPOINT_INTERVAL=1000      # Save progress every 1000 messages

# ============================================
# PHASE 2: TRAINING (Don't change yet)
# ============================================
# ... keep defaults for now ...
```

**Save and close** the file.

---

### Step 3: Run Message Scraper (30-90 minutes)

#### 3.1 Start the scraper
```powershell
# Run backfill script
python scripts/backfill_messages.py
```

#### 3.2 What to expect

**Initial Output:**
```
[INFO] Discord Message Backfill Script
[INFO] Target: Server ID 123..., Channel ID 456...
[INFO] Rate limit: 40 requests/second
[INFO] Checkpoint enabled: data/backfill_checkpoint.json
[INFO] Starting message collection...
```

**During Collection:**
```
[PROGRESS] Collected 1000/65000 messages (1.5%)
[PROGRESS] Collected 5000/65000 messages (7.7%)
[PROGRESS] Collected 10000/65000 messages (15.4%)
...
[CHECKPOINT] Saved progress: 10000 messages collected
```

**Time Estimates:**
- **Fast collection (40 req/s):** 30-40 minutes for 65k messages
- **Standard (20 req/s):** 60-80 minutes
- **Conservative (10 req/s):** 90-120 minutes

#### 3.3 If interrupted

Don't worry! The script saves checkpoints every 1000 messages.

**Just run it again:**
```powershell
python scripts/backfill_messages.py
```

**Output:**
```
[INFO] Found checkpoint: 10000 messages collected
[INFO] Resuming from message ID: abc123...
[PROGRESS] Collected 11000/65000 messages (16.9%)
```

#### 3.4 Completion

```
[SUCCESS] Collection complete!
[INFO] Total messages collected: 65,234
[INFO] Raw data saved to: data/raw_messages.jsonl
[INFO] Time taken: 35 minutes
[INFO] Next step: Run data analysis script
```

---

### Step 4: Analyze Dataset (5 minutes)

#### 4.1 Run analysis script
```powershell
python scripts/analyze_training_data.py
```

#### 4.2 Review statistics

**Expected Output:**
```
=== DISCORD TRAINING DATA ANALYSIS ===

📊 Dataset Statistics:
  Total messages: 65,234
  Unique authors: 47
  Date range: 2023-01-15 to 2026-01-02
  Average message length: 42 words
  Median message length: 28 words

🤖 Target Bot Messages:
  Bot username: sususbot
  Bot messages: 31,456 (48.2%)
  Average response length: 38 words

📝 Message Distribution:
  Very short (<5 words): 8,234 (12.6%)
  Short (5-15 words): 18,567 (28.5%)
  Medium (15-30 words): 22,145 (33.9%)
  Long (30-50 words): 11,892 (18.2%)
  Very long (>50 words): 4,396 (6.7%)

✅ Quality Metrics:
  Messages with context: 62,891 (96.4%)
  Single-word messages: 1,234 (1.9%)
  Emoji-only messages: 567 (0.9%)
  Command messages: 2,145 (3.3%)

🎯 Training Recommendations:
  ✅ Dataset size: Excellent (65k messages)
  ✅ Bot response rate: Good (48%)
  ✅ Message variety: Excellent
  ⚠️  Consider filtering: Commands, emoji-only
  
  Recommended filters:
    - Remove commands (!, /, .)
    - Remove emoji-only messages
    - Remove single-word replies
    
  Expected after filtering: ~63,000 messages
  Training time estimate: 13-18 hours (1 epoch)
```

#### 4.3 Save the report
```powershell
# Report is auto-saved to:
# data/analysis_report.txt
```

---

### Step 5: Prepare Training Data (10 minutes)

#### 5.1 Run data preparation script
```powershell
python scripts/prepare_training_data.py
```

#### 5.2 What this does

**Filtering:**
- ✅ Remove bot commands (`!`, `/`, `.` prefixes)
- ✅ Remove emoji-only messages
- ✅ Remove single-word replies
- ✅ Remove duplicate messages
- ✅ Remove system messages

**Formatting:**
- ✅ Convert to Mistral training format
- ✅ Add conversation context (previous 3-5 messages)
- ✅ Format as instruction-response pairs
- ✅ Validate token lengths

**Example Training Format:**
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are sususbot, a friendly Discord chatbot with a casual, playful personality."
    },
    {
      "role": "user", 
      "content": "UserA: hey what's up\nUserB: not much, you?\nUserC: @sususbot what do you think?"
    },
    {
      "role": "assistant",
      "content": "honestly same lol, just vibing"
    }
  ]
}
```

#### 5.3 Expected output

```
[INFO] Loading raw messages from: data/raw_messages.jsonl
[INFO] Total messages loaded: 65,234

[FILTER] Removing commands... (2,145 removed)
[FILTER] Removing emoji-only... (567 removed)
[FILTER] Removing single-word... (1,234 removed)
[FILTER] Removing duplicates... (89 removed)
[INFO] Messages after filtering: 63,199

[FORMAT] Converting to training format...
[FORMAT] Adding conversation context...
[FORMAT] Validating token lengths...
[INFO] Training examples created: 31,456
       (One example per bot response)

[VALIDATE] Checking data quality...
  ✅ All examples have context
  ✅ No empty responses
  ✅ Token lengths within limits
  ✅ Format validation passed

[SUCCESS] Training data ready!
[INFO] Saved to: data/training_data.jsonl
[INFO] Size: 247 MB
[INFO] Ready for Phase 2 (Training)

📊 Final Statistics:
  Training examples: 31,456
  Average context length: 156 tokens
  Average response length: 42 tokens
  Total tokens: ~6.2M tokens
  Estimated training time: 13-18 hours (1 epoch, optimized)
```

---

## ✅ Phase 1 Complete!

You now have:
- ✅ `data/raw_messages.jsonl` - Raw scraped data (65k messages)
- ✅ `data/training_data.jsonl` - Filtered training data (31k examples)
- ✅ `data/analysis_report.txt` - Dataset statistics
- ✅ `data/backfill_checkpoint.json` - Resume checkpoint (can delete)

---

## 🎯 Next Steps

### Verify Your Data

```powershell
# Check file sizes
Get-ChildItem data\*.jsonl | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}

# Expected output:
# Name                    Size(MB)
# ----                    --------
# raw_messages.jsonl      412.34
# training_data.jsonl     247.89
```

### Quick Data Sample

```powershell
# View first training example
Get-Content data\training_data.jsonl -First 1 | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Ready for Phase 2?

When you're ready to train:
```powershell
# Just say: "Start Phase 2"
# I'll create the training script and guide you through it!
```

---

## 🐛 Troubleshooting

### "Forbidden: Missing Access" Error
```powershell
# Your bot needs these permissions:
# - Read Message History
# - Read Messages/View Channels

# Fix: Go to Discord Developer Portal → Bot → Privileged Gateway Intents
# Enable: MESSAGE CONTENT INTENT
```

### "Rate Limited" Warning
```powershell
# Script will automatically slow down
# You'll see: [WARN] Rate limited, waiting 60 seconds...
# This is normal, just wait
```

### Script Crashes/Freezes
```powershell
# 1. Check logs
Get-Content logs\backfill.log -Tail 50

# 2. Restart from checkpoint
python scripts/backfill_messages.py

# 3. Reduce request rate in .env
# Change: REQUESTS_PER_SECOND=20 (instead of 40)
```

### Out of Disk Space
```powershell
# Check available space
Get-PSDrive C | Select-Object Used, Free

# You need at least 5GB free for:
# - Raw messages: ~400MB
# - Training data: ~250MB  
# - Model cache: ~3GB
# - Temp files: ~1GB
```

---

## 📊 Progress Tracking

Use this checklist to track your progress:

- [ ] Environment setup complete
- [ ] .env configured with Discord credentials
- [ ] Backfill script started
- [ ] Message collection complete (65k+ messages)
- [ ] Analysis script run
- [ ] Analysis report reviewed
- [ ] Training data prepared
- [ ] Final validation passed
- [ ] Ready for Phase 2! 🎉

---

## 💡 Tips

**Tip 1: Run overnight**
If you have millions of messages, start the scraper before bed:
```powershell
python scripts/backfill_messages.py > logs\scraper.log 2>&1
```

**Tip 2: Multiple channels**
Want data from multiple channels? Edit the script:
```python
CHANNEL_IDS = [123, 456, 789]  # Multiple channels
```

**Tip 3: Speed vs Safety**
- Fast (40 req/s): Risky, may hit rate limits
- Standard (20 req/s): Recommended balance
- Safe (10 req/s): Slow but guaranteed no issues

---

## 📞 Need Help?

If something goes wrong:

1. **Check logs:** `logs\backfill.log` and `logs\prep.log`
2. **Review error messages:** They usually explain the issue
3. **Try the troubleshooting section above**
4. **Ask me!** Just describe what you're seeing

---

**Ready?** Let's start with Step 1! 🚀

```powershell
# Copy and paste:
cd "c:\Users\abyia\iCloudDrive\Documents\python scripts\Discord Chatbot v0.2"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
