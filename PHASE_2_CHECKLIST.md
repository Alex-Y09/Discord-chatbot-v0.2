# ✅ Phase 2 Checklist - LLM Training

**Track your progress through Phase 2!**

---

## 📋 Pre-Training Setup (10 minutes)

- [ ] Virtual environment activated
- [ ] Phase 1 complete (`data/training_data.jsonl` exists)
- [ ] GPU available (CUDA enabled)
- [ ] VRAM checked (11GB+ available)
- [ ] Disk space checked (15GB+ free)
- [ ] Training dependencies installed (`peft`, `bitsandbytes`, `accelerate`)
- [ ] `.env` Phase 2 settings reviewed

**Checkpoint:** Can you run `nvidia-smi` and see your GPU?

---

## 🔧 Configuration Verification (5 minutes)

- [ ] `.env` file has Phase 2 settings
- [ ] `EPOCHS=1` (DO NOT change for 63k messages)
- [ ] `GRADIENT_ACCUMULATION_STEPS=32` (for speed)
- [ ] `USE_FP16=true` (for speed)
- [ ] `LOAD_IN_4BIT=true` (for 11GB VRAM)
- [ ] `LEARNING_RATE=2.5e-4` (optimized)

**Checkpoint:** Review `.env` - all Phase 2 settings look correct?

---

## 📥 Model Download (5-10 minutes, one-time)

- [ ] HuggingFace cache directory has space
- [ ] Internet connection stable
- [ ] Model download started (automatic on first run)
- [ ] Model download completed (~7GB)
- [ ] Model cached in `~/.cache/huggingface/`

**Checkpoint:** Model download = 7GB, should take 5-10 mins on good internet.

---

## 🚀 Training Start (1 minute)

- [ ] Training script started: `python training\train_lora.py`
- [ ] Initial output shows configuration
- [ ] Tokenizer loaded successfully
- [ ] Model loaded with 4-bit quantization
- [ ] LoRA configured (trainable params shown)
- [ ] Dataset loaded (31k+ examples)
- [ ] Training started (step 0/980)

**Checkpoint:** Do you see "Step 10/980 | Loss: X.XXX"?

---

## ⏰ During Training (13-18 hours)

- [ ] Training running without errors
- [ ] Progress updates every 10 steps
- [ ] Loss is decreasing over time
- [ ] GPU utilization 90-100% (`nvidia-smi`)
- [ ] VRAM usage 8-9GB / 11GB
- [ ] Temperature 70-80°C (normal)
- [ ] First checkpoint saved (step 500)
- [ ] Logs being written to `logs/training.log`

**Checkpoint:** Is GPU showing 90-100% utilization?

---

## 📊 Monitoring (periodic checks)

- [ ] Check progress every few hours
- [ ] Loss trending downward
- [ ] No NaN or Inf values in loss
- [ ] No OOM (Out of Memory) errors
- [ ] Checkpoints saving successfully
- [ ] Log file growing (no freeze)
- [ ] Estimated completion time reasonable

**Checkpoint:** Loss at step 500 should be lower than step 10.

---

## ✅ Training Completion

- [ ] Training reached final step (~980/980)
- [ ] Final loss <1.5 (ideally <1.0)
- [ ] "Training complete!" message shown
- [ ] Final model being saved
- [ ] No errors during save
- [ ] Adapter files created in `adapters/discord-lora/`

**Checkpoint:** Did you see "✅ Training complete!" message?

---

## 📁 Verify Output Files

- [ ] `adapters/discord-lora/` directory exists
- [ ] `adapter_config.json` present (~1 KB)
- [ ] `adapter_model.bin` or `.safetensors` present (~30-50 MB)
- [ ] Tokenizer files present (4-5 files)
- [ ] `training_args.bin` present
- [ ] Checkpoint folders can be deleted (optional cleanup)

**Checkpoint:** Does `adapter_model.bin` exist and is ~30-50 MB?

---

## 🧪 Quick Verification

- [ ] Check final loss value:
  ```powershell
  Get-Content logs\training.log | Select-String "Loss:" | Select-Object -Last 5
  ```

- [ ] Check adapter size:
  ```powershell
  Get-ChildItem adapters\discord-lora\adapter_model.* | Select-Object Name, Length
  ```

- [ ] Check training time:
  ```powershell
  Get-Content logs\training.log | Select-String "Training started", "Training complete"
  ```

- [ ] View VRAM usage during training:
  ```powershell
  Get-Content logs\training.log | Select-String "VRAM"
  ```

**Checkpoint:** All verification commands return expected results?

---

## 🎉 Phase 2 Complete!

- [ ] Training completed successfully
- [ ] All output files verified
- [ ] Training metrics look good
- [ ] Adapter ready for deployment

**When ready, say: "Start Phase 3"**

---

## 🐛 Troubleshooting Checklist

If training fails, check:

### OOM (Out of Memory)
- [ ] Reduce `GRADIENT_ACCUMULATION_STEPS` to 16
- [ ] Close other GPU applications
- [ ] Reduce `CONTEXT_TOKENS` to 256
- [ ] Check VRAM with `nvidia-smi`

### Slow Training
- [ ] GPU utilization is 90-100%
- [ ] Using CUDA not CPU
- [ ] No background GPU tasks
- [ ] Drivers up to date

### Loss Not Decreasing
- [ ] Check after 100+ steps
- [ ] Try reducing learning rate to 1e-4
- [ ] Verify dataset format is correct

### Training Crashed
- [ ] Check `logs/training.log` for errors
- [ ] Resume from latest checkpoint
- [ ] Verify disk space available
- [ ] Check GPU temperature <85°C

### Model Download Failed
- [ ] Check internet connection
- [ ] Check HuggingFace status
- [ ] Try manual download
- [ ] Check disk space in cache dir

---

## 💾 Backup (Optional but Recommended)

After training completes:

- [ ] Copy `adapters/discord-lora/` to backup location
- [ ] Save `logs/training.log` for reference
- [ ] Note final loss value: _______
- [ ] Note training time: _______ hours

---

## 📊 Expected Results

After Phase 2, you should have:

```
adapters/discord-lora/
├── adapter_config.json       ✅ (~1 KB)
├── adapter_model.bin         ✅ (~30-50 MB)
├── tokenizer_config.json     ✅
├── tokenizer.json            ✅
├── special_tokens_map.json   ✅
└── training_args.bin         ✅

logs/
└── training.log              ✅ (detailed training log)
```

**Training Time:** 13-18 hours  
**Final Loss:** <1.5 (ideally <1.0)  
**Adapter Size:** 30-50 MB  

---

## 📈 Training Metrics to Record

| Metric | Value |
|--------|-------|
| Start Time | __________ |
| End Time | __________ |
| Total Time | __________ hours |
| Initial Loss | __________ |
| Final Loss | __________ |
| Total Steps | __________ |
| GPU Model | __________ |
| Max VRAM Used | __________ GB |
| Avg GPU Util | _________% |

---

## 🎯 Next Steps

- [ ] Phase 2 complete and verified
- [ ] Ready to proceed to Phase 3
- [ ] Backup created (optional)

**Next:** [PHASE_3_START_GUIDE.md](PHASE_3_START_GUIDE.md) ← (Will be created in Phase 3)

---

**Training Time:** 13-18 hours  
**Hands-On Time:** ~15 minutes  
**Rest:** Automated! ☕

Good luck! 🚀
