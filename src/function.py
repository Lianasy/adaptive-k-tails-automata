import json
from pathlib import Path
import random
from typing import List, Tuple, Dict

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

def k_fold_split(
    pos: List[List[str]],
    neg: List[List[str]],
    n_splits: int = 5,
    seed: int = 20,
) -> List[Tuple[List[List[str]], List[List[str]], List[List[str]], List[List[str]]]]:
    """
    K-fold 划分（正负样本分别划分，近似分层）
    返回 folds:
      [(train_pos, train_neg, val_pos, val_neg), ...]  长度 = n_splits
    """
    if n_splits < 2:
        raise ValueError("n_splits must >= 2")
    pos_cp = [list(t) for t in pos]
    neg_cp = [list(t) for t in neg]
    if len(pos_cp) < n_splits or len(neg_cp) < n_splits:
        raise ValueError(
            f"too few samples：len(pos)={len(pos_cp)}, len(neg)={len(neg_cp)}, n_splits={n_splits}"
        )
    rnd = random.Random(seed)
    rnd.shuffle(pos_cp)
    rnd.shuffle(neg_cp)
    def build_folds(data: List[List[str]], k: int) -> List[List[List[str]]]:
        buckets = [[] for _ in range(k)]
        for i, item in enumerate(data):
            buckets[i % k].append(item)
        return buckets
    pos_folds = build_folds(pos_cp, n_splits)
    neg_folds = build_folds(neg_cp, n_splits)
    result = []
    for i in range(n_splits):
        val_pos = pos_folds[i]
        val_neg = neg_folds[i]
        train_pos = [x for j, fold in enumerate(pos_folds) if j != i for x in fold]
        train_neg = [x for j, fold in enumerate(neg_folds) if j != i for x in fold]
        result.append((train_pos, train_neg, val_pos, val_neg))
    return result

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

def debug_print(debug:bool, msg: str):
    """DEBUG=True -> print msg，False dont print"""
    if debug:
        print(msg)
# ==========================================
def parse_traces_dummy():
    # 简单的测试数据
    # pos = [['a', 'b'], ['a', 'b', 'b'], ['a', 'c']]
    # neg = [['a'], ['b']]
    pos = [['a','b'],['a','a','b'],['b','a','b'],['a','a','a','b']]
    neg = [['a'], ['b'], ['a','a'], ['b','a'], ['a','b','a'], ['a','b','c']]
    return pos, neg

def k_vector_to_json(
    k_vector: Dict[str, int],
    output_path: str,
    file_name: str
) -> None:
    """
    将 k-vector 字典输出为格式化 JSON 文件
    :param k_vector: 形如 {'L0': 2, 'L1': 2, 'L2': 2} 的字典
    :param output_path: 输出文件夹路径，如 './output'
    :param file_name: 文件名（无需加 .json 后缀）
    """
    # 确保文件名以 .json 结尾
    if not file_name.endswith('.json'):
        file_name += '.json'

    # 创建输出目录
    out_dir = Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 完整输出路径
    full_path = out_dir / file_name

    # 写入 JSON（格式化、易读）
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(k_vector, f, ensure_ascii=False, indent=2)

    # print(f"✅ k-vector JSON saved: {full_path}")