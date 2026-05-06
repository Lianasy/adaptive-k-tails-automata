import pytest
from tests.testcase.canMerge.testcase_canMerge_1 import TEST_CASES

@pytest.mark.parametrize(
    "keep_state_id, delete_state_id, expected",
    TEST_CASES,
    ids=[f"Merge S{b} into S{a}" for (a, b, _) in TEST_CASES]
)  
def test_can_merge(
    atm_case_1,
    keep_state_id,
    delete_state_id,
    expected
):
    atm = atm_case_1
    
    result = atm.can_merge(keep_state_id, delete_state_id)
    
    assert result == expected
    