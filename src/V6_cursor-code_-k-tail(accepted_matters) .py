import sys
sys.stdout = open("output.txt", "w", encoding="utf-8")


def read_trace_file(file_path=None):
    """
    Generic function to read trace files (1_pos.txt/1_neg.txt)
    :param file_path: String, path of the trace file (e.g., "1_pos.txt")
    :return: List of lists, format: [[L1,L0,...], [L1,L0,...], ...]
             Each sublist represents a single trace (sequence of L0/L1)
    """

    traces = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Remove leading/trailing whitespace/newlines and split by comma
            trace = line.strip().split(',')
            # Filter empty elements (avoid invalid data from blank lines/extra commas)
            trace = [elem for elem in trace if elem]
            # Only add non-empty traces to the list
            if trace:
                traces.append(trace)
    return traces

def read_labeled_traces_file(file_path=None):
    """
    读取带 +/- 标签的 trace 文件：
    - 以 '+' 开头：正例
    - 以 '-' 开头：负例
    :return: (positive_traces, negative_traces)，每项为 List[List[str]]
    """
    positive_traces = []
    negative_traces = []
    with open(file_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            first = line[0]
            rest = line[1:].lstrip()  # 去掉 +/- 后的内容
            if first == "+":
                bucket = positive_traces
            elif first == "-":
                bucket = negative_traces
            else:
                # 无标签行：可选当作旧格式正例，或跳过
                parts = [p.strip() for p in line.split(",") if p.strip()]
                if parts:
                    positive_traces.append(parts)
                continue
            trace = [elem.strip() for elem in rest.split(",") if elem.strip()]
            if trace:
                bucket.append(trace)
    return positive_traces, negative_traces

def extract_alphabet(traces=None):
    """
    Extract alphabet (all unique symbols) from positive traces
    :param positive_traces: List of positive traces (nested list: [[L0,L1,...], ...])
    :return: Set of unique symbols (alphabet) + sorted list for consistent order
    """

    alphabet = set()  # Use set to automatically deduplicate symbols
    for trace in traces:
        for symbol in trace:
            alphabet.add(symbol)
    # Convert to sorted list for consistent order (avoid randomness in set)
    alphabet_list = sorted(list(alphabet))
    return alphabet_list


def init_k_vector(alphabet=None, init_k=2):
    """
    Initialize k-vector with the same initial k value for all symbols
    :param alphabet: Set/list of unique symbols (alphabet)
    :param init_k: Initial k value (default: 1, common choice for k-tail)
    :return: Dictionary (k-vector): {symbol: init_k, ...}
    """
    k_vector = {symbol: init_k for symbol in alphabet}
    return k_vector


def format_tail(tail, indent=0):
    """
    格式化打印k-tail的嵌套结构，增加缩进和换行，提升可读性
    :param tail: 待打印的tail（列表/元组）
    :param indent: 缩进级别（控制换行后的空格数）
    :return: 格式化后的字符串
    """
    indent_str = "  " * indent  # 每级缩进2个空格
    if isinstance(tail, (list, tuple)):
        if len(tail) == 0:  # 空元组/列表
            return f"{indent_str}()"
        # 处理嵌套结构
        parts = []
        for i, item in enumerate(tail):
            if isinstance(item, (list, tuple)):
                # 子元素也是嵌套结构，递归格式化
                sub_part = format_tail(item, indent + 1)
                parts.append(f"\n{sub_part}")
            else:
                # 普通元素直接显示
                parts.append(f"{item}")
        # 拼接结果
        if len(parts) == 1:
            return f"{indent_str}({''.join(parts)})"
        else:
            return f"{indent_str}({','.join(parts)}\n{indent_str})"
    else:
        # 非容器类型直接返回
        return f"{indent_str}{tail}"
    

# 1. 定义状态类（仅保留核心属性：ID、转移、是否接受）
class State:
    def __init__(self, state_id=None):
        self.id = state_id               # 状态唯一ID
        self.transitions = []            # 转移列表: ((字符,目标状态))
        self.is_accept = False           # 是否为接受状态（轨迹终点）
    
    def get_transition(self):
        transitions = [(sym, tgt_state.id) for sym, tgt_state in self.transitions]
        return transitions
    
    

# 2. 定义极简PTA类（仅实现轨迹构建功能）
class PTA:
    def __init__(self):
        self.states_list = []                 # 存储所有状态
        self.initial_state = self._add_state()  # 初始状态（根节点）

    # 内部方法：添加新状态
    def _add_state(self):
        new_state = State(state_id=len(self.states_list))  # 用列表长度作为状态ID（自动递增）
        self.states_list.append(new_state)
        return new_state

    # 核心方法：从正例轨迹构建PTA
    def build_from_traces(self, traces=None):
        for trace in traces:          # 遍历每条轨迹
            current_state = self.initial_state # 每条轨迹从初始状态开始
            for symbol in trace:               # 遍历轨迹中的每个字符
                
                sym_found = False
                # 检查当前状态没有该字符的后续转移，如果有，则current_state 转移到下一个状态，
                for sym, tgt_state in current_state.transitions:
                    if sym == symbol:
                        current_state = tgt_state
                        sym_found = True
                        break
                # 检查当前状态没有该字符的后续转移，如果没有则创建新状态并添加转移，然后进入到下一个状态
                if not sym_found:
                    next_state = self._add_state()
                    current_state.transitions.append((symbol, next_state))
                    current_state = next_state
            # 当所有symbol都已经遍历之后，那肯定就是trace末端了，因此标记此刻的state为接受态
            current_state.is_accept = True

    # 辅助打印：查看PTA结构（便于验证）
    def print_pta(self):
        print(f"\n=== 极简PTA结构（总状态数：{len(self.states_list)}）===")
        print(f"初始状态ID：{self.initial_state.id}")
        for state in self.states_list:# 从state_list里面按照state的顺序进行遍历
            # 打印当前的state的ID、是否接受、后续转移关系
            accept_tag = "✅ accepted" if state.is_accept else "❌ unaccepted"
            transitions = state.get_transition()
            print(f"S{state.id} {accept_tag} | T：{transitions}")

    
    def accepts_trace(self, trace=None):
        """
        检查单条trace是否被当前PTA接受
        :param trace: 例如 ["L0", "L1", "L0"]
        :return: (is_accepted, fail_reason)
                 is_accepted: True/False
                 fail_reason: 失败原因（成功时为None）
        """
        if trace is None:
            return False, "trace is None"
        current_state = self.initial_state
        for step_idx, symbol in enumerate(trace):
            next_state = None
            for sym, tgt_state in current_state.transitions:# 这里是从当前PTA的当前状态的transition
                if sym == symbol:                           # 如果找到当前PTA下当前状态的transition中有个当前trace的符号，
                    next_state = tgt_state                  # 那就将next_state 标记为transition中的tgt_state
                    break                                   # 相当这个trace的当前符号在当前状态下找到了，找到了就可以break了
            if next_state is None:
                return False, f"step {step_idx}: no transition for symbol {symbol} from S{current_state.id}"
            current_state = next_state                      # 将当前state替换为tgt_state，相当于进入下一个state，然后继续循环-看trace的下一个符号是否在下一个state的transition中能否找到。
        if current_state.is_accept:
            return True, None
        return False, f"ended at non-accept state S{current_state.id}"    

    def validate_traces(self, traces=None, verbose=True):
        """
        检查多条trace是否都能被PTA接受
        :param traces: [[L0,L1,...], [L1,...], ...]
        :param verbose: 是否打印每条trace的结果
        :return: (all_passed, failed_cases)
                 all_passed: 是否全部通过
                 failed_cases: 失败详情列表
        """
        if traces is None:
            traces = []
        failed_cases = []
        for idx, trace in enumerate(traces):
            ok, reason = self.accepts_trace(trace)
            if verbose:
                if ok:
                    print(f"✅ Trace#{idx} accepted: {trace}")
                else:
                    print(f"❌ Trace#{idx} rejected: {trace} | reason: {reason}")
            if not ok:
                failed_cases.append({
                    "index": idx,
                    "trace": trace,
                    "reason": reason
                })
        all_passed = (len(failed_cases) == 0)
        print("\n================ Trace Validation Summary ================")
        print(f"Total traces: {len(traces)}")
        print(f"Accepted: {len(traces) - len(failed_cases)}")
        print(f"Rejected: {len(failed_cases)}")
        print(f"All passed: {all_passed}")
        print("=========================================================\n")
    

    def _state_exists(self, st):
        return any(s.id == st.id for s in self.states_list) #只要有任意一个状态的id和传入的st的id相等，就返回True，否则返回False。
    
    def _k_tail(self, state, k):
        """
        k-tail签名（包含accept信息）：
        - k=0时返回当前状态是否accept
        - k>0时返回 (accept, 按symbol排序的后续签名)
        """
        if k == 0:
            return ("ACC", state.is_accept)
        items = []
        for sym, nxt in state.transitions:
            sub = self._k_tail(nxt, k - 1)
            items.append((sym, sub))
        items.sort(key=lambda x: (x[0], str(x[1])))
        return ("ACC", state.is_accept, tuple(items))
    
    def merge_states(self, state_1=None, state_2=None):
        """
        合并state_2到state_1，并保持DFA：
        若同一symbol指向多个目标，则递归（迭代实现）继续合并这些目标。
        """
        # 边界检查：参数为空/两个状态相同/状态不存在 → 直接返回
        if state_1 is None or state_2 is None:
            return
        if state_1.id == state_2.id:
            return
        if (not self._state_exists(state_1)) or (not self._state_exists(state_2)):
            return
        
        # 用栈迭代，避免递归爆栈
        pair_stack = [(state_1, state_2)]
        seen_pairs = set()
        while pair_stack:
            s_keep, s_del = pair_stack.pop() # 弹出要合并的对：保留s_keep，删除s_del

            # 再次检查：状态相同/不存在 → 跳过
            if s_keep.id == s_del.id:
                continue
            if (not self._state_exists(s_keep)) or (not self._state_exists(s_del)):
                continue

            # 生成唯一key（排序id，避免(1,2)和(2,1)重复处理）
            key = tuple(sorted((s_keep.id, s_del.id)))
            if key in seen_pairs:
                continue
            seen_pairs.add(key)

            # 1) 合并accept属性， 只要其中一个是接受状态，合并后就是接受状态
            s_keep.is_accept = s_keep.is_accept or s_del.is_accept

            # 2) 把所有指向s_del的边改到s_keep（重定向入边）
            for s in self.states_list:
                for i, (sym, tgt) in enumerate(s.transitions):
                    if tgt.id == s_del.id:
                        s.transitions[i] = (sym, s_keep)

            # 3) 合并出边（先并上，后面统一处理冲突）
            for sym, tgt in s_del.transitions:
                if tgt.id == s_del.id:
                    tgt = s_keep  # 自环重定向：先让s_del里的自环指向s_keep
                s_keep.transitions.append((sym, tgt)) # 再让所有的s_del的transition指向s_keep 没毛病

            # 4) 删除s_del
            self.states_list = [s for s in self.states_list if s.id != s_del.id]

            # 5) 检查s_keep上是否出现“同symbol多个目标”
            #    如果有，把这些目标两两并入第一个目标
            sym_to_targets = {}
            for sym, tgt in s_keep.transitions:
                sym_to_targets.setdefault(sym, {})  # 设置了一个插键规则：键存在则返回原值，不存在则赋值空字典并返回
                sym_to_targets[sym][tgt.id] = tgt  # 按id去重 它只会去掉“同一个目标状态被重复记录多次”的重复项（例如同样的 L0 -> S5 出现两次）
            for sym, id2st in sym_to_targets.items(): # 找内层字典里的
                targets = list(id2st.values()) # 找内层字典里的value，也就是同sym下，不同tgt.id对应不同的state（也就是找到NFA的target state，准备进行合并）
                if len(targets) <= 1: # 如果同sym下只有一个target state，那就继续下一个循环（找下一个sym下的情况）
                    continue
                targets.sort(key=lambda x: x.id) # 如果同sym下有多个target state，那就state先按id排序
                rep = targets[0]                 # 选ID最小的state作为合并后要保留的对象
                for other in targets[1:]:        # 如果其他的state与rep不同，那么就加入栈循环中
                    if rep.id != other.id:
                        pair_stack.append((rep, other))

            # 6) 当前先做一次轻量去重（s_keep的transition中相同sym+target只保留1个）
            uniq = []
            seen = set()
            for sym, tgt in s_keep.transitions:
                k = (sym, tgt.id)
                if k not in seen:
                    seen.add(k)
                    uniq.append((sym, tgt))
            s_keep.transitions = uniq

    def find_state_parents(self):
        """
        返回每个状态的父状态和进入字符:
        {state_id: [(parent_id, symbol), ...]}
        """
        parent_map = {s.id: [] for s in self.states_list}
        for s in self.states_list:
            for sym, child in s.transitions:
                parent_map[child.id].append((s.id, sym))
        return parent_map

    def k_tail_merge(self, k=2):
        """
        稳定版 k-tail 合并：
        每次只做一次合并，合并后立刻基于最新图重新搜索候选对。
        """
        step = 1

        while True:
            merged_pair = None
            current_states = sorted(self.states_list, key=lambda s: s.id)

            print(f"\n===== 第{step}次 k-tail 合并搜索 (k={k}) =====")

            # 在“当前最新图”中找第一对可合并状态
            for i in range(len(current_states)):
                s1 = current_states[i]
                if not self._state_exists(s1):
                    continue

                for j in range(i + 1, len(current_states)):
                    s2 = current_states[j]
                    if not self._state_exists(s2):
                        continue
                    if s1.id == s2.id:
                        continue

                    t1 = self._k_tail(s1, k)
                    t2 = self._k_tail(s2, k)

                    if t1 == t2:
                        merged_pair = (s1, s2)
                        break

                if merged_pair is not None:
                    break

            # 当前图找不到可合并对，就结束
            if merged_pair is None:
                print("本轮无可合并状态对，结束。")
                break #用这里来结束总的while loop

            # 执行一次合并，然后进入下一轮（基于最新图）
            s1, s2 = merged_pair
            print(f"✅ 合并 S{s1.id} <- S{s2.id}")
            self.merge_states(s1, s2)
            print(f"当前状态数: {len(self.states_list)}")
            step += 1

        print("\n🎉 k-tail 合并完成")
        self.print_pta()
    
    def is_dfa(self, verbose=True):
        """
        检查当前自动机是否为 DFA（部分 DFA 也算：未出现的符号视为无转移）。
        规则：每个状态上，同一 symbol 至多指向一个目标状态。
        """
        ok = True
        for s in self.states_list:
            seen = {}  # symbol -> first target id
            for sym, tgt in s.transitions:
                if sym in seen:
                    if seen[sym] != tgt.id:
                        ok = False
                        if verbose:
                            print(
                                f"❌ 非确定性: S{s.id} 上符号 {sym} 指向多个目标 "
                                f"S{seen[sym]} 与 S{tgt.id}"
                            )
                else:
                    seen[sym] = tgt.id
        if verbose and ok:
            print("✅ 当前图是 DFA（每个状态、每个符号至多一条出边）")
        return ok

def main():
    training_pos_traces = read_trace_file(file_path="D:/NonEntertainment/Life_Data/UK_Sheffield/Module/COM6911_Team_Project/adaptive-k-tails-automata/data/automaton_5s/automaton_5s/training_data/2_pos.txt")
    # positive_traces, negative_traces= read_labeled_traces_file(file_path="D:/NonEntertainment/Life_Data/UK_Sheffield/Module/COM6911_Team_Project/adaptive-k-tails-automata/data/training_data/automaton_5s~1.txt")
    print(training_pos_traces)
    print()
    alphabet = extract_alphabet(traces=training_pos_traces)
    print(f"alphabet : {alphabet}")
    print()
    k_vector = init_k_vector(alphabet=alphabet, init_k=2)
    print(f"k_vector : {k_vector}")

        # 2. 构建极简PTA
    pta = PTA()
    pta.build_from_traces(training_pos_traces)

    # 3. 打印PTA结构（验证是否构建成功）
    pta.print_pta()

    pta.k_tail_merge(k=3)
    
    testing_pos_traces = read_trace_file(file_path="D:/NonEntertainment/Life_Data/UK_Sheffield/Module/COM6911_Team_Project/adaptive-k-tails-automata/data/automaton_5s/automaton_5s/testing_data/2_pos.txt")
    # # testing_pos_traces = read_trace_file(file_path="./Input/data/data/5 state automata/1/training_data/3_pos.txt")

    # positive_traces_testing= read_labeled_traces_file(file_path="D:/NonEntertainment/Life_Data/UK_Sheffield/Module/COM6911_Team_Project/adaptive-k-tails-automata/data/training_data/automaton_5s~1.txt")
    # testing_pos_traces = read_trace_file(file_path="./Input/data/data/5 state automata/1/training_data/3_pos.txt")
    pta.validate_traces(testing_pos_traces, verbose=True)
    pta.is_dfa(verbose=True)
    # pta.get_k_tail(state=pta.states_list[2],k=2)


    # pta.merge_states(state_left=pta.states_list[1],state_right=pta.states_list[4])
    # pta.print_pta()


if __name__ == "__main__":
    main()
