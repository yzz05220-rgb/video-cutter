#!/usr/bin/env python3
"""
查看项目统计信息
"""
import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PROJECTS_DIR = Path(r"D:\vibe\projects")


def main():
    print("\n" + "=" * 60)
    print("📊 项目统计")
    print("=" * 60)

    # 列出所有项目
    projects = [d for d in PROJECTS_DIR.iterdir() if d.is_dir()]

    if not projects:
        print("❌ 暂无项目")
        return

    # 显示项目列表
    for i, project in enumerate(projects, 1):
        stats_file = project / "temp" / "stats.json"
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)

            print(f"\n[{i}] {project.name}")
            print(f"   原视频: {stats.get('original_duration', 0):.1f}秒 ({stats.get('original_size_mb', 0):.1f}MB)")
            print(f"   输出: {stats.get('output_duration', 0):.1f}秒 ({stats.get('output_size_mb', 0):.1f}MB)")
            print(f"   压缩: {stats.get('size_reduction', 0):.1f}%")
            print(f"   字符: {stats.get('total_chars', 0)} 个")
            print(f"   金句: {stats.get('total_quotes', 0)} 条")
        else:
            print(f"\n[{i}] {project.name}")
            print(f"   (未生成统计)")


if __name__ == "__main__":
    main()
