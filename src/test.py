from k_tail_V5_7_PTA_V2_compute_k_tailV6_NFAMergeV2_canMergeV4_GlobalMergeV5_Nstrict_redirectinoutV2_singleMergeV2 import *
import sys
sys.stdout = open("./output/output.txt", "w", encoding="utf-8")


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
    atm.build_PTA_from_trace(train_pos, train_neg)

    return atm,test_pos,test_neg

def build_PTA_mannually_example4() -> Automaton:
    """
    测试NFA_validation_check
    """
    atm = Automaton(name="example4")
    pos_trace = [["a","a","a",]]
    neg_trace = [["b","a","a"]]
    atm.build_PTA_from_trace(pos_trace,neg_trace)
    return atm

def build_PTA_mannually_example5() -> Automaton:
    """
    测试NFA_validation_check
    """
    atm = Automaton(name="example5")
    pos_trace = [["a","a","a",],["a","b","b"], ["b","a","a"]]
    neg_trace = [["b","b","b"]]
    atm.build_PTA_from_trace(pos_trace,neg_trace)
    return atm

def build_PTA_mannually_example6() -> Automaton:
    """
    测试NFA_validation_check
    """
    atm = Automaton(name="example6")
    pos_trace = [
        ["a","a","a",],
        ["a","a","b"], 
                 
        ["a","b","b"],
        ["b","a","a"],
        ["b","a","b"],
        ["b","b","a"]]
    neg_trace = [
        ["a","b","a"],
        ["b","b","b"]]
    atm.build_PTA_from_trace(pos_trace,neg_trace)
    return atm

def build_PTA_mannually_example7() -> Automaton:
    """
    test for NFA_merge
    """
    atm = Automaton(name="example7")
    pos_trace = [
        ["a","a","a",],
        
        ["a","a","b"],      
        ["a","b"],
        ["b","a","a"],
        ["b","a","b"],
    ]
    neg_trace = [
        ]
    atm.build_PTA_from_trace(pos_trace,neg_trace)
    return atm

def build_PTA_mannually_example8() -> Automaton:
    atm = Automaton(name = "example8")
    S0 = atm.initial_state
    S1 = atm._add_state()
    S2 = atm._add_state()
    S3 = atm._add_state()
    S4 = atm._add_state()
    S5 = atm._add_state()
    S6 = atm._add_state()

    S0.is_accept = True
    S1.is_accept = True
    S2.is_accept = True
    S3.is_accept = True
    S4.is_accept = True
    S5.is_accept = False
    S6.is_accept = True

    S0.transitions.append(("a",S1))
    S0.transitions.append(("b",S4))

    S1.transitions.append(("a",S2))
    S1.transitions.append(("b",S3))

    S2.transitions.append(("a",S2))

    S4.transitions.append(("a",S5))
    S4.transitions.append(("b",S6))

    S5.transitions.append(("a",S5))

    return atm

def build_PTA_mannually_example9() -> Automaton:
    atm = Automaton(name = "example9")
    S0 = atm.initial_state
    S1 = atm._add_state()
    S2 = atm._add_state()
    
    S0.is_accept = True
    S1.is_accept = True
    S2.is_accept = True

    S0.transitions.append(("a",S1))
    S0.transitions.append(("a",S2))
    S1.transitions.append(("a",S1))

    return atm

def build_PTA_mannually_example10() -> Automaton:
    atm = Automaton(name = "example10")
    S0 = atm.initial_state
    S1 = atm._add_state()
    S2 = atm._add_state()
    S3 = atm._add_state()

    S0.is_accept = True
    S1.is_accept = True
    S2.is_accept = True
    S3.is_accept = True

    S0.transitions.append(("a",S1))
    S0.transitions.append(("a",S3))
    S1.transitions.append(("a",S2))
    S3.transitions.append(("a",S2))

    return atm

def build_PTA_mannually_example11() -> Automaton:
    """自环的NFA，用于测试NFA_merge会不会无限循环"""
    atm = Automaton(name = "example11")
    S0 = atm.initial_state
    S1 = atm._add_state()

    S0.is_accept = True
    S1.is_accept = True

    S0.transitions.append(("a",S0))
    S0.transitions.append(("a",S1))

    return atm

def build_PTA_mannually_example12() -> Automaton:
    """3个a去向不同的state，用于测试NFA_merge会不会将3条NFA边合并成1条DFA边"""
    atm = Automaton(name = "example12")
    S0 = atm.initial_state
    S1 = atm._add_state()
    S2 = atm._add_state()
    S3 = atm._add_state()

    S0.is_accept = True
    S1.is_accept = True
    S2.is_accept = True
    S3.is_accept = True

    S0.transitions.append(("a",S1))
    S0.transitions.append(("a",S2))
    S0.transitions.append(("a",S3))

    return atm

