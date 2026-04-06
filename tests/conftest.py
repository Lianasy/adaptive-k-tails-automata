import pytest
from src.function import parse_traces
from src.k_tail_V5_2 import Automaton


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