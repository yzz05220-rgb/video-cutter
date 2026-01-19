# 🎬 智能视频剪辑工具 (Video Cutter)

> 自动转录语音、智能识别语气词/重复/静音、一键剪辑、金句检测、GIF生成

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 特性

### 🚀 核心功能
- **自动语音识别** - 使用 FunASR 进行逐字转录
- **智能剪辑** - 自动识别并删除语气词、重复字、静音段落
- **金句检测** - 智能识别精彩片段（关键词、句式、AI分析）
- **GIF生成** - 自动生成金句的 GIF 预览
- **统计分析** - 语速、停顿、压缩率等详细报告

### 🆕 新增功能
- ✅ **一键处理** - 自动化完整工作流
- ✅ **预览模式** - 剪辑前预览要删除的片段
- ✅ **批量处理** - 并行处理多个视频
- ✅ **智能边界** - 自动添加缓冲避免生硬剪辑
- ✅ **可配置** - 完整的 YAML 配置文件
- ✅ **AI分析** - 可选的 GPT-4 金句评分

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

| 工具 | 说明 |
|------|------|
| `all_in_one.py` | 一键处理（推荐） |
| `analyzer_v2.py` | 增强版分析器 |
| `golden_quote_detector.py` | 金句检测器 |
| `gif_generator.py` | GIF 生成器 |
| `stats_analyzer.py` | 统计分析工具 |
| `batch_processor.py` | 批量处理器 |
| `transcriber.py` | 语音转录 |
| `clipper.py` | 视频剪辑 |

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 许可证

MIT License

## 🙏 致谢

- [FunASR](https://github.com/alibaba-damo-academy/FunASR) - 语音识别
- [FFmpeg](https://ffmpeg.org/) - 视频处理
- [Whisper](https://github.com/openai/whisper) - 字幕生成

---

**链接**: [GitHub Repository](https://github.com/yzz05220-rgb/video-cutter)
