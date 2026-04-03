import re
import random
from typing import List, Tuple

def parse_traces(filename):
    """解析输入文件
    """
    import re
    positive_traces = []
    negative_traces = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            # 解析 "+ L1,L0..."
            sign = line[0]
            trace_str = line[1:].strip()
            
            # 处理可能的逗号分隔或空格分隔(异常处理, 可要可不要)
            symbols = re.split(r'[, ]+', trace_str)
            symbols = [s for s in symbols if s] # 去除空字符串
            
            if sign == '+':
                positive_traces.append(symbols)
            else:
                negative_traces.append(symbols)
    
    return positive_traces, negative_traces

def _read_trace_lines(file_path: str) -> List[List[str]]:
    """
    读取单个 trace 文件（每行一条 trace，符号可用逗号或空格分隔）
    返回: List[List[str]]
    """
    traces = []
    with open(file_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            # 兼容 "L0,L1,L0" / "L0 L1 L0" / "L0, L1, L0"
            parts = [x for x in line.replace(",", " ").split() if x]
            if parts:
                traces.append(parts)
    return traces

def split_train_test(
    pos: List[List[str]],
    neg: List[List[str]],
    train_ratio: float = 0.8,
    seed: int = 20
) -> Tuple[List[List[str]], List[List[str]], List[List[str]], List[List[str]]]:
    """
    按比例分割正负样本（分别分割，保持类别分布）
    返回: train_pos, train_neg, test_pos, test_neg
    """
    if not (0.0 < train_ratio < 1.0):
        raise ValueError("train_ratio 必须在 (0, 1) 之间，例如 0.8")
    rnd = random.Random(seed)
    rnd.shuffle(pos)
    rnd.shuffle(neg)

    n_pos = int(len(pos) * train_ratio)
    n_neg = int(len(neg) * train_ratio)

    train_pos, test_pos = pos[:n_pos], pos[n_pos:]
    train_neg, test_neg = neg[:n_neg], neg[n_neg:]

    return train_pos, train_neg, test_pos, test_neg

def read_split_traces_from_files(
    positive_train_file: str,
    negative_train_file: str,
    positive_test_file: str,
    negative_test_file: str,
) -> Tuple[List[List[str]], List[List[str]], List[List[str]], List[List[str]]]:
    """
    读取四个独立文件，返回:
    train_pos, train_neg, test_pos, test_neg
    """
    train_pos = _read_trace_lines(positive_train_file)
    train_neg = _read_trace_lines(negative_train_file)
    test_pos = _read_trace_lines(positive_test_file)
    test_neg = _read_trace_lines(negative_test_file)
    return train_pos, train_neg, test_pos, test_neg


# ==========================================
def parse_traces_dummy():
    # 简单的测试数据
    # pos = [['a', 'b'], ['a', 'b', 'b'], ['a', 'c']]
    # neg = [['a'], ['b']]
    pos = [['a','b'],['a','a','b'],['b','a','b'],['a','a','a','b']]
    neg = [['a'], ['b'], ['a','a'], ['b','a'], ['a','b','a'], ['a','b','c']]
    return pos, neg