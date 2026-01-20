#!/usr/bin/env python3
"""
视频剪辑项目管理器
用于创建和管理视频剪辑项目
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PROJECTS_DIR = Path(r"D:\vibe\projects")
SKILLS_DIR = Path(r"C:\Users\无我\.claude\skills\video-cutter\scripts")


def list_projects():
    """列出所有项目"""
    print("\n" + "=" * 60)
    print("📁 所有项目")
    print("=" * 60)

    if not PROJECTS_DIR.exists():
        print("❌ 项目目录不存在")
        return

    projects = [d for d in PROJECTS_DIR.iterdir() if d.is_dir()]

    if not projects:
        print("❌ 暂无项目")
        return

    for i, project in enumerate(projects, 1):
        print(f"\n[{i}] {project.name}")

        # 统计文件
        source_files = list((project / "source").glob("*.mp4")) if (project / "source").exists() else []
        output_files = list((project / "output").glob("*.mp4")) if (project / "output").exists() else []
        temp_files = list((project / "temp").glob("*.json")) if (project / "temp").exists() else []

        print(f"    📹 源视频: {len(source_files)} 个")
        print(f"    ✂️  输出视频: {len(output_files)} 个")
        print(f"    📊 临时文件: {len(temp_files)} 个")

        # 读取统计信息
        stats_file = project / "temp" / "stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    print(f"    📅 处理时间: {stats.get('output_duration', 0):.1f}秒")
            except:
                pass


def create_project(project_name: str):
    """创建新项目"""
    project_path = PROJECTS_DIR / project_name

    if project_path.exists():
        print(f"❌ 项目已存在: {project_name}")
        return False

    # 创建目录结构
    (project_path / "source").mkdir(parents=True)
    (project_path / "output").mkdir()
    (project_path / "temp").mkdir()

    # 创建项目说明
    readme = project_path / "README.md"
    readme.write_text(f"""# {project_name}

## 项目信息
- 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 项目名称: {project_name}

## 文件说明
- `source/`: 原始视频文件
- `output/`: 输出结果（视频、GIF）
- `temp/`: 临时处理文件（转录、分析等）

