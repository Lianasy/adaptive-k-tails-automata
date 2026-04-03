from k_tail_V4_4_compute_k_tailV3_mergeV1 import *


def build_PTA_mannually_example1() -> Automaton:
    """
    手动构造示例 PTA：唯一状态 A（即初始状态 0），在符号 "a" 上自环 A --a--> A。
    将 A 标为接受态，对应语言 a*（含空串）。
    """
    atm = Automaton(name="example1")
    A = atm.initial_state
    A.transitions.append(("a", A))
    A.is_accept = True
    return atm

def build_PTA_mannually_example2() -> Automaton:
    """
    手动 PTA：两状态 A(初始, id=0)、B(id=1)，环 A --a--> B --b--> A。
    仅 A 为接受态（典型：语言包含 ε 与 (ab)^n 等以 A 结尾的串）。
    """
    atm = Automaton(name="example2")
    A = atm.initial_state
    B = atm._add_state()
    A.transitions.append(("a", B))
    B.transitions.append(("b", A))
    atm.alphabet.update({"a", "b"})
    A.is_accept = True
    B.is_accept = False
    return atm

def build_PTA_mannually_example3() -> Automaton:
    train_file = 'training_data/automaton_5_2_2_0~0.txt' 
    test_file  = 'training_data/automaton_5_2_2_0~1.txt'
    automaton_name = Path(train_file).name

    train_pos, train_neg = parse_traces(train_file)
    test_pos, test_neg = parse_traces(test_file)

    atm = Automaton(automaton_name)
    atm.build_PTA_from_trace(train_pos)

    return atm



def test1():
    atm = build_PTA_mannually_example1()
    atm.export_to_dot(file_name="0-self-circle")
    atm.compute_state_k_tail(0,4)

def test2():
    atm = build_PTA_mannually_example2()
    atm.export_to_dot(file_name="01-mutual-circle")
    atm.compute_state_k_tail(1,4)

def test3():
    atm = build_PTA_mannually_example3()
    all_state_ids = list(atm.states_Dict.keys())
    random_state_id = random.choice(all_state_ids)

    # 随机选 k = 0 ~ 4
    random_k = random.randint(0, 4)
    random_state = 98
    random_k = 4
    print(f"🎲 随机选择状态: S{random_state}")
    print(f"🎲 随机选择 k    : {random_k}")
    print()

    atm.compute_state_k_tail(start_state_id=random_state_id, k=random_k)

def test4():
    atm = build_PTA_mannually_example3()
    atm.export_to_dot(file_name=f"{atm.name}" + "_before_merge")
    all_state_ids = list(atm.states_Dict.keys())
    # keep_state_id = random.choice(all_state_ids)
    # delete_state_id = random.choice(all_state_ids)
    keep_state_id = 21
    delete_state_id = 22

    atm.do_single_merge(keep_state_id,delete_state_id)
    atm.export_to_dot(file_name=f"{atm.name}" + "_after_merge1")

    keep_state_id = 21
    delete_state_id = 15

    atm.do_single_merge(keep_state_id,delete_state_id)
    atm.export_to_dot(file_name=f"{atm.name}" + "_after_merge2")

    keep_state_id = 21
    delete_state_id = 12

    atm.do_single_merge(keep_state_id,delete_state_id)
    atm.export_to_dot(file_name=f"{atm.name}" + "_after_merge3")

    return atm


def test5():
    atm = test4()
    atm.compute_state_k_tail(21,0)
    atm.compute_state_k_tail(21,1)
    atm.compute_state_k_tail(21,2)





def main():
    # test1()
    # test2()
    # test3()
    # test4()
    # test5()
    pass

    
if __name__ == "__main__":
    main()
