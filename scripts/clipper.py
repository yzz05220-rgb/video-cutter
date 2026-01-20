import sys
import subprocess
import os

# 设置控制台编码为UTF-8（仅在直接运行时）
if sys.platform == 'win32' and __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def clip_video(input_video, filter_file, output_video):
    if not os.path.exists(filter_file):
        print(f"❌ Filter 文件不存在: {filter_file}")
        return
        
    print(f"✂️ 开始剪辑: {input_video}")
    cmd = [
        'ffmpeg', '-y',
        '-i', input_video,
        '-filter_complex_script', filter_file,
        '-map', '[outv]', '-map', '[outa]',
        output_video
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ 剪辑完成: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 剪辑失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python clipper.py <input_video> <filter_file> <output_video>")
        sys.exit(1)
    clip_video(sys.argv[1], sys.argv[2], sys.argv[3])
