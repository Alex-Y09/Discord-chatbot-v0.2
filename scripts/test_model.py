"""
Test Trained Model - Quick Inference Test
Loads your trained LoRA adapter and generates test responses
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("  TESTING YOUR TRAINED MODEL")
print("="*60)
print()

# Configuration
BASE_MODEL = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-v0.3")
ADAPTER_PATH = Path("adapters/discord-lora")

# Check if adapter exists
if not ADAPTER_PATH.exists():
    print("[X] Adapter not found!")
    print(f"Expected location: {ADAPTER_PATH}")
    print()
    print("Make sure Phase 2 training completed successfully.")
    exit(1)

print(f"[OK] Found adapter: {ADAPTER_PATH}")
print()

# Load model
print("[1/4] Loading base model with 4-bit quantization...")
print("This will take 2-3 minutes...")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

print("[OK] Base model loaded")
print()

# Load tokenizer
print("[2/4] Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token
print("[OK] Tokenizer loaded")
print()

# Load LoRA adapter
print("[3/4] Loading your trained adapter...")
model = PeftModel.from_pretrained(model, str(ADAPTER_PATH))
print("[OK] Adapter loaded!")
print()

# Check VRAM
if torch.cuda.is_available():
    allocated = torch.cuda.memory_allocated() / 1024**3
    print(f"VRAM usage: {allocated:.2f} GB")
print()

print("[4/4] Model ready! Starting test generation...")
print()
print("="*60)
print()

# Test prompts (simulating Discord conversations)
test_conversations = [
    {
        "context": "UserA: hey what's up\nUserB: not much, just chilling\nUserC: anyone wanna play games later?",
        "description": "Casual greeting"
    },
    {
        "context": "UserA: that movie was amazing\nUserB: which one?\nUserA: the new action one that just came out",
        "description": "Movie discussion"
    },
    {
        "context": "UserA: I'm so tired today\nUserB: same, didn't sleep well\nUserC: coffee time lol",
        "description": "Tired/sleepy topic"
    },
    {
        "context": "UserA: what game should we play\nUserB: idk maybe minecraft?\nUserC: or valorant",
        "description": "Gaming suggestion"
    }
]

# System prompt (same as training)
SYSTEM_PROMPT = "You are sususbot, a friendly Discord chatbot with a casual, playful personality. You chat naturally like a regular Discord user, using informal language, occasional slang, and emojis. You're helpful but keep things light and fun."

def generate_response(context, max_length=100):
    """Generate a response given conversation context"""
    
    # Format as chat
    prompt = f"### System:\n{SYSTEM_PROMPT}\n\n### User:\n{context}\n\n### Assistant:\n"
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=384)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    # Decode
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract just the assistant's response
    if "### Assistant:" in full_response:
        response = full_response.split("### Assistant:")[-1].strip()
        # Remove any trailing system/user prompts that might have been generated
        if "###" in response:
            response = response.split("###")[0].strip()
        return response
    else:
        return full_response.strip()

# Run tests
for i, test in enumerate(test_conversations, 1):
    print(f"Test {i}/4: {test['description']}")
    print("-" * 60)
    print("Conversation context:")
    for line in test['context'].split('\n'):
        print(f"  {line}")
    print()
    
    print("Generating response...")
    response = generate_response(test['context'])
    
    print("Bot response:")
    print(f"  sususbot: {response}")
    print()
    print("="*60)
    print()

# Final summary
print("="*60)
print("  TEST COMPLETE!")
print("="*60)
print()
print("Review the responses above. Your bot should:")
print("  ✅ Sound natural and conversational")
print("  ✅ Match the personality from your training data")
print("  ✅ Stay on-topic with the conversation")
print("  ✅ Use casual language/slang appropriately")
print()
print("If responses look good: Ready for Phase 3 (deployment)!")
print("If responses are weird: May need to adjust training or test with more prompts")
print()

# Optional: Interactive test
print("="*60)
print("INTERACTIVE TEST (Optional)")
print("="*60)
print()
print("Want to test with your own prompts? (y/n)")
choice = input("> ").strip().lower()

if choice == 'y':
    print()
    print("Enter conversation context (end with empty line):")
    print("Example format:")
    print("  UserA: hey")
    print("  UserB: what's up")
    print("  [press Enter on empty line]")
    print()
    
    while True:
        lines = []
        print("Context (empty line to generate):")
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        if not lines:
            break
        
        context = "\n".join(lines)
        print()
        print("Generating...")
        response = generate_response(context)
        print(f"sususbot: {response}")
        print()
        print("-"*60)
        print("Try another? (Enter context or empty line to quit)")
        print()

print()
print("Testing complete! Ready to proceed to Phase 3.")
