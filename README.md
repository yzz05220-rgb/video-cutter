# 🎬 智能视频剪辑工具 (Video Cutter)

> 自动转录语音、智能识别语气词/重复/静音、一键剪辑、金句检测、GIF生成

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📝 项目说明

本仓库是对 [Ceeon/videocut-skills](https://github.com/Ceeon/videocut-skills) 的**功能升级和优化版本**。

**原始项目**: [Ceeon/videocut-skills](https://github.com/Ceeon/videocut-skills) by [Ceeon](https://github.com/Ceeon)

**主要升级**: 由 **yzz05220-rgb** 在原有基础上新增 20+ 项实用功能，包括金句检测、GIF生成、一键处理、批量处理等。

## ✨ 特性

### 🚀 核心功能（基础版）
- **自动语音识别** - 使用 FunASR 进行逐字转录
- **智能剪辑** - 自动识别并删除语气词、重复字、静音段落
- **项目管理** - 简单的项目结构和文件管理

### 🆕 升级优化功能（主要改进）
> 以下功能为本项目新增和优化

- ✅ **一键处理** - 自动化完整工作流，无需手动执行多个步骤
- ✅ **金句检测** - 智能识别精彩片段
  - 关键词匹配（重要、核心、秘密等）
  - 句式模式识别（总的来说、一句话等）
  - 长度和复杂度分析
  - 可选的 AI 分析支持（GPT-4）
- ✅ **GIF生成** - 自动生成金句的 GIF 预览
  - 可配置宽度、帧率、质量
  - 智能缓冲时间（前后自动扩展）
  - 支持批量生成
- ✅ **预览模式** - 剪辑前预览要删除的片段，避免误操作
- ✅ **批量处理** - 并行处理多个视频，提高效率
- ✅ **智能边界** - 自动添加缓冲避免生硬剪辑
- ✅ **完整配置** - YAML 配置文件，所有参数可自定义
- ✅ **统计分析** - 语速、停顿、压缩率等详细报告
  - 语速分析（字符/分钟、词/分钟）
  - 停顿统计（次数、频率、最长停顿）
  - 填充词比例分析
  - Top 5 金句展示
- ✅ **增强分析器** - 支持预览、智能边界、可配置规则
- ✅ **进度显示** - 长视频处理时的进度提示

## 📦 安装

### 依赖要求
- Python 3.8+
- FFmpeg
- FunASR

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yzz05220-rgb/video-cutter.git
cd video-cutter/scripts

# 安装 Python 依赖
pip install funasr torch whisper pyyaml openai tqdm
```

## 🎯 快速开始

### 一键处理（推荐）

```bash
# 基础用法
python all_in_one.py video.mp4

# 完整参数
python all_in_one.py video.mp4 \
  --project my_video \
  --remove-silence \
  --gifs 10

# 预览模式
python all_in_one.py video.mp4 --preview
```

### 分步处理

```bash
# 1. 创建项目
python manager.py create my_project

# 2. 转录视频
python transcriber.py input.mp4 transcript.json ./temp

# 3. 分析（带预览）
python analyzer_v2.py transcript.json filter.txt --preview

# 4. 执行剪辑
python clipper.py input.mp4 filter.txt output.mp4

# 5. 检测金句
python golden_quote_detector.py transcript.json -o quotes.json

# 6. 生成 GIF
python gif_generator.py input.mp4 --quotes quotes.json -o gifs/
```

## 📊 使用示例

### 场景1：快速剪辑口播视频
```bash
python all_in_one.py speech.mp4 --remove-silence --gifs 5
```

### 场景2：批量处理课程视频
```bash
python batch_processor.py ./course_videos \
  --pattern "*.mp4" \
  --parallel 3 \
  --gifs 3
```

### 场景3：提取精彩片段做预告
```bash
python golden_quote_detector.py transcript.json -o quotes.json --top 10
python gif_generator.py video.mp4 --quotes quotes.json -o preview_gifs/
```

## ⚙️ 配置

编辑 `config.yaml` 自定义所有参数：

```yaml
# 语气词配置
filler_words:
  - 嗯
  - 啊
  - 哎
  # ... 更多

# 静音配置
silence:
  threshold: 1.0
  enable: true

# 金句检测配置
golden_quotes:
  enable: true
  rules:
    - type: keyword
      keywords: [重要, 核心, 秘密]
    - type: pattern
      patterns: [".*的来说$"]

  # GIF 生成配置
  gif:
    width: 480
    fps: 15
```

详细配置说明请查看 [SKILL.md](SKILL.md)

## 📈 输出示例

```
✅ 处理完成！

📊 统计信息：
  原视频时长：10分47秒
  剪辑后时长：23.6秒 (3.6%)
  文件大小：39.4MB → 1.4MB

🗣️ 语速分析：
  平均语速：234 字/分钟
  停顿次数：47 次

✨ 金句：
  检测到 12 条金句
  平均评分：76.3

📁 输出文件：
  - 视频：output/剪辑后_video.mp4
  - 字幕：output/video.srt
  - GIF：output/gifs/ (10个)
```

## 🛠️ 工具说明

| 工具 | 说明 | 状态 |
|------|------|------|
| `all_in_one.py` | 一键处理（推荐使用） | 🆕 新增 |
| `analyzer_v2.py` | 增强版分析器（预览、智能边界） | 🆕 新增 |
| `golden_quote_detector.py` | 金句检测器 | 🆕 新增 |
| `gif_generator.py` | GIF 生成器 | 🆕 新增 |
| `stats_analyzer.py` | 统计分析工具 | 🆕 新增 |
| `batch_processor.py` | 批量处理器 | 🆕 新增 |
| `config.yaml` | 完整配置文件 | 🆕 新增 |
| `analyzer.py` | 基础分析器 | 原有 |
| `transcriber.py` | 语音转录 | 原有 |
| `clipper.py` | 视频剪辑 | 原有 |
| `manager.py` | 项目管理 | 原有 |
| `subtitler.py` | 字幕生成 | 原有 |

## 🔄 升级记录

### v2.0 - 重大功能升级（本版本）

新增功能：
- 一键处理工作流
- 智能金句检测系统
- GIF 自动生成
- 批量处理支持
- 完整配置系统
- 预览模式
- 统计分析报告
- 智能边界调整

优化改进：
- 增强版分析器
- 更智能的删除规则
- 可配置的参数系统
- 完善的错误处理
- 详细的用户文档

### v1.0 - 基础版本

基础功能：
- FunASR 语音转录
- 语气词/重复/静音检测
- FFmpeg 视频剪辑
- 简单的项目管理

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 许可证

MIT License

## 📜 致谢

### 原始项目

本项目基于 [Ceeon/videocut-skills](https://github.com/Ceeon/videocut-skills) 进行功能扩展。

**原作者**: [Ceeon](https://github.com/Ceeon)

**原始仓库**: https://github.com/Ceeon/videocut-skills

原始项目提供了基础的智能视频剪辑功能，包括 FunASR 语音转录、口误识别、静音检测等核心能力。

### 主要升级贡献

**yzz05220-rgb** - 20+ 项功能升级和优化

在原有基础上新增：
- 一键处理工作流
- 智能金句检测系统
- GIF 自动生成
- 批量处理支持
- 完整配置系统
- 预览模式
- 统计分析报告
- 智能边界调整

### 使用的开源技术

本项目的实现基于以下优秀的开源项目：

- **FunASR** - 阿里巴巴达摩院语音识别工具
- **FFmpeg** - 多媒体处理框架
- **Whisper** - OpenAI 语音识别模型
- **PyTorch** - 深度学习框架

感谢这些开源项目的贡献者！

---

**本仓库**: https://github.com/yzz05220-rgb/video-cutter

**原始仓库**: https://github.com/Ceeon/videocut-skills

**主要升级**: yzz05220-rgb (20+ 项新增功能)
