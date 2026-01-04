# Discord Chatbot v0.2 - Deployment Guide

## Phase 3: Deployment

You've successfully trained your model! Now let's deploy the bot to Discord.

---

## Quick Start

### Option 1: Interactive Menu (Recommended)
```powershell
.\deploy.ps1
```

### Option 2: Direct Command
```powershell
python src\bot.py
```

---

## Pre-Deployment Checklist

Before starting the bot, make sure:

- [ ] Virtual environment activated (`.\venv\Scripts\Activate.ps1`)
- [ ] `.env` file configured with your Discord bot token
- [ ] Trained model exists at `adapters/discord-lora/`
- [ ] Bot has been invited to your Discord server
- [ ] Bot has required permissions (Read Messages, Send Messages, Read Message History)

---

## Bot Configuration

### Discord Bot Token

1. **Get your bot token** (if you don't have one):
   - Go to https://discord.com/developers/applications
   - Select your application → Bot → Reset Token
   - Copy the token

2. **Add token to `.env`**:
   ```env
   DISCORD_BOT_TOKEN=your_token_here
   ```

### Bot Invite Link

Generate an invite link with these permissions:
- Read Messages/View Channels
- Send Messages  
- Read Message History
- Use Slash Commands (optional)

**Required Permission Integer**: `3072` (minimum)

**Invite URL Template**:
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=3072&scope=bot
```

Replace `YOUR_CLIENT_ID` with your bot's Client ID from the Discord Developer Portal.

---

## How It Works

### Bot Behavior

- **Trigger**: Bot responds when mentioned (`@sususbot`)
- **Multi-Channel**: Works in any channel it has access to
- **Context Aware**: Remembers last 20 messages per channel
- **Personality**: Uses your trained model to respond naturally

### Example Interaction

```
User: @sususbot hey what's up?
Bot: hey! not much, just vibing. wbu?

User: @sususbot wanna watch a movie?
Bot: yeah sure! what kind of movie you thinking?
```

### Memory System

**Short-Term Memory**:
- Keeps last 20 messages per channel
- Provides conversation context
- Resets when bot restarts

**Long-Term Memory** (optional, disabled by default):
- Stores important conversations in vector database
- Retrieves relevant context from past conversations
- Persists across bot restarts

To enable long-term memory, uncomment these lines in [src/bot.py](src/bot.py):
```python
# Line ~44-45
self.long_term_memory = LongTermMemory()
await self.long_term_memory.initialize()
```

---

## Running the Bot

### Foreground Mode (Recommended for Testing)

```powershell
python src\bot.py
```

**Pros**:
- See logs in real-time
- Easy to stop (Ctrl+C)
- Good for debugging

**Cons**:
- Blocks terminal
- Stops if terminal closes

### Background Mode (Recommended for Production)

**PowerShell** (Windows):
```powershell
Start-Job -ScriptBlock { 
    Set-Location "C:\path\to\Discord Chatbot v0.2"
    .\venv\Scripts\python.exe src\bot.py 
}
```

**Or use the deploy script**:
```powershell
.\deploy.ps1
# Select option 3: Start bot (background)
```

**Linux/Mac**:
```bash
nohup python src/bot.py > logs/bot.log 2>&1 &
```

---

## Monitoring

### View Logs (Live)

**PowerShell**:
```powershell
Get-Content logs\bot.log -Wait -Tail 50
```

**Linux/Mac**:
```bash
tail -f logs/bot.log
```

### View Logs (File)

```powershell
notepad logs\bot.log
```

### Check Bot Status

Look for these log messages:

✅ **Successful Startup**:
```
[INFO] Bot connected as sususbot
[INFO] Bot ID: 123456789
[INFO] Bot is ready! Mention me (@sususbot) to chat!
```

❌ **Common Errors**:
- `DISCORD_BOT_TOKEN not set` → Add token to `.env`
- `Trained model not found` → Run Phase 2 training first
- `Improper token` → Check your bot token is correct
- `Missing Access` → Bot needs permissions in the channel

---

## Performance Optimization

### Startup Time

**First load**: 2-3 minutes (loading Mistral-7B + adapter)
**Subsequent responses**: <1 second

**Tip**: Keep bot running 24/7 to avoid reload time.

### Memory Usage

- **GPU VRAM**: ~5-6 GB (4-bit quantization)
- **RAM**: ~2-3 GB
- **Disk**: ~15 GB (model files)

### Response Time

- **Typical**: 500ms - 1 second
- **Long responses**: 1-2 seconds
- **First response**: 3-4 seconds (if just started)

---

## Advanced Configuration

### Environment Variables

Edit `.env` to customize:

```env
# Response length (tokens)
MAX_NEW_TOKENS=150

# Temperature (0.0-1.0, higher = more random)
TEMPERATURE=0.7

# Top-p sampling (0.0-1.0)
TOP_P=0.9

# Top-k sampling
TOP_K=40

# Repetition penalty (1.0-2.0, higher = less repetition)
REPETITION_PENALTY=1.1
```

### Generation Parameters

**Temperature**: Controls randomness
- `0.7` (default): Balanced, natural responses
- `0.9`: More creative, sometimes wild
- `0.5`: More focused, conservative

**Max Tokens**: Response length
- `150` (default): ~1-2 Discord messages
- `100`: Shorter, snappier responses
- `200`: Longer, more detailed responses

---

## Troubleshooting

### Bot doesn't respond

1. **Check bot is online in Discord** (green status)
2. **Verify bot was mentioned** (`@sususbot`)
3. **Check permissions** (Read Messages, Send Messages)
4. **View logs** for errors (`logs/bot.log`)

### Responses are slow

1. **Check GPU usage** → Should be ~80-100% during generation
2. **Reduce MAX_NEW_TOKENS** → Shorter = faster
3. **Check VRAM** → If low, close other GPU applications

### Responses are repetitive

1. **Increase REPETITION_PENALTY** → Try `1.2` or `1.3`
2. **Increase TEMPERATURE** → Try `0.8` or `0.9`
3. **Check training data** → May need more diverse examples

### Bot crashes or disconnects

1. **Check logs** → `logs/bot.log` for error messages
2. **Check internet** → Bot needs stable connection
3. **Check token** → May have expired or been reset
4. **Check VRAM** → Out-of-memory errors

---

## Stopping the Bot

### Foreground Mode
Press `Ctrl+C` in the terminal

### Background Mode

**PowerShell**:
```powershell
Get-Job | Where-Object { $_.Command -like "*bot.py*" } | Stop-Job
Get-Job | Remove-Job
```

**Linux/Mac**:
```bash
pkill -f "python src/bot.py"
```

---

## Next Steps

### Production Deployment

1. **Use a VPS/Cloud Server**:
   - DigitalOcean, AWS, Google Cloud
   - Minimum: 16GB RAM, GPU optional (can use CPU)
   - Keep bot running 24/7

2. **Enable Long-Term Memory**:
   - Uncomment LTM initialization in `src/bot.py`
   - Improves personality consistency over time

3. **Add Monitoring**:
   - Set up log rotation
   - Monitor memory usage
   - Track response times

4. **Implement Auto-Restart**:
   - Use systemd (Linux) or Task Scheduler (Windows)
   - Automatically restart if bot crashes

### Feature Additions

- **Multi-user conversations**: Group chat support
- **Image understanding**: Add vision capabilities
- **Voice chat**: Text-to-speech responses
- **Custom commands**: Add utility commands
- **Dashboard**: Web interface for monitoring

---

## Support

If you encounter issues:

1. **Check logs**: `logs/bot.log`
2. **Review checklist**: Deployment readiness
3. **Test model**: Run `python scripts\test_model.py`
4. **Check GPU**: Run `python scripts\check_gpu.py`

---

## Files Created

```
src/
├── bot.py                    # Main Discord bot
├── model/
│   └── inference.py          # Model inference engine
└── memory/
    ├── short_term.py         # Short-term memory (20 messages)
    ├── long_term.py          # Long-term memory (RAG/ChromaDB)
    └── summarizer.py         # Conversation summarizer

deploy.ps1                    # Deployment quick-start menu
DEPLOYMENT_GUIDE.md          # This file
```

---

## Summary

✅ **Phase 1**: Data collection (Complete)
✅ **Phase 2**: Model training (Complete)
✅ **Phase 3**: Deployment (Ready!)

Your bot is ready to go live! Start with foreground mode to test, then switch to background for production.

**Have fun chatting with your AI! 🎉**
