import os
import sys
import shutil
import argparse

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "..", "Projects")
TOOLS_DIR = BASE_DIR

def create_project(project_name):
    """创建新项目结构"""
    project_path = os.path.join(PROJECTS_DIR, project_name)
    if os.path.exists(project_path):
        print(f"⚠️ 项目已存在: {project_path}")
        return
        
    os.makedirs(os.path.join(project_path, "source"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "output"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "temp"), exist_ok=True)
    
    print(f"✅ 项目创建成功: {project_path}")
    print(f"👉 请将视频文件放入: {os.path.join(project_path, 'source')}")

def list_projects():
    """列出所有项目"""
    if not os.path.exists(PROJECTS_DIR):
        print("无项目")
        return
        
    projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
    print("\n📂 当前项目:")
    for p in projects:
        print(f"  - {p}")
    print("")

def main():
    parser = argparse.ArgumentParser(description="视频剪辑项目管理器")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # create 命令
    create_parser = subparsers.add_parser("create", help="创建新项目")
    create_parser.add_argument("name", help="项目名称 (英文/拼音)")
    
    # list 命令
    subparsers.add_parser("list", help="列出所有项目")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_project(args.name)
    elif args.command == "list":
        list_projects()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
