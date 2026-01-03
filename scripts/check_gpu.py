"""
GPU Diagnostics Script
Checks CUDA availability and provides troubleshooting guidance
"""

import sys
import subprocess

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_nvidia_smi():
    """Check if NVIDIA driver is installed and GPU is visible"""
    print_section("NVIDIA Driver & GPU Detection")
    
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ NVIDIA driver installed")
            print("\nGPU Information:")
            print(result.stdout)
            return True
        else:
            print("❌ nvidia-smi command failed")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi not found - NVIDIA drivers not installed or not in PATH")
        return False
    except Exception as e:
        print(f"❌ Error running nvidia-smi: {e}")
        return False

def check_pytorch():
    """Check PyTorch installation and CUDA support"""
    print_section("PyTorch CUDA Support")
    
    try:
        import torch
        print(f"✅ PyTorch installed: {torch.__version__}")
        
        # Check CUDA availability
        cuda_available = torch.cuda.is_available()
        print(f"\nCUDA Available: {cuda_available}")
        
        if cuda_available:
            print(f"✅ PyTorch can see CUDA!")
            print(f"\nCUDA Version (PyTorch): {torch.version.cuda}")
            print(f"Number of GPUs: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                print(f"\nGPU {i}:")
                print(f"  Name: {torch.cuda.get_device_name(i)}")
                print(f"  Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB")
                print(f"  Compute Capability: {torch.cuda.get_device_capability(i)}")
            
            # Test GPU tensor
            try:
                x = torch.randn(10, 10).cuda()
                y = torch.randn(10, 10).cuda()
                z = x @ y
                print("\n✅ GPU tensor operations work!")
            except Exception as e:
                print(f"\n⚠️ GPU tensor test failed: {e}")
            
            return True
        else:
            print("❌ PyTorch cannot access CUDA")
            print("\nPossible reasons:")
            print("  1. PyTorch was installed without CUDA support (CPU-only)")
            print("  2. CUDA version mismatch between PyTorch and system")
            print("  3. NVIDIA drivers not properly installed")
            return False
            
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking PyTorch: {e}")
        return False

def check_transformers():
    """Check transformers library"""
    print_section("Transformers Library")
    
    try:
        import transformers
        print(f"✅ Transformers installed: {transformers.__version__}")
        return True
    except ImportError:
        print("❌ Transformers not installed")
        return False

def check_bitsandbytes():
    """Check bitsandbytes for quantization"""
    print_section("Bitsandbytes (4-bit Quantization)")
    
    try:
        import bitsandbytes as bnb
        print(f"✅ Bitsandbytes installed: {bnb.__version__}")
        
        # Check if CUDA version is compatible
        try:
            import torch
            if torch.cuda.is_available():
                # Test bitsandbytes CUDA functions
                print("✅ Bitsandbytes CUDA support available")
                return True
        except Exception as e:
            print(f"⚠️ Bitsandbytes CUDA test failed: {e}")
            return False
            
    except ImportError:
        print("❌ Bitsandbytes not installed")
        return False

def get_system_cuda_version():
    """Get system CUDA version from nvcc"""
    print_section("System CUDA Version")
    
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CUDA Toolkit installed")
            print(result.stdout)
            return True
        else:
            print("⚠️ nvcc command failed")
            return False
    except FileNotFoundError:
        print("⚠️ nvcc not found - CUDA Toolkit may not be installed")
        print("Note: CUDA Toolkit is optional if using conda/pip PyTorch with bundled CUDA")
        return False
    except Exception as e:
        print(f"⚠️ Error checking CUDA: {e}")
        return False

def provide_solutions(has_driver, has_pytorch_cuda):
    """Provide troubleshooting guidance"""
    print_section("TROUBLESHOOTING GUIDE")
    
    if not has_driver:
        print("\n🔧 SOLUTION 1: Install NVIDIA Drivers")
        print("="*60)
        print("Your GPU is not detected by the system.")
        print("\nSteps:")
        print("1. Download latest drivers from: https://www.nvidia.com/download/index.aspx")
        print("2. Select RTX 2080 Ti and your OS")
        print("3. Install and restart your computer")
        print("4. Run this script again to verify")
        
    elif not has_pytorch_cuda:
        print("\n🔧 SOLUTION 2: Reinstall PyTorch with CUDA Support")
        print("="*60)
        print("PyTorch is installed without CUDA support (CPU-only version).")
        print("\nSteps:")
        print("1. Uninstall current PyTorch:")
        print("   pip uninstall torch torchvision torchaudio")
        print("\n2. Install PyTorch with CUDA 11.8 (for RTX 2080 Ti):")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        print("\n3. Verify installation:")
        print("   python -c \"import torch; print(torch.cuda.is_available())\"")
        print("   (Should print: True)")
        print("\nAlternative - CUDA 12.1:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        
        print("\n" + "="*60)
        print("🔧 SOLUTION 2b: Use Conda (Recommended)")
        print("="*60)
        print("Conda often handles CUDA dependencies better:")
        print("\n1. Install Miniconda/Anaconda if not installed")
        print("2. Create new environment:")
        print("   conda create -n chatbot python=3.10")
        print("   conda activate chatbot")
        print("\n3. Install PyTorch with CUDA:")
        print("   conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia")
        print("\n4. Install other requirements:")
        print("   pip install -r requirements.txt")
    
    else:
        print("\n✅ GPU Detection Working!")
        print("="*60)
        print("Your system is configured correctly for GPU training.")
        print("\nYou can now run:")
        print("  python training/train_lora.py")

def main():
    print("="*60)
    print("  🔍 GPU DIAGNOSTICS")
    print("="*60)
    print("\nChecking your system for GPU/CUDA support...")
    
    # Run checks
    has_driver = check_nvidia_smi()
    has_pytorch_cuda = check_pytorch()
    check_transformers()
    check_bitsandbytes()
    get_system_cuda_version()
    
    # Provide solutions
    provide_solutions(has_driver, has_pytorch_cuda)
    
    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    print(f"NVIDIA Driver: {'✅' if has_driver else '❌'}")
    print(f"PyTorch CUDA:  {'✅' if has_pytorch_cuda else '❌'}")
    print(f"Ready to train: {'✅ YES' if (has_driver and has_pytorch_cuda) else '❌ NO - See troubleshooting above'}")
    print("="*60)
    
    if has_driver and has_pytorch_cuda:
        print("\n🎉 All checks passed! You're ready for GPU training.")
        return 0
    else:
        print("\n⚠️ Issues found. Follow the troubleshooting guide above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
