import pytest
from src.k_tail_V5_2 import Automaton
from tests.testcase.testcase_2_1 import TEST_CASES

def create_automaton():

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

@pytest.mark.parametrize(
    "keep_state_id, delete_state_id, expected",
    TEST_CASES,
    ids=[f"S{a}->S{b}" for (a, b, _) in TEST_CASES]
)
    
def test_can_merge(keep_state_id, delete_state_id, expected):
    atm = create_automaton()
    
    result = atm.can_merge(keep_state_id, delete_state_id)
    
    assert result == expected
    