import pytest
from src.function import parse_traces
from src.k_tail_V5_8 import Automaton


@pytest.fixture(scope="function")
def atm_case_5220():
    """
    PTA from automaton_5_2_2_0~0.txt
    """
    traces = "data/training_data/automaton_5_2_2_0~0.txt"
    train_pos, train_neg = parse_traces(traces)
    atm = Automaton()
    atm.build_PTA_from_trace(train_pos, train_neg)
    return atm

@pytest.fixture(scope="function")
def atm_case_1():
    """
    Selected branch of a PTA
    """
    atm = Automaton()
    
    S0 = atm.initial_state
    S1 = atm._add_state()
    S2 = atm._add_state()
    S3 = atm._add_state()
    S4 = atm._add_state()
    S5 = atm._add_state()
    S6 = atm._add_state()
    S7 = atm._add_state()
    S8 = atm._add_state()
    S9 = atm._add_state()
    S10 = atm._add_state()
    S11 = atm._add_state()
    S12 = atm._add_state()
    S13 = atm._add_state()
    S14 = atm._add_state()
    
    S0.transitions.append(("a", S1))
    S0.transitions.append(("b", S2))
    S1.transitions.append(("a", S3))
    S1.transitions.append(("b", S4))
    S2.transitions.append(("a", S5))
    S2.transitions.append(("b", S6))
    S3.transitions.append(("a", S7))
    S3.transitions.append(("b", S8))
    S4.transitions.append(("a", S9))
    S4.transitions.append(("b", S10))
    S5.transitions.append(("a", S11))
    S5.transitions.append(("b", S12))
    S6.transitions.append(("a", S13))
    S6.transitions.append(("b", S14))
    
    S0.is_accept = True
    S1.is_accept = True
    S2.is_accept = True
    S3.is_accept = True
    S4.is_accept = True
    S5.is_accept = True
    S6.is_accept = True
    S7.is_accept = True
    S8.is_accept = False
    S9.is_accept = True
    S10.is_accept = False
    S11.is_accept = True
    S12.is_accept = False
    S13.is_accept = False
    S14.is_accept = False
    
    return atm

@pytest.fixture(scope="function")
def atm_case_2():
    """
    Simple PTA with loops and alternating accept states
    """
    atm = Automaton()
    
    S0 = atm.initial_state
    S1 = atm._add_state()
    S2 = atm._add_state()
    S3 = atm._add_state()
    S4 = atm._add_state()
    S5 = atm._add_state()
    S6 = atm._add_state()

    S0.transitions.append(("a", S1))
    S0.transitions.append(("b", S4))
    S1.transitions.append(("a", S2))
    S1.transitions.append(("b", S2))
    S2.transitions.append(("a", S3))
    S4.transitions.append(("a", S4))
    S4.transitions.append(("b", S5))
    S5.transitions.append(("a", S6))
    S5.transitions.append(("b", S5))
    
    S0.is_accept = True
    S1.is_accept = True
    S2.is_accept = False
    S3.is_accept = True
    S4.is_accept = False
    S5.is_accept = True
    S6.is_accept = False
    
    return atm

@pytest.fixture(scope="function")
def atm_case_3():
    """
    Complex automaton
    """
    atm = Automaton()
    
    S0 = atm.initial_state
    S1 = atm._add_state()
    S2 = atm._add_state()
    S3 = atm._add_state()
    S4 = atm._add_state()
    S5 = atm._add_state()
    
    S0.transitions.append(("a", S1))
    S0.transitions.append(("b", S2))
    S0.transitions.append(("c", S4))
    S1.transitions.append(("a", S0))
    S2.transitions.append(("a", S3))
    S2.transitions.append(("b", S2))
    S2.transitions.append(("c", S4))
    S3.transitions.append(("a", S0))
    S4.transitions.append(("a", S5))
    S5.transitions.append(("a", S0))
    S5.transitions.append(("b", S0))
    S5.transitions.append(("c", S0))
    
    S0.is_accept = False
    S1.is_accept = True
    S2.is_accept = False
    S3.is_accept = True
    S4.is_accept = False
    S5.is_accept = True

    return atm