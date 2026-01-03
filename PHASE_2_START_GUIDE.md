# 🚀 Phase 2 Start Guide - LLM Training

**Goal:** Fine-tune Mistral-7B with your Discord data using LoRA  
**Time Estimate:** 13-18 hours (automated, optimized for RTX 2080 Ti)  
**What You'll Get:** Trained LoRA adapter in `adapters/discord-lora/`

---

## 📋 Prerequisites Checklist

Before starting Phase 2, verify:

- [x] **Phase 1 Complete** - You have `data/training_data.jsonl`
- [ ] **GPU Available** - NVIDIA GPU with CUDA (RTX 2080 Ti or better)
- [ ] **VRAM Check** - At least 11GB VRAM (check with `nvidia-smi`)
- [ ] **Disk Space** - At least 15GB free (model + checkpoints)
- [ ] **Time Available** - 13-18 hours (can run overnight/background)
- [ ] **Python Environment** - Virtual environment activated

---

## 🎯 Phase 2 Overview

```
Step 1: Pre-Training Setup (10 mins)
   ↓
Step 2: Download Model (5-10 mins, ~7GB)
   ↓
Step 3: Start Training (13-18 hours automated)
   ↓
Step 4: Verify Training (5 mins)
   ↓
✅ Ready for Phase 3 (Deployment)!
```

---

## 📝 Step-by-Step Instructions

### Step 1: Pre-Training Setup (10 minutes)

#### 1.1 Verify Phase 1 completion
```powershell
# Check if training data exists
if (Test-Path "data\training_data.jsonl") {
    Write-Host "✅ Training data found" -ForegroundColor Green
    $size = (Get-Item "data\training_data.jsonl").Length / 1MB
    Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
} else {
    Write-Host "❌ Training data not found! Run Phase 1 first." -ForegroundColor Red
}
```

**Expected:** `data/training_data.jsonl` should be ~250 MB

#### 1.2 Check GPU availability
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Check GPU
python -c "import torch; print('GPU Available:', torch.cuda.is_available()); print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'); print('VRAM:', torch.cuda.get_device_properties(0).total_memory / 1024**3, 'GB' if torch.cuda.is_available() else '')"
```

**Expected Output:**
```
GPU Available: True
GPU Name: NVIDIA GeForce RTX 2080 Ti
VRAM: 11.0 GB
```

#### 1.3 Install additional training dependencies
```powershell
# Install training-specific packages
pip install peft bitsandbytes accelerate
```

**Note:** These weren't in Phase 1 requirements - they're only needed for training.

#### 1.4 Check .env configuration
```powershell
# Review training settings
notepad .env
```

**Verify these Phase 2 settings:**
```bash
# Training Settings (OPTIMIZED - DO NOT CHANGE)
LEARNING_RATE=2.5e-4
EPOCHS=1
BATCH_SIZE=1
GRADIENT_ACCUMULATION_STEPS=32
GRADIENT_CHECKPOINTING=true
USE_FP16=true
LOAD_IN_4BIT=true

# Model
MODEL_NAME=mistralai/Mistral-7B-v0.3
CONTEXT_TOKENS=384
```

---

### Step 2: Download Model (5-10 minutes)

The training script will automatically download Mistral-7B-v0.3 (~7GB) on first run.

**To pre-download (optional):**
```powershell
python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; print('Downloading model...'); AutoTokenizer.from_pretrained('mistralai/Mistral-7B-v0.3'); print('✅ Model cached')"
```

**What's happening:**
- Downloads to: `~/.cache/huggingface/`
- Size: ~7GB (one-time download)
- Time: 5-10 minutes (depends on internet speed)

---

### Step 3: Start Training (13-18 hours)

#### 3.1 Start training script

**Option A: Foreground (watch progress)**
```powershell
python training\train_lora.py
```

**Option B: Background (recommended for overnight)**
```powershell
# Run in background and log to file
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python training\train_lora.py" -WindowStyle Minimized
```

**Option C: Linux/tmux (if on Linux)**
```bash
tmux new -s training
python training/train_lora.py
# Detach: Ctrl+B, then D
# Reattach: tmux attach -t training
```

#### 3.2 What to expect - Initial output

```
==========================================================
Discord Chatbot Training - Phase 2
==========================================================
Model: mistralai/Mistral-7B-v0.3
Training data: ./data/training_data.jsonl
Output: ./adapters/discord-lora
Epochs: 1
Learning rate: 2.5e-4
Gradient accumulation: 32
Mixed precision (FP16): True
4-bit quantization: True
==========================================================
Loading tokenizer...
✅ Tokenizer loaded: 32000 tokens
Loading model with 4-bit quantization...
This will take 5-10 minutes (downloading ~7GB)...
```

#### 3.3 During training

**Progress updates (every 10 steps):**
```
Step 10/980 | Loss: 2.453 | LR: 0.00024 | Time: 45s
Step 20/980 | Loss: 2.234 | LR: 0.00024 | Time: 1m 30s
Step 30/980 | Loss: 2.087 | LR: 0.00024 | Time: 2m 15s
...
```

**Checkpoints (every 500 steps):**
```
Saving checkpoint at step 500...
✅ Checkpoint saved: ./adapters/discord-lora/checkpoint-500
```

**Time estimates:**
- **Total steps:** ~980 (depends on your data)
- **Time per step:** ~50-70 seconds
- **Total time:** 13-18 hours
- **Checkpoint frequency:** Every 500 steps (~7-8 hours)

#### 3.4 Monitor progress (separate terminal)

```powershell
# Watch log file
Get-Content logs\training.log -Wait -Tail 20

