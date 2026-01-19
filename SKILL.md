---
name: video-cutter
description: 智能口播视频剪辑工具。自动转录语音、识别语气词/重复字/静音、智能剪辑、金句检测、GIF生成。触发词：剪辑视频、视频去废话、口播剪辑、视频剪辑、智能剪辑、金句提取、视频GIF
---

# 视频剪辑技能 (Video Cutter)

智能口播视频剪辑工具，使用AI自动识别并删除视频中的语气词、重复字、静音段落，快速生成精简版本。**新功能：一键处理、金句检测、GIF生成、统计分析、批量处理。**

## 如何工作

1. **转录视频** - 使用FunASR进行逐字语音识别，生成带时间戳的转录文本
2. **智能分析** - 自动识别并标记需要删除的片段：
   - 语气词：嗯、啊、哎、诶、呃、额、唉、哦、噢、呀、欸、那个、然后、就是
   - 重复字：连续重复的字符（如"好的好的"、"受受了"）
   - 静音：≥1秒的静音段落（可选）
   - 智能边界调整：自动添加缓冲，避免生硬剪辑
3. **执行剪辑** - 使用FFmpeg精确剪辑并拼接保留片段
4. **金句检测** 🆕 - 智能识别精彩片段（关键词、句式模式、AI分析）
5. **GIF生成** 🆕 - 自动生成金句的 GIF 预览
6. **统计分析** 🆕 - 生成详细的剪辑报告（语速、停顿、压缩率等）

## 使用方法

### 🚀 一键处理（推荐）

**最简单的方式 - 自动完成所有步骤：**

```bash
# 基础用法
python all_in_one.py <视频文件>.mp4

# 完整参数
python all_in_one.py <视频文件>.mp4 \
  --project my_video \      # 项目名称
  --remove-silence \         # 删除静音
  --gifs 10 \                # 生成 10 个金句 GIF
  --config config.yaml       # 自定义配置

# 预览模式（不实际剪辑）
python all_in_one.py <视频文件>.mp4 --preview
```

**输出：**
- ✅ 剪辑后的视频
- ✅ 字幕文件（.srt）
- ✅ 金句 JSON 文件
- ✅ 金句 GIF 文件夹
- ✅ 统计报告（.json）

### 传统分步处理

```bash
# 1. 创建项目
python manager.py create <项目名称>

# 2. 将视频放入项目的 source 目录

# 3. 转录视频
python transcriber.py "<项目路径>/source/<视频>.mp4" "<项目路径>/temp/transcript.json" "<项目路径>/temp"

# 4. 分析并生成剪辑方案（增强版）
python analyzer_v2.py "<项目路径>/temp/transcript.json" "<项目路径>/temp/filter.txt" --remove-silence --preview

# 5. 执行剪辑
python clipper.py "<项目路径>/source/<视频>.mp4" "<项目路径>/temp/filter.txt" "<项目路径>/output/剪辑后_<视频>.mp4"
```

### 单独使用工具

**transcriber.py**（转录）
```bash
python transcriber.py <输入视频> <输出json> <临时目录>
```

**analyzer.py**（分析）
```bash
python analyzer.py <转录json> <输出filter> [--remove-silence]
```

**clipper.py**（剪辑）
```bash
python clipper.py <输入视频> <filter文件> <输出视频>
```

**subtitler.py**（字幕）
```bash
python subtitler.py <输入视频> <输出视频> [--srt 字幕路径]
```

**manager.py**（项目管理）
```bash
python manager.py create <项目名称>
python manager.py list
```

### 🆕 新增工具

**all_in_one.py**（一键处理）
```bash
python all_in_one.py <视频文件> [--project <名称>] [--remove-silence] [--gifs N] [--preview]
```

**analyzer_v2.py**（增强分析器）
```bash
python analyzer_v2.py <转录json> <输出filter> [--remove-silence] [--preview] [--config config.yaml]
```
- 支持预览模式（不实际剪辑）
- 智能边界调整（避免生硬）
- 可配置的删除规则
- 自动过滤过短片段

**golden_quote_detector.py**（金句检测器）
```bash
python golden_quote_detector.py <转录json> -o golden_quotes.json [--top N]
```
检测规则：
- 关键词匹配：重要、核心、秘密、必须知道、一定要...
- 句式模式：总的来说、一句话、重点、本质上...
- 长度和复杂度：15-100 字、5+ 词
- AI 分析：使用当前对话的 LLM（在 Skills 环境中自动启用）

