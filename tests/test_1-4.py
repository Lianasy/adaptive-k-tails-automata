import pytest
from src.k_tail_V4_6 import Automaton, parse_traces
from tests.automaton_5_2_2_0_all_ktails import TEST_CASES

def create_automaton():
    """
    PTA from automaton_5_2_2_0~0.txt
    """
    traces = "data/training_data/automaton_5_2_2_0~0.txt"
    train_pos, train_neg = parse_traces(traces)
    atm = Automaton()
    atm.build_PTA_from_trace(train_pos, train_neg)
    return atm

@ pytest.mark.parametrize(
    "start_state_id, k, expected",
    TEST_CASES,
    ids=[f"S{state_id}-k{k}" for (state_id, k, _) in TEST_CASES]
    )

def test_cyclic(start_state_id, k, expected):
    atm = create_automaton()

    result = atm.compute_state_k_tail(start_state_id, k)
    
    assert result == expected