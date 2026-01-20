#!/usr/bin/env python3
"""
GIF 生成器 - 从视频中提取精彩片段生成 GIF
支持金句自动检测、自定义片段、批量生成
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict

# 设置控制台编码为UTF-8（仅在直接运行时）
if sys.platform == 'win32' and __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class GifGenerator:
    """GIF 生成器主类"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            'golden_quotes': {
                'gif': {
                    'width': 480,
                    'fps': 15,
                    'start_offset': -0.5,
                    'end_offset': 0.5,
                    'max_duration': 10,
                    'quality': 'medium'
                }
            }
        }

        try:
            import yaml
            if config_path and os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    try:
                        config = yaml.safe_load(f)
                        # 如果 yaml.safe_load 返回 None 或空字典，使用默认配置
                        if config and isinstance(config, dict):
                            # 合并配置，确保 golden_quotes.gif 存在
                            if 'golden_quotes' not in config:
                                config['golden_quotes'] = {}
                            if 'gif' not in config.get('golden_quotes', {}):
                                config['golden_quotes']['gif'] = default_config['golden_quotes']['gif']
                            return config
                        else:
                            return default_config
                    except Exception as e:
                        # 如果yaml读取失败，返回默认配置
                        print(f"⚠️  警告: 无法读取配置文件 {config_path}: {e}，使用默认配置")
                        return default_config
        except ImportError:
            pass

        # 默认配置
        return default_config

    def generate_from_quotes(
        self,
        video_path: str,
        quotes_json: str,
        output_dir: str,
        max_gifs: int = None
    ) -> List[str]:
        """
        从金句 JSON 文件生成 GIF

        Args:
            video_path: 输入视频路径
            quotes_json: 金句 JSON 文件路径
            output_dir: 输出目录
            max_gifs: 最多生成多少个 GIF

        Returns:
            生成的 GIF 文件路径列表
        """
        print(f"🎬 开始生成 GIF...")

        # 加载金句数据
        try:
            with open(quotes_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ 无法读取金句文件: {e}")
            return []

        quotes = data.get('quotes', [])
        if not quotes:
            print("❌ 没有找到金句数据")
            return []

        if max_gifs:
            quotes = quotes[:max_gifs]

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 获取 GIF 配置
        gif_config = self.config.get('golden_quotes', {}).get('gif', {})

        generated = []
        for i, quote in enumerate(quotes, 1):
            start_sec = quote['start_ms'] / 1000.0
            end_sec = quote['end_ms'] / 1000.0

            # 应用偏移
            start_offset = gif_config.get('start_offset', -0.5)
            end_offset = gif_config.get('end_offset', 0.5)

            actual_start = max(0, start_sec + start_offset)
            actual_end = end_sec + end_offset
            duration = actual_end - actual_start

            # 限制最大时长
            max_duration = gif_config.get('max_duration', 10)
            if duration > max_duration:
                actual_end = actual_start + max_duration
                duration = max_duration

            # 生成文件名
            text_preview = quote['text'][:20].replace(' ', '_').replace('/', '_')
            output_name = f"金句{i}_{text_preview}.gif"
            output_path = os.path.join(output_dir, output_name)

            # 生成 GIF
            try:
                self._generate_single_gif(
                    video_path,
                    actual_start,
                    actual_end,
                    output_path,
                    gif_config
                )
                generated.append(output_path)
                print(f"  ✅ [{i}/{len(quotes)}] {output_name}")
                print(f"     {quote['text'][:40]}{'...' if len(quote['text']) > 40 else ''}")

            except Exception as e:
                print(f"  ❌ [{i}/{len(quotes)}] 生成失败: {e}")

        print(f"\n✅ 成功生成 {len(generated)} 个 GIF 至: {output_dir}")
        return generated

    def generate_from_time_ranges(
        self,
        video_path: str,
        time_ranges: List[tuple],
        output_dir: str,
        prefix: str = "clip"
    ) -> List[str]:
        """
        从指定时间范围生成 GIF

        Args:
            video_path: 输入视频路径
            time_ranges: 时间范围列表 [(start1, end1), (start2, end2)]
            output_dir: 输出目录
            prefix: 文件名前缀

        Returns:
            生成的 GIF 文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)

        gif_config = self.config.get('golden_quotes', {}).get('gif', {})
        generated = []

        for i, (start, end) in enumerate(time_ranges, 1):
            output_path = os.path.join(output_dir, f"{prefix}_{i}.gif")

            try:
                self._generate_single_gif(
                    video_path,
                    start,
                    end,
                    output_path,
                    gif_config
                )
                generated.append(output_path)
                print(f"✅ 生成: {output_path}")

            except Exception as e:
                print(f"❌ 生成失败: {e}")

        return generated

    def _generate_single_gif(
        self,
        video_path: str,
        start: float,
        end: float,
        output_path: str,
        config: Dict
    ):
        """
        生成单个 GIF

        Args:
            video_path: 输入视频
            start: 开始时间（秒）
            end: 结束时间（秒）
            output_path: 输出路径
            config: GIF 配置
        """
        width = config.get('width', 480)
        fps = config.get('fps', 15)
        quality = config.get('quality', 'medium')

        # 质量设置
        quality_settings = {
            'low': {'scale': f'scale=320:-1', 'palette': 'max_colors=64'},
            'medium': {'scale': f'scale={width}:-1', 'palette': 'max_colors=128'},
            'high': {'scale': f'scale={width}:-1', 'palette': 'max_colors=256'}
        }

        qs = quality_settings.get(quality, quality_settings['medium'])

        # 临时调色板文件
        palette_path = output_path.replace('.gif', '_palette.png')

        try:
            # 步骤1: 生成调色板
            palette_cmd = [
                'ffmpeg', '-y',
                '-ss', str(start),
                '-i', video_path,
                '-t', str(end - start),
                '-vf', f"{qs['scale']},palettegen={qs['palette']}",
                palette_path
            ]

            result = subprocess.run(palette_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"    ⚠️  调色板生成警告: {result.stderr[-100:]}")

            # 步骤2: 使用调色板生成 GIF
            gif_cmd = [
                'ffmpeg', '-y',
                '-ss', str(start),
                '-i', video_path,
                '-t', str(end - start),
                '-i', palette_path,
                '-filter_complex', f"{qs['scale']} [x]; [x][1:v] paletteuse",
                '-r', str(fps),
                output_path
            ]

            result = subprocess.run(gif_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg错误: {result.stderr}")

        finally:
            # 清理临时文件
            if os.path.exists(palette_path):
                os.remove(palette_path)

    def generate_highlights_gif(
        self,
        video_path: str,
        transcript_file: str,
        output_dir: str,
        num_highlights: int = 5
    ) -> List[str]:
        """
        自动检测金句并生成 GIF（便捷方法）

        Args:
            video_path: 输入视频
            transcript_file: 转录文件
            output_dir: 输出目录
            num_highlights: 生成数量

        Returns:
            生成的 GIF 路径列表
        """
        # 先检测金句
        quotes_json = os.path.join(output_dir, 'golden_quotes.json')

        try:
            from golden_quote_detector import GoldenQuoteDetector

            detector = GoldenQuoteDetector(self.config.get('golden_quotes', {}))
            detector.detect(transcript_file, quotes_json)

            # 生成 GIF
            return self.generate_from_quotes(
                video_path,
                quotes_json,
                output_dir,
                num_highlights
            )

        except ImportError:
            print("❌ 无法导入金句检测器，请确保 golden_quote_detector.py 在同一目录")
            return []


def main():
    parser = argparse.ArgumentParser(
        description="GIF 生成器 - 从视频中提取精彩片段生成 GIF"
    )

    # 输入参数
    parser.add_argument("video", help="输入视频路径")
    parser.add_argument("-o", "--output", help="输出目录", default="gifs")

    # 模式选择
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--quotes", help="从金句 JSON 文件生成")
    group.add_argument("--time", help="从时间范围生成 (格式: start-end,多个用逗号分隔)")
    group.add_argument("--auto", help="自动检测金句并生成 (需指定转录文件)", metavar='TRANSCRIPT')

    # 可选参数
    parser.add_argument("--max", type=int, help="最多生成 N 个 GIF", default=None)
    parser.add_argument("--config", help="配置文件路径", default="config.yaml")
    parser.add_argument("--prefix", help="文件名前缀 (用于 --time 模式)", default="clip")

    args = parser.parse_args()

    generator = GifGenerator(args.config)

    if args.quotes:
        # 从金句文件生成
        generator.generate_from_quotes(
            args.video,
            args.quotes,
            args.output,
            args.max
        )

    elif args.time:
        # 从时间范围生成
        ranges = []
        for segment in args.time.split(','):
            start, end = segment.strip().split('-')
            ranges.append((float(start), float(end)))

        generator.generate_from_time_ranges(
            args.video,
            ranges,
            args.output,
            args.prefix
        )

    elif args.auto:
        # 自动检测金句并生成
        generator.generate_highlights_gif(
            args.video,
            args.auto,
            args.output,
            args.max or 5
        )


if __name__ == "__main__":
    main()