## 处理命令
```bash
cd {SKILLS_DIR}
python all_in_one.py "{project_path / 'source' / '视频.mp4'}" --gifs 3
```
""", encoding='utf-8')

    print(f"✅ 项目创建成功: {project_name}")
    print(f"   路径: {project_path}")
    print(f"   请将视频文件放入: {project_path / 'source'}")
    return True


def open_project(project_name: str):
    """打开项目文件夹"""
    project_path = PROJECTS_DIR / project_name

    if not project_path.exists():
        print(f"❌ 项目不存在: {project_name}")
        return False

    os.startfile(project_path)
    print(f"✅ 已打开项目: {project_name}")
    return True


def clip_video(project_name: str, video_file: str = None, num_gifs: int = 3):
    """剪辑视频"""
    project_path = PROJECTS_DIR / project_name

    if not project_path.exists():
        print(f"❌ 项目不存在: {project_name}")
        return False

    source_dir = project_path / "source"

    if not video_file:
        # 自动查找视频文件
        videos = list(source_dir.glob("*.mp4"))
        if not videos:
            print(f"❌ 未找到视频文件: {source_dir}")
            return False
        if len(videos) > 1:
            print("⚠️  发现多个视频文件:")
            for i, v in enumerate(videos, 1):
                print(f"  [{i}] {v.name}")
            return False
        video_file = videos[0]
    else:
        video_file = source_dir / video_file
        if not video_file.exists():
            print(f"❌ 视频文件不存在: {video_file}")
            return False

    print(f"🎬 开始剪辑: {video_file.name}")
    print(f"   项目: {project_name}")

    # 调用 all_in_one.py
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SKILLS_DIR / "all_in_one.py"),
         str(video_file), "--gifs", str(num_gifs)],
        cwd=str(SKILLS_DIR)
    )

    if result.returncode == 0:
        print(f"✅ 剪辑完成")
        return True
    else:
        print(f"❌ 剪辑失败")
        return False


def show_stats(project_name: str):
    """显示项目统计"""
    project_path = PROJECTS_DIR / project_name

    if not project_path.exists():
        print(f"❌ 项目不存在: {project_name}")
        return

    try:
        project_name_encoded = project_name.encode('utf-8', errors='ignore').decode('utf-8')
    except:
        project_name_encoded = "Unknown"

    stats_file = project_path / "temp" / "stats.json"

    if not stats_file.exists():
        print(f"❌ 统计文件不存在，请先运行剪辑")
        return

    with open(stats_file, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    print("\n" + "=" * 60)
    print(f"📊 项目统计: {project_name_encoded}")
    print("=" * 60)

    print(f"\n📹 视频信息:")
    print(f"   原视频时长: {stats.get('original_duration', 0):.1f} 秒")
    print(f"   输出时长: {stats.get('output_duration', 0):.1f} 秒")
    print(f"   时长压缩: {stats.get('duration_reduction', 0):.1f}%")

    print(f"\n💾 文件大小:")
    print(f"   原视频: {stats.get('original_size_mb', 0):.1f} MB")
    print(f"   输出: {stats.get('output_size_mb', 0):.1f} MB")
    print(f"   压缩率: {stats.get('size_reduction', 0):.1f}%")

    print(f"\n🗣️ 语速分析:")
    print(f"   总字符数: {stats.get('total_chars', 0)}")
    print(f"   语速: {stats.get('speech_rate_chars_per_min', 0):.1f} 字/分钟")
    print(f"   停顿次数: {stats.get('total_pauses', 0)}")

    print(f"\n✨ 金句:")
    print(f"   检测数量: {stats.get('total_quotes', 0)}")


def delete_project(project_name: str):
    """删除项目"""
    project_path = PROJECTS_DIR / project_name

    if not project_path.exists():
        print(f"❌ 项目不存在: {project_name}")
        return False

    confirm = input(f"⚠️  确认删除项目 '{project_name}'？所有文件将被永久删除！(y/N): ")
    if confirm.lower() != 'y':
        print("❌ 已取消")
        return False

    shutil.rmtree(project_path)
    print(f"✅ 项目已删除: {project_name}")
    return True


def main():
    """主菜单"""
    while True:
        print("\n" + "=" * 60)
        print("🎬 视频剪辑项目管理器 v1.0")
        print("=" * 60)
        print("\n[1] 创建新项目")
        print("[2] 列出所有项目")
        print("[3] 打开项目文件夹")
        print("[4] 剪辑视频")
        print("[5] 查看项目统计")
        print("[6] 删除项目")
        print("[0] 退出")
        print()

        choice = input("请选择操作 (0-6): ").strip()

        if choice == "1":
            project_name = input("请输入项目名称: ").strip()
            if project_name:
                create_project(project_name)

        elif choice == "2":
            list_projects()

        elif choice == "3":
            project_name = input("请输入项目名称: ").strip()
            if project_name:
                open_project(project_name)

        elif choice == "4":
            project_name = input("请输入项目名称: ").strip()
            num_gifs = input("生成 GIF 数量 (默认3): ").strip()
            num_gifs = int(num_gifs) if num_gifs.isdigit() else 3
            if project_name:
                clip_video(project_name, num_gifs=num_gifs)

        elif choice == "5":
            project_name = input("请输入项目名称: ").strip()
            if project_name:
                show_stats(project_name)

        elif choice == "6":
            project_name = input("请输入项目名称: ").strip()
            if project_name:
                delete_project(project_name)

        elif choice == "0":
            print("👋 感谢使用！")
            break

        else:
            print("❌ 无效选择")


if __name__ == "__main__":
    main()
