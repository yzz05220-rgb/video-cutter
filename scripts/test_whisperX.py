#!/usr/bin/env python3
"""
WhisperX 快速测试
验证 WhisperX 是否正常工作
"""

import sys

# 设置编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("WhisperX Installation Test")
print("=" * 60)

# 1. 测试导入
print("\n[1/4] Testing import...")
try:
    import whisperx
    print("OK whisperx imported successfully")
except ImportError as e:
    print(f"FAIL {e}")
    sys.exit(1)

# 2. 检查依赖
print("\n[2/4] Checking dependencies...")
dependencies = {
    'ctranslate2': 'faster-whisper backend',
    'torch': 'PyTorch',
    'torchaudio': 'PyTorch audio',
    'transformers': 'HuggingFace transformers',
    'pyannote.audio': 'Speaker diarization'
}

for module, desc in dependencies.items():
    try:
        __import__(module)
        print(f"OK {module:20s} ({desc})")
    except ImportError:
        print(f"WARN {module:20s} (missing)")

# 3. 检查 GPU
print("\n[3/4] Checking GPU availability...")
try:
    import torch
    if torch.cuda.is_available():
        print(f"OK CUDA available")
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        print("INFO CUDA not available, using CPU")
except Exception as e:
    print(f"WARN Could not check GPU: {e}")

# 4. 列出可用模型
print("\n[4/4] WhisperX models:")
models = [
    ("tiny", "~39MB", "Fastest", "Quick tests"),
    ("base", "~74MB", "Fast", "Daily use"),
    ("small", "~244MB", "Medium", "Balanced"),
    ("medium", "~769MB", "Slow", "Recommended"),
    ("large-v2", "~1.5GB", "Slower", "High accuracy"),
    ("large-v3", "~1.5GB", "Slowest", "Best accuracy"),
]

print(f"{'Model':15} {'Size':>10} {'Speed':>10} {'Use Case'}")
print("-" * 60)
for model, size, speed, use_case in models:
    print(f"{model:15} {size:>10} {speed:>10} {use_case}")

print("\n" + "=" * 60)
print("Installation complete!")
print("=" * 60)
print("\nQuick start:")
print("  python transcriber_whisperX.py video.mp4 output.json")
print("\nOr use with all_in_one.py:")
print("  python all_in_one.py video.mp4")
