import pytest
from src.k_tail_V5_2 import Automaton

def create_automaton():
    """
    Self-loop PTA
    One state A
    Transition:
        A --a--> A (self-loop)
    """
    atm = Automaton()
    A = atm.initial_state
    A.transitions.append(("a", A))
    A.is_accept = True
    return atm

@pytest.mark.parametrize(
    "k, expected",
    [
        (0, [" (accept)"]),
        (1, ["a (accept)"]),
        (2, ["aa (accept)"]),
        (3, ["aaa (accept)"]),
        (4, ["aaaa (accept)"]),
    ],
    ids=["k=0","k=1","k=2","k=3","k=4"]
    )

def test_loop(k, expected):
    atm = create_automaton()

    result = atm.compute_state_k_tail(0, k)

    assert result == expected