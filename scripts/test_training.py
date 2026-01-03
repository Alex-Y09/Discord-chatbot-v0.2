"""
Quick GPU Training Test
Tests if your system can train on GPU
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import sys

print("="*60)
print("  GPU TRAINING TEST")
print("="*60)

# Check CUDA
print(f"\n1. CUDA Available: {torch.cuda.is_available()}")
if not torch.cuda.is_available():
    print("❌ CUDA not available! Cannot train on GPU.")
    sys.exit(1)

print(f"   GPU: {torch.cuda.get_device_name(0)}")
print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

# Test small model loading with quantization
print("\n2. Testing 4-bit quantization loading...")
try:
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    
    # Use tiny model for testing
    print("   Loading tiny test model (TinyLlama)...")
    model = AutoModelForCausalLM.from_pretrained(
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    
    print("   ✅ Model loaded with 4-bit quantization")
    
    # Check which device model is on
    print(f"   Model device: {next(model.parameters()).device}")
    
    # Check VRAM
    allocated = torch.cuda.memory_allocated() / 1024**3
    print(f"   VRAM used: {allocated:.2f} GB")
    
    # Clean up
    del model
    torch.cuda.empty_cache()
    
except Exception as e:
    print(f"   ❌ Failed to load model: {e}")
    sys.exit(1)

# Test LoRA setup
print("\n3. Testing LoRA setup...")
try:
    model = AutoModelForCausalLM.from_pretrained(
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        quantization_config=bnb_config,
        device_map="auto",
    )
    
    model = prepare_model_for_kbit_training(model)
    
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    
    model = get_peft_model(model, lora_config)
    print("   ✅ LoRA adapters configured")
    
    # Check trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   Trainable: {trainable_params:,} / {total_params:,} ({trainable_params/total_params*100:.2f}%)")
    
    # Clean up
    del model
    torch.cuda.empty_cache()
    
except Exception as e:
    print(f"   ❌ LoRA setup failed: {e}")
    sys.exit(1)

# Test training step
print("\n4. Testing training step...")
try:
    model = AutoModelForCausalLM.from_pretrained(
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        quantization_config=bnb_config,
        device_map="auto",
    )
    
    tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, lora_config)
    
    # Test forward pass
    inputs = tokenizer("Test input", return_tensors="pt").to(model.device)
    outputs = model(**inputs, labels=inputs["input_ids"])
    loss = outputs.loss
    
    print(f"   ✅ Forward pass works (loss: {loss.item():.4f})")
    
    # Test backward pass
    loss.backward()
    print("   ✅ Backward pass works")
    
    # Clean up
    del model, tokenizer
    torch.cuda.empty_cache()
    
except Exception as e:
    print(f"   ❌ Training step failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("  ✅ ALL TESTS PASSED!")
print("="*60)
print("\nYour system is ready for GPU training!")
print("The training script should work correctly.")
print("\nIf the training script still shows errors, please share")
print("the exact error message so I can help debug.")
print("="*60)