def build_PTA_mannually_example13() -> Tuple[Automaton, List[List[str]], List[List[str]]]:
    train_file = 'training_data/automaton_5_2_2_0~0_test.txt' 
    test_file  = 'training_data/automaton_5_2_2_0~1.txt'
    automaton_name = Path(train_file).name

    train_pos, train_neg = parse_traces(train_file)
    test_pos, test_neg = parse_traces(test_file)

    atm = Automaton(automaton_name)
    atm.build_PTA_from_trace(train_pos, train_neg)

    return atm, test_pos, test_neg

def test1_compotektail():
    """ 自环"""
    atm = build_PTA_mannually_example1()
    atm.export_to_dot(file_name="0-self-circle")
    atm.compute_state_k_tail(0,4)

def test2_computektail():
    """互相环"""
    atm = build_PTA_mannually_example2()
    atm.export_to_dot(file_name="01-mutual-circle")
    atm.compute_state_k_tail(1,4)

def test3_computektail():
    """用trace建立巨型PTA来随机测试computektail"""
    atm,test_pos,test_neg = build_PTA_mannually_example3()
    atm.export_to_dot(file_name="0_test3")
    all_state_ids = list(atm.states_Dict.keys())
    # state_id = random.choice(all_state_ids)
    # k = random.randint(0, 4)

    state_id = 46
    k = 3
    print(f"🎲 随机选择状态: S{state_id}")
    print(f"🎲 随机选择 k    : {k}")
    print()

    k_tail = atm.compute_state_k_tail(start_state_id=state_id, k=k)
    print(f"k-tail = {k_tail}")

def test4_dosinglemerge():
    """在PTA上随机找两对进行singlemerge"""
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

def test5_computektail():
    """用trace 来创建PTA，然后尝试得到不同的state的ktail"""
    atm = build_PTA_mannually_example3()
    atm.compute_state_k_tail(21,0)
    atm.compute_state_k_tail(21,1)
    atm.compute_state_k_tail(21,2)
    return atm

def test6_canmerge():
    """用trace来创建PTA，然后尝试使用单次can_merge检查是否两个state可以合法合并"""
    atm = build_PTA_mannually_example3()
    atm.export_to_dot(file_name="test6ForCanMerge")
    atm.can_merge(60,66)

def test7_canmerge():
    """用自建PTA来测试canmerge"""
    atm = build_PTA_mannually_example4()
    atm.export_to_dot(file_name="example4")
    atm.can_merge(1,4)

def test8_canmerge():
    """用自建PTA来测试canmerge"""
    atm = build_PTA_mannually_example5()
    atm.export_to_dot(file_name="example5")
    atm.can_merge(1,6)

def test9_canmerge():
    """用自建PTA来测试canmerge"""
    atm = build_PTA_mannually_example6()
    atm.export_to_dot(file_name="example6")
    atm.can_merge(1,7)

def test10_NFAmerge():
    """用自建PTA来测试NFAmerge"""
    atm = build_PTA_mannually_example7()
    atm.export_to_dot(file_name="example7")
    can_merge = atm.can_merge(1,6)
    if can_merge == True:
        atm.do_single_merge(1,6)
        atm.export_to_dot(file_name="example7_after_merge")
        atm.NFA_merge(1)
        atm.export_to_dot(file_name="example7_after_NFA_merge")

def test11_GlobalMerge():
    """用trace PTA来测试k=2的global_merge"""
    atm,test_pos,test_neg = build_PTA_mannually_example13()
    atm.export_to_dot(file_name="example13_before_merge")
    atm.evaluate_PTA(test_pos,test_neg)
    atm.Global_merge(k=2,verbose=False)
    atm.export_to_dot(file_name="example13_after_global_merge")
    atm.evaluate_bcr(test_pos,test_neg)
    
def test12_canmerge():
    """用自建PTA来测试canmerge"""
    atm = build_PTA_mannually_example8()
    atm.export_to_dot(file_name="example8_PTA")
    can_merge = atm.can_merge(1,4)
    
def test13_NFAmerge():
    """用自建PTA来测试NFA_merge"""
    atm = build_PTA_mannually_example9()
    atm.export_to_dot(file_name="example9_PTA")
    can_merge = atm.can_merge(1,2)
    if can_merge == True:
        atm.do_single_merge(1,2)
        atm.export_to_dot(file_name="example9_after_merge")
        atm.NFA_merge(1)

def test14_singlemerge():
    """用自建PTA来测试singlemerge"""
    atm = build_PTA_mannually_example10()
    atm.export_to_dot(file_name="example10_PTA")
    atm.do_single_merge(1,3)
    atm.export_to_dot(file_name="example10_after_merge")

