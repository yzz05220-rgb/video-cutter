#!/usr/bin/env python3
"""
金句检测器 - 智能识别视频中的精彩片段
支持多种规则：关键词、句式模式、长度、AI分析
"""

import json
import sys
import re
import argparse
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


@dataclass
class Quote:
    """金句数据结构"""
    text: str
    start_ms: int
    end_ms: int
    score: float
    reason: str  # 检测原因
    timestamp: str  # 格式化的时间戳


class GoldenQuoteDetector:
    """金句检测器主类"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.quotes: List[Quote] = []

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        import yaml

        default_config = {
            'golden_quotes': {
                'enable': True,
                'rules': []
            }
        }

        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ 配置文件加载失败，使用默认配置: {e}")

        return default_config

    def detect(self, transcript_file: str, output_file: str = None) -> List[Quote]:
        """
        检测金句

        Args:
            transcript_file: 转录JSON文件路径
            output_file: 输出JSON文件路径（可选）

        Returns:
            检测到的金句列表
        """
        print("🔍 开始检测金句...")

        # 加载转录数据
        with open(transcript_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        segments = data['segments']
        if not segments:
            print("❌ 转录数据为空")
            return []

        # 将字符级片段转换为句子级
        sentences = self._segment_to_sentences(segments)

        # 应用所有规则
        self.quotes = []
        quote_config = self.config.get('golden_quotes', {})

        for rule in quote_config.get('rules', []):
            rule_type = rule.get('type')

            if rule_type == 'keyword':
                self._detect_by_keywords(sentences, rule.get('keywords', []))

            elif rule_type == 'pattern':
                self._detect_by_patterns(sentences, rule.get('patterns', []))

            elif rule_type == 'length':
                self._detect_by_length(sentences, rule)

            elif rule_type == 'ai':
                if rule.get('enable', False):
                    self._detect_by_ai(sentences, rule)

        # 去重和排序
        self.quotes = self._deduplicate_quotes()
        self.quotes.sort(key=lambda x: x.score, reverse=True)

        # 输出结果
        if output_file:
            self._save_quotes(output_file, data.get('video_path', ''))

        self._print_summary()
        return self.quotes

    def _segment_to_sentences(self, segments: List[Dict]) -> List[Dict]:
        """将字符级片段转换为句子级"""
        sentences = []
        current_sentence = []
        current_start = None

        for i, seg in enumerate(segments):
            if not current_sentence:
                current_start = seg['start']

            current_sentence.append(seg['char'])

            # 句子结束标记：。！？……\n
            if seg['char'] in ['。', '！', '？', '…', '…', '\n']:
                text = ''.join(current_sentence).strip()
                if text:
                    sentences.append({
                        'text': text,
                        'start': current_start,
                        'end': seg['end']
                    })
                current_sentence = []
                current_start = None

            # 处理标点后的停顿（超过 500ms 认为是新句子）
            elif i < len(segments) - 1:
                gap = segments[i + 1]['start'] - seg['end']
                if gap > 500 and current_sentence:
                    text = ''.join(current_sentence).strip()
                    if text:
                        sentences.append({
                            'text': text,
                            'start': current_start,
                            'end': seg['end']
                        })
                    current_sentence = []
                    current_start = None

        # 处理最后剩余的内容
        if current_sentence:
            text = ''.join(current_sentence).strip()
            if text:
                sentences.append({
                    'text': text,
                    'start': current_start,
                    'end': segments[-1]['end']
                })

        return sentences

    def _detect_by_keywords(self, sentences: List[Dict], keywords: List[str]):
        """基于关键词检测"""
        print(f"  📌 关键词规则: {len(keywords)} 个关键词")

        for sent in sentences:
            text = sent['text']
            for keyword in keywords:
                if keyword in text:
                    # 计算分数：关键词出现次数 + 句子长度
                    count = text.count(keyword)
                    score = 10 * count + min(len(text) / 10, 10)

                    self.quotes.append(Quote(
                        text=text,
                        start_ms=sent['start'],
                        end_ms=sent['end'],
                        score=score,
                        reason=f"包含关键词「{keyword}」",
                        timestamp=self._format_timestamp(sent['start'])
                    ))
                    break  # 一个句子只记录一次

    def _detect_by_patterns(self, sentences: List[Dict], patterns: List[str]):
        """基于正则模式检测"""
        print(f"  🔧 句式规则: {len(patterns)} 个模式")

        compiled_patterns = [re.compile(p) for p in patterns]

        for sent in sentences:
            text = sent['text']
            for pattern in compiled_patterns:
                if pattern.search(text):
                    score = 15 + min(len(text) / 10, 10)

                    self.quotes.append(Quote(
                        text=text,
                        start_ms=sent['start'],
                        end_ms=sent['end'],
                        score=score,
                        reason=f"匹配句式模式",
                        timestamp=self._format_timestamp(sent['start'])
                    ))
                    break

    def _detect_by_length(self, sentences: List[Dict], rule: Dict):
        """基于长度和复杂度检测"""
        min_chars = rule.get('min_chars', 15)
        max_chars = rule.get('max_chars', 100)
        min_words = rule.get('min_words', 5)

        print(f"  📏 长度规则: {min_chars}-{max_chars} 字，{min_words}+ 词")

        for sent in sentences:
            text = sent['text']
            char_count = len(text)
            word_count = len(text.replace('，', ' ').replace('。', ' ').split())

            if min_chars <= char_count <= max_chars and word_count >= min_words:
                # 额外加分：包含标点、数字等
                bonus = 0
                if '，' in text or '：' in text:
                    bonus += 2
                if any(c.isdigit() for c in text):
                    bonus += 3

                score = 5 + bonus

                self.quotes.append(Quote(
                    text=text,
                    start_ms=sent['start'],
                    end_ms=sent['end'],
                    score=score,
                    reason=f"优秀长度 ({char_count} 字)",
                    timestamp=self._format_timestamp(sent['start'])
                ))

    def _detect_by_ai(self, sentences: List[Dict], rule: Dict):
        """使用 AI 分析检测金句（需要 API）"""
        print("  🤖 AI 分析规则")

        try:
            import openai
            api_key = rule.get('api_key') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("  ⚠️ 未配置 API Key，跳过 AI 分析")
                return

            client = openai.OpenAI(api_key=api_key)
            model = rule.get('model', 'gpt-4')
            max_quotes = rule.get('max_quotes', 5)

            # 构建提示词
            all_text = '\n'.join([f"{i+1}. {s['text']}" for i, s in enumerate(sentences)])

            prompt = f"""请从以下文本中找出 {max_quotes} 最有价值的金句（名言、总结、重点、精彩观点）。

