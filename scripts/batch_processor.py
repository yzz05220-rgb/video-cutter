#!/usr/bin/env python3
"""
批量处理器 - 批量处理多个视频文件
支持并行处理、进度显示、错误恢复
"""

import os
import sys
import argparse
import glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class BatchProcessor:
    """批量处理器"""

    def __init__(self, max_workers: int = 3, config_path: str = None):
        self.max_workers = max_workers
        self.config_path = config_path or "config.yaml"
        self.results = []

    def process_batch(
        self,
        input_dir: str,
        output_dir: str = None,
        pattern: str = "*.mp4",
        remove_silence: bool = False,
        generate_gifs: bool = True,
        num_gifs: int = 5
    ):
        """
        批量处理视频

        Args:
            input_dir: 输入目录
            output_dir: 输出目录（可选，默认在输入目录下创建 output 子目录）
            pattern: 文件匹配模式
            remove_silence: 是否删除静音
            generate_gifs: 是否生成 GIF
            num_gifs: 生成 GIF 数量
        """
        # 查找视频文件
        search_pattern = os.path.join(input_dir, pattern)
        video_files = glob.glob(search_pattern, recursive=True)

        if not video_files:
            print(f"❌ 未找到匹配的视频文件: {search_pattern}")
            return

        print(f"\n{'=' * 70}")
        print(f"📦 批量处理模式")
        print(f"{'=' * 70}")
        print(f"找到 {len(video_files)} 个视频文件")
        print(f"并行处理: {self.max_workers} 个线程")
        print(f"{'=' * 70}\n")

        # 设置输出目录
        if not output_dir:
            output_dir = os.path.join(input_dir, "batch_output")

        os.makedirs(output_dir, exist_ok=True)

        # 并行处理
        completed = 0
        failed = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任务
            futures = {}
            for video_path in video_files:
                future = executor.submit(
                    self._process_single,
                    video_path,
                    output_dir,
                    remove_silence,
                    generate_gifs,
                    num_gifs
                )
                futures[future] = video_path

            # 收集结果
            for future in as_completed(futures):
                video_path = futures[future]
                try:
                    result = future.result()
                    self.results.append(result)

                    if result['success']:
                        completed += 1
                        print(f"✅ [{completed + failed}/{len(video_files)}] {os.path.basename(video_path)}")
                    else:
                        failed += 1
                        print(f"❌ [{completed + failed}/{len(video_files)}] {os.path.basename(video_path)}")
                        print(f"   错误: {result.get('error', 'Unknown')}")

                except Exception as e:
                    failed += 1
                    print(f"❌ [{completed + failed}/{len(video_files)}] {os.path.basename(video_path)}")
                    print(f"   异常: {e}")

        # 打印总结
        self._print_summary(completed, failed, output_dir)

    def _process_single(
        self,
        video_path: str,
        output_dir: str,
        remove_silence: bool,
        generate_gifs: bool,
        num_gifs: int
    ) -> dict:
        """
        处理单个视频

        Returns:
            结果字典
        """
        try:
            # 导入 all_in_one 模块
            import importlib.util
            spec = importlib.util.spec_from_file_location("all_in_one", "all_in_one.py")
            aio = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(aio)

            # 创建项目名称（使用视频文件名）
            video_name = Path(video_path).stem
            project_name = f"batch_{video_name}"

            # 运行处理流程
            pipeline = aio.VideoCutterPipeline(self.config_path)

            # 静默运行（不打印横幅）
            success = pipeline.run(
                video_path=video_path,
                project_name=project_name,
                remove_silence=remove_silence,
                generate_gifs=generate_gifs,
                num_gifs=num_gifs,
                preview_only=False
            )

            return {
                'video': video_path,
                'success': True,
                'project': project_name
            }

        except Exception as e:
            return {
                'video': video_path,
                'success': False,
                'error': str(e)
            }

    def _print_summary(self, completed: int, failed: int, output_dir: str):
        """打印批量处理总结"""
        print("\n" + "=" * 70)
        print("📊 批量处理完成")
        print("=" * 70)
        print(f"✅ 成功: {completed} 个")
        print(f"❌ 失败: {failed} 个")
        print(f"📁 输出目录: {output_dir}")

        if failed > 0:
            print("\n⚠️ 失败的视频:")
            for r in self.results:
                if not r['success']:
                    print(f"  - {os.path.basename(r['video'])}")

        print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="批量处理器 - 批量处理多个视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 处理当前目录所有 MP4
  python batch_processor.py .

  # 处理指定目录
  python batch_processor.py /path/to/videos

  # 自定义文件模式
  python batch_processor.py . --pattern "*.mkv"

  # 并行处理 5 个视频
  python batch_processor.py . --parallel 5

  # 删除静音
  python batch_processor.py . --remove-silence

  # 不生成 GIF
  python batch_processor.py . --no-gifs
        """
    )

    parser.add_argument("input_dir", help="输入目录路径")
    parser.add_argument("--output", "-o", help="输出目录（默认: input_dir/batch_output）")
    parser.add_argument("--pattern", "-p", help="文件匹配模式", default="*.mp4")
    parser.add_argument("--parallel", "-j", type=int, help="并行处理数量", default=3)
    parser.add_argument("--remove-silence", action="store_true", help="删除静音")
    parser.add_argument("--gifs", type=int, help="每个视频生成 N 个 GIF", default=5)
    parser.add_argument("--no-gifs", action="store_true", help="不生成 GIF")
    parser.add_argument("--config", "-c", help="配置文件路径", default="config.yaml")

    args = parser.parse_args()

    processor = BatchProcessor(
        max_workers=args.parallel,
        config_path=args.config
    )

    processor.process_batch(
        input_dir=args.input_dir,
        output_dir=args.output,
        pattern=args.pattern,
        remove_silence=args.remove_silence,
        generate_gifs=not args.no_gifs,
        num_gifs=args.gifs
    )


if __name__ == "__main__":
    main()
