"""
LoRA Fine-Tuning Script for Mistral-7B
Optimized for RTX 2080 Ti (11GB VRAM) - 13-18 hour training time

Features:
- 4-bit quantization (reduces VRAM from 14GB to 5GB)
- LoRA adapters (efficient fine-tuning)
- Gradient accumulation (32 steps = 2x speedup)
- Mixed precision FP16 (1.3x speedup)
- Gradient checkpointing (saves VRAM)
- Automatic checkpointing and resume
- WandB integration (optional)
"""

import os
import sys
import json
import torch
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import logging
from datetime import datetime
from dotenv import load_dotenv

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType,
)
from datasets import load_dataset

# Load environment variables
load_dotenv()

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Training configuration"""
    
    # Model
    model_name: str = field(default=os.getenv("MODEL_NAME", "mistralai/Mistral-7B-v0.3"))
    
    # Data
    training_data_path: str = field(default=os.getenv("TRAINING_DATA_PATH", "./data/training_data.jsonl"))
    
    # Training hyperparameters (OPTIMIZED for 13-18 hours!)
    learning_rate: float = field(default=float(os.getenv("LEARNING_RATE", "2.5e-4")))
    num_train_epochs: int = field(default=int(os.getenv("EPOCHS", "1")))
    per_device_train_batch_size: int = field(default=int(os.getenv("BATCH_SIZE", "1")))
    gradient_accumulation_steps: int = field(default=int(os.getenv("GRADIENT_ACCUMULATION_STEPS", "32")))
    
    # Optimization flags
    fp16: bool = field(default=os.getenv("USE_FP16", "true").lower() == "true")
    gradient_checkpointing: bool = field(default=os.getenv("GRADIENT_CHECKPOINTING", "true").lower() == "true")
    
    # 4-bit quantization (CRITICAL for 11GB VRAM)
    load_in_4bit: bool = field(default=os.getenv("LOAD_IN_4BIT", "true").lower() == "true")
    bnb_4bit_compute_dtype: str = field(default="float16")
    bnb_4bit_quant_type: str = field(default="nf4")
    bnb_4bit_use_double_quant: bool = field(default=True)
    
    # LoRA configuration
    lora_r: int = field(default=16)
    lora_alpha: int = field(default=32)
    lora_dropout: float = field(default=0.05)
    lora_target_modules: list = field(default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj"])
    
    # Training settings
    max_seq_length: int = field(default=int(os.getenv("CONTEXT_TOKENS", "384")))
    warmup_steps: int = field(default=100)
    logging_steps: int = field(default=10)
    save_steps: int = field(default=500)
    save_total_limit: int = field(default=3)
    
    # Output
    output_dir: str = field(default="./adapters/discord-lora")
    
    # Optional
    wandb_project: Optional[str] = field(default=os.getenv("WANDB_PROJECT", None))
    resume_from_checkpoint: Optional[str] = field(default=None)


class DiscordTrainer:
    """Trainer for Discord chatbot fine-tuning"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.dataset = None
        
        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info("="*60)
        logger.info("Discord Chatbot Training - Phase 2")
        logger.info("="*60)
        logger.info(f"Model: {config.model_name}")
        logger.info(f"Training data: {config.training_data_path}")
        logger.info(f"Output: {config.output_dir}")
        logger.info(f"Epochs: {config.num_train_epochs}")
        logger.info(f"Learning rate: {config.learning_rate}")
        logger.info(f"Gradient accumulation: {config.gradient_accumulation_steps}")
        logger.info(f"Mixed precision (FP16): {config.fp16}")
        logger.info(f"4-bit quantization: {config.load_in_4bit}")
        logger.info("="*60)
    
    def load_tokenizer(self):
        """Load tokenizer"""
        logger.info("Loading tokenizer...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True,
            padding_side="right"
        )
        
        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        logger.info(f"✅ Tokenizer loaded: {len(self.tokenizer)} tokens")
    
    def load_model(self):
        """Load model with 4-bit quantization"""
        logger.info("Loading model with 4-bit quantization...")
        logger.info("This will take 5-10 minutes (downloading ~7GB)...")
        
        # Configure quantization
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=self.config.load_in_4bit,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type=self.config.bnb_4bit_quant_type,
            bnb_4bit_use_double_quant=self.config.bnb_4bit_use_double_quant,
        )
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        
        # Prepare for k-bit training
        self.model = prepare_model_for_kbit_training(
            self.model,
            use_gradient_checkpointing=self.config.gradient_checkpointing
        )
        
        logger.info("✅ Model loaded")
        
        # Log VRAM usage
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            logger.info(f"VRAM allocated: {allocated:.2f} GB")
            logger.info(f"VRAM reserved: {reserved:.2f} GB")
    
    def setup_lora(self):
        """Configure and apply LoRA"""
        logger.info("Configuring LoRA adapters...")
        
        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )
        
        self.model = get_peft_model(self.model, lora_config)
        
        # Print trainable parameters
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_percent = 100 * trainable_params / total_params
        
        logger.info(f"✅ LoRA configured")
        logger.info(f"Trainable parameters: {trainable_params:,} ({trainable_percent:.2f}%)")
        logger.info(f"Total parameters: {total_params:,}")
    
    def load_dataset(self):
        """Load and prepare training dataset"""
        logger.info(f"Loading dataset from {self.config.training_data_path}...")
        
        # Check if file exists
        if not Path(self.config.training_data_path).exists():
            logger.error(f"Training data not found: {self.config.training_data_path}")
            logger.error("Run Phase 1 first: python scripts/prepare_training_data.py")
            raise FileNotFoundError(f"Training data not found: {self.config.training_data_path}")
        
        # Load dataset
        self.dataset = load_dataset('json', data_files=self.config.training_data_path, split='train')
        
        logger.info(f"✅ Dataset loaded: {len(self.dataset)} examples")
        
        # Preprocess dataset
        logger.info("Preprocessing dataset...")
        self.dataset = self.dataset.map(
            self._preprocess_function,
            batched=True,
            remove_columns=self.dataset.column_names,
            desc="Tokenizing"
        )
        
        logger.info("✅ Dataset preprocessed")
    
    def _preprocess_function(self, examples):
        """Preprocess training examples"""
        # Format messages into training text
        texts = []
        for messages in examples['messages']:
            # Convert messages to Mistral format
            text = self._format_mistral_prompt(messages)
            texts.append(text)
        
        # Tokenize
        tokenized = self.tokenizer(
            texts,
            truncation=True,
            max_length=self.config.max_seq_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        # Labels are the same as input_ids for causal LM
        tokenized["labels"] = tokenized["input_ids"].clone()
        
        return tokenized
    
    def _format_mistral_prompt(self, messages):
        """Format messages into Mistral prompt format"""
        formatted = ""
        
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                formatted += f"[INST] {content} [/INST]\n"
            elif role == 'user':
                formatted += f"[INST] {content} [/INST]\n"
            elif role == 'assistant':
                formatted += f"{content}\n"
        
        return formatted
    
    def train(self):
        """Run training"""
        logger.info("Starting training...")
        logger.info("="*60)
        
        # Calculate training time estimate
        total_steps = len(self.dataset) // (
            self.config.per_device_train_batch_size * 
            self.config.gradient_accumulation_steps
        ) * self.config.num_train_epochs
        
        logger.info(f"Total training steps: {total_steps}")
        logger.info(f"Estimated time: 13-18 hours")
        logger.info(f"Checkpoints saved every {self.config.save_steps} steps")
        logger.info("="*60)
        
        # Configure training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            fp16=self.config.fp16,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            save_total_limit=self.config.save_total_limit,
            warmup_steps=self.config.warmup_steps,
            gradient_checkpointing=self.config.gradient_checkpointing,
            optim="paged_adamw_8bit",  # Memory efficient optimizer
            lr_scheduler_type="cosine",
            report_to="wandb" if self.config.wandb_project else "none",
            run_name=f"discord-bot-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.dataset,
            data_collator=data_collator,
        )
        
        # Resume from checkpoint if specified
        checkpoint = None
        if self.config.resume_from_checkpoint:
            checkpoint = self.config.resume_from_checkpoint
            logger.info(f"Resuming from checkpoint: {checkpoint}")
        
        # Train!
        logger.info("🚀 Training started!")
        logger.info("You can safely close this window - training will continue")
        logger.info("Monitor progress: tail -f logs/training.log")
        logger.info("")
        
        try:
            trainer.train(resume_from_checkpoint=checkpoint)
            
            logger.info("="*60)
            logger.info("✅ Training complete!")
            logger.info("="*60)
            
            # Save final model
            logger.info("Saving final model...")
            trainer.save_model()
            self.tokenizer.save_pretrained(self.config.output_dir)
            
            logger.info(f"✅ Model saved to: {self.config.output_dir}")
            logger.info("")
            logger.info("Next steps:")
            logger.info("  1. Test the trained model")
            logger.info("  2. Deploy the bot: python src/bot.py")
            logger.info("="*60)
            
        except KeyboardInterrupt:
            logger.info("\nTraining interrupted by user")
            logger.info(f"Progress saved to: {self.config.output_dir}")
            logger.info("Resume with: --resume_from_checkpoint")
        
        except Exception as e:
            logger.error(f"Training failed: {e}", exc_info=True)
            raise


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Train Discord chatbot with LoRA")
    parser.add_argument("--resume", type=str, default=None, help="Resume from checkpoint")
    parser.add_argument("--wandb", action="store_true", help="Enable WandB logging")
    args = parser.parse_args()
    
    # Load config
    config = TrainingConfig()
    
    if args.resume:
        config.resume_from_checkpoint = args.resume
    
    if args.wandb:
        import wandb
        wandb.init(project=config.wandb_project or "discord-chatbot")
    
    # Create trainer
    trainer = DiscordTrainer(config)
    
    # Pipeline
    try:
        trainer.load_tokenizer()
        trainer.load_model()
        trainer.setup_lora()
        trainer.load_dataset()
        trainer.train()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
