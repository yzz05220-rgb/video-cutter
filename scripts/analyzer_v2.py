#!/usr/bin/env python3
"""
增强版分析器 - 支持预览模式、智能边界调整、可配置规则
"""

import json
import sys
import argparse
from typing import List, Tuple, Dict
from dataclasses import dataclass

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


@dataclass
class DeleteSegment:
    """删除片段"""
    start_ms: int
    end_ms: int
    reason: str  # 删除原因
    duration_ms: int


class EnhancedAnalyzer:
    """增强版分析器"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.delete_segments: List[DeleteSegment] = []

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            import yaml
            if config_path and os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except ImportError:
            pass

        # 默认配置
        return {
            'filler_words': ['嗯', '啊', '哎', '诶', '呃', '额', '唉', '哦', '噢', '呀', '欸', '那个', '然后', '就是'],
            'silence': {'threshold': 1.0, 'enable': True},
            'buffer': {'before': 0.05, 'after': 0.05, 'min_clip_duration': 0.5}
        }

    def analyze(
        self,
        transcript_file: str,
        output_filter_file: str,
        remove_silence: bool = False,
        preview_mode: bool = False,
        config_path: str = None
    ) -> bool:
        """
        分析转录并生成剪辑滤镜

        Args:
            transcript_file: 转录 JSON 文件
            output_filter_file: 输出滤镜文件
            remove_silence: 是否删除静音
            preview_mode: 预览模式（不生成滤镜文件）
            config_path: 配置文件路径

        Returns:
            是否成功
        """
        # 加载转录数据
        with open(transcript_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        segments = data['segments']
        if not segments:
            print("❌ 转录数据为空")
            return False

        print(f"📊 开始分析转录数据 ({len(segments)} 个字符片段)...")

        # 重新加载配置（如果指定了新路径）
        if config_path:
            self.config = self._load_config(config_path)

        self.delete_segments = []

        # 1. 检测语气词
        self._detect_fillers(segments)

        # 2. 检测重复字
        self._detect_repeats(segments)

        # 3. 检测静音
        if remove_silence or self.config.get('silence', {}).get('enable', False):
            self._detect_silence(segments)

        # 4. 应用智能边界调整
        self._apply_smart_buffers()

        # 5. 合并重叠片段
        self._merge_overlaps()

        # 6. 过滤过短片段
        self._filter_short_clips()

        # 打印统计
        self._print_statistics(data['duration_ms'])

        # 预览模式
        if preview_mode:
            self._print_preview()
            return True

        # 生成滤镜文件
        return self._generate_filter(segments, data['duration_ms'], output_filter_file)

    def _detect_fillers(self, segments: List[Dict]):
        """检测语气词"""
        filler_words = self.config.get('filler_words', [])

        for i, item in enumerate(segments):
            if item['char'] in filler_words:
                # 计算删除范围（前后扩展）
                start = segments[i - 1]['end'] if i > 0 else item['start']
                end = segments[i + 1]['start'] if i < len(segments) - 1 else item['end']

                self.delete_segments.append(DeleteSegment(
                    start_ms=start,
                    end_ms=end,
                    reason=f"语气词「{item['char']}」",
                    duration_ms=end - start
                ))

    def _detect_repeats(self, segments: List[Dict]):
        """检测重复字"""
        for i in range(len(segments) - 1):
            if segments[i]['char'] == segments[i + 1]['char']:
                self.delete_segments.append(DeleteSegment(
                    start_ms=segments[i]['start'],
                    end_ms=segments[i]['end'],
                    reason=f"重复字「{segments[i]['char']}」",
                    duration_ms=segments[i]['end'] - segments[i]['start']
                ))

    def _detect_silence(self, segments: List[Dict]):
        """检测静音"""
        threshold_ms = self.config.get('silence', {}).get('threshold', 1.0) * 1000

        # 开头静音
        if segments[0]['start'] > threshold_ms:
            self.delete_segments.append(DeleteSegment(
                start_ms=0,
                end_ms=segments[0]['start'],
                reason="开头静音",
                duration_ms=segments[0]['start']
            ))

        # 中间静音
        for i in range(len(segments) - 1):
            gap = segments[i + 1]['start'] - segments[i]['end']
            if gap >= threshold_ms:
                self.delete_segments.append(DeleteSegment(
                    start_ms=segments[i]['end'],
                    end_ms=segments[i + 1]['start'],
                    reason=f"静音 ({gap / 1000:.1f}秒)",
                    duration_ms=gap
                ))

    def _apply_smart_buffers(self):
        """应用智能边界调整"""
        buffer_before = self.config.get('buffer', {}).get('before', 0.05) * 1000
        buffer_after = self.config.get('buffer', {}).get('after', 0.05) * 1000

        for seg in self.delete_segments:
            # 前后保留缓冲
            seg.start_ms = max(0, seg.start_ms - buffer_before)
            seg.end_ms = seg.end_ms + buffer_after

    def _merge_overlaps(self):
        """合并重叠的删除片段"""
        if not self.delete_segments:
            return

        # 按开始时间排序
        self.delete_segments.sort(key=lambda x: x.start_ms)

        merged = []
        curr = self.delete_segments[0]

        for seg in self.delete_segments[1:]:
            # 如果重叠或相邻（间隔 < 100ms），合并
            if seg.start_ms <= curr.end_ms + 100:
                curr.end_ms = max(curr.end_ms, seg.end_ms)
                curr.duration_ms = curr.end_ms - curr.start_ms
                # 合并原因
                if "合并" not in curr.reason:
                    curr.reason = f"{curr.reason} + {seg.reason}"
            else:
                merged.append(curr)
                curr = seg

        merged.append(curr)
        self.delete_segments = merged

    def _filter_short_clips(self):
        """过滤过短的保留片段"""
        min_clip_duration = self.config.get('buffer', {}).get('min_clip_duration', 0.5) * 1000

        # 计算保留片段的时长
        if not self.delete_segments:
            return

        # 按时间排序
        self.delete_segments.sort(key=lambda x: x.start_ms)

        # 标记需要删除的过短片段
        to_remove = []
        last_end = 0

        for seg in self.delete_segments:
            # 检查之前的保留片段
            if seg.start_ms - last_end < min_clip_duration and seg.start_ms > last_end:
                # 保留片段太短，将其合并到删除片段中
                to_remove.append(seg)
            last_end = seg.end_ms

        # 扩展删除片段以覆盖过短的保留片段
        for seg in to_remove:
            # 找到前一个删除片段并扩展
            for other in self.delete_segments:
                if other.end_ms <= seg.start_ms:
                    other.end_ms = seg.end_ms
                    other.duration_ms = other.end_ms - other.start_ms
                    other.reason = f"{other.reason} (扩展以覆盖过短片段)"
                    break

    def _print_statistics(self, total_duration_ms: int):
        """打印统计信息"""
        total_delete_ms = sum(seg.duration_ms for seg in self.delete_segments)
        delete_ratio = (total_delete_ms / total_duration_ms * 100) if total_duration_ms > 0 else 0

        # 按原因分类统计
        by_reason = {}
        for seg in self.delete_segments:
            key = seg.reason.split('(')[0].strip()  # 提取主要原因
            by_reason[key] = by_reason.get(key, 0) + 1

        print(f"\n{'=' * 60}")
        print("📊 分析统计")
        print(f"{'=' * 60}")
        print(f"总删除片段: {len(self.delete_segments)} 处")
        print(f"删除时长: {total_delete_ms / 1000:.1f} 秒 ({delete_ratio:.1f}%)")
        print(f"\n删除原因分布:")
        for reason, count in sorted(by_reason.items(), key=lambda x: -x[1]):
            print(f"  - {reason}: {count} 处")
        print(f"{'=' * 60}\n")

        # 智能建议
        self._print_smart_suggestions(delete_ratio, by_reason)

    def _print_smart_suggestions(self, delete_ratio: float, by_reason: Dict):
        """打印智能建议"""
        suggestions = self.config.get('advanced', {}).get('smart_suggestions', {})

        if not suggestions.get('enable', True):
            return

        print("💡 智能建议:")

        # 静音过多建议
        silence_count = by_reason.get("静音", 0)
        if silence_count > suggestions.get('suggest_remove_silence', {}).get('threshold', 20):
            print("  - 检测到大量静音 ({0} 处)，建议添加 --remove-silence 参数".format(silence_count))

        # 删除比例过高建议
        if delete_ratio > suggestions.get('suggest_keep_filler', {}).get('threshold', 0.3) * 100:
            print(f"  - 删除比例较高 ({delete_ratio:.1f}%)，考虑保留部分语气词使语速更自然")

        print()

    def _print_preview(self):
        """打印预览"""
        print(f"{'=' * 60}")
        print("🔍 预览模式 - 将要删除的片段")
        print(f"{'=' * 60}\n")

        max_show = self.config.get('preview', {}).get('max_show', 20)

        for i, seg in enumerate(self.delete_segments[:max_show], 1):
            start_sec = seg.start_ms / 1000
            end_sec = seg.end_ms / 1000
            print(f"{i:2d}. [{start_sec:7.2f} - {end_sec:7.2f}] ({seg.duration_ms/1000:5.2f}秒) - {seg.reason}")

        if len(self.delete_segments) > max_show:
            print(f"\n... 还有 {len(self.delete_segments) - max_show} 处\n")

        print(f"\n{'=' * 60}")
        print("⚠️ 预览模式，不生成滤镜文件")
        print("   如需执行剪辑，请去掉 --preview 参数")
        print(f"{'=' * 60}\n")

        # 导出报告
        if self.config.get('preview', {}).get('export_report', True):
            report_file = "preview_report.txt"
            self._export_report(report_file)

    def _export_report(self, report_file: str):
        """导出预览报告"""
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("视频剪辑预览报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"总删除片段: {len(self.delete_segments)} 处\n\n")

            for i, seg in enumerate(self.delete_segments, 1):
                start_sec = seg.start_ms / 1000
                end_sec = seg.end_ms / 1000
                f.write(f"{i}. [{start_sec:.2f} - {end_sec:.2f}] ({seg.duration_ms/1000:.2f}秒) - {seg.reason}\n")

        print(f"📄 预览报告已保存: {report_file}\n")

    def _generate_filter(self, segments: List[Dict], total_duration_ms: int, output_file: str) -> bool:
        """生成 FFmpeg 滤镜文件"""
        if not self.delete_segments:
            print("⚠️ 没有检测到需要删除的片段")
            return False

        # 转换为秒
        delete_ranges_sec = [(s.start_ms / 1000.0, s.end_ms / 1000.0) for s in self.delete_segments]

        # 计算保留片段
        keeps = []
        curr_time = 0.0

        for start, end in delete_ranges_sec:
            if start > curr_time:
                keeps.append((curr_time, start))
            curr_time = max(curr_time, end)

        if curr_time < total_duration_ms / 1000.0:
            keeps.append((curr_time, total_duration_ms / 1000.0))

        if not keeps:
            print("❌ 警告：所有内容都被删除了！")
            return False

        # 生成滤镜
        filter_complex = ""
        inputs = ""

        for i, (start, end) in enumerate(keeps):
            filter_complex += f"[0:v]trim=start={start:.3f}:end={end:.3f},setpts=PTS-STARTPTS[v{i}];"
            filter_complex += f"[0:a]atrim=start={start:.3f}:end={end:.3f},asetpts=PTS-STARTPTS[a{i}];"
            inputs += f"[v{i}][a{i}]"

        filter_complex += f"{inputs}concat=n={len(keeps)}:v=1:a=1[outv][outa]"

        # 保存文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(filter_complex)

        print(f"✅ 滤镜文件已生成: {output_file}")
        print(f"   保留片段: {len(keeps)} 个")
        return True


def analyze_transcript(
    transcript_file: str,
    output_filter_file: str,
    remove_silence: bool = False,
    preview_mode: bool = False,
    config_path: str = None
) -> bool:
    """便捷函数：分析转录文件"""
    analyzer = EnhancedAnalyzer(config_path)
    return analyzer.analyze(transcript_file, output_filter_file, remove_silence, preview_mode)


def main():
    parser = argparse.ArgumentParser(
        description="增强版分析器 - 支持预览模式和智能边界调整"
    )

    parser.add_argument("transcript", help="转录 JSON 文件")
    parser.add_argument("output", help="输出滤镜文件")
    parser.add_argument("--remove-silence", action="store_true", help="删除静音")
    parser.add_argument("--preview", action="store_true", help="预览模式（不生成滤镜）")
    parser.add_argument("--config", "-c", help="配置文件路径", default="config.yaml")

    args = parser.parse_args()

    analyze_transcript(
        args.transcript,
        args.output,
        args.remove_silence,
        args.preview,
        args.config
    )


if __name__ == "__main__":
    main()