**gif_generator.py**（GIF 生成器）
```bash
# 从金句文件生成
python gif_generator.py <视频文件> --quotes golden_quotes.json -o gifs/

# 从时间范围生成
python gif_generator.py <视频文件> --time "10-15,20-25" -o clips/

# 自动检测并生成
python gif_generator.py <视频文件> --auto <转录json> -o gifs/
```

**stats_analyzer.py**（统计分析）
```bash
python stats_analyzer.py \
  --original <原视频> \
  --output <剪辑后视频> \
  --transcript <转录json> \
  --quotes <金句json> \
  --report stats_report.json
```

**batch_processor.py**（批量处理）
```bash
python batch_processor.py <视频目录> \
  --pattern "*.mp4" \
  --parallel 3 \
  --remove-silence \
  --gifs 5
```

## 工作目录结构

```
VideoProjects/
├── Tools/           # 工具脚本
└── Projects/        # 项目目录
    └── <项目名称>/
        ├── source/  # 原视频
        ├── output/  # 输出视频
        └── temp/    # 临时文件（转录、filter等）
```

## 输出文件

**transcript.json** - 转录结果
```json
{
  "video_path": "视频路径",
  "duration_ms": 646791,
  "segments": [
    {"char": "好", "start": 8160, "end": 8200},
    {"char": "的", "start": 8200, "end": 8240}
  ]
}
```

**filter.txt** - FFmpeg剪辑滤镜
```
[0:v]trim=start=8.16:end=8.81,setpts=PTS-STARTPTS[v0];
[0:a]atrim=start=8.16:end=8.81,asetpts=PTS-STARTPTS[a0];
...
[v0][a0][v1][a1]...concat=n=28:v=1:a=1[outv][outa]
```

**golden_quotes.json** - 金句检测结果
```json
{
  "video_path": "视频路径",
  "total_quotes": 12,
  "quotes": [
    {
      "text": "这个知识点非常重要，大家一定要记住",
      "start_ms": 12345,
      "end_ms": 15789,
      "score": 88.5,
      "reason": "包含关键词「重要」",
      "timestamp": "00:12"
    }
  ]
}
```

**stats_report.json** - 统计报告
```json
{
  "original_duration": 646.8,
  "output_duration": 23.6,
  "duration_reduction": 96.4,
  "speech_rate_chars_per_min": 234,
  "total_quotes": 12,
  "avg_quote_score": 76.3
}
```

## 🆕 配置文件

所有参数都可以通过 `config.yaml` 自定义：

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

# 智能边界配置
buffer:
  before: 0.05  # 删除前保留 50ms
  after: 0.05   # 删除后保留 50ms

# 金句检测配置
golden_quotes:
  enable: true
  rules:
    - type: keyword
      keywords: [重要, 核心, 秘密, 必须知道]
    - type: pattern
      patterns: [".*的来说$", ".*一句话.*"]
    - type: ai
      enable: true  # AI 分析（使用当前对话 LLM）
      max_quotes: 5

  # GIF 生成配置
  gif:
    width: 480
    fps: 15
    start_offset: -0.5
    end_offset: 0.5

# 输出配置
output:
  quality: medium  # low/medium/high
  generate_srt: true
  extract_audio: false
```

**注意：** AI 金句分析会自动使用当前对话的 LLM，无需额外配置 API Key。

## 向用户展示结果

剪辑完成后，展示：
- ✅ 原视频时长 vs 剪辑后时长
- ✅ 文件大小对比
- ✅ 删除片段数量（语气词、重复、静音）
- ✅ 语速分析（字符/分钟）
- ✅ 停顿统计（次数、平均时长）
- ✅ 检测到的金句数量及 Top 5
- ✅ 输出文件路径

示例：
```
✅ 处理完成！

📊 统计信息：
  原视频时长：10分47秒
  剪辑后时长：23.6秒 (3.6%)
  文件大小：39.4MB → 1.4MB
  删除片段：36处

🗣️ 语速分析：
  平均语速：234 字/分钟
  停顿次数：47 次
  平均停顿：1.2 秒

