import pytest
from tests.testcase.testcase_ktail_5220 import TEST_CASES

@pytest.mark.parametrize(
    "start_state_id, k, expected",
    TEST_CASES,
    ids=[f"S{state_id}-k{k}" for (state_id, k, _) in TEST_CASES]
    )

def test_cyclic(atm_case_5220, start_state_id, k, expected):

    result = atm_case_5220.compute_state_k_tail(start_state_id, k)
    
    assert result == expected