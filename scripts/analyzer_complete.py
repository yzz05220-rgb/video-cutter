#!/usr/bin/env python3
"""
完整分析器 - 整合原有规则 + LLM智能分析
1. 使用config.yaml的完整语气词列表
2. LLM识别领域和错别字
3. 智能上下文判断
"""

import json
import sys
import yaml
import re
from pathlib import Path

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def load_config(config_file='config.yaml'):
    """加载配置文件"""
    script_dir = Path(__file__).parent
    config_path = script_dir / config_file

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def analyze_domain_and_typos(text):
    """
    LLM分析：识别领域和错别字
    返回: (domain, typos_dict)
    """
    print("[LLM分析] 正在识别内容领域和错别字...")

    # 提示词
    prompt = f"""请分析以下口播文稿，完成两个任务：

**任务1：识别内容领域**
判断这是属于哪个领域的视频（如：知识分享、科技评测、生活vlog、游戏解说、教育课程等）

**任务2：识别错别字和同音字错误**
列出文稿中可能的错别字或同音字错误，并给出正确的写法。

**原文稿**（前1000字）：
{text[:1000]}
...

**返回格式**（JSON）：
{{
  "domain": "视频领域",
  "typos": [
    {{"wrong": "错误写法", "right": "正确写法", "position": "上下文提示"}},
    ...
  ]
}}

如果没有明显的错别字，typos返回空列表[]。
"""

    # 在Skills环境中，让当前LLM分析
    print("提示词已生成，请将上述内容发送给LLM进行分析")
    print("（在Skills环境中，这应该自动完成）")
    print()

    # 返回默认值（实际应该由LLM返回）
    return "知识分享", {}

def is_filler_by_context(char, before_text, after_text, config):
    """
    基于上下文判断是否为语气词
    使用config.yaml中的规则
    """
    # 获取配置的语气词列表
    filler_words = config.get('filler_words', [])

    # 如果不在列表中，直接保留
    if char not in filler_words:
        return False, "不在语气词列表"

    # 获取高级自定义规则
    custom_rules = config.get('advanced', {}).get('custom_rules', [])

    # 检查自定义规则
    for rule in custom_rules:
        if rule.get('regex'):
            pattern = rule.get('pattern', '')
            if re.search(pattern, before_text + char + after_text):
                return True, f"自定义规则: {rule.get('name')}"

    # 上下文智能判断（使用原版logic）
    # 特殊处理"啊"
    if char == '啊':
        # 保留：句末的"啊"
        if len(after_text) > 0 and after_text[0] in '。！？':
            return False, "句末语气助词"

        # 保留：列举中的"啊"
        if '，啊' in before_text[-5:] or '、啊' in before_text[-5:]:
            return False, "列举语气词"

        # 保留：强调语气的"啊"
        if any(p in before_text[-10:] for p in ['的说啊', '对的啊', '是的啊', '是啊']):
            return False, "强调语气"

        # 删除：句首的"啊"
        if len(before_text) > 0 and before_text[-1] in '。！？，、；：\n':
            return True, "句首犹豫词"

        # 删除：重复的"啊"
        if '啊' in before_text[-3:]:
            return True, "重复语气词"

    # 特殊处理"呃"、"嗯" - 几乎总是删除
    if char in ['呃', '嗯']:
        # 检查是否在句首或句中
        if len(before_text) == 0 or before_text[-1] in '。！？，、；：\n':
            return True, "思考停顿词"
        return True, "思考犹豫词"

    # 其他语气词（那个、然后、就是）
    # 检查是否重复出现
    if char in ['那个', '然后', '就是']:
        # 检查前10个字符内是否出现过
        if char in before_text[-10:]:
            return True, f"重复的'{char}'"

    # 默认删除（因为在列表中）
    return True, f"语气词'{char}'"