# Check GPU usage
nvidia-smi -l 5  # Updates every 5 seconds

# Check disk space
Get-PSDrive C
```

**Expected GPU usage:**
- **VRAM:** 8-9 GB / 11 GB (~80%)
- **GPU Utilization:** 95-100%
- **Temperature:** 70-80°C (normal under load)
- **Power:** 200-250W

#### 3.5 What if training stops?

**Resume from checkpoint:**
```powershell
# Find latest checkpoint
Get-ChildItem adapters\discord-lora\checkpoint-* | Sort-Object Name | Select-Object -Last 1

# Resume training
python training\train_lora.py --resume adapters\discord-lora\checkpoint-500
```

---

### Step 4: Verify Training (5 minutes)

#### 4.1 Check if training completed

**Look for this in logs:**
```
==========================================================
✅ Training complete!
==========================================================
Saving final model...
✅ Model saved to: ./adapters/discord-lora
```

#### 4.2 Verify output files

```powershell
# Check adapter directory
Get-ChildItem adapters\discord-lora -Recurse | Select-Object Name, Length

# Expected files:
# adapter_config.json
# adapter_model.bin (or .safetensors)
# tokenizer files
# training_args.bin
```

**Expected structure:**
```
adapters/discord-lora/
├── adapter_config.json       (~1 KB)
├── adapter_model.bin         (~30-50 MB)
├── tokenizer_config.json
├── tokenizer.json
├── special_tokens_map.json
└── checkpoint-xxx/           (can delete after completion)
```

#### 4.3 Check training metrics

```powershell
# View final loss
Get-Content logs\training.log | Select-String "Loss:" | Select-Object -Last 5
```

**Good training indicators:**
- Loss decreases over time (e.g., 2.5 → 1.2)
- No NaN or infinite values
- Checkpoints saved successfully
- Final model files present

---

## ⏱️ Time Management

### Can I Close My Computer?

**Yes, with caveats:**

1. **Desktop PC:** Leave it on, training continues ✅
2. **Laptop:** 
   - Plugged in: ✅ OK (may get hot)
   - On battery: ❌ Don't do this (will drain + thermal throttle)
   - Closing lid: ❌ May sleep/hibernate

**Best practices:**
- ☕ Start in the morning, check in the evening
- 🌙 Start before bed, check next morning
- 🖥️ Use a desktop PC if possible
- 🔌 Keep laptop plugged in and lid open
- ❄️ Ensure good ventilation

### Training Schedule

| Start Time | Expected Completion | Best For |
|------------|---------------------|----------|
| 8 AM | 1-2 AM next day | Start before work |
| 6 PM | 9-12 PM next day | Overnight training |
| 10 PM | 1-4 PM next day | Sleep through it |

---

## 🐛 Troubleshooting

### Issue 1: Out of Memory (OOM)

**Error:**
```
RuntimeError: CUDA out of memory
```

**Solution 1 - Reduce batch accumulation:**
```bash
# Edit .env:
GRADIENT_ACCUMULATION_STEPS=16  # Was 32
```
⚠️ This will make training slower (~25 hours instead of 13-18)

**Solution 2 - Close other programs:**
```powershell
# Close browser, Discord, other GPU apps
# Check GPU usage:
nvidia-smi
```

**Solution 3 - Reduce context length:**
```bash
# Edit .env:
CONTEXT_TOKENS=256  # Was 384
```

### Issue 2: Training is Very Slow

**Check GPU utilization:**
```powershell
nvidia-smi
```

**If GPU is <50% utilized:**
- Check if using CPU instead: `DEVICE=cuda` in .env
- Update GPU drivers
- Close background applications

**If GPU is 100% utilized:**
- This is normal! Just wait.
- Each step should take 50-70 seconds

### Issue 3: Loss Not Decreasing

**Check after 100 steps:**
- Loss should be decreasing (even slowly)
- If stuck or increasing, learning rate may be wrong

**Solution:**
```bash
# Edit .env - reduce learning rate:
LEARNING_RATE=1e-4  # Was 2.5e-4
```

Then restart training.

### Issue 4: Training Crashed

**Check logs:**
```powershell
Get-Content logs\training.log -Tail 50
```

**Resume from checkpoint:**
```powershell
# Find latest checkpoint
$latest = Get-ChildItem adapters\discord-lora\checkpoint-* | Sort-Object Name | Select-Object -Last 1
python training\train_lora.py --resume $latest.FullName
```

### Issue 5: Model Download Fails

**Error:**
```
HTTPError: 404 Client Error
```

**Solution:**
```powershell
# Check internet connection
# Check HuggingFace status: https://status.huggingface.co
# Try manual download:
python -c "from huggingface_hub import snapshot_download; snapshot_download('mistralai/Mistral-7B-v0.3')"
```

---

## 📊 Understanding Training Output

### What is "Loss"?

**Loss** measures how wrong the model's predictions are:
- **High loss (>2.0):** Model is still learning
- **Medium loss (1.0-2.0):** Model is improving
- **Low loss (<1.0):** Model is well-trained
- **Very low loss (<0.5):** May be overfitting (but with 63k messages, unlikely)

### Training Phases

```
Steps 0-100:   Warmup (loss may fluctuate)
Steps 100-500: Fast learning (loss drops quickly)
Steps 500-800: Refinement (loss decreases slowly)
Steps 800-980: Fine-tuning (loss stabilizes)
```

### Good vs. Bad Training

**✅ Good Signs:**
- Loss decreases steadily
- GPU utilization 90-100%
- Checkpoints save successfully
- No NaN/Inf values

**❌ Bad Signs:**
- Loss increases or stays constant
- Loss becomes NaN
- GPU utilization <50%
- Frequent crashes

---

## ✅ Success Criteria

Phase 2 is complete when:

- ✅ Training script ran for ~13-18 hours
- ✅ Final loss <1.5 (ideally <1.0)
- ✅ `adapters/discord-lora/adapter_model.bin` exists (~30-50 MB)
- ✅ No errors in `logs/training.log`
- ✅ All checkpoint saves successful

---

## 🎯 Next Steps

Once Phase 2 is complete:

### Immediate
- ✅ Verify adapter files exist
- ✅ Check training log for errors
- ✅ Note final loss value
- ✅ Backup adapter folder (optional)

### Quick Test
```powershell
# Test the trained model (creates Phase 3 test script)
python scripts/test_model.py
```

### When Ready for Phase 3
Say: **"Start Phase 3"**

Phase 3 will:
- Create bot deployment code
- Integrate trained adapter
- Setup memory systems (RAG + summarization)
- Deploy the Discord bot

---

## 💡 Pro Tips

**Tip 1: Use WandB for monitoring**
```powershell
# Install wandb
pip install wandb

