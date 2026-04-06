import pytest
from tests.testcase.doSingleMerge.testcase_doSingleMerge_2 import TEST_CASES

@pytest.mark.parametrize(
    "keep_state_id, delete_state_id, expected_keep_accept, expected_keep_transitions, redirected_edges",
    TEST_CASES,
    ids=[f"keep_{k}_delete_{d}" for k, d, *_ in TEST_CASES],
)
def test_do_single_merge(
    atm_case_2,
    keep_state_id,
    delete_state_id,
    expected_keep_accept,
    expected_keep_transitions,
    redirected_edges,
):
    before_count = len(atm_case_2.states_Dict)

    result = atm_case_2.do_single_merge(keep_state_id, delete_state_id)

    assert result is True
    assert keep_state_id in atm_case_2.states_Dict
    assert delete_state_id not in atm_case_2.states_Dict
    assert len(atm_case_2.states_Dict) == before_count - 1

    keep_state = atm_case_2.states_Dict[keep_state_id]

    assert keep_state.is_accept == expected_keep_accept
    assert sorted(keep_state.get_transition()) == sorted(expected_keep_transitions)

    for source_id, label, new_target_id in redirected_edges:
        assert (label, new_target_id) in atm_case_2.states_Dict[source_id].get_transition()
        
    for state in atm_case_2.states_Dict.values():
        assert all(target_id != delete_state_id for _, target_id in state.get_transition())