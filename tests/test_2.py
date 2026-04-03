import pytest
from src.k_tail_V4_6 import Automaton

def create_automaton():
    """
    Mutual circle PTA
    Two states A and B
    Transitions:
        A --a--> B
        B --b--> A
    """
    atm = Automaton()
    A = atm.initial_state
    B = atm._add_state()
    A.transitions.append(("a", B))
    B.transitions.append(("b", A))
    A.is_accept = True
    B.is_accept = False
    return atm

@pytest.mark.parametrize(
    "start_state_id, k, expected",
    [
        (0, 0, [" (accept)"]),
        (0, 1, ["a (rejected)"]),
        (0, 2, ["ab (accept)"]),
        (0, 3, ["aba (rejected)"]),
        (0, 4, ["abab (accept)"]),
        (1, 0, [" (rejected)"]),
        (1, 1, ["b (accept)"]),
        (1, 2, ["ba (rejected)"]),
        (1, 3, ["bab (accept)"]),
        (1, 4, ["baba (rejected)"]),
    ],
    ids=["S0_k0","S0_k1","S0_k2","S0_k3","S0_k4","S1_k0","S1_k1","S1_k2","S1_k3","S1_k4"]
    )

def test_circle(start_state_id, k, expected):
    atm = create_automaton()

    result = atm.compute_state_k_tail(start_state_id, k)

    assert result == expected