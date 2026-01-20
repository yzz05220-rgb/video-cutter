# 工作区项目配置示例

本文档说明如何在你的工作区设置视频剪辑项目管理。

## 🎯 快速设置（3步）

### 步骤1：创建项目目录

在你的工作区创建 `projects` 文件夹：

```bash
# Windows (D盘示例)
mkdir D:\vibe\projects

# 或其他位置
mkdir C:\Users\你的用户名\Videos\projects
```

### 步骤2：复制管理工具

将 `tools/` 目录中的文件复制到你的工作区：

```bash
# 复制项目管理器
copy "C:\Users\无我\.claude\skills\video-cutter\tools\project_manager.py" "D:\vibe\"

# 复制统计查看器
copy "C:\Users\无我\.claude\skills\video-cutter\tools\show_stats.py" "D:\vibe\"
```

### 步骤3：配置路径

编辑 `project_manager.py`，修改以下路径：

```python
# 第15-16行
PROJECTS_DIR = Path(r"D:\vibe\projects")  # 改为你的项目目录
SKILLS_DIR = Path(r"C:\Users\无我\.claude\skills\video-cutter\scripts")  # 改为skill路径
```

## 📁 推荐的工作区结构

```
你的工作区\
├── projects\                    # 所有视频项目
│   ├── 项目1\
│   │   ├── source\
│   │   ├── output\
│   │   └── temp\
│   └── 项目2\
│       └── ...
├── project_manager.py           # 项目管理器
├── show_stats.py               # 统计查看器
└── 原始视频.mp4                # 待处理视频
```

## 🚀 开始使用

### 创建第一个项目

```bash
# 运行项目管理器
python project_manager.py

# 选择 [1] 创建新项目
# 输入项目名称：我的第一个视频
# 将视频放入 projects/我的第一个视频/source/
```

### 剪辑视频

```bash
# 在项目管理器中
# 选择 [4] 剪辑视频
# 输入项目名称：我的第一个视频
# 输入 GIF 数量：3（可选）
```

### 查看统计

```bash
# 方式1：使用统计查看器
python show_stats.py

# 方式2：在项目管理器中
# 选择 [5] 查看项目统计
```

## 💡 不同操作系统的设置

### Windows

```bash
# 创建项目目录
mkdir D:\Projects\VideoEditing

# 复制工具
copy "C:\Users\无我\.claude\skills\video-cutter\tools\*.py" "D:\Projects\VideoEditing\"

# 创建快捷方式
# 1. 右键点击 project_manager.py
# 2. 发送到 -> 桌面快捷方式
```

### macOS/Linux

```bash
# 创建项目目录
mkdir -p ~/Projects/VideoEditing

# 复制工具
cp ~/.claude/skills/video-cutter/tools/*.py ~/Projects/VideoEditing/

# 添加执行权限
chmod +x ~/Projects/VideoEditing/*.py

# 创建别名（可选）
echo 'alias video-manager="python ~/Projects/VideoEditing/project_manager.py"' >> ~/.bashrc
source ~/.bashrc
```

## 🎨 自定义配置

### 修改默认 GIF 数量

编辑 `project_manager.py` 第260行：
```python
num_gifs = int(num_gifs) if num_gifs.isdigit() else 3  # 改为你想要的数量
```

### 修改项目目录

编辑 `project_manager.py` 第15行：
```python
PROJECTS_DIR = Path(r"你的\自定义\路径")
```

### 修改 Skill 目录

编辑 `project_manager.py` 第16行：
```python
SKILLS_DIR = Path(r"你的\skill\路径")
```

## 📊 示例项目结构

创建项目后，结构如下：

```
projects/
└── 知识区视频剪辑/
    ├── source/
    │   └── 知识区.mp4
    ├── output/
    │   ├── 剪辑后_知识区.mp4.mp4
    │   └── gifs/
    │       ├── 金句1_...gif
    │       ├── 金句2_...gif
    │       └── 金句3_...gif
    ├── temp/
    │   ├── transcript.json
    │   ├── filter.txt
    │   ├── golden_quotes.json
    │   └── stats.json
    └── README.md
```

## 🔧 故障排除

### 问题1：找不到项目目录

**错误**：`❌ 项目目录不存在`

**解决**：
1. 检查 `PROJECTS_DIR` 路径是否正确
2. 确保目录已创建：`mkdir D:\vibe\projects`

### 问题2：找不到 Skill 脚本

**错误**：`❌ 找不到 all_in_one.py`

**解决**：
1. 检查 `SKILLS_DIR` 路径是否正确
2. 确保 video-cutter skill 已正确安装

### 问题3：中文显示乱码

**错误**：控制台显示乱码

**解决**：
1. 脚本已自动设置 UTF-8 编码
2. 如果仍有问题，执行：`chcp 65001` (Windows)

## 📚 下一步

1. 阅读 [PROJECT_GUIDE.md](PROJECT_GUIDE.md) 了解详细用法
2. 查看 [WORKFLOW.md](../WORKFLOW.md) 了解工作流程
3. 开始你的第一个视频剪辑项目！

---

**需要帮助？** 提交 Issue：https://github.com/yzz05220-rgb/video-cutter/issues
