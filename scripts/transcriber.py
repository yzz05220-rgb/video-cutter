import os
import sys
import subprocess
import json
import shutil
from funasr import AutoModel

# 设置控制台编码为UTF-8（仅在直接运行时）
if sys.platform == 'win32' and __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_duration(file_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"❌ 获取时长失败: {e}")
        return 0

def transcribe_video(video_path, output_json, temp_dir):
    print(f"🎬 开始转录: {os.path.basename(video_path)}")
    
    # 1. 加载模型
    print("⏳ 加载 FunASR 模型...")
    try:
        model = AutoModel(
            model="paraformer-zh",
            vad_model="fsmn-vad",
            punc_model="ct-punc",
            disable_update=True
        )
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return False

    # 2. 分段转录
    duration = get_duration(video_path)
    SEGMENT_LEN = 30
    all_chars = []
    
    num_segments = int(duration // SEGMENT_LEN) + 1
    
    for i in range(num_segments):
        start = i * SEGMENT_LEN
        dur = min(SEGMENT_LEN, duration - start)
        if dur <= 0: continue
        
        wav_path = os.path.join(temp_dir, f"seg_{i}.wav")
        
        cmd = [
            'ffmpeg', '-y', '-i', video_path, 
            '-ss', str(start), '-t', str(dur),
            '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', 
            wav_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        
        # 转录
        res = model.generate(input=wav_path, return_raw_text=True, timestamp_granularity="character")
        
        if res:
             for item in res:
                if 'timestamp' in item and 'text' in item:
                    text = item['text'].replace(' ', '')
                    timestamps = item['timestamp']
                    valid_len = min(len(text), len(timestamps))
                    for k in range(valid_len):
                        all_chars.append({
                            'char': text[k],
                            'start': round(start * 1000 + timestamps[k][0]),
                            'end': round(start * 1000 + timestamps[k][1])
                        })
        
        if os.path.exists(wav_path):
            os.remove(wav_path)
    
    # 保存结果
    result_data = {
        "video_path": video_path,
        "duration_ms": duration * 1000,
        "segments": all_chars
    }
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 转录完成，已保存至: {output_json}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python transcriber.py <input_video> <output_json> <temp_dir>")
        sys.exit(1)
    transcribe_video(sys.argv[1], sys.argv[2], sys.argv[3])
