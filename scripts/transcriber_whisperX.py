#!/usr/bin/env python3
"""
WhisperX 增强转录器
- 更快的转录速度（70x realtime）
- 更精准的词级时间戳
- 支持说话人分离（diarization）
"""

import os
import sys
import json
import argparse

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def transcribe_with_whisperX(
    video_path: str,
    output_json: str,
    model_size: str = "large-v3",
    compute_type: str = "float16",
    diarization: bool = False,
    batch_size: int = 16
):
    """
    使用 WhisperX 进行增强转录

    Args:
        video_path: 输入视频路径
        output_json: 输出 JSON 文件路径
        model_size: 模型大小 (tiny/base/small/medium/large-v2/large-v3)
        compute_type: 计算类型 (float16/float32/int8)
        diarization: 是否启用说话人分离
        batch_size: 批处理大小
    """
    import whisperx

    print(f"🎬 开始 WhisperX 转录: {os.path.basename(video_path)}")
    print(f"   模型: {model_size}")
    print(f"   计算: {compute_type}")
    print(f"   批处理: {batch_size}")
    if diarization:
        print(f"   说话人分离: 启用")

    # 1. 转录
    print("\n⏳ 步骤 1/3: 转录中...")
    try:
        device = "cuda" if __import__('torch').cuda.is_available() else "cpu"
        print(f"   设备: {device}")

        audio = whisperx.load_audio(video_path)

        model = whisperx.load_model(
            model_size,
            device=device,
            compute_type=compute_type,
            language="zh"  # 中文
        )

        result = model.transcribe(
            audio,
            batch_size=batch_size,
            language="zh"
        )

        print(f"   ✅ 转录完成，识别了 {len(result['segments'])} 个片段")

    except Exception as e:
        print(f"   ❌ 转录失败: {e}")
        return False

    # 2. 对齐（词级时间戳）
    print("\n⏳ 步骤 2/3: 对齐词级时间戳...")
    try:
        model_a, metadata = whisperx.load_align_model(
            language_code="zh",
            device=device
        )

        result = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            device,
            return_char_alignments=False  # 使用词级对齐
        )

        print(f"   ✅ 对齐完成")

    except Exception as e:
        print(f"   ⚠️ 对齐失败: {e}")
        print(f"   将使用句子级时间戳")

    # 3. 说话人分离（可选）
    if diarization:
        print("\n⏳ 步骤 3/3: 说话人分离...")
        try:
            diarize_model = whisperx.DiarizationPipeline(
                use_auth_token=False,  # 不使用 HF token
                device=device
            )

            result = whisperx.assign_word_speakers(
                diarize_model,
                result,
                audio
            )

            print(f"   ✅ 说话人分离完成")

        except Exception as e:
            print(f"   ⚠️ 说话人分离失败: {e}")
            print(f"   继续不使用说话人信息")

    # 4. 转换为兼容格式
    print("\n📦 转换输出格式...")

    # 获取视频时长
    try:
        import subprocess
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result_check = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration_ms = float(result_check.stdout.strip()) * 1000
    except:
        duration_ms = sum([seg['end'] - seg['start'] for seg in result['segments']])

    # 如果有词级时间戳，使用词级；否则使用句子级
    all_chars = []

    for seg in result["segments"]:
        if "words" in seg and len(seg["words"]) > 0:
            # 使用词级时间戳
            for word in seg["words"]:
                if "word" in word:
                    # 每个字符使用词的时间戳
                    for char in word["word"]:
                        all_chars.append({
                            'char': char,
                            'start': round(word["start"] * 1000),
                            'end': round(word["end"] * 1000)
                        })
        else:
            # 使用句子级时间戳
            for char in seg["text"]:
                all_chars.append({
                    'char': char,
                    'start': round(seg["start"] * 1000),
                    'end': round(seg["end"] * 1000)
                })

    # 保存结果
    output_data = {
        "video_path": video_path,
        "duration_ms": duration_ms,
        "model": f"WhisperX-{model_size}",
        "segments": all_chars,
        "speaker_segments": result.get("segments", [])  # 包含说话人信息
    }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ WhisperX 转录完成！")
    print(f"   识别字符数: {len(all_chars)}")
    print(f"   视频时长: {duration_ms/1000:.1f} 秒")
    print(f"   输出文件: {output_json}")

    # 打印说话人统计（如果有）
    if diarization and "segments" in result:
        speakers = set()
        for seg in result["segments"]:
            if "speaker" in seg:
                speakers.add(seg["speaker"])
        if speakers:
            print(f"   识别说话人: {len(speakers)} 个 - {', '.join(sorted(speakers))}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="WhisperX 增强转录器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 基础用法（使用默认 large-v3 模型）
  python transcriber_whisperX.py video.mp4 output.json

  # 使用 medium 模型（更快）
  python transcriber_whisperX.py video.mp4 output.json --model medium

  # 启用说话人分离
  python transcriber_whisperX.py video.mp4 output.json --diarization

  # GPU 加速（float16）
  python transcriber_whisperX.py video.mp4 output.json --compute float16

  # 调整批处理大小（显存不足时减小）
  python transcriber_whisperX.py video.mp4 output.json --batch-size 8
        """
    )

    parser.add_argument("video", help="输入视频路径")
    parser.add_argument("output", help="输出 JSON 文件路径")
    parser.add_argument("--model", default="large-v3",
                       help="WhisperX 模型 (tiny/base/small/medium/large-v2/large-v3)")
    parser.add_argument("--compute", default="float16",
                       help="计算类型 (float16/float32/int8)")
    parser.add_argument("--diarization", action="store_true",
                       help="启用说话人分离")
    parser.add_argument("--batch-size", type=int, default=16,
                       help="批处理大小 (默认 16，显存不足时可减小)")

    args = parser.parse_args()

    transcribe_with_whisperX(
        args.video,
        args.output,
        model_size=args.model,
        compute_type=args.compute,
        diarization=args.diarization,
        batch_size=args.batch_size
    )


if __name__ == "__main__":
    main()