# Login (one-time)
wandb login

# Train with wandb
python training\train_lora.py --wandb
```

**Tip 2: Training overnight**
```powershell
# Start before bed (10 PM)
# Check in morning (8-10 AM)
# Total: 10-12 hours = good overlap
```

**Tip 3: Keep checkpoints**
Don't delete checkpoint folders until training completes - you can resume from them!

**Tip 4: Monitor remotely**
- Use TeamViewer/AnyDesk to check progress from phone
- Or: SSH into your machine if on Linux

---

## 📞 Need Help?

If something goes wrong:

1. **Check logs:** `logs/training.log` has detailed errors
2. **Check GPU:** `nvidia-smi` shows VRAM/utilization
3. **Review troubleshooting:** Above section covers common issues
4. **Resume from checkpoint:** Training can always be resumed
5. **Ask me!** Describe what you're seeing

---

## 📚 Optional: WandB Monitoring

WandB (Weights & Biases) provides a web dashboard for training:

### Setup
```powershell
pip install wandb
wandb login
# Get key from: https://wandb.ai/authorize
```

### Enable in .env
```bash
WANDB_PROJECT=discord-chatbot
```

### View Dashboard
- Go to: https://wandb.ai
- See real-time graphs of loss, learning rate, etc.
- Compare different training runs

---

**Ready to train?** 

```powershell
# Make sure you're in venv
.\venv\Scripts\Activate.ps1

# Start training!
python training\train_lora.py
```

See you in 13-18 hours! ⏰ 

**Good luck!** 🚀
