import sys
# sys.stdout = open("output.txt", "w", encoding="utf-8")


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


    def get_k_tail_with_visited(self, state=None, k=None, visited=None):
        """
        计算一个状态的k-tail（递归实现）
        :param state: 目标状态
        :param k: k值（如k_L0=1）
        :param visited: 避免循环（简单PTA可忽略，你的场景无循环）
        :return: 元组形式的k-tail（可哈希，便于比较）
        """
        print()
        print(f"state_ID = {state.id}")
        print(f"state_Transition = {state.get_transition()}")
        print(f"k = {k}")
        print(f"visited = {visited}")
        if k == 0 or not state.transitions:  # k=0或无转移，返回空
            return "end"
        if visited is None:
            visited = set()
        if state.id in visited:  # 避免循环
            return tuple()
        visited.add(state.id)

        # # 递归计算每个转移的k-1-tail
        # tail = []
        # # NFA：按 symbol 排序，保证和原来一样
        # sym_list = sorted({sym for sym, _ in state.transitions})
        # for symbol in sym_list:  
        #     # 核心修改：收集该symbol对应的所有目标状态（适配NFA）
        #     next_states_list = [tgt_state for sym, tgt_state in state.transitions if sym == symbol]
            
        #     # 遍历该symbol下的所有目标状态
        #     for next_state in next_states_list:
        #         print(f"next_symbol = {symbol}| next_state = {next_state.id}")
        #         # 递归计算每个目标状态的k-1-tail
        #         sub_tail = self.get_k_tail(next_state, k-1, visited.copy())
        #         tail.append((symbol, next_state.id, sub_tail))
        
        # print(f"tail = {tail}")
        # return tuple(tail)  # 转元组便于比较

        tail = []
        for (sym, next_states) in state.transitions:
            print(f"next_symbol = {sym}| next_state = {next_states.id}")
            sub_tail = self.get_k_tail(state=next_states,k=k-1,visited=visited.copy())
            tail.append((sym,next_states.id,sub_tail))
        
        #统一按照symbol升序排列，排列的原因是因为后续需要比对tail是否一致，用元组进行比对就需要先排序，否则同样内容的tail会因为tail顺序不同而被认定为不一致
        tail.sort(key=lambda x: (x[0], x[1]))
        print(f"tail = {tail}")
        return tuple(tail)  # 转元组便于比较

    def get_k_tail(self, state=None, k=None):
        """
        计算一个状态的k-tail（递归实现）
        :param state: 目标状态
        :param k: k值（如k_L0=1）
        :param visited: 避免循环（简单PTA可忽略，你的场景无循环）
        :return: 元组形式的k-tail（可哈希，便于比较）
        """
        print()
        print(f"state_ID = {state.id}")
        print(f"state_Transition = {state.get_transition()}")
        print(f"k = {k}")
        if k == 0 or not state.transitions:  # k=0或无转移，返回空
            return "end"


        # # 递归计算每个转移的k-1-tail
        # tail = []
        # # NFA：按 symbol 排序，保证和原来一样
        # sym_list = sorted({sym for sym, _ in state.transitions})
        # for symbol in sym_list:  
        #     # 核心修改：收集该symbol对应的所有目标状态（适配NFA）
        #     next_states_list = [tgt_state for sym, tgt_state in state.transitions if sym == symbol]
            
        #     # 遍历该symbol下的所有目标状态
        #     for next_state in next_states_list:
        #         print(f"next_symbol = {symbol}| next_state = {next_state.id}")
        #         # 递归计算每个目标状态的k-1-tail
        #         sub_tail = self.get_k_tail(next_state, k-1, visited.copy())
        #         tail.append((symbol, next_state.id, sub_tail))
        
        # print(f"tail = {tail}")
        # return tuple(tail)  # 转元组便于比较

        tail = []
        for (sym, next_states) in state.transitions:
            print(f"next_symbol = {sym}| next_state = {next_states.id}")
            sub_tail = self.get_k_tail(state=next_states,k=k-1)
            tail.append((sym,sub_tail))
        
        #统一按照symbol升序排列，排列的原因是因为后续需要比对tail是否一致，用元组进行比对就需要先排序，否则同样内容的tail会因为tail顺序不同而被认定为不一致
        tail.sort(key=lambda x: (x[0], x[1]))
        print(f"tail = {tail}")
        return tuple(tail)  # 转元组便于比较
    
    def find_state_parents(self):
        """
        找到每个状态的父状态和触发字符：{state_id: [(父状态ID, 触发字符), ...]}
        核心：为了知道每个状态是被哪个字符触发的（从而取对应k值）
        """
        parent_map = {state.id: [] for state in self.states_list}
        for state in self.states_list:
            for symbol, child_state in state.transitions:
                parent_map[child_state.id].append((state.id, symbol))
        print("Finding entering transition:")
        print(parent_map)
        return parent_map


    def merge_states(self, state_1=None, state_2=None):
        """
        合并两个状态（将state2的转移/接受状态合并到state1，删除state2）
        """
        # 1. 合并接受状态（只要有一个是接受状态，合并后就是接受状态）
        state_1.is_accept = state_1.is_accept or state_2.is_accept


        # 2. 暂存 state_2 的转移用于后续比对
        old_transitions_2 = list(state_2.transitions)
        # print(f"old_transition_2 = {old_transitions_2}")

        # 2. 合并转移（state_2的转移添加到state_1，避免重复）
        for symbol, target_state in state_2.transitions:
                state_1.transitions.append((symbol, target_state))  # 直接添加

        # 3. 更新所有指向state_2的转移，改为指向state_1
        for state in self.states_list:
            # 遍历副本，避免修改列表时出错
            for i, (sym, tgt_state) in enumerate(state.transitions):
                if tgt_state.id == state_2.id:
                    state.transitions[i] = (sym, state_1)


        # 4. 从PTA中删除state_2
        self.states_list = [s for s in self.states_list if s.id != state_2.id]
        # 重新分配状态ID（可选，便于阅读）
        # for idx, state in enumerate(self.states_list):
        #     state.id = idx

        # 5. 【核心改动】处理转移冲突（确定化递归）
        # 遍历 state_2 原有的转移，看 state_1 是否已经有了相同字符的转移
        for sym_2, tgt_2 in old_transitions_2:
            # 找到 state_1 中相同字符的转移
            # print(f"sym_2 = {sym_2}")
            # print(f"tgt_2 = {tgt_2}")
            match_found = False
            for i, (sym_1, tgt_1) in enumerate(state_1.transitions):
                # print(f"sym_1 = {sym_1}")
                # print(f"tgt_1 = {tgt_1}")
                if sym_1 == sym_2:
                    match_found = True
                    # 如果目标状态不同，递归合并它们
                    if tgt_1.id != tgt_2.id:
                        self.merge_states(tgt_1, tgt_2)
                    # break 
            
            # 如果 state_1 之前没有这个字符的转移，直接添加（注意此时 tgt_2 可能已被重定向）
            # if not match_found:
            #     state_1.transitions.append((sym_2, tgt_2))

        # 6. 【新增：彻底去重】由于递归合并可能导致 tgt_1 后来变成了 tgt_2，
        # 我们对 state_1 的 transitions 列表进行一次最终去重
        unique_transitions = []
        seen = set()
        for sym, tgt in state_1.transitions:
            if (sym, tgt.id) not in seen:
                unique_transitions.append((sym, tgt))
                seen.add((sym, tgt.id))
        state_1.transitions = unique_transitions

                    

    def adaptive_k_tail_merge_not_strict(self, k_vector=None, using_maximum_or_minimum_k="min"):
        """
        非严格模式：按“轮次”执行k-tail合并（你的想法）
        - 每轮完整遍历所有状态对，本轮有合并则开启下一轮，无则结束
        :param k_vector: 字典形式，如{'L0':1, 'L1':1}
        :param using_maximum_or_minimum_k: 极值选择，可选"max"/"min"；默认使用"min"
        """
        print("\n*************************** adaptive_k_tail_merge_not_strict *****************************\n")
        
        round_num = 1  # 记录当前是第几轮合并
        has_merged_in_round = True  # 标记是否需要开启下一轮
        
        # 核心循环：每轮完整遍历 → 检查是否有合并 → 决定是否开启下一轮
        while has_merged_in_round:
            # 每轮初始化
            has_merged_in_round = False  # 初始化为“本轮无合并”
            merged_this_round = set()    # 本轮已合并的状态ID（避免本轮重复处理）
            parent_map = self.find_state_parents()  # 每轮重新获取最新父状态映射
            states_copy = self.states_list.copy()   # 每轮获取最新状态列表
            
            print(f"\n=====================================")
            print(f"🚀 第 {round_num} 轮k-tail合并（当前状态数：{len(states_copy)}）")
            print("=====================================\n")

            # 本轮完整遍历所有状态对（i<j）
            for i in range(len(states_copy)):
                s1 = states_copy[i]
                # 跳过：已合并/已被删除的状态
                if s1.id in merged_this_round or s1 not in self.states_list:
                    continue
                
                for j in range(i+1, len(states_copy)):
                    s2 = states_copy[j]
                    # 跳过：已合并/已被删除的状态
                    if s2.id in merged_this_round or s2 not in self.states_list:
                        continue

                    # 1. 提取共同进入字符
                    s1_triggers = set([p[1] for p in parent_map.get(s1.id, [])])
                    s2_triggers = set([p[1] for p in parent_map.get(s2.id, [])])
                    print(f"!!!!!!!!!!!!!!!!!!!!! 检查状态对 (S{s1.id}, S{s2.id}) !!!!!!!!!!!!!!!!!")
                    print(f"S{s1.id} 进入字符 = {s1_triggers} | 转移 = {s1.get_transition()}")
                    print(f"S{s2.id} 进入字符 = {s2_triggers} | 转移 = {s2.get_transition()}")

                    common_triggers = s1_triggers & s2_triggers
                    if not common_triggers:
                        print(f"❌ S{s1.id}和S{s2.id}无共同进入字符，跳过\n")
                        continue
                    
                    # 2. 计算极值k值
                    common_k_values = [k_vector.get(c, 1) for c in common_triggers]
                    if using_maximum_or_minimum_k == "max":
                        k = max(common_k_values)
                        k_type = "最大值"
                    elif using_maximum_or_minimum_k == "min":
                        k = min(common_k_values)
                        k_type = "最小值"
                    else:
                        print(f"❌ 无效极值参数：{using_maximum_or_minimum_k}，默认用最小值")
                        k = min(common_k_values)
                        k_type = "最小值"
                    
                    # 3. 计算k-tail并比对
                    print(f"\n🔍 验证S{s1.id}和S{s2.id}（共同字符：{common_triggers}，{k_type}k值：{k}）")
                    print(f"################ 计算S{s1.id}的{k}-tail #################")
                    s1_tail = self.get_k_tail(s1, k)
                    print(f"################ 计算S{s2.id}的{k}-tail #################")
                    s2_tail = self.get_k_tail(s2, k)
                    
                    if s1_tail == s2_tail:
                        print(f"✅ 第{round_num}轮：合并S{s1.id}和S{s2.id}（k值：{k}）")
                        self.merge_states(s1, s2)
                        merged_this_round.add(s2.id)  # 标记本轮已合并
                        has_merged_in_round = True    # 标记“本轮有合并”，需要下一轮
                        print(f"⚠️  S{s2.id}已合并，本轮继续遍历剩余状态对\n")
                    else:
                        print(f"❌ S{s1.id}和S{s2.id}的{k}-tail不相等，不合并")
                        print(f"S{s1.id} {k}-tail = {s1_tail}")
                        print(f"S{s2.id} {k}-tail = {s2_tail}\n\n\n")
            
            # 本轮遍历结束，更新轮次
            print(f"\n🔚 第 {round_num} 轮合并结束（本轮合并状态数：{len(merged_this_round)}）")
            round_num += 1
            
            # 若本轮无合并，结束循环
            if not has_merged_in_round:
                print("\n🎉 无新状态可合并，k-tail合并完成！")
                print(f"📊 最终PTA状态数：{len(self.states_list)}")
                print("====================================================================\n")
        print("\n==================== 合并后的PTA结构 ====================\n")
        self.print_pta()

def main():
    training_pos_traces = read_trace_file(file_path="./Input/data/data/5 state automata/1/training_data/test4.txt")
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
    # pta.get_k_tail(state=pta.states_list[2],k=2)
    pta.get_k_tail(state=pta.initial_state,k=2)
    pta.find_state_parents()
    # pta.merge_states(state_left=pta.states_list[1],state_right=pta.states_list[4])
    # pta.print_pta()
    pta.adaptive_k_tail_merge_not_strict(k_vector=k_vector, using_maximum_or_minimum_k="min")

if __name__ == "__main__":
    main()
