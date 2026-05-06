import pytest
from tests.testcase.nfaMerge.testcase_nfaMerge_3 import TESTCASE
from tests.utils import is_dfa, has_dangling_transitions

@pytest.mark.parametrize(
    "keep_state_id, delete_state_id",
    TESTCASE,
    ids=[f"Keep_S{keep}-delete_S{delete}" for keep, delete in TESTCASE]
)
def test_nfa_merge(
    atm_case_3,
    keep_state_id,
    delete_state_id
):
    atm = atm_case_3

    if not atm.can_merge(keep_state_id, delete_state_id):
        pytest.skip(f"S{keep_state_id}, S{delete_state_id} not mergeable")

    ok = atm.do_single_merge(keep_state_id, delete_state_id)
    assert ok

    atm.NFA_merge(keep_state_id)

    assert keep_state_id in atm.states_Dict
    assert is_dfa(atm)
    assert not has_dangling_transitions(atm)