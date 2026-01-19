# AI 金句分析使用指南

## 🚀 快速开始

### 方式1：自动模式（推荐）

无需配置，系统会自动检测并使用可用的 AI 模型：

```bash
# 只需设置环境变量，其他全自动
export ANTHROPIC_API_KEY="your-key-here"  # 或 OPENAI_API_KEY

# 运行视频剪辑，AI 自动启用
python all_in_one.py video.mp4
```

**自动检测顺序：**
1. 🔹 Anthropic Claude (优先)
2. 🔹 OpenAI GPT
3. 🔹 Ollama 本地模型

### 方式2：指定提供商

编辑 `config.yaml`:

```yaml
golden_quotes:
  rules:
    - type: ai
      enable: true
      provider: anthropic  # 或 openai/ollama
      model: claude-3-5-sonnet-20241022
      api_key: ""  # 留空从环境变量读取
```

## 📋 支持的 AI 提供商

### 1️⃣ Anthropic Claude（推荐）

**优势：** 理解能力强，中文支持好，价格实惠

**支持模型：**
- `claude-3-5-sonnet-20241022` (最新，推荐)
- `claude-3-sonnet-20240229`
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

**配置：**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2️⃣ OpenAI GPT

**支持模型：**
- `gpt-4o` (最新，推荐)
- `gpt-4`
- `gpt-4-turbo`
- `gpt-3.5-turbo` (便宜)

**配置：**
```bash
export OPENAI_API_KEY="sk-..."
```

### 3️⃣ Ollama 本地模型（免费）

**优势：** 完全免费，本地运行，隐私安全

**支持模型：**
- `llama3.1` (推荐)
- `llama3`
- `qwen2`
- 其他 Ollama 支持的模型

**配置：**
```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 拉取模型
ollama pull llama3.1

# 3. 运行 Ollama
ollama serve

# 4. 配置（可选，默认使用 localhost:11434）
# 编辑 config.yaml:
# provider: ollama
# api_base: "http://localhost:11434"
```

## ⚙️ 配置示例

### 示例1：完全自动（默认）

```yaml
golden_quotes:
  rules:
    - type: ai
      enable: auto       # 自动检测
      provider: auto     # 自动选择
      model: auto        # 自动模型
```

### 示例2：使用 Claude

```yaml
golden_quotes:
  rules:
    - type: ai
      enable: true
      provider: anthropic
      model: claude-3-5-sonnet-20241022
      api_key: ""        # 从环境变量读取
      max_quotes: 10     # 识别 10 条金句
```

### 示例3：使用 GPT-4

```yaml
golden_quotes:
  rules:
    - type: ai
      enable: true
      provider: openai
      model: gpt-4o
      max_quotes: 5
```

### 示例4：使用本地 Ollama

```yaml
golden_quotes:
  rules:
    - type: ai
      enable: true
      provider: ollama
      model: llama3.1
      api_base: "http://localhost:11434"
      max_quotes: 5
```

## 💡 高级配置

### 自定义模型优先级

```yaml
golden_quotes:
  rules:
    - type: ai
      enable: auto
      provider: auto
      model_priority:
        - gpt-4o              # 最优先
        - claude-3-5-sonnet
        - gpt-4
        - claude-3-opus
```

### 自定义 API 端点

```yaml
golden_quotes:
  rules:
    - type: ai
      enable: true
      provider: openai
      api_base: "https://your-proxy.com/v1"  # 代理或兼容端点
```

### 超时和重试

```yaml
golden_quotes:
  rules:
    - type: ai
      enable: true
      timeout: 60          # 60 秒超时
      max_quotes: 10
```

## 🔍 检测日志

运行时会显示使用的 AI 模型：

```bash
python all_in_one.py video.mp4

# 输出：
# 🤖 AI 分析规则
# 🔹 使用 Anthropic Claude: claude-3-5-sonnet-20241022
# ✅ Claude 分析完成，识别 5 条金句
```

## 🛠️ 故障排除

### 问题1：AI 分析未启用

**原因：** 没有配置任何 API Key

**解决：**
```bash
export ANTHROPIC_API_KEY="your-key"
# 或
export OPENAI_API_KEY="your-key"
```

### 问题2：连接超时

**原因：** 网络问题或 API 端点不可达

**解决：**
```yaml
timeout: 60  # 增加超时时间
# 或使用代理
api_base: "https://your-proxy.com/v1"
```

### 问题3：模型不可用

**原因：** 模型名称错误或无权限

**解决：**
```yaml
# 检查模型名称是否正确
model: gpt-4o  # 确保拼写正确

# 使用你账户有权访问的模型
model: gpt-3.5-turbo  # 更便宜且有权限
```

### 问题4：Ollama 未运行

**检查：**
```bash
curl http://localhost:11434/api/tags
```

**启动 Ollama：**
```bash
ollama serve
```

## 💰 成本对比

| 提供商 | 模型 | 成本（1M tokens） | 推荐场景 |
|--------|------|------------------|----------|
| Anthropic | Claude 3.5 Sonnet | $3 输入 / $15 输出 | 日常使用（推荐） |
| OpenAI | GPT-4o | $5 输入 / $15 输出 | 高质量需求 |
| OpenAI | GPT-3.5 Turbo | $0.5 输入 / $1.5 输出 | 预算有限 |
| Ollama | Llama 3.1 | **免费** | 本地、隐私 |

## 📝 最佳实践

1. **开发测试**：使用 Ollama 本地模型（免费）
2. **日常使用**：使用 Claude 3.5 Sonnet（性价比高）
3. **高质量需求**：使用 GPT-4o 或 Claude Opus
4. **批量处理**：使用 GPT-3.5 Turbo（便宜）

## 🎯 快速命令

```bash
# 使用 Claude（推荐）
export ANTHROPIC_API_KEY="sk-ant-..."
python all_in_one.py video.mp4 --gifs 10

# 使用 GPT-4
export OPENAI_API_KEY="sk-..."
python all_in_one.py video.mp4

# 使用本地 Ollama（免费）
ollama pull llama3.1 && ollama serve &
python all_in_one.py video.mp4

# 禁用 AI 分析
python all_in_one.py video.mp4  # config.yaml 中 enable: false
```

---

**提示：** 默认 `enable: auto` 模式即可，系统会自动选择最合适的 AI 模型！
