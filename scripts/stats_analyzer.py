#!/usr/bin/env python3
"""
统计分析工具 - 生成详细的视频剪辑报告
包括时长对比、语速分析、停顿统计、金句总结等
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List
from collections import Counter

# 设置控制台编码为UTF-8（仅在直接运行时）
if sys.platform == 'win32' and __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class StatsAnalyzer:
    """统计分析器"""

    def __init__(self):
        self.stats = {}

    def generate_report(
        self,
        original_video: str,
        output_video: str = None,
        transcript_file: str = None,
        quotes_file: str = None,
        output_json: str = None
    ):
        """
        生成统计报告

        Args:
            original_video: 原视频路径
            output_video: 输出视频路径（可选）
            transcript_file: 转录文件（可选）
            quotes_file: 金句文件（可选）
            output_json: 输出 JSON 文件路径
        """
        print("📊 生成统计报告...")

        # 1. 基本信息
        self.stats['original_video'] = original_video
        self.stats['original_size_mb'] = self._get_file_size_mb(original_video)
        self.stats['original_duration'] = self._get_video_duration(original_video)

        if output_video and os.path.exists(output_video):
            self.stats['output_video'] = output_video
            self.stats['output_size_mb'] = self._get_file_size_mb(output_video)
            self.stats['output_duration'] = self._get_video_duration(output_video)
            self.stats['size_reduction'] = (1 - self.stats['output_size_mb'] / self.stats['original_size_mb']) * 100
            self.stats['duration_reduction'] = (1 - self.stats['output_duration'] / self.stats['original_duration']) * 100

        # 2. 转录分析
        if transcript_file and os.path.exists(transcript_file):
            self._analyze_transcript(transcript_file)

        # 3. 金句分析
        if quotes_file and os.path.exists(quotes_file):
            self._analyze_quotes(quotes_file)

        # 4. 打印报告
        self._print_report()

        # 5. 保存 JSON
        if output_json:
            self._save_json(output_json)

    def _get_file_size_mb(self, file_path: str) -> float:
        """获取文件大小（MB）"""
        return os.path.getsize(file_path) / (1024 * 1024)

    def _get_video_duration(self, video_path: str) -> float:
        """获取视频时长（秒）"""
        import subprocess

        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except:
            return 0.0

    def _analyze_transcript(self, transcript_file: str):
        """分析转录文件"""
        with open(transcript_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        segments = data['segments']
        duration_sec = data['duration_ms'] / 1000.0

        # 文本统计
        full_text = ''.join([s['char'] for s in segments])
        self.stats['total_chars'] = len(full_text)
        self.stats['total_words'] = len(full_text.replace('，', ' ').replace('。', ' ').split())

        # 语速分析（字符/分钟）
        self.stats['speech_rate_chars_per_min'] = (self.stats['total_chars'] / duration_sec) * 60
        self.stats['speech_rate_words_per_min'] = (self.stats['total_words'] / duration_sec) * 60

        # 停顿分析
        pauses = []
        for i in range(len(segments) - 1):
            gap = segments[i + 1]['start'] - segments[i]['end']
            if gap > 300:  # 超过 300ms 认为是停顿
                pauses.append(gap / 1000.0)  # 转换为秒

        self.stats['total_pauses'] = len(pauses)
        self.stats['pause_rate'] = len(pauses) / duration_sec * 60  # 每分钟停顿次数
        self.stats['avg_pause_duration'] = sum(pauses) / len(pauses) if pauses else 0
        self.stats['max_pause_duration'] = max(pauses) if pauses else 0

        # 字符频率
        char_freq = Counter([s['char'] for s in segments if s['char'].strip()])
        self.stats['top_chars'] = char_freq.most_common(10)

        # 填充词检测
        filler_words = ['嗯', '啊', '哎', '诶', '呃', '额', '唉', '哦', '噢', '呀', '欸', '那个', '然后', '就是']
        filler_count = sum([full_text.count(fw) for fw in filler_words])
        self.stats['filler_ratio'] = (filler_count / self.stats['total_chars'] * 100) if self.stats['total_chars'] > 0 else 0

    def _analyze_quotes(self, quotes_file: str):
        """分析金句文件"""
        with open(quotes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        quotes = data.get('quotes', [])
        self.stats['total_quotes'] = len(quotes)
        self.stats['avg_quote_score'] = sum([q['score'] for q in quotes]) / len(quotes) if quotes else 0
        self.stats['top_quotes'] = quotes[:5] if quotes else []

    def _print_report(self):
        """打印报告"""
        print("\n" + "=" * 70)
        print("📊 视频剪辑统计报告")
        print("=" * 70)

        # 时长对比
        print("\n⏱️  时长对比:")
        orig_min = int(self.stats['original_duration'] // 60)
        orig_sec = int(self.stats['original_duration'] % 60)
        print(f"  原视频: {orig_min}分{orig_sec}秒 ({self.stats['original_duration']:.1f}秒)")

        if 'output_duration' in self.stats:
            out_min = int(self.stats['output_duration'] // 60)
            out_sec = int(self.stats['output_duration'] % 60)
            print(f"  剪辑后: {out_min}分{out_sec}秒 ({self.stats['output_duration']:.1f}秒)")
            print(f"  压缩率: {self.stats['duration_reduction']:.1f}%")

        # 文件大小
        print("\n💾 文件大小:")
        print(f"  原视频: {self.stats['original_size_mb']:.1f} MB")

        if 'output_size_mb' in self.stats:
            print(f"  剪辑后: {self.stats['output_size_mb']:.1f} MB")
            print(f"  减小: {self.stats['size_reduction']:.1f}%")

        # 语速分析
        if 'speech_rate_chars_per_min' in self.stats:
            print("\n🗣️  语速分析:")
            print(f"  平均语速: {self.stats['speech_rate_chars_per_min']:.0f} 字/分钟")
            print(f"           {self.stats['speech_rate_words_per_min']:.0f} 词/分钟")

            # 速度评级
            rate = self.stats['speech_rate_chars_per_min']
            if rate < 150:
                speed_label = "较慢"
            elif rate < 250:
                speed_label = "适中"
            elif rate < 350:
                speed_label = "较快"
            else:
                speed_label = "极快"
            print(f"  速度评级: {speed_label}")

        # 停顿统计
        if 'total_pauses' in self.stats:
            print("\n⏸️  停顿统计:")
            print(f"  停顿次数: {self.stats['total_pauses']} 次")
            print(f"  停顿频率: {self.stats['pause_rate']:.1f} 次/分钟")
            print(f"  平均时长: {self.stats['avg_pause_duration']:.2f} 秒")
            print(f"  最长停顿: {self.stats['max_pause_duration']:.2f} 秒")

        # 填充词
        if 'filler_ratio' in self.stats:
            print("\n🔤 填充词:")
            print(f"  比例: {self.stats['filler_ratio']:.1f}%")

        # 金句
        if 'total_quotes' in self.stats:
            print(f"\n✨ 金句:")
            print(f"  检测到 {self.stats['total_quotes']} 条金句")
            print(f"  平均评分: {self.stats['avg_quote_score']:.1f}")

            if self.stats['top_quotes']:
                print(f"\n  🏆 Top 5 金句:")
                for i, q in enumerate(self.stats['top_quotes'], 1):
                    text = q['text'][:50] + '...' if len(q['text']) > 50 else q['text']
                    print(f"    {i}. [{q['timestamp']}] {text}")
                    print(f"       💯 {q['score']:.1f} | {q['reason']}")

        # 常用字
        if 'top_chars' in self.stats:
            print(f"\n📝 常用字 Top 10:")
            for i, (char, count) in enumerate(self.stats['top_chars'], 1):
                if char.strip():
                    print(f"    {i}. 「{char}」: {count} 次")

        print("\n" + "=" * 70 + "\n")

    def _save_json(self, output_file: str):
        """保存 JSON 报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

        print(f"💾 详细报告已保存: {output_file}\n")


def main():
    parser = argparse.ArgumentParser(
        description="统计分析工具 - 生成视频剪辑统计报告"
    )

    parser.add_argument("--original", required=True, help="原视频路径")
    parser.add_argument("--output", help="剪辑后视频路径（可选）")
    parser.add_argument("--transcript", help="转录文件路径（可选）")
    parser.add_argument("--quotes", help="金句文件路径（可选）")
    parser.add_argument("--report", help="输出 JSON 报告路径", default="stats_report.json")

    args = parser.parse_args()

    analyzer = StatsAnalyzer()
    analyzer.generate_report(
        args.original,
        args.output,
        args.transcript,
        args.quotes,
        args.report
    )


if __name__ == "__main__":
    main()
