# Video Cutter Skill - 完整工作流程

## 📋 目录结构

```
video-cutter/
├── scripts/
│   ├── transcriber.py          # 转录器（FunASR）
│   ├── analyzer.py              # 基础分析器（简单规则）
│   ├── analyzer_complete.py     # 完整分析器（推荐使用）✨
│   ├── clipper.py               # 剪辑器（FFmpeg）
│   ├── subtitler.py             # 字幕生成器
│   ├── all_in_one.py            # 一键处理脚本
│   ├── gif_generator.py         # GIF生成器
│   ├── golden_quote_detector.py # 金句检测器
│   ├── stats_analyzer.py        # 统计分析器
│   ├── batch_processor.py       # 批量处理
│   ├── manager.py               # 项目管理
│   └── config.yaml              # 配置文件
├── SKILL.md                     # Skill说明文档
└── CHANGELOG.md                 # 更新日志
```

---

## 🎬 完整工作流程

### 方式1：一键处理（推荐）⭐

```bash
cd scripts
python all_in_one.py "视频文件.mp4"
```

**自动完成**：
1. 转录视频（FunASR）
2. 分析语气词和重复
3. 执行剪辑
4. 生成字幕
5. 检测金句
6. 生成统计报告

---

### 方式2：分步处理

#### 步骤1：转录视频

```bash
cd scripts
python transcriber.py "视频.mp4" "transcript.json" "./temp"
```

**输出**：`transcript.json`（包含每个字的时间戳）

---

#### 步骤2：分析并生成剪辑方案

**基础分析器**（简单规则）：
```bash
python analyzer.py "transcript.json" "filter.txt"
```

**完整分析器**（推荐，包含智能判断）✨：
```bash
python analyzer_complete.py "transcript.json" "filter.txt"
```

**区别**：
- `analyzer.py`：简单删除config.yaml中列出的所有语气词
- `analyzer_complete.py`：智能上下文判断 + 使用config.yaml完整规则

**输出**：`filter.txt`（FFmpeg滤镜脚本）

---

#### 步骤3：执行剪辑

```bash
python clipper.py "原视频.mp4" "filter.txt" "剪辑后_视频.mp4"
```

**输出**：`剪辑后_视频.mp4`

---

#### 步骤4：（可选）生成字幕

```bash
python subtitler.py "剪辑后_视频.mp4" --srt "字幕.srt"
```

---

### 方式3：使用项目管理

```bash
# 创建项目
python manager.py create "我的视频"

# 视频放入项目目录后，一键处理
python all_in_one.py "视频.mp4" --project "我的视频"
```

---

## 🔧 配置文件说明

`config.yaml` 包含所有可配置参数：

### 1. 语气词列表
```yaml
filler_words:
  - 嗯
  - 啊
  - 呃
  - 嗯
  - 那个
  - 然后
  - 就是
  # ... 等23个
```

### 2. 静音检测
```yaml
silence:
  threshold: 1.0   # 删除≥1秒的静音
  enable: true     # 是否启用
```

### 3. 智能边界
```yaml
buffer:
  before: 0.05     # 删除前保留50ms
  after: 0.05      # 删除后保留50ms
```

### 4. 高级功能
```yaml
advanced:
  custom_rules:    # 自定义删除规则
  smart_suggestions:  # 智能建议
```

---

## 📊 分析器对比

| 分析器 | 特点 | 使用场景 |
|--------|------|----------|
| **analyzer.py** | 简单规则 | 快速处理，不介意误删 |
| **analyzer_complete.py** ✨ | 智能判断 | 推荐使用，精准删除 |

---

## 🎯 核心功能

### 1. 转录器（transcriber.py）
- 使用 FunASR 进行中文语音识别
- 生成带时间戳的逐字转录
- 支持长视频分段处理

### 2. 分析器（analyzer_complete.py）
- 使用 config.yaml 的完整规则
- 智能上下文判断（区分有意义语气词）
- 重复字检测
- 可选LLM分析（领域识别、错别字纠正）

