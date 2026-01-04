"""
Inference Engine - Loads trained model and generates responses
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class InferenceEngine:
    """Handles model loading and response generation"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Paths
        self.base_model_name = "mistralai/Mistral-7B-v0.3"
        self.adapter_path = Path("adapters/discord-lora")
        
        logger.info(f"Inference engine initialized (device: {self.device})")
    
    def load_model(self):
        """Load base model and trained adapter"""
        
        if self.model is not None:
            logger.info("Model already loaded")
            return
        
        logger.info("Loading model components...")
        
        try:
            # Configure 4-bit quantization
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            )
            
            # Load base model with quantization
            logger.info(f"Loading base model: {self.base_model_name}")
            logger.info("This will take 2-3 minutes...")
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True
            )
            
            logger.info("Base model loaded!")
            
            # Load trained adapter
            logger.info(f"Loading trained adapter: {self.adapter_path}")
            self.model = PeftModel.from_pretrained(
                self.model,
                str(self.adapter_path),
                is_trainable=False
            )
            
            logger.info("Adapter loaded!")
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.adapter_path)
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Set to eval mode
            self.model.eval()
            
            logger.info("Model ready for inference!")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            raise
    
    def generate_response(
        self,
        context: str,
        long_term_context: str = "",
        max_length: int = 150,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        repetition_penalty: float = 1.1
    ) -> str:
        """
        Generate a response given conversation context
        
        Args:
            context: Recent conversation history
            long_term_context: Optional long-term memory context
            max_length: Maximum tokens to generate
            temperature: Sampling temperature (0.7 = balanced)
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling limit
            repetition_penalty: Penalty for repeated tokens
        
        Returns:
            Generated response text
        """
        
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded! Call load_model() first")
        
        try:
            # Build prompt in Mistral instruction format
            system_prompt = "You are a casual, playful Discord user chatting with friends."
            
            # Add long-term context if available
            if long_term_context:
                system_prompt += f"\n\nRelevant past conversations:\n{long_term_context}"
            
            # Format prompt
            prompt = f"<s>[INST] {system_prompt}\n\n{context} [/INST]"
            
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=384  # Match training context length
            ).to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repetition_penalty=repetition_penalty,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the response (remove prompt)
            # The response starts after [/INST]
            if "[/INST]" in full_response:
                response = full_response.split("[/INST]")[-1].strip()
            else:
                response = full_response.strip()
            
            # Clean up
            response = response.strip()
            
            # Remove any remaining special tokens
            response = response.replace("<s>", "").replace("</s>", "").strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            raise
    
    def unload_model(self):
        """Unload model from memory"""
        if self.model is not None:
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("Model unloaded from memory")
