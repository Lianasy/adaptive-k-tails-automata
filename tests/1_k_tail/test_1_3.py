import pytest
from src.k_tail_V5_2 import Automaton

def create_automaton():
    """
    Cyclic PTA
    Two states A and B.
    Transitions: 
        A --a--> B, A --b--> A,
        B --b--> A, B --a--> B.
    """
    atm = Automaton()
    A = atm.initial_state
    B = atm._add_state()
    A.transitions.append(("a", B))
    A.transitions.append(("b", A))
    B.transitions.append(("b", A))
    B.transitions.append(("a", B))
    A.is_accept = True
    B.is_accept = False
    return atm

@pytest.mark.parametrize(
    "start_state_id, k, expected",
    [
        (0, 0, [" (accept)"]),
        (0, 1, ["a (rejected)","b (accept)"]),
        (0, 2, ["aa (rejected)","ab (accept)","ba (rejected)","bb (accept)"]),
        (0, 3, ["aaa (rejected)","aab (accept)","aba (rejected)","abb (accept)","baa (rejected)","bab (accept)","bba (rejected)","bbb (accept)"]),
        (0, 4, ["aaaa (rejected)","aaab (accept)","aaba (rejected)","aabb (accept)","abaa (rejected)","abab (accept)","abba (rejected)","abbb (accept)","baaa (rejected)","baab (accept)","baba (rejected)","babb (accept)","bbaa (rejected)","bbab (accept)","bbba (rejected)","bbbb (accept)"]),
        (1, 0, [" (rejected)"]),
        (1, 1, ["a (rejected)","b (accept)"]),
        (1, 2, ["aa (rejected)","ab (accept)","ba (rejected)","bb (accept)"]),
        (1, 3, ["aaa (rejected)","aab (accept)","aba (rejected)","abb (accept)","baa (rejected)","bab (accept)","bba (rejected)","bbb (accept)"]),
        (1, 4, ["aaaa (rejected)","aaab (accept)","aaba (rejected)","aabb (accept)","abaa (rejected)","abab (accept)","abba (rejected)","abbb (accept)","baaa (rejected)","baab (accept)","baba (rejected)","babb (accept)","bbaa (rejected)","bbab (accept)","bbba (rejected)","bbbb (accept)"]),
    ],
    ids=["S0_k0","S0_k1","S0_k2","S0_k3","S0_k4","S1_k0","S1_k1","S1_k2","S1_k3","S1_k4"]
    )

def test_cyclic(start_state_id, k, expected):
    atm = create_automaton()

    result = atm.compute_state_k_tail(start_state_id, k)
    
    assert result == expected