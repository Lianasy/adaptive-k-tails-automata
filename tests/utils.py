def is_dfa(atm) -> bool:
    for state in atm.states_Dict.values():
        seen = {}
        for sym, nxt in state.transitions:
            if sym in seen and seen[sym] != nxt.id:
                return False
            seen[sym] = nxt.id
    return True


def has_dangling_transitions(atm) -> bool:
    valid_ids = set(atm.states_Dict.keys())
    for state in atm.states_Dict.values():
        for sym, nxt in state.transitions:
            if nxt.id not in valid_ids:
                return True
    return False