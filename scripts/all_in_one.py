#!/usr/bin/env python3
"""
一键视频处理 - 自动化整个工作流
转录 → 分析 → 剪辑 → 生成金句 → 输出统计
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class VideoCutterPipeline:
    """视频剪辑流水线"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config.yaml"
        self.steps_completed = []

    def print_banner(self):
        """打印欢迎横幅"""
        print("\n" + "=" * 60)
        print("🎬 智能视频剪辑工具 - 一键处理")
        print("=" * 60 + "\n")

    def print_step(self, step_num: int, total: int, title: str):
        """打印步骤信息"""
        print(f"\n{'─' * 60}")
        print(f"[{step_num}/{total}] {title}")
        print(f"{'─' * 60}\n")

    def run(
        self,
        video_path: str,
        project_name: str = None,
        remove_silence: bool = False,
        generate_gifs: bool = True,
        num_gifs: int = 5,
        preview_only: bool = False
    ):
        """
        运行完整流程

        Args:
            video_path: 输入视频路径
            project_name: 项目名称（可选）
            remove_silence: 是否删除静音
            generate_gifs: 是否生成 GIF
            num_gifs: 生成 GIF 数量
            preview_only: 仅预览不执行剪辑
        """
        self.print_banner()

        # 验证输入
        if not os.path.exists(video_path):
            print(f"❌ 视频文件不存在: {video_path}")
            return

        # 设置项目目录
        if project_name:
            from manager import create_project
            base_dir = os.path.dirname(os.path.abspath(__file__))
            projects_dir = os.path.join(base_dir, "..", "Projects")
            project_path = os.path.join(projects_dir, project_name)

            if not os.path.exists(project_path):
                create_project(project_name)
        else:
            # 使用视频所在目录
            project_path = os.path.dirname(video_path)

        source_dir = os.path.join(project_path, "source")
        output_dir = os.path.join(project_path, "output")
        temp_dir = os.path.join(project_path, "temp")

        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)

        video_name = os.path.basename(video_path)
        video_basename = os.path.splitext(video_name)[0]

        # 定义文件路径
        transcript_json = os.path.join(temp_dir, "transcript.json")
        filter_txt = os.path.join(temp_dir, "filter.txt")
        quotes_json = os.path.join(temp_dir, "golden_quotes.json")
        stats_json = os.path.join(temp_dir, "stats.json")
        output_video = os.path.join(output_dir, f"剪辑后_{video_name}.mp4")
        gifs_dir = os.path.join(output_dir, "gifs")

        total_steps = 5
        if generate_gifs:
            total_steps += 1

        # ===== 步骤 1: 转录 =====
        self.print_step(1, total_steps, "转录视频 (FunASR)")
        if not self._transcribe(video_path, transcript_json, temp_dir):
            return
        self.steps_completed.append("transcribe")

        # ===== 步骤 2: 分析 =====
        self.print_step(2, total_steps, "分析并生成剪辑方案")
        if not self._analyze(transcript_json, filter_txt, remove_silence, preview_only):
            return
        self.steps_completed.append("analyze")

        if preview_only:
            print("\n⚠️ 预览模式，跳过实际剪辑")
            return

        # ===== 步骤 3: 剪辑 =====
        self.print_step(3, total_steps, "执行剪辑 (FFmpeg)")
        if not self._clip(video_path, filter_txt, output_video):
            return
        self.steps_completed.append("clip")

        # ===== 步骤 4: 生成字幕 =====
        self.print_step(4, total_steps, "生成字幕文件")
        srt_path = os.path.join(output_dir, f"{video_basename}.srt")
        self._generate_subtitle(video_path, srt_path)
        self.steps_completed.append("subtitle")

        # ===== 步骤 5: 金句检测 =====
        self.print_step(5, total_steps, "检测金句")
        self._detect_quotes(transcript_json, quotes_json)
        self.steps_completed.append("quotes")

        # ===== 步骤 6: 生成 GIF =====
        if generate_gifs:
            self.print_step(6, total_steps, f"生成前 {num_gifs} 条金句的 GIF")
            self._generate_gifs(video_path, quotes_json, gifs_dir, num_gifs)
            self.steps_completed.append("gifs")

        # ===== 步骤 7: 统计分析 =====
        self.print_step(len(self.steps_completed) + 1, total_steps, "生成统计报告")
        self._generate_stats(
            video_path,
            output_video,
            transcript_json,
            quotes_json,
            stats_json
        )

        # ===== 完成 =====
        self.print_completion(output_video, stats_json, gifs_dir if generate_gifs else None)

    def _transcribe(self, video_path: str, output_json: str, temp_dir: str) -> bool:
        """转录视频"""
        try:
            # 导入转录模块
            import importlib.util
            spec = importlib.util.spec_from_file_location("transcriber", "transcriber.py")
            transcriber = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(transcriber)

            return transcriber.transcribe_video(video_path, output_json, temp_dir)

        except Exception as e:
            print(f"❌ 转录失败: {e}")
            return False

    def _analyze(self, transcript_json: str, filter_txt: str, remove_silence: bool, preview_only: bool) -> bool:
        """分析转录"""
        try:
            # 使用增强的分析器
            if os.path.exists("analyzer_v2.py"):
                import importlib.util
                spec = importlib.util.spec_from_file_location("analyzer_v2", "analyzer_v2.py")
                analyzer = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(analyzer)

                return analyzer.analyze_transcript(
                    transcript_json,
                    filter_txt,
                    remove_silence=remove_silence,
                    preview_mode=preview_only,
                    config_path=self.config_path
                )
            else:
                # 使用原版分析器
                import importlib.util
                spec = importlib.util.spec_from_file_location("analyzer", "analyzer.py")
                analyzer = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(analyzer)

                return analyzer.analyze_transcript(transcript_json, filter_txt, remove_silence)

        except Exception as e:
            print(f"❌ 分析失败: {e}")
            return False

    def _clip(self, video_path: str, filter_txt: str, output_video: str) -> bool:
        """剪辑视频"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("clipper", "clipper.py")
            clipper = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(clipper)

            clipper.clip_video(video_path, filter_txt, output_video)
            return True

        except Exception as e:
            print(f"❌ 剪辑失败: {e}")
            return False

    def _generate_subtitle(self, video_path: str, srt_path: str) -> bool:
        """生成字幕"""
        try:
            if os.path.exists("subtitler.py"):
                import importlib.util
                spec = importlib.util.spec_from_file_location("subtitler", "subtitler.py")
                subtitler = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(subtitler)

                return subtitler.generate_srt(video_path, srt_path)

        except Exception as e:
            print(f"⚠️ 字幕生成失败: {e}")
            return False

    def _detect_quotes(self, transcript_json: str, quotes_json: str):
        """检测金句"""
        try:
            if os.path.exists("golden_quote_detector.py"):
                import importlib.util
                spec = importlib.util.spec_from_file_location("detector", "golden_quote_detector.py")
                detector = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(detector)

                dq = detector.GoldenQuoteDetector(self.config_path)
                dq.detect(transcript_json, quotes_json)

        except Exception as e:
            print(f"⚠️ 金句检测失败: {e}")

    def _generate_gifs(self, video_path: str, quotes_json: str, gifs_dir: str, num_gifs: int):
        """生成 GIF"""
        try:
            if os.path.exists("gif_generator.py") and os.path.exists(quotes_json):
                import importlib.util
                spec = importlib.util.spec_from_file_location("gif_gen", "gif_generator.py")
                gif_gen = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(gif_gen)

                gg = gif_gen.GifGenerator(self.config_path)
                gg.generate_from_quotes(video_path, quotes_json, gifs_dir, num_gifs)

        except Exception as e:
            print(f"⚠️ GIF 生成失败: {e}")

    def _generate_stats(self, original_video: str, output_video: str,
                       transcript_json: str, quotes_json: str, stats_json: str):
        """生成统计报告"""
        try:
            if os.path.exists("stats_analyzer.py"):
                import importlib.util
                spec = importlib.util.spec_from_file_location("stats", "stats_analyzer.py")
                stats = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(stats)

                sa = stats.StatsAnalyzer()
                sa.generate_report(
                    original_video,
                    output_video if os.path.exists(output_video) else None,
                    transcript_json,
                    quotes_json if os.path.exists(quotes_json) else None,
                    stats_json
                )

        except Exception as e:
            print(f"⚠️ 统计分析失败: {e}")

    def print_completion(self, output_video: str, stats_json: str, gifs_dir: str = None):
        """打印完成信息"""
        print("\n" + "=" * 60)
        print("✅ 处理完成！")
        print("=" * 60)

        # 显示文件大小
        if os.path.exists(output_video):
            size_mb = os.path.getsize(output_video) / (1024 * 1024)
            print(f"\n📁 输出视频: {output_video}")
            print(f"   文件大小: {size_mb:.1f} MB")

        if gifs_dir and os.path.exists(gifs_dir):
            gifs = [f for f in os.listdir(gifs_dir) if f.endswith('.gif')]
            if gifs:
                print(f"\n🎨 生成 GIF: {len(gifs)} 个")
                print(f"   目录: {gifs_dir}")

        if os.path.exists(stats_json):
            print(f"\n📊 统计报告: {stats_json}")

        print("\n" + "=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="智能视频剪辑 - 一键处理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 基础用法
  python all_in_one.py video.mp4

  # 指定项目名称
  python all_in_one.py video.mp4 --project my_video

  # 删除静音
  python all_in_one.py video.mp4 --remove-silence

  # 生成 10 个 GIF
  python all_in_one.py video.mp4 --gifs 10

  # 预览模式（不实际剪辑）
  python all_in_one.py video.mp4 --preview
        """
    )

    parser.add_argument("video", help="输入视频路径")
    parser.add_argument("--project", "-p", help="项目名称（可选）", default=None)
    parser.add_argument("--remove-silence", action="store_true", help="删除静音段落")
    parser.add_argument("--gifs", type=int, help="生成 N 个金句 GIF (默认: 5)", default=5)
    parser.add_argument("--no-gifs", action="store_true", help="不生成 GIF")
    parser.add_argument("--preview", action="store_true", help="预览模式，不执行实际剪辑")
    parser.add_argument("--config", "-c", help="配置文件路径", default="config.yaml")

    args = parser.parse_args()

    pipeline = VideoCutterPipeline(args.config)

    pipeline.run(
        video_path=args.video,
        project_name=args.project,
        remove_silence=args.remove_silence,
        generate_gifs=not args.no_gifs,
        num_gifs=args.gifs,
        preview_only=args.preview
    )


if __name__ == "__main__":
    main()
