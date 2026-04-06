import pytest
from tests.testcase.canMerge.testcase_canMerge_3 import TEST_CASES

@pytest.mark.parametrize(
    "keep_state_id, delete_state_id, expected",
    TEST_CASES,
    ids=[f"S{a}->S{b}" for (a, b, _) in TEST_CASES]
)
def test_can_merge(
    atm_case_3,
    keep_state_id,
    delete_state_id,
    expected
    ):
    
    result = atm_case_3.can_merge(keep_state_id, delete_state_id)
    
    assert result == expected
    