def test15_NFAmerge():
    """自环的NFA，用于测试NFA_merge会不会无限循环"""
    atm = build_PTA_mannually_example11()
    atm.export_to_dot(file_name="example11_PTA")
    atm.NFA_merge(0)
    atm.export_to_dot(file_name="example11_NFA_merge")

def test16_NFAmerge():
    """用自建PTA来测试NFAmerge"""
    atm = build_PTA_mannually_example12()
    atm.export_to_dot(file_name="example12_PTA")
    atm.NFA_merge(0)
    atm.export_to_dot(file_name="example12_NFA_merge")

def test17_GlobalMerge():
    """用一个小一点的trace PTA，一步一步手动模拟lobal Merge"""
    atm = build_PTA_mannually_example13()
    can_merge = atm.can_merge(0,3)
    if can_merge:
        atm.do_single_merge(0,3)
        atm.export_to_dot(file_name="example13-0vs3")
        atm.do_single_merge(1,4)
        atm.export_to_dot(file_name="example13-0vs3-1vs4")
        atm.do_single_merge(2,5)
        atm.export_to_dot(file_name="example13-0vs3-1vs4-2vs5")
        atm.do_single_merge(0,6)
        atm.export_to_dot(file_name="example13-0vs3-1vs4-2vs5-0vs6")
        atm.do_single_merge(1,7)
        atm.export_to_dot(file_name="example13-0vs3-1vs4-2vs5-0vs6-1vs7")
        atm.do_single_merge(2,8)
        atm.export_to_dot(file_name="example13-0vs3-1vs4-2vs5-0vs6-1vs7-2vs8")
        atm.do_single_merge(19,14)
        atm.export_to_dot(file_name="example13-0vs3-1vs4-2vs5-0vs6-1vs7-2vs8-19vs14")
        atm.do_single_merge(20,15)
        atm.export_to_dot(file_name="example13-0vs3-1vs4-2vs5-0vs6-1vs7-2vs8-19vs14-20vs15")
        atm.do_single_merge(21,16)
        atm.export_to_dot(file_name="example13-0vs3-1vs4-2vs5-0vs6-1vs7-2vs8-19vs14-20vs15-21vs16")
        atm.do_single_merge(22,17)
        atm.export_to_dot(file_name="example13-0vs3-1vs4-2vs5-0vs6-1vs7-2vs8-19vs14-20vs15-21vs16-22vs17")
        atm.do_single_merge(23,18)
        atm.export_to_dot(file_name="example13-0vs3-1vs4-2vs5-0vs6-1vs7-2vs8-19vs14-20vs15-21vs16-22vs17-23vs18")
        atm.do_single_merge(19,9)
        atm.export_to_dot(file_name="example13-0vs3-1vs4-2vs5-0vs6-1vs7-2vs8-19vs14-20vs15-21vs16-22vs17-23vs18-19vs9")
        atm.do_single_merge(19,14)
        atm.export_to_dot(file_name="example13-0vs3-1vs4-2vs5-0vs6-1vs7-2vs8-19vs14-20vs15-21vs16-22vs17-23vs18-19vs9")

def test18_NFAMerge():
    """用一个小一点的trace PTA，一步一步手动模拟NFAMerge"""
    atm, test_pos, test_neg = build_PTA_mannually_example13()
    atm.export_to_dot(file_name="example13_before_merge")
    # atm.Global_merge(k=2,verbose=True)
    # atm.export_to_dot(file_name="example13_global_merge")
    atm.can_merge(0,1)
    atm.do_single_merge(0,1)
    atm.export_to_dot(file_name="example13-0vs1")
    
    atm.NFA_merge(0)
    atm.export_to_dot(file_name="example13-0vs1-NFAmerge0")
    # atm.export_to_dot(file_name="example13_NFA_merge0")
    print("\n\n\n\n\n*******************************")
    atm.can_merge(0,2)
    atm.do_single_merge(0,2)
    atm.export_to_dot(file_name="example13-0vs1-NFAmerge0-0vs2")

    atm.do_single_merge(0,3)
    atm.export_to_dot(file_name="example13-0vs1-NFAmerge0-0vs2-0vs3")

def main():
    # test1()
    # test2()
    # test3_computektail()
    # test4()
    # test5()
    # test6()
    # test7()
    # test8()
    # test9()
    # test10()
    # test11_GlobalMerge()    
    # test12()
    # test13()
    # test14()
    # test15()
    # test16()
    # test17_GlobalMerge()
    test18_NFAMerge()
    pass

    
if __name__ == "__main__":
    main()
