import pytest
from src.k_tail_V5_2 import Automaton
from tests.testcase.testcase_2_2 import TEST_CASES

def create_automaton():

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

@pytest.mark.parametrize(
    "keep_state_id, delete_state_id, expected",
    TEST_CASES,
    ids=[f"S{a}->S{b}" for (a, b, _) in TEST_CASES]
)
    
def test_can_merge(keep_state_id, delete_state_id, expected):
    atm = create_automaton()
    
    result = atm.can_merge(keep_state_id, delete_state_id)
    
    assert result == expected
    