### 3. 剪辑器（clipper.py）
- 使用 FFmpeg 精确剪辑
- 音频交叉淡化（50ms淡入淡出）
- 自动合并片段

### 4. 金句检测（golden_quote_detector.py）
- 关键词匹配
- 句式模式识别
- AI智能分析（可选）

### 5. 统计分析（stats_analyzer.py）
- 语速分析
- 停顿统计
- 压缩率计算
- 生成详细报告

---

## 🚀 快速开始

### 最简单的用法

```bash
# 1. 进入脚本目录
cd C:\Users\无我\.claude\skills\video-cutter\scripts

# 2. 放置视频到当前目录

# 3. 一键处理
python all_in_one.py "你的视频.mp4"
```

### 输出文件

- ✅ 剪辑后的视频
- ✅ 字幕文件（.srt）
- ✅ 统计报告（.json）
- ✅ 金句列表（.json）
- ✅ GIF预览（可选）

---

## ⚙️ 高级用法

### 自定义配置

1. 复制 `config.yaml`
2. 修改语气词列表
3. 使用 `--config` 参数指定：
```bash
python analyzer_complete.py "transcript.json" "filter.txt" --config "my_config.yaml"
```

### 批量处理

```bash
python batch_processor.py "视频文件夹/" --pattern "*.mp4" --parallel 3
```

### 只分析不剪辑（预览模式）

```bash
python all_in_one.py "视频.mp4" --preview
```

---

## 📌 关键改进总结

### v2.0 更新（2025-01-20）

#### 新增文件
1. **analyzer_complete.py** - 完整分析器
   - 整合config.yaml所有规则
   - 智能上下文判断
   - LLM领域识别和错别字纠正

#### 删除文件（临时测试版本）
- analyzer_fixed.py
- analyzer_llm.py
- analyzer_llm_smart.py
- analyzer_precision.py
- analyzer_smart.py
- analyzer_ultimate.py
- analyzer_v2.py

#### 核心改进
- ✅ 使用config.yaml的完整语气词列表（23个类型）
- ✅ 智能上下文判断（区分有意义语气词）
- ✅ 69个语气词检测（vs 之前的23个）
- ✅ 音频交叉淡化（50ms）
- ✅ 重复字检测（29个）
- ✅ 可选LLM分析

---

## 📝 使用建议

### 推荐工作流

**日常使用**：
```bash
python all_in_one.py "视频.mp4"
```

**需要精准控制**：
```bash
# 1. 转录
python transcriber.py "视频.mp4" "transcript.json" "./temp"

# 2. 分析（查看详细日志）
python analyzer_complete.py "transcript.json" "filter.txt"

# 3. 预览filter.txt，确认无误后
# 4. 剪辑
python clipper.py "视频.mp4" "filter.txt" "输出.mp4"
```

**需要自定义规则**：
```bash
# 1. 复制配置
cp config.yaml my_config.yaml

# 2. 编辑my_config.yaml，修改filler_words等

# 3. 使用自定义配置
python all_in_one.py "视频.mp4" --config my_config.yaml
```

---

## ❓ 常见问题

**Q: 删除太多了怎么办？**
A: 编辑 config.yaml，删除不必要的语气词，或使用 analyzer.py

**Q: 想保留某些语气词？**
A: 在 config.yaml 的 filler_words 列表中删除它们

**Q: 可以只删除停顿，不删除语气词吗？**
A: 可以，设置 silence.enable: true，并将 filler_words 清空

**Q: 如何查看详细的分析过程？**
A: analyzer_complete.py 会输出详细的删除日志

---

## 🔗 相关文件

- **SKILL.md** - Skill完整说明
- **CHANGELOG.md** - 更新日志
- **AUTHORS.md** - 作者信息

---

## 📧 反馈

如有问题或建议，请在GitHub提出：
https://github.com/yourusername/video-cutter
