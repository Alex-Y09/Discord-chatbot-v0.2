# Phase 3 Deployment Checklist

## Pre-Deployment

- [ ] **Phase 1 Complete**: Training data collected (`data/training_data.jsonl`)
- [ ] **Phase 2 Complete**: Model trained (`adapters/discord-lora/adapter_model.safetensors`)
- [ ] **Virtual Environment Active**: Run `.\venv\Scripts\Activate.ps1`
- [ ] **GPU Working**: Run `python scripts\check_gpu.py` to verify
- [ ] **Dependencies Installed**: Run `pip install -r requirements.txt`

## Bot Configuration

- [ ] **Discord Bot Created**: Created at https://discord.com/developers/applications
- [ ] **Bot Token Copied**: Copy from Developer Portal → Bot → Reset Token
- [ ] **Token in .env**: Add `DISCORD_BOT_TOKEN=your_token_here` to `.env`
- [ ] **Bot Invited to Server**: Use OAuth2 URL with proper permissions
- [ ] **Permissions Granted**: Read Messages, Send Messages, Read Message History (minimum 3072)

## Deployment Files

- [ ] **Bot Code**: `src/bot.py` exists
- [ ] **Inference Engine**: `src/model/inference.py` exists
- [ ] **Memory Systems**: `src/memory/*.py` files exist
- [ ] **Logs Directory**: `logs/` directory exists

## Testing

- [ ] **Model Test**: Run `python scripts\test_model.py` to verify responses
- [ ] **Readiness Check**: Run `.\deploy.ps1` → Option 1 (Check deployment readiness)

## Deployment Options

### Option A: Quick Test (Foreground)
```powershell
python src\bot.py
```
- See logs in real-time
- Press Ctrl+C to stop
- Good for initial testing

### Option B: Production (Background)
```powershell
.\deploy.ps1
```
- Select option 3: Start bot (background)
- Bot runs in background
- View logs with option 5

## Post-Deployment

- [ ] **Bot Online**: Check Discord - bot shows as online (green status)
- [ ] **Test Mention**: Send `@sususbot hey` in a channel
- [ ] **Bot Responds**: Bot should reply within 1-2 seconds
- [ ] **Check Logs**: Run `.\deploy.ps1` → Option 5 to view logs
- [ ] **Monitor Performance**: Watch for errors or slow responses

## Verification

**Expected Startup Logs**:
```
[INFO] Bot initialized
[INFO] Loading inference engine (this takes 2-3 minutes)...
[INFO] Loading base model: mistralai/Mistral-7B-v0.3
[INFO] Base model loaded!
[INFO] Loading trained adapter: adapters\discord-lora
[INFO] Adapter loaded!
[INFO] Inference engine ready!
[INFO] Bot setup complete!
[INFO] Bot connected as sususbot
[INFO] Bot is ready! Mention me (@sususbot) to chat!
```

**Expected Response Flow**:
1. User mentions bot: `@sususbot what's up?`
2. Bot shows typing indicator
3. Bot responds: `not much, just chillin. wbu?`
4. Logs show: `[INFO] Mentioned in #general by Username`
5. Logs show: `[INFO] Response sent in #general`

## Troubleshooting

**Bot doesn't start**:
- Check `.env` has `DISCORD_BOT_TOKEN`
- Verify model exists at `adapters/discord-lora/`
- Check virtual environment is activated
- View error in `logs/bot.log`

**Bot doesn't respond**:
- Verify bot has permissions in channel
- Check bot was mentioned correctly (`@sususbot`)
- View logs for errors
- Test model with `python scripts\test_model.py`

**Responses are slow**:
- First response takes 3-4 seconds (normal)
- Subsequent responses should be <1 second
- Check GPU usage (should be 80-100% during generation)

**Bot crashes**:
- Check `logs/bot.log` for error messages
- Verify VRAM not full (should use ~5-6GB)
- Check internet connection is stable

## Success Criteria

✅ Bot shows online in Discord
✅ Bot responds to @mentions within 1-2 seconds
✅ Responses sound natural and match personality
✅ Bot remembers context within conversation
✅ No errors in logs
✅ GPU usage normal (~5-6GB VRAM)

## Next Steps

Once bot is running smoothly:

1. **Enable Long-Term Memory** (optional):
   - Edit `src/bot.py`
   - Uncomment lines 44-45:
     ```python
     self.long_term_memory = LongTermMemory()
     await self.long_term_memory.initialize()
     ```
   - Restart bot

2. **Production Deployment**:
   - Run bot on VPS/cloud server
   - Set up auto-restart (systemd/Task Scheduler)
   - Enable log rotation
   - Monitor uptime

3. **Fine-Tune Settings**:
   - Adjust `TEMPERATURE` in `.env` (0.7 = balanced, 0.9 = creative)
   - Adjust `MAX_NEW_TOKENS` (150 = longer responses, 100 = shorter)
   - Adjust `REPETITION_PENALTY` (1.1 = less repetition, 1.3 = even less)

## Notes

- **First startup**: Takes 2-3 minutes (loading model)
- **Memory usage**: ~5-6GB VRAM, ~2-3GB RAM
- **Response time**: <1 second (after first response)
- **Context memory**: Last 20 messages per channel
- **Multi-channel**: Works in any channel with permissions

---

**Your bot is ready! 🚀**

Start with foreground mode for testing:
```powershell
python src\bot.py
```

Then switch to background for production:
```powershell
.\deploy.ps1
# Select option 3: Start bot (background)
```

Have fun chatting with your AI! 🎉