✨ 金句：
  检测到 12 条金句
  平均评分：76.3

  🏆 Top 3 金句：
    1. [00:15] 这个知识点非常重要，大家一定要记住
       💯 88.5 | 包含关键词「重要」
    2. [01:23] 简单来说，核心就是这三点
       💯 82.0 | 匹配句式模式
    3. [02:45] 总结一下，成功的关键在于坚持
       💯 79.5 | 包含关键词「总结」「关键」

📁 输出文件：
  - 视频：VideoProjects/Projects/spa_video/output/剪辑后_视频.mp4
  - 字幕：VideoProjects/Projects/spa_video/output/视频.srt
  - 金句：VideoProjects/Projects/spa_video/temp/golden_quotes.json
  - GIF：VideoProjects/Projects/spa_video/output/gifs/ (10个)
  - 统计：VideoProjects/Projects/spa_video/temp/stats_report.json
```

## 依赖

### 必需
- FunASR（语音识别模型）
- FFmpeg（视频处理）
- Python 3.8+
- 必要的Python包：`funasr`, `torch`, `whisper`

### 可选
- `pyyaml` - 配置文件支持
- `openai` - AI 金句分析
- `tqdm` - 进度条显示

安装依赖：
```bash
pip install funasr torch whisper pyyaml openai tqdm
```

## 高级用法

### 预览模式
在实际剪辑前预览将要删除的片段：
```bash
python all_in_one.py video.mp4 --preview
```

### 自定义金句规则
编辑 `config.yaml` 添加自己的关键词和模式：
```yaml
golden_quotes:
  rules:
    - type: keyword
      keywords:
        - 你的领域关键词
        - 重要术语
    - type: pattern
      patterns:
        - ".*你的正则模式.*"
```

### 批量处理文件夹
```bash
python batch_processor.py /path/to/videos \
  --pattern "*.mp4" \
  --parallel 5 \
  --gifs 3
```

### 生成多种质量版本
编辑 `config.yaml`：
```yaml
output:
  formats:
    - mp4
    - webm
  quality: medium  # 生成 medium 质量
```

### 金句检测 AI 分析

金句检测会自动使用当前对话的 LLM 进行智能分析，无需额外配置 API。

```yaml
golden_quotes:
  rules:
    - type: ai
      enable: true  # 启用 AI 分析
      max_quotes: 5  # 识别金句数量
```

### 提取音频
```yaml
output:
  extract_audio: true
  audio_format: mp3
```

## 常见问题

**Q: 转录结果为空？**
A: 可能视频没有中文语音内容，或音频流损坏。使用 `ffprobe` 检查音频流。

**Q: 剪辑太激进？**
A: 不使用 `--remove-silence` 参数可保留静音段落，或修改 `config.yaml` 中的 `filler_words` 列表。

**Q: 想保留某些语气词？**
A: 编辑 `config.yaml` 中的 `filler_words` 列表，删除不需要识别的词。

**Q: 编码错误（Windows）？**
A: 脚本已自动设置UTF-8编码，确保控制台支持中文显示。

**Q: 金句检测不准确？**
A: 编辑 `config.yaml` 调整金句检测规则，添加你领域的关键词和模式。

**Q: GIF 生成太慢？**
A: 减少 `gif.width` 和 `gif.fps`，或降低生成数量。

**Q: 批量处理内存不足？**
A: 降低 `--parallel` 参数，减少并行处理数量。

**Q: 配置文件不生效？**
A: 确保安装了 `pyyaml`，并使用 `--config` 参数指定配置文件路径。

## 🎯 使用场景

### 场景1：快速剪辑口播视频
```bash
python all_in_one.py speech.mp4 --remove-silence --gifs 5
```

### 场景2：预览后决定
```bash
# 先预览
python all_in_one.py long_video.mp4 --preview

# 满意后再执行
python all_in_one.py long_video.mp4 --remove-silence
```

### 场景3：批量处理课程视频
```bash
python batch_processor.py ./course_videos \
  --pattern "lesson_*.mp4" \
  --parallel 3 \
  --remove-silence
```

### 场景4：提取精彩片段做预告
```bash
# 1. 先转录
python transcriber.py video.mp4 transcript.json ./temp

# 2. 检测金句
python golden_quote_detector.py transcript.json -o quotes.json --top 10

# 3. 生成 GIF
python gif_generator.py video.mp4 --quotes quotes.json -o preview_gifs/
```

### 场景5：生成详细的剪辑报告
```bash
python all_in_one.py video.mp4

# 查看统计报告
cat ./VideoProjects/Projects/*/temp/stats_report.json
```
