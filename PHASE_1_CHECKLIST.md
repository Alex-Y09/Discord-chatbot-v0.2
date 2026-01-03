# ✅ Phase 1 Checklist - Data Collection & Preparation

**Track your progress through Phase 1!**

---

## 📋 Setup (5-10 minutes)

- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Virtual environment activated (`.\venv\Scripts\Activate.ps1`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created from template
- [ ] Discord bot token added to `.env`
- [ ] Server ID (Guild ID) added to `.env`
- [ ] Channel ID added to `.env`

**Checkpoint:** Can you see your bot online in Discord?

---

## 📥 Data Collection (30-90 minutes automated)

- [ ] `backfill_messages.py` script started
- [ ] Collection running without errors
- [ ] Progress updates appearing (every 100 messages)
- [ ] Checkpoints saving (every 1000 messages)
- [ ] Collection completed successfully
- [ ] `data/raw_messages.jsonl` file exists
- [ ] Message count matches expected (~63,000-65,000)

**Checkpoint:** Do you have a `raw_messages.jsonl` file that's ~400MB?

---

## 📊 Data Analysis (5 minutes)

- [ ] `analyze_training_data.py` script run
- [ ] Statistics displayed (total messages, authors, etc.)
- [ ] Bot detected correctly
- [ ] Message distribution looks reasonable
- [ ] Analysis report saved (`data/analysis_report.txt`)

**Checkpoint:** Does the bot username look correct? Is message count ~63k?

---

## 🔧 Data Preparation (10 minutes)

- [ ] `prepare_training_data.py` script started
- [ ] Filtering completed (commands, emoji-only, etc. removed)
- [ ] Training format conversion completed
- [ ] Validation passed (no errors)
- [ ] `data/training_data.jsonl` created
- [ ] Training examples count looks correct (~31,000)
- [ ] Sample examples reviewed and look good

**Checkpoint:** Do you have a `training_data.jsonl` file that's ~250MB?

---

## ✅ Verification (5 minutes)

- [ ] Check file sizes:
  ```powershell
  Get-ChildItem data\*.jsonl | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}
  ```
  Expected:
  - `raw_messages.jsonl`: ~400 MB
  - `training_data.jsonl`: ~250 MB

- [ ] View sample training example:
  ```powershell
  Get-Content data\training_data.jsonl -First 1 | ConvertFrom-Json | ConvertTo-Json -Depth 10
  ```

- [ ] Verify training example structure:
  - Has `messages` array with 3 items
  - Roles: system, user, assistant
  - Content is not empty
  - Context looks like real conversation

---

## 🎉 Phase 1 Complete!

- [ ] All files created successfully
- [ ] Data quality looks good
- [ ] Ready to proceed to Phase 2

**When ready, say: "Start Phase 2"**

---

## 🐛 Troubleshooting

### If collection fails:

1. **Check bot permissions:**
   - Discord Developer Portal → Bot → Privileged Gateway Intents
   - Enable: MESSAGE CONTENT INTENT ✅

2. **Check credentials in .env:**
   ```powershell
   Get-Content .env | Select-String "DISCORD"
   ```

3. **View logs:**
   ```powershell
   Get-Content logs\backfill.log -Tail 50
   ```

4. **Resume from checkpoint:**
   ```powershell
   python scripts/backfill_messages.py
   # Will automatically resume if checkpoint exists
   ```

### If analysis fails:

1. **Check if raw_messages.jsonl exists:**
   ```powershell
   Test-Path data\raw_messages.jsonl
   ```

2. **Check file is not empty:**
   ```powershell
   Get-Content data\raw_messages.jsonl -First 5
   ```

### If preparation fails:

1. **Check logs:**
   ```powershell
   Get-Content logs\prep.log -Tail 50
   ```

2. **Verify raw messages format:**
   ```powershell
   Get-Content data\raw_messages.jsonl -First 1 | ConvertFrom-Json
   ```

---

## 📊 Expected Results

After Phase 1, you should have:

```
data/
├── raw_messages.jsonl          (~400 MB, 63-65k messages)
├── training_data.jsonl         (~250 MB, 31k examples)
├── backfill_checkpoint.json    (can delete after completion)
└── analysis_report.txt         (statistics)

logs/
├── backfill.log                (collection logs)
└── prep.log                    (preparation logs)
```

**Training Time Estimate:** 13-18 hours (Phase 2)

---

## 💡 Tips

**Tip 1:** Run collection overnight if it's slow
**Tip 2:** Keep checkpoint file until collection complete
**Tip 3:** Don't delete raw_messages.jsonl (backup data)
**Tip 4:** Review sample examples to ensure quality

---

**Next:** [PHASE_2_START_GUIDE.md](PHASE_2_START_GUIDE.md) ← (Will be created in Phase 2)
