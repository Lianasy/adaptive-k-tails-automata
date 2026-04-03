from src.function import *
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
from pathlib import Path
import json



class State:
    def __init__(self, state_id=None):
        self.id = state_id               # 状态唯一ID
        self.transitions = []            # 转移列表: ((字符,目标状态))
        self.is_accept = False           # 是否为接受状态（轨迹终点）
    
    def get_transition(self):
        transitions = [(sym, tgt_state.id) for sym, tgt_state in self.transitions]
        return transitions
    
    def __repr__(self):
        return f"State(id={self.id:3d}, is_ac={self.is_accept:>1}, trans={self.get_transition()})"

class Automaton():
    def __init__(self,
                 name: str = "None"):
        self.states_Dict: Dict[int, State] = {}
        self.alphabet: Set[str] = set()
        self.initial_state = self._add_state()  # 初始状态（根节点）
        self.name = name

    def _add_state(self):
        state_id=len(self.states_Dict)
        new_state = State(state_id)  # 用列表长度作为状态ID（自动递增）
        self.states_Dict[state_id] =new_state
        return new_state

    def build_PTA_from_trace(self, pos_traces=None, neg_traces=None):
        # 处理正样本：所有状态（中间 + 终点）全部标记为 accept
        if pos_traces is not None:
            for trace in pos_traces:
                current_state = self.initial_state
                # 初始状态必须 accept
                current_state.is_accept = True

                for symbol in trace:
                    self.alphabet.add(symbol)
                    sym_found = False
                    for sym, tgt_state in current_state.transitions:
                        if sym == symbol:
                            current_state = tgt_state
                            current_state.is_accept = True  # 中间态 accept
                            sym_found = True
                            break
                    if not sym_found:
                        next_state = self._add_state()
                        next_state.is_accept = True         # 新建态 accept
                        current_state.transitions.append((symbol, next_state))
                        current_state = next_state

                current_state.is_accept = True  # 终点 accept

        # 处理负样本：中间态全部 accept，仅终点 reject
        if neg_traces is not None:
            for trace in neg_traces:
                current_state = self.initial_state
                current_state.is_accept = True  # 初始态一定是 accept

                for symbol in trace:
                    self.alphabet.add(symbol)
                    sym_found = False
                    for sym, tgt_state in current_state.transitions:
                        if sym == symbol:
                            current_state = tgt_state
                            current_state.is_accept = True  # 中间态强制 accept
                            sym_found = True
                            break
                    if not sym_found:
                        next_state = self._add_state()
                        next_state.is_accept = True         # 中间新建态也 accept
                        current_state.transitions.append((symbol, next_state))
                        current_state = next_state

                # 负样本关键：只把最后一个状态设为 rejected
                current_state.is_accept = False

    def build_PTA_mannually_example1():
        pass

    def print_pta(
        self,
        to_screen: bool = True,
        output_dir: str = "output",
        filename: str = "PTA_structure.txt",
    ) -> None:
        alpha_str = ", ".join(sorted(self.alphabet)) if self.alphabet else "(empty)"
        lines = [
            "",
            f"=== Minimal PTA (total states: {len(self.states_Dict)}) ===",
            f"Initial state ID: {self.initial_state.id}",
            f"Alphabet: {{{alpha_str}}}",
        ]
        for state in sorted(self.states_Dict.values(), key=lambda s: s.id):
            accept_tag = "✅ accepted" if state.is_accept else "❌ unaccepted"
            transitions = state.get_transition()
            lines.append(f"S{state.id} [{accept_tag}] | T: {transitions}")
        text = "\n".join(lines)
        if to_screen:
            print(text)
        else:
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / filename
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(text)

    def export_pta_to_json(
        self,
        output_dir: str = "output",
        filename: str = "pta.json",
    ) -> None:
        """
        Export the current PTA as a JSON file .
        """
        data = []
        for state in sorted(self.states_Dict.values(), key=lambda s: s.id):
            transitions = [
                [sym, f"S{tgt_state.id}"]
                for sym, tgt_state in state.transitions
            ]
            data.append({
                "state_id": state.id,
                "accepted": "Y" if state.is_accept else "N",
                "T": transitions,
            })
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / filename
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def test_trace(self, trace: List[str]) -> bool:
        """
        在当前自动机上读入一条 trace：每步沿符号转移；走到末尾且停在接受态则 True。
        若某步无对应转移，或读完未停在接受态，则 False。
        """
        current = self.initial_state
        for symbol in trace:
            nxt = None
            for sym, tgt_state in current.transitions:
                if sym == symbol:
                    nxt = tgt_state
                    break
            if nxt is None:
                return False
            current = nxt
        return current.is_accept
    
    def evaluate_bcr(
        self,
        pos_traces: List[List[str]],
        neg_traces: List[List[str]],
        *,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        pos_traces = pos_traces or []
        neg_traces = neg_traces or []
        tp = sum(1 for t in pos_traces if self.test_trace(t))
        fn = len(pos_traces) - tp
        tn = sum(1 for t in neg_traces if not self.test_trace(t))
        fp = len(neg_traces) - tn
        sens = tp / len(pos_traces) if pos_traces else float("nan")
        spec = tn / len(neg_traces) if neg_traces else float("nan")
        bcr = (sens + spec) / 2 if pos_traces and neg_traces else float("nan")
        result = {
            "BCR": bcr,
            "sensitivity": sens,
            "specificity": spec,
            "TP": tp,
            "FN": fn,
            "TN": tn,
            "FP": fp,
            "num_pos": len(pos_traces),
            "num_neg": len(neg_traces),
        }
        if verbose:
            print("=== BCR evaluation ===")
            print(f"Positive traces: {len(pos_traces)} | Negative traces: {len(neg_traces)}")
            print(f"TP={tp}  FN={fn}  TN={tn}  FP={fp}")
            print(f"Sensitivity (TPR): {sens:.4f}")
            print(f"Specificity (TNR): {spec:.4f}")
            print(f"BCR:               {bcr:.4f}")
        return result
    
    def evaluate_PTA(self, test_pos, test_neg) -> None:
        res = self.evaluate_bcr(test_pos, test_neg, verbose=False)
        bcr = res["BCR"]
        sens = res["sensitivity"]
        spec = res["specificity"]
        alpha_str = ", ".join(sorted(self.alphabet)) if self.alphabet else "(empty)"
        print("=== PTA evaluation ===")
        print(f"PTA states num = {len(self.states_Dict)}")
        print(f"PTA alphabet: {{{alpha_str}}}")
        print(f"PTA (BCR): {bcr:.4f}")
        print(f"PTA (Sensitivity): {sens:.4f}")
        print(f"PTA (Specificity): {spec:.4f}")
        print()
    
    def compute_state_k_tail(
        self,
        start_state_id: int,
        k: int
    ) -> Optional[List[str]]:  # 注意返回类型：可能是 None
        """
        计算一个状态的 k-tail：
        1. 只返回 长度 = k 的路径（不是 ≤k）
        2. 每条路径末尾标注是否为接受状态
        3. 如果没有任何长度为 k 的路径 → 返回 None
        """
        if start_state_id not in self.states_Dict:
            return None  # 状态不存在 → None

        start_state = self.states_Dict[start_state_id]
        result = set()

        # ------------------------------
        # DFS 只收集长度 = k 的路径
        # ------------------------------
        def dfs(current_state: State, current_path: str, depth: int):
            if depth == 0:
                # 只有走到 depth=0 才记录
                if current_state.is_accept:
                    result.add(f"{current_path} (accept)")
                else:
                    result.add(f"{current_path} (rejected)")
                return

            # 继续遍历所有转移
            for sym, next_state in current_state.transitions:
                dfs(next_state, current_path + sym, depth - 1)

        # 开始搜索
        dfs(start_state, "", k)

        # ======================
        # 关键：空 → 返回 None
        # ======================
        if not result:
            print(f"=== {k}-tail at S{start_state_id} ===")
            print(f"❌ No {k}-tail for S{start_state_id}")
            return None

        # 有结果 → 返回排序后的列表
        final = sorted(list(result))
        print(f"=== {k}-tail at S{start_state_id} ===")
        print(final)
        return final

    def export_to_dot(
        self,
        output_path: str = "./output/",
        file_name: Optional[str] = None  # 不传则用自动机 name
    ) -> None:
        """
        将当前自动机导出为 Graphviz DOT 文件，可直接可视化状态机。
        特点：
        - 初始状态用箭头标出
        - 接受状态用双圈表示
        - 转移边清晰标注
        - 自动创建目录
        - 可自动使用 automaton.name 作为文件名
        """
        # ========================
        # 智能文件名处理
        # ========================
        if file_name is None:
            file_name = f"{self.name}.dot"  # 用自动机名字

        # 确保后缀是 .dot
        if not file_name.endswith(".dot"):
            file_name += ".dot"

        # ========================
        # 拼接路径 + 自动建目录
        # ========================
        out_dir = Path(output_path)
        out_dir.mkdir(parents=True, exist_ok=True)  # 自动创建目录
        final_path = out_dir / file_name             # 正确路径拼接

        # ========================
        # DOT 内容
        # ========================
        lines = []
        lines.append("digraph Automaton {")
        lines.append("    rankdir = LR;")
        lines.append("    node [shape = circle];")

        init_id = self.initial_state.id
        lines.append(f'    __start [shape="point",style="invis"];')
        lines.append(f'    __start -> S{init_id};')

        for state in self.states_Dict.values():
            sid = state.id
            if state.is_accept:
                lines.append(f'    S{sid} [shape="doublecircle"];')
            else:
                lines.append(f'    S{sid} [shape="circle"];')

            for sym, next_st in state.transitions:
                lines.append(f'    S{sid} -> S{next_st.id} [label="{sym}"];')

        lines.append("}")

        # ========================
        # 写入文件
        # ========================
        with open(final_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"✅ DOT saved：{final_path}")


    def can_merge(self, keep_state_id: int, delete_state_id: int) -> bool:
        """检查两个状态是否可以合并的辅助方法
        各种检查，检查到不合理就return false，如果各种检查都通过，直接最后自动return True
        """
        if keep_state_id == delete_state_id:                                      # 如果两个状态ID一致，那么肯定就不合并，自己跟自己合并要出问题
            print(f"keep_state_id = {keep_state_id} is the same as delete_state_id = {delete_state_id}")
            print(f"❌Fail to pass the can_merge check for S{delete_state_id} and S{keep_state_id}")
            return False

        if keep_state_id not in self.states_Dict or delete_state_id not in self.states_Dict:
            print(f"keep_state_id = {keep_state_id} or delete_state_id = {delete_state_id} not existed in Automaton.states_Dict")
            print(f"❌Fail to pass the can_merge check for S{delete_state_id} and S{keep_state_id}")
            return False
        
        return True

    def do_single_merge(self, keep_state_id: int, delete_state_id: int) -> bool:
        # 🔴 先做合法性检查
        if not self.can_merge(keep_state_id, delete_state_id):
            return False

        # 🟢 执行真正的合并：入边 + 出边全部转接
        self.redirect_incoming(keep_state_id, delete_state_id)
        self.redirect_outgoing(keep_state_id, delete_state_id)

        # 🟢 把被删除状态的「接受状态」属性同步给保留状态
        keep_state = self.states_Dict[keep_state_id]
        delete_state = self.states_Dict[delete_state_id]
        keep_state.is_accept = keep_state.is_accept or delete_state.is_accept

        del self.states_Dict[delete_state_id]

        print(f"✅ Keep_S{keep_state_id} <- Delete_S{delete_state_id} merged")
        return True
        
    def redirect_outgoing(self, keep_state_id: int, delete_state_id: int) -> None:
        """
        把 delete_state 的**所有出边**，全部转移给 keep_state。
        然后清空 delete_state 的出边。
        """
        if delete_state_id not in self.states_Dict or keep_state_id not in self.states_Dict:
            print(f"keep_state_id = {keep_state_id} or delete_state_id = {delete_state_id} not existed in Automaton.states_Dict")
            print(f"Fail: ❌ Redirecting outgoing of S{delete_state_id} to S{keep_state_id}")
            return

        keep_state = self.states_Dict[keep_state_id]
        delete_state = self.states_Dict[delete_state_id]

        # 把被删除状态的所有出边，追加到保留状态上
        for sym, tgt in delete_state.transitions:
            keep_state.transitions.append((sym, tgt))

        # 清空被删除状态的出边（安全清理）
        delete_state.transitions.clear()

    def redirect_incoming(self, keep_state_id: int, delete_state_id: int) -> None:
        """
        遍历**所有状态**，把所有指向 delete_state 的入边
        全部改成指向 keep_state。
        """
        if delete_state_id not in self.states_Dict or keep_state_id not in self.states_Dict:
            print(f"keep_state_id = {keep_state_id} or delete_state_id = {delete_state_id} not existed in Automaton.states_Dict")
            print(f"Fail: ❌ Redirecting outgoing of S{delete_state_id} to S{keep_state_id}")
            return

        keep_state = self.states_Dict[keep_state_id]
        # delete_state = self.states_Dict[delete_state_id]

        # 遍历所有状态，检查它们的出边是否指向 delete_state, 创建新的trasition，替代旧的transition
        for state in self.states_Dict.values():
            new_trans = []
            for sym, tgt in state.transitions:
                if tgt.id == delete_state_id:
                    # 原来指向被删除状态 → 重定向到保留状态
                    new_trans.append((sym, keep_state))
                else:
                    # 不变
                    new_trans.append((sym, tgt))
            # 替换成新的转移列表
            state.transitions = new_trans

# testing area





def main():
    train_file = 'data/training_data/automaton_5_2_2_0~0.txt' 
    test_file  = 'data/training_data/automaton_5_2_2_0~1.txt'
    automaton_name = Path(train_file).name

    train_pos, train_neg = parse_traces(train_file)
    test_pos, test_neg = parse_traces(test_file)

    atm = Automaton(automaton_name)
    atm.build_PTA_from_trace(train_pos, train_neg)
    atm.print_pta(to_screen=False)
    atm.export_pta_to_json()
    atm.evaluate_PTA(test_pos,test_neg)
    atm.export_to_dot(file_name=automaton_name)




    
if __name__ == "__main__":
    main()
