import os
import subprocess
import argparse
import shutil
import whisper
import torch

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds * 1000) % 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def generate_srt(video_path, srt_path, model_size="medium"):
    print(f"🎙️ 开始生成字幕 (Model: {model_size})...")
    
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = whisper.load_model(model_size, device=device)
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return False
        
    prompt = "简体中文。按摩，SPA，推油，技师，放松，身心。"
    result = model.transcribe(video_path, language="zh", initial_prompt=prompt, fp16=False)
    
    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result["segments"]):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"{i+1}\n{start} --> {end}\n{text}\n\n")
            
    print(f"✅ SRT 生成完成: {srt_path}")
    return True

def burn_subtitle(video_path, srt_path, output_path):
    print("🔥 正在烧录字幕...")
    
    temp_srt = "temp_sub_burn.srt"
    shutil.copy2(srt_path, temp_srt)
    
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-vf', f"subtitles={temp_srt}",
        '-c:a', 'copy',
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ 字幕烧录完成: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 烧录失败: {e}")
    finally:
        if os.path.exists(temp_srt):
            os.remove(temp_srt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="输入视频")
    parser.add_argument("output", help="输出视频")
    parser.add_argument("--srt", help="指定 SRT 输出路径", default="subtitle.srt")
    parser.add_argument("--skip-transcribe", action="store_true", help="跳过转录")
    args = parser.parse_args()
    
    if not args.skip_transcribe:
        if not generate_srt(args.video, args.srt):
            sys.exit(1)
            
    burn_subtitle(args.video, args.srt, args.output)
