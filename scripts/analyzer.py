import json
import sys
import argparse

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

FILLER_WORDS = ['嗯', '啊', '哎', '诶', '呃', '额', '唉', '哦', '噢', '呀', '欸', '那个', '然后', '就是']

def analyze_transcript(transcript_file, output_filter_file, remove_silence=False):
    with open(transcript_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    segments = data['segments']
    to_delete = [] # milliseconds
    
    # 1. 语气词
    for i, item in enumerate(segments):
        if item['char'] in FILLER_WORDS:
            start = segments[i-1]['end'] if i > 0 else item['start']
            end = segments[i+1]['start'] if i < len(segments)-1 else item['end']
            to_delete.append((start, end))
            
    # 2. 重复字
    for i in range(len(segments) - 1):
        if segments[i]['char'] == segments[i+1]['char']:
             to_delete.append((segments[i]['start'], segments[i]['end']))
             
    # 3. 静音 (仅当启用时)
    if remove_silence:
        if segments[0]['start'] > 1000:
            to_delete.append((0, segments[0]['start']))
        for i in range(len(segments) - 1):
            gap = segments[i+1]['start'] - segments[i]['end']
            if gap >= 1000:
                to_delete.append((segments[i]['end'], segments[i+1]['start']))
                
    # 合并时间段
    if not to_delete:
        print("未检测到需要删除的片段。")
        return []
        
    to_delete.sort(key=lambda x: x[0])
    merged = []
    curr_s, curr_e = to_delete[0]
    for s, e in to_delete[1:]:
        if s <= curr_e:
            curr_e = max(curr_e, e)
        else:
            merged.append((curr_s, curr_e))
            curr_s, curr_e = s, e
    merged.append((curr_s, curr_e))
    
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
        
    # 生成 Filter
    if not keeps:
        print("❌ 警告：所有内容都被删除了！")
        return []
        
    filter_complex = ""
    inputs = ""
    for i, (start, end) in enumerate(keeps):
        filter_complex += f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}];"
        filter_complex += f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}];"
        inputs += f"[v{i}][a{i}]"
    
    filter_complex += f"{inputs}concat=n={len(keeps)}:v=1:a=1[outv][outa]"
    
    with open(output_filter_file, 'w', encoding='utf-8') as f:
        f.write(filter_complex)
        
    print(f"✅ 分析完成，检测到 {len(to_delete)} 处删除项。")
    print(f"Filter 已保存至: {output_filter_file}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript", help="转录JSON文件")
    parser.add_argument("output", help="输出 Filter 文件")
    parser.add_argument("--remove-silence", action="store_true", help="是否删除静音")
    args = parser.parse_args()
    
    analyze_transcript(args.transcript, args.output, args.remove_silence)