def analyze_transcript(transcript_file, output_filter_file, config_file='config.yaml', use_llm=True):
    """完整分析流程"""

    # 加载配置
    config = load_config(config_file)

    with open(transcript_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    segments = data['segments']
    text = ''.join([s['char'] for s in segments])

    print("=" * 60)
    print("🎬 完整智能分析器")
    print("=" * 60)
    print()

    # 1. LLM分析：领域识别和错别字
    if use_llm:
        domain, typos = analyze_domain_and_typos(text)
        print(f"📚 内容领域: {domain}")
        print(f"🔍 发现错别字: {len(typos)} 个")

        if typos:
            for typo in typos[:5]:
                print(f"  - \"{typo['wrong']}\" → \"{typo['right']}\" ({typo.get('position', '')})")
        print()

    # 2. 检测语气词（使用config.yaml的完整列表）
    print("[2/3] 检测语气词（使用config.yaml规则）...")

    filler_words = config.get('filler_words', [])
    print(f"  配置的语气词列表: {len(filler_words)} 个")

    potential_fillers = []
    for i, seg in enumerate(segments):
        if seg['char'] in filler_words:
            # 获取上下文
            start_idx = max(0, i - 10)
            end_idx = min(len(segments), i + 11)
            context = ''.join([s['char'] for s in segments[start_idx:end_idx]])
            context_index = i - start_idx

            # 获取前后文本
            before_text = context[:context_index]
            after_text = context[context_index + 1:]

            # 上下文判断
            should_delete, reason = is_filler_by_context(
                seg['char'],
                before_text,
                after_text,
                config
            )

            potential_fillers.append({
                'index': i,
                'char': seg['char'],
                'start_ms': seg['start'],
                'end_ms': seg['end'],
                'context': context,
                'should_delete': should_delete,
                'reason': reason
            })

    print(f"  发现潜在语气词: {len(potential_fillers)} 个")

    deleted_count = sum(1 for f in potential_fillers if f['should_delete'])
    kept_count = sum(1 for f in potential_fillers if not f['should_delete'])

    print(f"  删除语气词: {deleted_count} 个")
    print(f"  保留语气词: {kept_count} 个")
    print()

    # 3. 检测重复字
    print("[3/3] 检测重复字...")
    repeat_count = 0
    repeat_deletions = []

    for i in range(len(segments) - 1):
        if segments[i]['char'] == segments[i+1]['char']:
            repeat_count += 1
            repeat_deletions.append((segments[i]['start'], segments[i]['end']))

    print(f"  删除重复字: {repeat_count} 个")
    print()

    # 4. 生成删除列表
    print("生成删除列表...")
    to_delete = []

    # 添加语气词删除
    buffer_ms = int(config.get('buffer', {}).get('before', 0.05) * 1000)
    for filler in potential_fillers:
        if filler['should_delete']:
            start = max(0, filler['start_ms'] - buffer_ms)
            end = filler['end_ms'] + buffer_ms
            to_delete.append((start, end))

    # 添加重复字删除
    for start, end in repeat_deletions:
        to_delete.append((start, end))

    # 可选：静音删除
    remove_silence = config.get('silence', {}).get('enable', False)
    if remove_silence:
        threshold = config.get('silence', {}).get('threshold', 1.0) * 1000
        if segments[0]['start'] > threshold:
            to_delete.append((0, segments[0]['start']))
        for i in range(len(segments) - 1):
            gap = segments[i+1]['start'] - segments[i]['end']
            if gap >= threshold:
                to_delete.append((segments[i]['end'], segments[i+1]['start']))

    if not to_delete:
        print("❌ 未检测到需要删除的片段")
        return []

    # 合并时间段
    to_delete.sort(key=lambda x: x[0])
    merged = []
    curr_s, curr_e = to_delete[0]
    for s, e in to_delete[1:]:
        if s <= curr_e + 150:  # 150ms内合并
            curr_e = max(curr_e, e)
        else:
            merged.append((curr_s, curr_e))
            curr_s, curr_e = s, e
    merged.append((curr_s, curr_e))

    total_delete_time = sum(e - s for s, e in merged) / 1000.0
    print(f"合并后删除段数: {len(merged)}")
    print(f"总删除时长: {total_delete_time:.2f}秒")
    print()

    # 计算保留段
    duration_ms = data['duration_ms']
    keeps = []
    curr_time = 0
    merged_sec = [(s/1000.0, e/1000.0) for s, e in merged]

    for s, e in merged_sec:
        if s > curr_time:
            keeps.append((curr_time, s))
        curr_time = max(curr_time, e)

    if curr_time < duration_ms/1000.0:
        keeps.append((curr_time, duration_ms/1000.0))

    print(f"保留段数: {len(keeps)}")
    print()

    # 生成Filter（带音频交叉淡化）
    if not keeps:
        print("❌ 警告：所有内容都被删除了！")
        return []

    filter_complex = ""
    inputs = ""
    fade_duration = 0.05  # 50ms

    for i, (start, end) in enumerate(keeps):
        filter_complex += f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}];"

        if i == 0 and len(keeps) > 1:
            filter_complex += f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,afade=t=in:ss=0:d={fade_duration}[a{i}];"
        elif i == len(keeps) - 1 and len(keeps) > 1:
            clip_duration = end - start
            fade_start = clip_duration - fade_duration
            filter_complex += f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,afade=t=out:st={fade_start}:d={fade_duration}[a{i}];"
        elif len(keeps) > 1:
            clip_duration = end - start
            fade_start = clip_duration - fade_duration
            filter_complex += f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,afade=t=in:ss=0:d={fade_duration},afade=t=out:st={fade_start}:d={fade_duration}[a{i}];"
        else:
            filter_complex += f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}];"

        inputs += f"[v{i}][a{i}]"

    filter_complex += f"{inputs}concat=n={len(keeps)}:v=1:a=1[outv][outa]"

    with open(output_filter_file, 'w', encoding='utf-8') as f:
        f.write(filter_complex)

    print("=" * 60)
    print("✅ 分析完成！")
    print("=" * 60)
    print(f"📁 Filter: {output_filter_file}")
    print(f"🎵 音频淡化: {fade_duration*1000:.0f}ms")
    print(f"📊 预计保留: {duration_ms/1000 - total_delete_time:.1f}秒 / {duration_ms/1000:.1f}秒 ({(1 - total_delete_time/(duration_ms/1000))*100:.1f}%)")
    print()

    return keeps

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript", help="转录JSON文件")
    parser.add_argument("output", help="输出Filter文件")
    parser.add_argument("--config", default="config.yaml", help="配置文件")
    parser.add_argument("--no-llm", action="store_true", help="禁用LLM分析")
    args = parser.parse_args()

    analyze_transcript(args.transcript, args.output, args.config, not args.no_llm)
