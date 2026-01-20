# Video Cutter - 小白安装教程

**最后更新**: 2025-01-20
**版本**: v2.0
**适用系统**: Windows 10/11, macOS, Linux

---

## 📋 目录

1. [环境要求](#环境要求)
2. [第一步：安装 Python](#第一步安装-python)
3. [第二步：安装 FFmpeg](#第二步安装-ffmpeg)
4. [第三步：克隆项目](#第三步克隆项目)
5. [第四步：安装依赖](#第四步安装依赖)
6. [第五步：下载 FunASR 模型](#第五步下载-funasr-模型)
7. [第六步：测试运行](#第六步测试运行)
8. [常见问题](#常见问题)
9. [使用教程](#使用教程)

---

## 环境要求

- **Python**: 3.8 或更高版本
- **FFmpeg**: 4.0 或更高版本
- **磁盘空间**: 至少 5GB（用于模型缓存）
- **内存**: 建议 8GB 以上

---

## 第一步：安装 Python

### Windows 用户

#### 方法1：从官网下载（推荐）

1. 访问 Python 官网：https://www.python.org/downloads/
2. 下载 **Python 3.12** 或更高版本
3. 安装时**务必勾选**：
   - ✅ **"Add Python to PATH"**（重要！）
   - ✅ **"Install for all users"**（可选）

4. 点击 "Install Now" 完成安装

#### 方法2：使用微软商店

1. 打开 Microsoft Store
2. 搜索 "Python 3.12"
3. 点击 "安装"

### 验证安装

打开命令提示符（CMD）或 PowerShell，输入：

```bash
python --version
```

应该显示类似：`Python 3.12.0`

---

## 第二步：安装 FFmpeg

### Windows 用户

#### 方法1：使用 chocolatey（最简单）

1. 以管理员身份打开 PowerShell
2. 安装 chocolatey（如果未安装）：
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol - bor 2.0, 2.0, 2, 1; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```
3. 安装 FFmpeg：
   ```powershell
   choco install ffmpeg
   ```

#### 方法2：手动下载

1. 访问：https://www.gyan.dev/ffmpeg/builds/
2. 下载最新版本的 FFmpeg（shared + static 版本）
3. 解压到 `C:\ffmpeg`
4. 将 `C:\ffmpeg\bin` 添加到系统 PATH 环境变量

### macOS 用户

```bash
brew install ffmpeg
```

### Linux 用户

```bash
sudo apt update
sudo apt install ffmpeg
```

### 验证安装

```bash
ffmpeg -version
```

应该显示 FFmpeg 版本信息。

---

## 第三步：克隆项目

打开命令行（Windows: CMD 或 PowerShell，macOS/Linux: Terminal），执行：

```bash
# 克隆项目到本地
git clone https://github.com/yzz05220-rgb/video-cutter.git

# 进入项目目录
cd video-cutter
```

---

## 第四步：安装依赖

### 1. 升级 pip（重要！）

```bash
python -m pip install --upgrade pip
```

### 2. 安装 Python 依赖

```bash
cd scripts
pip install -r requirements.txt
```

**如果没有 requirements.txt**，手动安装核心依赖：

```bash
pip install torch torchvision torchaudio
pip install funasr
pip install pyyaml
pip install tqdm
```

### Windows 用户额外安装

如果遇到编译错误，安装预编译包：

```bash
pip install funasr onnxruntime
```

---

## 第五步：下载 FunASR 模型

### 方法1：自动下载（推荐）

第一次运行时会自动下载模型到缓存目录：

**Windows 缓存位置**：
```
C:\Users\<你的用户名>\.cache\modelscope
```

**首次运行时会自动下载**：
- `speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch` (~400MB)
- `speech_fsmn_vad_zh-cn-16k-common-pytorch` (~10MB)
- `punc_ct-transformer_cn-en-common-vocab471067-large` (~50MB)

**预计下载时间**：根据网速，约 5-20 分钟

### 方法2：手动下载

如果自动下载失败，访问 ModelScope：

1. 访问：https://www.modelscope.cn/
2. 搜索并下载：
   - `paraformer-zh` (语音识别模型)
   - `fsmn-vad` (语音活动检测)
   - `ct-punc` (标点符号模型)

3. 解压到缓存目录

---

## 第六步：测试运行

### 1. 准备测试视频

将一个测试视频文件（如 `test.mp4`）放在项目根目录或任意位置。

### 2. 一键处理测试

```bash
cd scripts
python all_in_one.py "../../test.mp4"
```

### 3. 查看结果

处理完成后，会在 `output/` 目录生成：

```
VideoProjects/Projects/test_mp4/
├── source/
│   └── test.mp4
├── output/
│   └── 剪辑后_test.mp4
└── temp/
    ├── transcript.json
    └── filter.txt
```

---

## 使用教程

### 方式1：一键处理（最简单）⭐

```bash
cd scripts
python all_in_one.py "你的视频.mp4"
```

**自动完成**：
- ✅ 转录视频
- ✅ 分析语气词
- ✅ 执行剪辑
- ✅ 生成字幕
- ✅ 检测金句
- ✅ 生成统计

---

### 方式2：分步处理（更灵活）

```bash
cd scripts

# 1. 转录视频
python transcriber.py "视频.mp4" "transcript.json" "./temp"

# 2. 分析（推荐使用完整分析器）
python analyzer_complete.py "transcript.json" "filter.txt"

# 3. 剪辑
python clipper.py "视频.mp4" "filter.txt" "剪辑后_视频.mp4"
```

---

### 方式3：自定义配置

```bash
# 1. 复制配置文件
cp config.yaml my_config.yaml

# 2. 用文本编辑器打开 my_config.yaml
#    - 修改 filler_words 列表
#    - 调整 silence 参数
#    - 自定义 golden_quotes 规则

# 3. 使用自定义配置
python all_in_one.py "视频.mp4" --config my_config.yaml
```

---

## 常见问题

### Q1: 提示 "python 不是内部或外部命令"

**A**: Python 没有添加到 PATH 环境变量

**解决方法**:
1. 重新安装 Python，确保勾选 "Add Python to PATH"
2. 或手动添加 Python 到 PATH：
   - Windows: `C:\Users\<用户名>\AppData\Local\Programs\Python\Python312\Scripts`
   - 添加到：系统属性 → 环境变量 → Path

---

### Q2: 提示 "ffmpeg 不是内部或外部命令"

**A**: FFmpeg 没有安装或没有添加到 PATH

**解决方法**:
1. 重新安装 FFmpeg（见第二步）
2. 或手动添加 FFmpeg 到 PATH：
   - Windows: `C:\ffmpeg\bin`
   - 添加到：系统属性 → 环境变量 → Path

---

### Q3: 提示 "No module named 'funasr'"

**A**: Python 依赖没有安装

**解决方法**:
```bash
pip install funasr
```

---

### Q4: 模型下载失败或很慢

**A**: ModelScope 连接问题

**解决方法**:
1. 使用 VPN 或代理
2. 手动下载模型（见第五步方法2）
3. 设置镜像源（如果可用）

---

### Q5: 提示 "UnicodeEncodeError"

**A**: Windows 控制台编码问题

**解决方法**:
脚本已自动处理 UTF-8 编码，如果仍有问题：
```bash
chcp 65001  # 在 CMD 中执行
```

---

### Q6: 剪辑后的视频没有声音

**A**: FFmpeg 音频编码问题

**解决方法**:
确保 FFmpeg 版本支持 AAC 编码：
```bash
ffmpeg -version  # 检查版本
```

---

### Q7: 内存不足错误

**A**: 模型加载占用大量内存

**解决方法**:
1. 关闭其他程序释放内存
2. 使用更小的模型（修改配置）
3. 增加虚拟内存（Windows）

---

### Q8: 转录速度很慢

**A**: 使用 CPU 处理视频

**正常情况**:
- 实时处理的 1-2 倍时间
- 10分钟视频约需 10-20 分钟

**优化**:
- 使用 GPU 版本（如果有显卡）
- 降低采样率

---

## 🎯 进阶使用

### 批量处理文件夹中的所有视频

```bash
python batch_processor.py "视频文件夹/" --pattern "*.mp4"
```

### 只生成金句 GIF

```bash
# 1. 先转录
python transcriber.py "视频.mp4" "transcript.json"

# 2. 生成金句 GIF
python gif_generator.py "视频.mp4" --auto "transcript.json" -o "gifs/" --max 5
```

### 查看详细统计

```bash
python stats_analyzer.py \
  --original "原视频.mp4" \
  --output "剪辑后.mp4" \
  --transcript "transcript.json" \
  --report "统计报告.json"
```

---

## 📂 项目结构说明

```
video-cutter/
├── scripts/               # 所有脚本
│   ├── transcriber.py    # 转录器
│   ├── analyzer.py       # 基础分析器
│   ├── analyzer_complete.py # 完整分析器⭐
│   ├── clipper.py        # 剪辑器
│   ├── all_in_one.py     # 一键处理
│   ├── gif_generator.py  # GIF生成器
│   └── config.yaml       # 配置文件
├── WORKFLOW.md           # 工作流程文档
└── INSTALL.md            # 本安装教程
```

---

## 💡 使用技巧

### 技巧1：快速测试

测试时可以先用短视频（1-2分钟）：
```bash
python all_in_one.py "test_short.mp4"
```

### 技巧2：只分析不剪辑（预览）

```bash
python all_in_one.py "视频.mp4" --preview
```

### 技巧3：调整删除强度

编辑 `config.yaml`：

```yaml
# 保守删除（只删除明显停顿）
filler_words:
  - 嗯
  - 呃
  - 嗯

# 激进删除（删除更多语气词）
filler_words:
  - 嗯
  - 啊
  - 呃
  - 额
  - 哎
  - 然后
  - 就是
  - 那个
```

### 技巧4：保留静音

```yaml
silence:
  threshold: 1.0
  enable: false  # 设为 false 不删除静音
```

---

## 🔧 配置文件详解

### config.yaml 主要参数

```yaml
# 语气词列表
filler_words:
  - 嗯、啊、呃...  # 添加更多：- 哎呀

# 静音检测
silence:
  threshold: 1.0   # 删除 >= 1秒的静音
  enable: true     # 是否删除静音

# 智能边界
buffer:
  before: 0.05     # 删除前保留 50ms
  after: 0.05      # 删除后保留 50ms

# 金句检测
golden_quotes:
  enable: true
  rules:
    - type: keyword
      keywords:
        - 重要
        - 关键
```

---

## 📞 获取帮助

### GitHub Issues

提交问题：https://github.com/yzz05220-rgb/video-cutter/issues

### 文档参考

- **完整工作流程**: [WORKFLOW.md](WORKFLOW.md)
- **技能说明**: [SKILL.md](SKILL.md)
- **更新日志**: [CHANGELOG.md](CHANGELOG.md)

---

## ✅ 安装检查清单

完成以下步骤确认安装成功：

- [ ] Python 3.8+ 已安装（`python --version`）
- [ ] FFmpeg 已安装（`ffmpeg -version`）
- [ ] 项目已克隆（`cd video-cutter`）
- [ ] 依赖已安装（`pip list | grep funasr`）
- [ ] FunASR 模型已下载（首次运行时自动）
- [ ] 测试视频处理成功（`python all_in_one.py test.mp4`）

---

## 🎉 开始使用

安装完成后，就可以开始使用视频剪辑工具了！

**推荐新手用法**：
```bash
cd video-cutter/scripts
python all_in_one.py "你的第一个视频.mp4"
```

祝使用愉快！
