from function import * 
from typing import Dict, List, Set, Tuple, Optional, Any, Literal
from collections import defaultdict
from pathlib import Path
import json
import itertools
import copy
import time
import pandas as pd



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
        self.k_vector: Dict[str, int] = {}

    def _add_state(self):
        state_id=len(self.states_Dict)
        new_state = State(state_id)  # 用列表长度作为状态ID（自动递增）
        self.states_Dict[state_id] =new_state
        return new_state

    def copy_automaton(self) -> "Automaton":
        """深拷贝结构：新自动机状态 id 与原来一致，仅 State 对象是新实例。"""
        old_ids = sorted(self.states_Dict.keys())
        if not old_ids:
            return Automaton(name=self.name + "_copy")
        new_atm = Automaton(name=self.name + "_copy")
        # __init__ 已创建 S0；补到与旧图相同 max_id
        max_id = max(old_ids)
        while len(new_atm.states_Dict) <= max_id:
            new_atm._add_state()
        for oid_id in old_ids:
            new_state = new_atm.states_Dict[oid_id]
            old_state = self.states_Dict[oid_id]
            new_state.is_accept = old_state.is_accept
            new_state.transitions.clear()
            for sym, tgt in old_state.transitions:
                new_state.transitions.append((sym, new_atm.states_Dict[tgt.id]))
        new_atm.initial_state = new_atm.states_Dict[self.initial_state.id]
        new_atm.alphabet = set(self.alphabet)
        if hasattr(self, "k_vector"):
            new_atm.k_vector = dict(self.k_vector)
        return new_atm

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

    def update_alphabet(self) -> None:
        """从当前所有状态的转移边上收集符号，填充 self.alphabet。"""
        self.alphabet.clear()
        for state in self.states_Dict.values():
            for sym, _tgt in state.transitions:
                self.alphabet.add(sym)

    def initialize_k_vector(
        self,
        values: Optional[Dict[str, int]] = None,
        All_k: int = 2,
    ) -> None:
        """
        填充 self.k_vector：symbol -> k。
        - 未传 values：所有符号均为 All_k（默认 2）。
        - 传入 values：键必须与 self.alphabet 完全一致，否则打印两边 key 并报错。
        """

        self.update_alphabet()

        if values is None:
            self.k_vector = {sym: int(All_k) for sym in sorted(self.alphabet)}
            return

        if values:
            atm_alphabet_keys = set(self.alphabet)
            passed_kvector_keys = set(values.keys())
            if atm_alphabet_keys != passed_kvector_keys:
                print("initialize_k_vector: key set mismatch between automaton alphabet and passed dict.")
                print(f"Automaton alphabet keys (sorted): {sorted(atm_alphabet_keys)}")
                print(f"Passed dict keys (sorted):        {sorted(passed_kvector_keys)}")
                print(f"Only in automaton: {sorted(atm_alphabet_keys - passed_kvector_keys)}")
                print(f"Only in passed dict: {sorted(passed_kvector_keys - atm_alphabet_keys)}")
                raise ValueError("k_vector: k_vector-dict passed must match alphabet exactly")
            if atm_alphabet_keys == passed_kvector_keys:
                self.k_vector = {sym: int(values[sym]) for sym in sorted(self.alphabet)}
    
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
        filename = f"{filename}.json"
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
        timer: float,
        *,
        verbose: bool = True,
        filename: Optional[str] = None,
        output_dir: str = "output",
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
            "num_states": len(self.states_Dict),
            **({"evaluation_time_sec": timer} if timer else {}),
        }
        lines = [
            f"=== BCR evaluation k-vector = {self.k_vector}===",
            f"ATM states num = {len(self.states_Dict)}",
            f"Positive traces: {len(pos_traces)} | Negative traces: {len(neg_traces)}",
            f"TP={tp}  FN={fn}  TN={tn}  FP={fp}",
            f"Sensitivity (TPR): {sens:.4f}",
            f"Specificity (TNR): {spec:.4f}",
            f"BCR:               {bcr:.4f}",
            f"Evaluation time: {timer:.2f} seconds" if timer else "",
        ]
        text = "\n".join(lines) + "\n"
        if filename is not None:
            filename = f"{filename}.txt"
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / filename, "w", encoding="utf-8") as f:
                f.write(text)
        elif verbose:
            print(text, end="")
        return result
    
    def evaluate_PTA(
        self,
        test_pos,
        test_neg,
        *,
        verbose: bool = True,
        filename: Optional[str] = None,
        output_dir: str = "output",
    ) -> None:
        res = self.evaluate_bcr(test_pos, test_neg, timer=None, verbose=False)
        bcr = res["BCR"]
        sens = res["sensitivity"]
        spec = res["specificity"]
        alpha_str = ", ".join(sorted(self.alphabet)) if self.alphabet else "(empty)"
        lines = [
            "=== PTA evaluation ===",
            f"PTA states num = {len(self.states_Dict)}",
            f"PTA alphabet: {{{alpha_str}}}",
            f"PTA (BCR): {bcr:.4f}",
            f"PTA (Sensitivity): {sens:.4f}",
            f"PTA (Specificity): {spec:.4f}",
            "",
        ]
        text = "\n".join(lines)
        
        if filename is not None:
            filename = f"{filename}.txt"
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / filename, "w", encoding="utf-8") as f:
                f.write(text)
        elif verbose:
            print(text)
    
    def compute_state_k_tail(
        self,
        start_state_id: int,
        k: int,
        verbose: bool = True,
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
            if verbose:
                print(f"=== {k}-tail at S{start_state_id} ===")
                print(f"❌ No {k}-tail for S{start_state_id}")
            return None

        # 有结果 → 返回排序后的列表
        final = sorted(list(result))
        if verbose:
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
        
        # print(f"✅ DOT saved：{final_path}")

    def can_merge(self, state1_id: int, state2_id: int, verbose: bool = True) -> bool:
        """检查两个状态是否可以合并的辅助方法
        各种检查，检查到不合理就return false，如果各种检查都通过，直接最后自动return True
        """

        keep_state_id = min(state1_id,state2_id)
        delete_state_id  = max(state1_id,state2_id)

        if keep_state_id == delete_state_id:                                      # 如果两个状态ID一致，那么肯定就不合并，自己跟自己合并要出问题
            if verbose: print(f"keep_state_id = {keep_state_id} is the same as delete_state_id = {delete_state_id}")
            if verbose: print(f"❌Fail to pass the can_merge check for S{delete_state_id} and S{keep_state_id}")
            return False

        if keep_state_id not in self.states_Dict or delete_state_id not in self.states_Dict:
            print(f"keep_state_id = {keep_state_id} or delete_state_id = {delete_state_id} not existed in Automaton.states_Dict")
            print(f"❌Fail to pass the can_merge check for S{delete_state_id} and S{keep_state_id}")
            return False

        dummy_atm = self.copy_automaton()
        dummy_atm.do_single_merge(keep_state_id,delete_state_id)
        can_merge_test = dummy_atm.simulate_NFA_merge(keep_state_id)

        return can_merge_test

    def do_single_merge(self, state1_id: int, state2_id: int) -> bool:

        keep_state_id = min(state1_id, state2_id)
        delete_state_id = max(state1_id, state2_id)

        if delete_state_id not in self.states_Dict or keep_state_id not in self.states_Dict:
            # print(f"When checking do_singale_merge:keep_state_id = {keep_state_id} or delete_state_id = {delete_state_id} not existed in Automaton.states_Dict")
            return False
        # 🟢 执行真正的合并：入边 + 出边全部转接
        self.redirect_incoming(keep_state_id, delete_state_id)
        self.redirect_outgoing(keep_state_id, delete_state_id)

        # 🟢 把被删除状态的「接受状态」属性同步给保留状态
        keep_state = self.states_Dict[keep_state_id]
        delete_state = self.states_Dict[delete_state_id]
        keep_state.is_accept = keep_state.is_accept or delete_state.is_accept

        del self.states_Dict[delete_state_id]

        # print(f"✅ Keep_S{keep_state_id} <- Delete_S{delete_state_id} merged")
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

        existing = set()
        for sym, tgt in keep_state.transitions:
            existing.add( (sym, tgt.id) )
        # -------------------------
        # 只添加【不存在的边】
        # 同符号同目标 → 跳过（去重）
        # 同符号不同目标 → 添加（保留NFA）
        # -------------------------
        for sym, tgt in delete_state.transitions:
            key = (sym, tgt.id)
            if key not in existing:
                keep_state.transitions.append( (sym, tgt) )
                existing.add(key)

        # 清空被删除状态的出边
        delete_state.transitions.clear()

    def redirect_incoming(self, keep_state_id: int, delete_state_id: int) -> None:
        """
        遍历**所有状态**，把所有指向 delete_state 的入边
        全部改成指向 keep_state。
        同一个 (状态, 符号) 只会保留一条边，不会重复！
        """
        if delete_state_id not in self.states_Dict or keep_state_id not in self.states_Dict:
            print(f"keep_state_id = {keep_state_id} or delete_state_id = {delete_state_id} not existed in Automaton.states_Dict")
            print(f"Fail: ❌ Redirecting outgoing of S{delete_state_id} to S{keep_state_id}")
            return

        keep_state = self.states_Dict[keep_state_id]
        # delete_state = self.states_Dict[delete_state_id]

        # 遍历每个状态
        for state in self.states_Dict.values():
            # 第一步：直接修改指向 delete_state 的边
            for i in range(len(state.transitions)):
                sym, tgt = state.transitions[i]
                if tgt.id == delete_state_id:
                    state.transitions[i] = (sym, keep_state)
        
            # 第二步：去重 —— 移除【完全重复】的边 (sym, target_id) 相同
            seen = set()
            unique_trans = []
            for sym, tgt in state.transitions:
                key = (sym, tgt.id)
                if key not in seen:
                    seen.add(key)
                    unique_trans.append((sym, tgt))
            
            # 覆盖回去 → 重复边消失，NFA 保留
            state.transitions = unique_trans

    def k_common_outgoing(
        self,
        state_a_id: State,
        state_b_id: State,
        k_aggregation_mode: Literal["max", "min"] = "max",
        verbose: bool = False
    ) -> Optional[int]:
        """
        对比两个 state 的出边：取「两边都出现过的符号」；
        对每个符号从 self.k_vector 取 k，再对所有 k 取 max 或 min。
        无公共符号、无有效 k、或 k_vector 未初始化时返回 None。
        """
        if state_a_id not in self.states_Dict or state_b_id not in self.states_Dict:
            if verbose:print(f"⚠️ S{state_a_id} or S{state_b_id} not in states_Dict, return None")
            return None

        if state_a_id == state_b_id:
            if verbose: print(f"⚠️ S{state_a_id} vs S{state_b_id}: same state, return None")
            return None
        
        state_a = self.states_Dict[state_a_id]
        state_b = self.states_Dict[state_b_id]

        syms_a = {sym for sym, _ in state_a.transitions}
        syms_b = {sym for sym, _ in state_b.transitions}
        common = syms_a & syms_b

        if not common:
            if verbose: print(f"⚠️ No common outgoing symbol found for S{state_a.id} vs S{state_b.id}")
            return None
        
        k_list: List[int] = []
        for sym in common:
            if sym not in self.k_vector.keys():
                if verbose: print(f"❌ No valid k value for '{sym}', or k-vector not initialized")
                continue
            k_list.append(int(self.k_vector[sym]))
        
        if not k_list:
            if verbose: print(f"❌ can not find common-symbol-k for S{state_a.id} vs S{state_b.id}, maybe k-vector not initialized")
            return None
        
        if k_list:
            if verbose: print(f"✅ found common sym for S{state_a_id} vs S{state_b_id}: {common}, k_list = {k_list}")
            k_decided = max(k_list) if k_aggregation_mode == "max" else min(k_list)

            return k_decided

    def NFA_merge(self, state_id: int, verbose:bool = False) -> None:
        """
        【纯递归消除 NFA】
        规则：
        1. 检查 state_id 下是否有 同一个sym → 多个不同state
        2. 如果有 → 直接合并这些目标状态（不需要k-tail！不需要判断！）
        3. 合并后，递归检查当前 state 是否还存在 NFA
        4. 直到完全无 NFA 为止
        """
        # 状态不存在，直接返回
        if state_id not in self.states_Dict:
            if verbose: print(f"S({state_id} no exists, can't do NFA merge)")
            return 
        
        state = self.states_Dict[state_id]

        # 按符号分组出边：sym -> [target_state1, target_state2...]
        sym_groups = defaultdict(list)
        for sym, tgt_state in state.transitions:
            sym_groups[sym].append(tgt_state)

        # 遍历每个符号，检查是否出现 NFA（一个符号 → 多个目标）
        for sym, target_states in sym_groups.items():
            if len(target_states) <= 1:
                if verbose: print(f"✅ S{state_id} [{sym}] has no repeted target")
                continue  # 没有NFA，跳过
            if len(target_states) > 1:
                target_states_sorted = sorted(target_states, key=lambda x: x.id)
                target_ids_sorted = [t.id for t in target_states_sorted]
                if verbose: print(f"\n⚠️  NFA found ：S{state_id} -{sym} → {target_ids_sorted}")

                # 策略：把后面所有的都合并到第一个 target 上
                keep_state_id = target_states_sorted[0].id
                if verbose:print(f"!!!!!!!!!!!!!target_states[1:] = {target_states_sorted[1:]}")
                for tgt in target_states_sorted[1:]:
                    if state_id not in self.states_Dict:
                        continue
                    del_id = tgt.id
                    if verbose:print(f"   → merge NFA：S{keep_state_id} <- S{del_id}")
                    # print(f"acceptable:S{keep_state_id}={self.states_Dict[keep_state_id].is_accept} ; S{del_id}={self.states_Dict[del_id].is_accept}")

                    # 直接合并（因为是修复NFA，必须合并）
                    self.do_single_merge(keep_state_id, del_id)
                    
                    self.NFA_merge(keep_state_id)
        return 

    def simulate_NFA_merge(self, state_id: int, verbose:bool = False) -> None:
        """
        在「当前dummy自动机」上模拟消除 NFA（与 NFA_merge 同结构，但返回是否全程可完成）：
        1. 若某符号存在多个不同目标，则依次将后续目标并入 id 最小的目标；
        2. 合并前若两个状态都在 states_Dict 中，则必须 is_accept 一致，否则返回 False；
        3. 若某一侧已不在 states_Dict（可能被前面合并删掉），跳过该次，不算失败；
        4. 递归直到当前 state 上无「同符多目标」；
        5. 全程无失败则返回 True。
        """
        # 状态不存在，直接返回
        if state_id not in self.states_Dict:
            if verbose: print(f"S({state_id} no exists, can't do NFA merge)")
            return 
        
        state = self.states_Dict[state_id]

        # 按符号分组出边：sym -> [target_state1, target_state2...]
        sym_groups = defaultdict(list)
        for sym, tgt_state in state.transitions:
            sym_groups[sym].append(tgt_state)

        # 遍历每个符号，检查是否出现 NFA（一个符号 → 多个目标）
        for sym, target_states in sym_groups.items():
            if len(target_states) <= 1:
                if verbose: print(f"DUMMY:✅ S{state_id} [{sym}] has no repeted target")
                continue  # 没有NFA，跳过
            if len(target_states) > 1:
                if verbose: print(f"DUMMY:now checking S{state_id}[{sym}], see if leading to multiple target state")
                target_states_sorted = sorted(target_states, key=lambda x: x.id)
                target_ids_sorted = [t.id for t in target_states_sorted]
                if verbose: print(f"\n⚠️  DUMMY:NFA found ：S{state_id} -{sym} → {target_ids_sorted}")

                # 策略：把后面所有的都合并到第一个 target 上
                keep_state_id = target_states_sorted[0].id
                if verbose: print(f"DUMMY:!!!!!!!!!!!!!target_states[1:] = {target_states_sorted[1:]}")
                for tgt in target_states_sorted[1:]:
                    if state_id not in self.states_Dict:
                        continue
                    del_id = tgt.id

                    if keep_state_id not in self.states_Dict or del_id not in self.states_Dict:
                        if verbose:print(f"DUMMY:⏭️ skip S{keep_state_id} <- S{del_id}: not both in states_Dict, continue")
                        continue
                    
                    keep_state = self.states_Dict[keep_state_id]
                    del_state = self.states_Dict[del_id]

                    if keep_state.is_accept != del_state.is_accept:
                        if verbose:print(f"DUMMY:❌ simulate_NFA_merge failed: S{keep_state_id}.is_accept={keep_state.is_accept} != S{del_id}.is_accept={del_state.is_accept}")
                        return False

                    if verbose: print(f"DUMMY:   → merge NFA：S{keep_state_id} <- S{del_id}")

                    # 直接合并（因为是修复NFA，必须合并）
                    self.do_single_merge(keep_state_id, del_id)
                    NFA_merge_succ = self.simulate_NFA_merge(keep_state_id,verbose=verbose)
                    if NFA_merge_succ == False:
                        return False
                    
        return True

    def Global_merge(self, verbose:bool = False, k_aggregation_mode: Literal["max", "min"] = "max",) -> None:
        """
        全局自动合并算法（严格按你的要求实现）
        1. 遍历所有状态两两配对
        2. 先检查 k-tail 是否相等
        3. 相等 → 再检查 can_merge 是否合法
        4. 合法 → 执行 do_single_merge
        5. 合并后 → 自动调用 NFA_merge 消除当前状态的 NFA
        6. 循环直到没有可合并状态为止
        """
        if verbose: print(f"\n===== GLOBAL MERGE (k-vector = {self.k_vector} =====")

        if_merged = True
        round_count = 0
        # 循环：直到一轮遍历中没有任何合并发生
        while if_merged:
            if_merged = False  # 先假设本轮不合并
            round_count += 1

            state_ids = list(self.states_Dict.keys())  # 每次重新获取当前所有状态
            state_total = len(state_ids)

            


            if verbose: print(f"\n===== {round_count}-th round | current state number :{state_total} =====")
            for i in range(state_total):
                state1_id = state_ids[i]
                for j in range(i + 1, state_total):
                    state2_id = state_ids[j]
                
                    if verbose: print(f"\n----------------------------------------")
                    if verbose: print(f"checking pairs to merge：S{state1_id} ↔ S{state2_id}")

                    if state1_id not in self.states_Dict or state2_id not in self.states_Dict:
                        if verbose: print(f"When providing two pairs:keep_state_id = {state1_id} or delete_state_id = {state2_id} not existed in Automaton.states_Dict, try next pair")
                        continue
                    
                    k = self.k_common_outgoing(state1_id,state2_id,k_aggregation_mode=k_aggregation_mode)
                    if k == None:   # 如果没找到相同字符下的k，那么这个循环就跳过，进入下一个循环
                        continue 

                    kt_state1 = self.compute_state_k_tail(state1_id, k,verbose=verbose)
                    kt_state2 = self.compute_state_k_tail(state2_id, k,verbose=verbose)
                    if verbose: print(f"{k}-tail of S{state1_id}: {kt_state1}")
                    if verbose: print(f"{k}-tail of S{state2_id}: {kt_state2}")

                    if (kt_state1 is None) or (kt_state2 is None):
                        if verbose: print(f"S{state1_id} ↔ S{state2_id} ❌ skip: k-tail missing (None)")
                        continue
                    
                    common_k_tail = set(kt_state1) & set(kt_state2)
                    
                    if not common_k_tail:
                        if verbose: print(f"S{state1_id} ↔ S{state2_id} ❌ have NO common {k}-tail different, try next pair")
                        continue
                    if common_k_tail:
                        if verbose: print(f"S{state1_id} ↔ S{state2_id} ✅ HAVE COMMON {k}-tail : {common_k_tail}, \n checking can_merge validation")
                        canMerge = self.can_merge(state1_id, state2_id,verbose=verbose)
                        
                        if canMerge == False:
                            if verbose: print(f"❌ can_merge FAIL, try next pair")
                            continue
                        if canMerge == True:
                            if verbose: print(f"✅ can_merge PASS, doing single_merging")
                            self.do_single_merge(state1_id, state2_id)
                            if_merged = True  # 标记本轮发生了合并
                            if verbose: print(f"✅ single_merge success {state1_id} <- S{state2_id}")
                            if verbose: print(f" conduct NFA_merge S{state1_id}")
                            keep_state_id = min(state1_id, state2_id)
                            self.NFA_merge(keep_state_id,verbose=verbose)

                            break # exit j loop

                if if_merged == True:
                    break   # exit i loop

def single_infer(
        atm: Automaton,
        test_pos: List[List[str]],
        test_neg: List[List[str]],
        ATM_fileName: str,
        k_vector: Optional[Dict[str, int]] = None,
        all_k: int = 2,
        k_aggregation_mode: Literal["max", "min"] = "max",
        output_dir: str = "output",
        global_merge_verbose: bool = False,
        eval_verbose: bool = True,
) -> Dict[str, Any]:
    
    if k_vector is not None:
        atm.initialize_k_vector(values=k_vector)
    else:
        atm.initialize_k_vector(values=None, All_k=all_k)

    
    atm.Global_merge(verbose=global_merge_verbose, k_aggregation_mode=k_aggregation_mode)
    atm.export_to_dot(file_name=ATM_fileName)

    # ATM_BCR_fileName = f"{ATM_fileName}_ATM_BCR"
    # metrics = atm.evaluate_bcr(
    #     test_pos,
    #     test_neg,
    #     verbose=eval_verbose,
    #     filename=ATM_BCR_fileName,
    #     output_dir=output_dir,
    # )

    return 
    
def optimal_k_vector(
    raw_training_file: Tuple[List[List[str]], List[List[str]]],
    k_upper: int,
    *,
    train_ratio: float = 0.6,
    seed: int = 20,
    k_aggregation_mode: Literal["max", "min"] = "max",
    verbose: bool = True,
) -> Dict[str, Any]:
    
    if k_upper < 1:
        raise ValueError("k_upper must >= 1")
    
    raw_pos, raw_neg = parse_traces(raw_training_file)
    
    # split_train_test 会原地 shuffle，所以先深拷贝
    pos_cp = copy.deepcopy(raw_pos)
    neg_cp = copy.deepcopy(raw_neg)

    train_pos, train_neg, val_pos, val_neg = split_train_test(pos_cp,neg_cp,train_ratio,seed)

    base_atm  =  Automaton(name="optimal_k_search_base")
    base_atm.build_PTA_from_trace(train_pos, train_neg)
    base_atm.update_alphabet()
    alphabet = sorted(base_atm.alphabet)

    if len(alphabet) == 0:
        raise ValueError("alphabet 为空，无法搜索 k-vector")
    
    all_results: List[Dict[str, Any]] = []
    best_bcr = float("-inf")
    best_k_vector: Optional[Dict[str, int]] = None

    for ks in itertools.product(range(1, k_upper + 1), repeat=len(alphabet)):
        kv = {sym: int(k) for sym, k in zip(alphabet, ks)}
        # 每个候选都在 fresh copy 上跑，避免互相污染
        atm = base_atm.copy_automaton()
        atm.initialize_k_vector(values=kv)
        atm.Global_merge(verbose=False, k_aggregation_mode=k_aggregation_mode)
        metrics = atm.evaluate_bcr(val_pos, val_neg, verbose=False)
        bcr = metrics["BCR"]
        single_result = {
            "k_vector": kv,
            "BCR": bcr,
            "sensitivity": metrics["sensitivity"],
            "specificity": metrics["specificity"],
        }
        if verbose: print(single_result)
        all_results.append(single_result)
        if bcr > best_bcr:
            best_bcr = bcr
            best_k_vector = kv
    result = {
        "best_k_vector": best_k_vector,
        "best_bcr": best_bcr,
        "num_candidates": len(all_results),
        "alphabet": alphabet,
        "all_results": all_results,
    }
    if verbose:
        print("=== optimal_k_vector result ===")
        print(f"alphabet: {alphabet}")
        print(f"num_candidates: {result['num_candidates']}")
        print(f"best_bcr: {best_bcr:.4f}")
        print(f"best_k_vector: {best_k_vector}")

    return result

def optimal_k_vector_cv(
    raw_training_file,
    k_upper: int,
    *,
    n_splits: int = 5,
    seed: int = 20,
    k_aggregation_mode: Literal["max", "min"] = "max",
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    使用 K-fold cross validation 搜索最优 k-vector：
      对每个候选 k-vector，计算 K 折平均 BCR，取平均 BCR 最大者
    """
    if k_upper < 1:
        raise ValueError("k_upper must >= 1")
    raw_pos, raw_neg = parse_traces(raw_training_file)
    folds = k_fold_split(raw_pos, raw_neg, n_splits=n_splits, seed=seed)
    # 先拿 alphabet（用全量训练集建 PTA 只用于确定搜索维度）
    t0 = time.perf_counter()
    base_atm = Automaton(name="optimal_k_search_base_cv")
    base_atm.build_PTA_from_trace(raw_pos, raw_neg)
    base_atm.update_alphabet()
    alphabet = sorted(base_atm.alphabet)
    if len(alphabet) == 0:
        raise ValueError("alphabet 为空，无法搜索 k-vector")
    all_results: List[Dict[str, Any]] = []
    best_mean_bcr = float("-inf")
    best_k_vector: Optional[Dict[str, int]] = None
    for ks in itertools.product(range(1, k_upper + 1), repeat=len(alphabet)):
        kv = {sym: int(k) for sym, k in zip(alphabet, ks)}
        fold_scores = []
        fold_sens = []
        fold_spec = []
        for fold_idx, (train_pos, train_neg, val_pos, val_neg) in enumerate(folds, start=1):
            atm = Automaton(name=f"cv_fold_{fold_idx}")
            atm.build_PTA_from_trace(train_pos, train_neg)
            atm.initialize_k_vector(values=kv)
            atm.Global_merge(verbose=False, k_aggregation_mode=k_aggregation_mode)
            m = atm.evaluate_bcr(val_pos, val_neg,timer=None, verbose=False)
            fold_scores.append(m["BCR"])
            fold_sens.append(m["sensitivity"])
            fold_spec.append(m["specificity"])
        mean_bcr = sum(fold_scores) / len(fold_scores)
        mean_sens = sum(fold_sens) / len(fold_sens)
        mean_spec = sum(fold_spec) / len(fold_spec)
        single_result = {
            "k_vector": kv,
            "mean_BCR": f"{mean_bcr:.4f}",
            "mean_sensitivity": f"{mean_sens:.4f}",
            "mean_specificity": f"{mean_spec:.4f}",
            "fold_BCRs": [f"{x:.4f}" for x in fold_scores],
        }
        all_results.append(single_result)
        if verbose:
            print(single_result)
        if mean_bcr > best_mean_bcr:
            best_mean_bcr = mean_bcr
            best_k_vector = kv
    
    result = {
        "best_k_vector": best_k_vector,
        "best_bcr": best_mean_bcr,  # 为了兼容你原先字段名
        "num_candidates": len(all_results),
        "alphabet": alphabet,
        "n_splits": n_splits,
        "all_results": all_results,
    }
    elapsed = time.perf_counter() - t0
    print(f"⏱️ optimal_k_vector_cv completed in {round(elapsed, 2)} seconds")
    if verbose:
        print("=== optimal_k_vector_cv result ===")
        print(f"alphabet: {alphabet}")
        print(f"n_splits: {n_splits}")
        print(f"num_candidates: {result['num_candidates']}")
        print(f"best_bcr(mean cv): {best_mean_bcr:.4f}")
        print(f"best_k_vector: {best_k_vector}")
    return result

def infer_pipline(output_dir: str, raw_train_file: str, test_file: str) -> dict:
    t0 = time.perf_counter()
    train_pos, train_neg = parse_traces(raw_train_file)
    test_pos, test_neg = parse_traces(test_file)

    ATM_name = Path(raw_train_file).stem

    atm = Automaton(ATM_name)
    atm.build_PTA_from_trace(train_pos,train_neg)
    pta_metrics = atm.evaluate_PTA(test_pos, test_neg,output_dir=output_dir, filename=f"{ATM_name}_PTA_BCR")
    
    atm.export_pta_to_json(output_dir=output_dir, filename=f"{ATM_name}_PTA")
    
    # optimal_kv = optimal_k_vector(raw_train_file,2,train_ratio=0.7,verbose=False)["best_k_vector"]
    optimal_kv = optimal_k_vector_cv(raw_train_file, k_upper=3, n_splits=5, seed=20, verbose=True)["best_k_vector"]
    k_vector_to_json(optimal_kv,output_dir,f"{ATM_name}_optimal_kv")

    single_infer(atm,test_pos, test_neg, ATM_name,k_vector=optimal_kv,k_aggregation_mode="max",output_dir=output_dir,global_merge_verbose=False,eval_verbose=True)

    total_time_sec = time.perf_counter() - t0

    atm.evaluate_bcr(test_pos, test_neg, timer=total_time_sec, verbose=True, filename=f"{ATM_name}_ATM_BCR", output_dir=output_dir)

    print(f"✅ {ATM_name} finished in {round(total_time_sec, 2)} s")

    return {
        "ATM_name": ATM_name,
        "optimal_k_vector": optimal_kv,
        "pta_metrics": pta_metrics,
        # "infer_metrics": infer_metrics,
        "total_time_sec": round(total_time_sec, 4),
    }


            
# testing area
def single_infer_test():
    train_file = 'training_data/automaton_10_2_5_0~2.txt' 
    test_file  = 'training_data/automaton_10_2_5_0~99.txt'
    automaton_name = Path(train_file).name

    train_pos, train_neg = parse_traces(train_file)
    test_pos, test_neg = parse_traces(test_file)

    atm = Automaton(automaton_name)
    atm.build_PTA_from_trace(train_pos, train_neg)
    pta_result = atm.evaluate_PTA(test_pos,test_neg,filename=f"{automaton_name}_PTA")

    k_vector = {"L0":2,"L1":2,"L2":2,"L3":2,"L4":2}

    result = single_infer(atm,test_pos, test_neg, "test25_ATM", k_vector=k_vector,k_aggregation_mode="max",output_dir="./output/10_state", eval_verbose=False)
    print(result)

def single_infer_test_NN(train_file=None, test_file  = 'training_data/automaton_10_2_5_0~99.txt', k_vector=None, output_name=None):
    timer0 = time.perf_counter()
    test_file  = 'training_data/automaton_10_2_5_0~99.txt'
    automaton_name = Path(train_file).name

    train_pos, train_neg = parse_traces(train_file)
    test_pos, test_neg = parse_traces(test_file)

    atm = Automaton(automaton_name)
    atm.build_PTA_from_trace(train_pos, train_neg)
    pta_result = atm.evaluate_PTA(test_pos,test_neg,filename=f"{automaton_name}_PTA")

    single_infer(atm,test_pos, test_neg, output_name, k_vector=k_vector,k_aggregation_mode="max",output_dir="./output/10_state", eval_verbose=False)
    timer1 = time.perf_counter()
    total_time_sec = timer1 - timer0
    atm.evaluate_bcr(test_pos, test_neg, timer=total_time_sec, verbose=True, filename=f"{automaton_name}_ATM_from_NN_BCR", output_dir="output/10_state")


def main():
    # raw_train_file = 'training_data/automaton_10_2_5_0~0.txt' 
    # test_file      = 'training_data/automaton_10_2_5_0~99.txt'
    # output_dir = "output/10_state"

    # global infer pipeline for all datasets

    # for i in range(0,3):
    #     raw_train_file = f"training_data/automaton_10_2_5_0~{i}.txt"
    #     test_file      = 'training_data/automaton_10_2_5_0~99.txt'
    #     output_dir = "output/10_state"
    #     infer_pipline(output_dir, raw_train_file, test_file)

    single_infer_test_NN(train_file='training_data/automaton_10_2_5_0~0.txt',
                         k_vector={"L0":2,"L1":2,"L2":1,"L3":1,"L4":2}, 
                         output_name="automaton_10_2_5_0~0_ATM_from_NN")
    
    single_infer_test_NN(train_file='training_data/automaton_10_2_5_0~1.txt',
                         k_vector={"L0":1,"L1":2,"L2":1,"L3":1,"L4":2}, 
                         output_name="automaton_10_2_5_0~1_ATM_from_NN")
    
    single_infer_test_NN(train_file='training_data/automaton_10_2_5_0~2.txt',
                         k_vector={"L0":2,"L1":1,"L2":1,"L3":2,"L4":1}, 
                         output_name="automaton_10_2_5_0~2_ATM_from_NN")
    
    single_infer_test_NN(train_file='training_data/automaton_10_2_5_0~3.txt',
                         k_vector={"L0":2,"L1":2,"L2":2,"L3":1,"L4":1}, 
                         output_name="automaton_10_2_5_0~3_ATM_from_NN")
    
    single_infer_test_NN(train_file='training_data/automaton_10_2_5_0~4.txt',
                         k_vector={"L0":1,"L1":1,"L2":2,"L3":1,"L4":2}, 
                         output_name="automaton_10_2_5_0~4_ATM_from_NN")
    
    single_infer_test_NN(train_file='training_data/automaton_10_2_5_0~5.txt',
                         k_vector={"L0":2,"L1":1,"L2":2,"L3":2,"L4":2}, 
                         output_name="automaton_10_2_5_0~5_ATM_from_NN")
    
    single_infer_test_NN(train_file='training_data/automaton_10_2_5_0~6.txt',
                         k_vector={"L0":2,"L1":2,"L2":1,"L3":2,"L4":2}, 
                         output_name="automaton_10_2_5_0~6_ATM_from_NN")
    
    single_infer_test_NN(train_file='training_data/automaton_10_2_5_0~7.txt',
                         k_vector={"L0":2,"L1":1,"L2":2,"L3":1,"L4":1}, 
                         output_name="automaton_10_2_5_0~7_ATM_from_NN")
    
    single_infer_test_NN(train_file='training_data/automaton_10_2_5_0~8.txt',
                         k_vector={"L0":1,"L1":1,"L2":1,"L3":2,"L4":1}, 
                         output_name="automaton_10_2_5_0~8_ATM_from_NN")
    
    single_infer_test_NN(train_file='training_data/automaton_10_2_5_0~9.txt',
                         k_vector={"L0":2,"L1":1,"L2":2,"L3":2,"L4":2}, 
                         output_name="automaton_10_2_5_0~9_ATM_from_NN")




    
if __name__ == "__main__":
    main()