文本内容：
{all_text}

请只返回JSON格式，包含以下字段：
- index: 金句序号（1-{len(sentences)}）
- reason: 选择理由（简短）
- score: 评分（1-100）

返回格式示例：
[
  {{"index": 5, "reason": "精辟的总结", "score": 95}},
  {{"index": 12, "reason": "核心观点", "score": 88}}
]
"""

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)

            for item in result:
                idx = item['index'] - 1
                if 0 <= idx < len(sentences):
                    sent = sentences[idx]
                    self.quotes.append(Quote(
                        text=sent['text'],
                        start_ms=sent['start'],
                        end_ms=sent['end'],
                        score=item['score'],
                        reason=f"AI分析: {item['reason']}",
                        timestamp=self._format_timestamp(sent['start'])
                    ))

            print(f"  ✅ AI 分析完成，识别 {len(result)} 条金句")

        except ImportError:
            print("  ⚠️ 未安装 openai 库，跳过 AI 分析")
        except Exception as e:
            print(f"  ❌ AI 分析失败: {e}")

    def _deduplicate_quotes(self) -> List[Quote]:
        """去重：移除重叠的金句"""
        if not self.quotes:
            return []

        # 按开始时间排序
        sorted_quotes = sorted(self.quotes, key=lambda x: x.start_ms)
        unique = []

        for quote in sorted_quotes:
            # 检查是否与已保留的金句重叠
            is_duplicate = False
            for kept in unique:
                # 如果重叠超过 50%，认为是重复
                overlap_start = max(quote.start_ms, kept.start_ms)
                overlap_end = min(quote.end_ms, kept.end_ms)
                overlap_duration = overlap_end - overlap_start
                quote_duration = quote.end_ms - quote.start_ms

                if overlap_duration > quote_duration * 0.5:
                    is_duplicate = True
                    # 保留分数更高的
                    if quote.score > kept.score:
                        unique.remove(kept)
                        unique.append(quote)
                    break

            if not is_duplicate:
                unique.append(quote)

        return unique

    def _format_timestamp(self, ms: int) -> str:
        """格式化时间戳"""
        seconds = ms / 1000
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

    def _save_quotes(self, output_file: str, video_path: str):
        """保存金句到文件"""
        data = {
            'video_path': video_path,
            'total_quotes': len(self.quotes),
            'quotes': [
                {
                    'text': q.text,
                    'start_ms': q.start_ms,
                    'end_ms': q.end_ms,
                    'score': q.score,
                    'reason': q.reason,
                    'timestamp': q.timestamp
                }
                for q in self.quotes
            ]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"💾 金句已保存至: {output_file}")

    def _print_summary(self):
        """打印摘要"""
        if not self.quotes:
            print("❌ 未检测到金句")
            return

        print(f"\n✅ 检测到 {len(self.quotes)} 条金句\n")

        # 显示前 10 条
        for i, quote in enumerate(self.quotes[:10], 1):
            print(f"{i}. [{quote.timestamp}] {quote.text[:50]}{'...' if len(quote.text) > 50 else ''}")
            print(f"   💯 评分: {quote.score:.1f} | {quote.reason}\n")

        if len(self.quotes) > 10:
            print(f"... 还有 {len(self.quotes) - 10} 条\n")


def main():
    parser = argparse.ArgumentParser(
        description="金句检测器 - 智能识别视频中的精彩片段"
    )
    parser.add_argument("transcript", help="转录JSON文件路径")
    parser.add_argument("-o", "--output", help="输出JSON文件路径", default="golden_quotes.json")
    parser.add_argument("-c", "--config", help="配置文件路径", default="config.yaml")
    parser.add_argument("--top", type=int, help="只保留前 N 条金句", default=None)

    args = parser.parse_args()

    # 检测金句
    detector = GoldenQuoteDetector(args.config)
    detector.detect(args.transcript, args.output)

    # 可选：只保留前 N 条
    if args.top and len(detector.quotes) > args.top:
        detector.quotes = detector.quotes[:args.top]
        print(f"\n🔝 只保留前 {args.top} 条金句")


if __name__ == "__main__":
    main()
