# 视频剪辑项目管理工具

## 📁 目录结构

```
video-cutter/
├── scripts/              # 核心脚本
│   ├── all_in_one.py    # 一键处理
│   ├── transcriber.py   # 转录
│   ├── analyzer_complete.py  # 分析
│   ├── clipper.py       # 剪辑
│   └── ...
├── tools/               # 项目管理工具（本目录）
│   ├── project_manager.py   # 项目管理器
│   ├── show_stats.py        # 统计查看器
│   └── README.md            # 本文件
└── docs/                # 文档
    ├── PROJECT_GUIDE.md         # 使用指南
    └── PROJECT_SETUP_SUMMARY.md # 整理总结
```

## 🚀 工具说明

### 1. project_manager.py - 项目管理器

**功能**：
- 创建新项目
- 列出所有项目
- 打开项目文件夹
- 剪辑视频
- 查看项目统计
- 删除项目

**使用方法**：
```bash
cd D:\vibe  # 或你的工作区
python project_manager.py
```

**配置**：
编辑脚本中的路径：
```python
PROJECTS_DIR = Path(r"D:\vibe\projects")  # 修改为你的项目目录
SKILLS_DIR = Path(r"C:\Users\无我\.claude\skills\video-cutter\scripts")
```

### 2. show_stats.py - 统计查看器

**功能**：
- 显示所有项目的统计信息
- 包括视频时长、文件大小、压缩率等

**使用方法**：
```bash
cd D:\vibe
python show_stats.py
```

## 📂 项目结构

每个项目的标准结构：

```
项目名称/
├── source/              # 原视频
│   └── 视频.mp4
├── output/              # 输出结果
│   ├── 剪辑后_视频.mp4
│   └── gifs/           # 金句 GIF
├── temp/               # 临时文件
│   ├── transcript.json
│   ├── filter.txt
│   ├── golden_quotes.json
│   └── stats.json
└── README.md
```

## 💡 使用建议

1. **修改路径**：将工具中的路径改为你的实际工作区路径
2. **创建快捷方式**：可以在桌面创建快捷方式指向这些工具
3. **定期备份**：定期备份 projects 目录

## 🔧 自定义

### 修改默认项目目录

编辑 `project_manager.py`：
```python
PROJECTS_DIR = Path(r"你的\项目\路径")
```

### 修改 GIF 生成数量

在项目管理器中，选择"剪辑视频"时可以指定 GIF 数量。

## 📖 相关文档

- **使用指南**：[../docs/PROJECT_GUIDE.md](../docs/PROJECT_GUIDE.md)
- **整理总结**：[../docs/PROJECT_SETUP_SUMMARY.md](../docs/PROJECT_SETUP_SUMMARY.md)
- **安装教程**：[../INSTALL.md](../INSTALL.md)
- **工作流程**：[../WORKFLOW.md](../WORKFLOW.md)

## ⚙️ 系统要求

- Python 3.8+
- 已安装 video-cutter skill
- FFmpeg（已包含在系统PATH中）

## 📞 获取帮助

遇到问题？
1. 查看 [docs/](../docs/) 目录中的文档
2. 提交 Issue：https://github.com/yzz05220-rgb/video-cutter/issues

---

**版本**：v1.0
**最后更新**：2025-01-20
