import pytest
from tests.testcase.ktail.testcase_ktail_2 import TEST_CASES

@pytest.mark.parametrize(
    "start_state_id, k, expected",
    TEST_CASES,
    ids=[f"S{a}_k{b}" for (a, b, _) in TEST_CASES]
    )
def test_k_tail(
    atm_case_2,
    start_state_id,
    k,
    expected
):
    atm = atm_case_2
    
    result = atm.compute_state_k_tail(start_state_id, k)

    assert result == expected