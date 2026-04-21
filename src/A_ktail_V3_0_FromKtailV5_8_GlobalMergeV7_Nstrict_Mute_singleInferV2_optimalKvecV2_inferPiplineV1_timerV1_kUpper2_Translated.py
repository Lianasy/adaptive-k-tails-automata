from function import * 
from typing import Dict, List, Set, Tuple, Optional, Any, Literal
from collections import defaultdict
from pathlib import Path
import json
import itertools
import copy
import time



class State:
    def __init__(self, state_id=None):
        self.id = state_id               
        self.transitions = []            
        self.is_accept = False           
    
    def get_transition(self):
        transitions = [(sym, tgt_state.id) for sym, tgt_state in self.transitions]
        return transitions
    
    def __repr__(self):
        return f"State(id={self.id:3d}, is_ac={self.is_accept:>1}, trans={self.get_transition()})"

class Automaton():
    def __init__(self,
                 name: str = "None"):
        self.states_Dict: Dict[int, State] = {}
        self.alphabet: Set[str] = set()
        self.initial_state = self._add_state()  
        self.name = name
        self.k_vector: Dict[str, int] = {}

    def _add_state(self):
        state_id=len(self.states_Dict)
        new_state = State(state_id)  
        self.states_Dict[state_id] =new_state
        return new_state

    def copy_automaton(self) -> "Automaton":
        old_ids = sorted(self.states_Dict.keys())
        if not old_ids:
            return Automaton(name=self.name + "_copy")
        new_atm = Automaton(name=self.name + "_copy")
        # __init__ 已创建 S0；补到与旧图相同 max_id
        max_id = max(old_ids)
        while len(new_atm.states_Dict) <= max_id:
            new_atm._add_state()
        for oid_id in old_ids:
            new_state = new_atm.states_Dict[oid_id]
            old_state = self.states_Dict[oid_id]
            new_state.is_accept = old_state.is_accept
            new_state.transitions.clear()
            for sym, tgt in old_state.transitions:
                new_state.transitions.append((sym, new_atm.states_Dict[tgt.id]))
        new_atm.initial_state = new_atm.states_Dict[self.initial_state.id]
        new_atm.alphabet = set(self.alphabet)
        if hasattr(self, "k_vector"):
            new_atm.k_vector = dict(self.k_vector)
        return new_atm

    def build_PTA_from_trace(self, pos_traces=None, neg_traces=None):
        if pos_traces is not None:
            for trace in pos_traces:
                current_state = self.initial_state
                current_state.is_accept = True

                for symbol in trace:
                    self.alphabet.add(symbol)
                    sym_found = False
                    for sym, tgt_state in current_state.transitions:
                        if sym == symbol:
                            current_state = tgt_state
                            current_state.is_accept = True 
                            sym_found = True
                            break
                    if not sym_found:
                        next_state = self._add_state()
                        next_state.is_accept = True      
                        current_state.transitions.append((symbol, next_state))
                        current_state = next_state

                current_state.is_accept = True 

        if neg_traces is not None:
            for trace in neg_traces:
                current_state = self.initial_state
                current_state.is_accept = True 

                for symbol in trace:
                    self.alphabet.add(symbol)
                    sym_found = False
                    for sym, tgt_state in current_state.transitions:
                        if sym == symbol:
                            current_state = tgt_state
                            current_state.is_accept = True  
                            sym_found = True
                            break
                    if not sym_found:
                        next_state = self._add_state()
                        next_state.is_accept = True         
                        current_state.transitions.append((symbol, next_state))
                        current_state = next_state

                current_state.is_accept = False

    def update_alphabet(self) -> None:
        self.alphabet.clear()
        for state in self.states_Dict.values():
            for sym, _tgt in state.transitions:
                self.alphabet.add(sym)

    def initialize_k_vector(
        self,
        values: Optional[Dict[str, int]] = None,
        All_k: int = 2,
    ) -> None:


        self.update_alphabet()

        if values is None:
            self.k_vector = {sym: int(All_k) for sym in sorted(self.alphabet)}
            return

        if values:
            atm_alphabet_keys = set(self.alphabet)
            passed_kvector_keys = set(values.keys())
            if atm_alphabet_keys != passed_kvector_keys:
                print("initialize_k_vector: key set mismatch between automaton alphabet and passed dict.")
                print(f"Automaton alphabet keys (sorted): {sorted(atm_alphabet_keys)}")
                print(f"Passed dict keys (sorted):        {sorted(passed_kvector_keys)}")
                print(f"Only in automaton: {sorted(atm_alphabet_keys - passed_kvector_keys)}")
                print(f"Only in passed dict: {sorted(passed_kvector_keys - atm_alphabet_keys)}")
                raise ValueError("k_vector: k_vector-dict passed must match alphabet exactly")
            if atm_alphabet_keys == passed_kvector_keys:
                self.k_vector = {sym: int(values[sym]) for sym in sorted(self.alphabet)}
    
    def print_pta(
        self,
        to_screen: bool = True,
        output_dir: str = "output",
        filename: str = "PTA_structure.txt",
    ) -> None:
        alpha_str = ", ".join(sorted(self.alphabet)) if self.alphabet else "(empty)"
        lines = [
            "",
            f"=== Minimal PTA (total states: {len(self.states_Dict)}) ===",
            f"Initial state ID: {self.initial_state.id}",
            f"Alphabet: {{{alpha_str}}}",
        ]
        for state in sorted(self.states_Dict.values(), key=lambda s: s.id):
            accept_tag = "✅ accepted" if state.is_accept else "❌ unaccepted"
            transitions = state.get_transition()
            lines.append(f"S{state.id} [{accept_tag}] | T: {transitions}")
        text = "\n".join(lines)
        if to_screen:
            print(text)
        else:
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / filename
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(text)

    def export_pta_to_json(
        self,
        output_dir: str = "output",
        filename: str = "pta.json",
    ) -> None:
        """
        Export the current PTA as a JSON file .
        """
        data = []
        for state in sorted(self.states_Dict.values(), key=lambda s: s.id):
            transitions = [
                [sym, f"S{tgt_state.id}"]
                for sym, tgt_state in state.transitions
            ]
            data.append({
                "state_id": state.id,
                "accepted": "Y" if state.is_accept else "N",
                "T": transitions,
            })
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{filename}.json"
        out_file = out_dir / filename
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def test_trace(self, trace: List[str]) -> bool:
        current = self.initial_state
        for symbol in trace:
            nxt = None
            for sym, tgt_state in current.transitions:
                if sym == symbol:
                    nxt = tgt_state
                    break
            if nxt is None:
                return False
            current = nxt
        return current.is_accept
    
    def evaluate_bcr(
        self,
        pos_traces: List[List[str]],
        neg_traces: List[List[str]],
        timer: float,
        *,
        verbose: bool = True,
        filename: Optional[str] = None,
        output_dir: str = "output",
    ) -> Dict[str, Any]:
        pos_traces = pos_traces or []
        neg_traces = neg_traces or []
        tp = sum(1 for t in pos_traces if self.test_trace(t))
        fn = len(pos_traces) - tp
        tn = sum(1 for t in neg_traces if not self.test_trace(t))
        fp = len(neg_traces) - tn
        sens = tp / len(pos_traces) if pos_traces else float("nan")
        spec = tn / len(neg_traces) if neg_traces else float("nan")
        bcr = (sens + spec) / 2 if pos_traces and neg_traces else float("nan")
        result = {
            "BCR": bcr,
            "sensitivity": sens,
            "specificity": spec,
            "TP": tp,
            "FN": fn,
            "TN": tn,
            "FP": fp,
            "num_pos": len(pos_traces),
            "num_neg": len(neg_traces),
            "num_states": len(self.states_Dict),
            **({"evaluation_time_sec": timer} if timer else {}),
        }
        lines = [
            f"=== BCR evaluation k-vector = {self.k_vector}===",
            f"ATM states num = {len(self.states_Dict)}",
            f"Positive traces: {len(pos_traces)} | Negative traces: {len(neg_traces)}",
            f"TP={tp}  FN={fn}  TN={tn}  FP={fp}",
            f"Sensitivity (TPR): {sens:.4f}",
            f"Specificity (TNR): {spec:.4f}",
            f"BCR:               {bcr:.4f}",
            f"Evaluation time: {timer:.2f} seconds" if timer else "",
        ]
        text = "\n".join(lines) + "\n"
        if filename is not None:
            filename = f"{filename}.txt"
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / filename, "w", encoding="utf-8") as f:
                f.write(text)
        elif verbose:
            print(text, end="")
        return result
    
    def evaluate_PTA(
        self,
        test_pos,
        test_neg,
        *,
        verbose: bool = True,
        filename: Optional[str] = None,
        output_dir: str = "output",
    ) -> None:
        res = self.evaluate_bcr(test_pos, test_neg, timer=None, verbose=False)
        bcr = res["BCR"]
        sens = res["sensitivity"]
        spec = res["specificity"]
        alpha_str = ", ".join(sorted(self.alphabet)) if self.alphabet else "(empty)"
        lines = [
            "=== PTA evaluation ===",
            f"PTA states num = {len(self.states_Dict)}",
            f"PTA alphabet: {{{alpha_str}}}",
            f"PTA (BCR): {bcr:.4f}",
            f"PTA (Sensitivity): {sens:.4f}",
            f"PTA (Specificity): {spec:.4f}",
            "",
        ]
        text = "\n".join(lines)
        
        if filename is not None:
            filename = f"{filename}.txt"
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / filename, "w", encoding="utf-8") as f:
                f.write(text)
        elif verbose:
            print(text)
    
    def compute_state_k_tail(
        self,
        start_state_id: int,
        k: int,
        verbose: bool = True,
    ) -> Optional[List[str]]: 
        if start_state_id not in self.states_Dict:
            return None  

        start_state = self.states_Dict[start_state_id]
        result = set()


        def dfs(current_state: State, current_path: str, depth: int):
            if depth == 0:

                if current_state.is_accept:
                    result.add(f"{current_path} (accept)")
                else:
                    result.add(f"{current_path} (rejected)")
                return


            for sym, next_state in current_state.transitions:
                dfs(next_state, current_path + sym, depth - 1)


        dfs(start_state, "", k)

        if not result:
            if verbose:
                print(f"=== {k}-tail at S{start_state_id} ===")
                print(f"❌ No {k}-tail for S{start_state_id}")
            return None


        final = sorted(list(result))
        if verbose:
                print(f"=== {k}-tail at S{start_state_id} ===")
                print(final)
        return final

    def export_to_dot(
        self,
        output_path: str = "./output/",
        file_name: Optional[str] = None 
    ) -> None:

        if file_name is None:
            file_name = f"{self.name}.dot"  


        if not file_name.endswith(".dot"):
            file_name += ".dot"


        out_dir = Path(output_path)
        out_dir.mkdir(parents=True, exist_ok=True)  
        final_path = out_dir / file_name             


        lines = []
        lines.append("digraph Automaton {")
        lines.append("    rankdir = LR;")
        lines.append("    node [shape = circle];")

        init_id = self.initial_state.id
        lines.append(f'    __start [shape="point",style="invis"];')
        lines.append(f'    __start -> S{init_id};')

        for state in self.states_Dict.values():
            sid = state.id
            if state.is_accept:
                lines.append(f'    S{sid} [shape="doublecircle"];')
            else:
                lines.append(f'    S{sid} [shape="circle"];')

            for sym, next_st in state.transitions:
                lines.append(f'    S{sid} -> S{next_st.id} [label="{sym}"];')

        lines.append("}")


        with open(final_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        # print(f"✅ DOT saved：{final_path}")

    def can_merge(self, state1_id: int, state2_id: int, verbose: bool = True) -> bool:
        """check whether two states can be merged
        Various checks, if any check fails, return False. If all checks pass, return True automatically.
        """

        keep_state_id = min(state1_id,state2_id)
        delete_state_id  = max(state1_id,state2_id)

        if keep_state_id == delete_state_id:                                      
            if verbose: print(f"keep_state_id = {keep_state_id} is the same as delete_state_id = {delete_state_id}")
            if verbose: print(f"❌Fail to pass the can_merge check for S{delete_state_id} and S{keep_state_id}")
            return False

        if keep_state_id not in self.states_Dict or delete_state_id not in self.states_Dict:
            print(f"keep_state_id = {keep_state_id} or delete_state_id = {delete_state_id} not existed in Automaton.states_Dict")
            print(f"❌Fail to pass the can_merge check for S{delete_state_id} and S{keep_state_id}")
            return False

        dummy_atm = self.copy_automaton()
        dummy_atm.do_single_merge(keep_state_id,delete_state_id)
        can_merge_test = dummy_atm.simulate_NFA_merge(keep_state_id)

        return can_merge_test

    def do_single_merge(self, state1_id: int, state2_id: int) -> bool:

        keep_state_id = min(state1_id, state2_id)
        delete_state_id = max(state1_id, state2_id)

        if delete_state_id not in self.states_Dict or keep_state_id not in self.states_Dict:
            # print(f"When checking do_singale_merge:keep_state_id = {keep_state_id} or delete_state_id = {delete_state_id} not existed in Automaton.states_Dict")
            return False
        self.redirect_incoming(keep_state_id, delete_state_id)
        self.redirect_outgoing(keep_state_id, delete_state_id)

        keep_state = self.states_Dict[keep_state_id]
        delete_state = self.states_Dict[delete_state_id]
        keep_state.is_accept = keep_state.is_accept or delete_state.is_accept

        del self.states_Dict[delete_state_id]

        # print(f"✅ Keep_S{keep_state_id} <- Delete_S{delete_state_id} merged")
        return True
        
    def redirect_outgoing(self, keep_state_id: int, delete_state_id: int) -> None:
        """
        transfer all outgoing edges of delete_state to keep_state.
        then clear the outgoing edges of delete_state.
        """
        if delete_state_id not in self.states_Dict or keep_state_id not in self.states_Dict:
            print(f"keep_state_id = {keep_state_id} or delete_state_id = {delete_state_id} not existed in Automaton.states_Dict")
            print(f"Fail: ❌ Redirecting outgoing of S{delete_state_id} to S{keep_state_id}")
            return

        keep_state = self.states_Dict[keep_state_id]
        delete_state = self.states_Dict[delete_state_id]

        existing = set()
        for sym, tgt in keep_state.transitions:
            existing.add( (sym, tgt.id) )

        for sym, tgt in delete_state.transitions:
            key = (sym, tgt.id)
            if key not in existing:
                keep_state.transitions.append( (sym, tgt) )
                existing.add(key)

        delete_state.transitions.clear()

    def redirect_incoming(self, keep_state_id: int, delete_state_id: int) -> None:
        """
        traverse **all states**, change all incoming edges to delete_state
        to point to keep_state.
        Only one edge for the same (state, symbol) will be kept, no duplicates!
        """
        if delete_state_id not in self.states_Dict or keep_state_id not in self.states_Dict:
            print(f"keep_state_id = {keep_state_id} or delete_state_id = {delete_state_id} not existed in Automaton.states_Dict")
            print(f"Fail: ❌ Redirecting outgoing of S{delete_state_id} to S{keep_state_id}")
            return

        keep_state = self.states_Dict[keep_state_id]
        # delete_state = self.states_Dict[delete_state_id]

        for state in self.states_Dict.values():
            for i in range(len(state.transitions)):
                sym, tgt = state.transitions[i]
                if tgt.id == delete_state_id:
                    state.transitions[i] = (sym, keep_state)
        
            seen = set()
            unique_trans = []
            for sym, tgt in state.transitions:
                key = (sym, tgt.id)
                if key not in seen:
                    seen.add(key)
                    unique_trans.append((sym, tgt))
            
            state.transitions = unique_trans

    def k_common_outgoing(
        self,
        state_a_id: State,
        state_b_id: State,
        k_aggregation_mode: Literal["max", "min"] = "max",
        verbose: bool = False
    ) -> Optional[int]:
        """
        compare two states' outgoing edges: take the symbols that appear in both;
        for each symbol, retrieve k from self.k_vector, then take max or min of all k.
        Return None if no common symbols, no valid k, or k_vector is not initialized.
        """
        if state_a_id not in self.states_Dict or state_b_id not in self.states_Dict:
            if verbose:print(f"⚠️ S{state_a_id} or S{state_b_id} not in states_Dict, return None")
            return None

        if state_a_id == state_b_id:
            if verbose: print(f"⚠️ S{state_a_id} vs S{state_b_id}: same state, return None")
            return None
        
        state_a = self.states_Dict[state_a_id]
        state_b = self.states_Dict[state_b_id]

        syms_a = {sym for sym, _ in state_a.transitions}
        syms_b = {sym for sym, _ in state_b.transitions}
        common = syms_a & syms_b

        if not common:
            if verbose: print(f"⚠️ No common outgoing symbol found for S{state_a.id} vs S{state_b.id}")
            return None
        
        k_list: List[int] = []
        for sym in common:
            if sym not in self.k_vector.keys():
                if verbose: print(f"❌ No valid k value for '{sym}', or k-vector not initialized")
                continue
            k_list.append(int(self.k_vector[sym]))
        
        if not k_list:
            if verbose: print(f"❌ can not find common-symbol-k for S{state_a.id} vs S{state_b.id}, maybe k-vector not initialized")
            return None
        
        if k_list:
            if verbose: print(f"✅ found common sym for S{state_a_id} vs S{state_b_id}: {common}, k_list = {k_list}")
            k_decided = max(k_list) if k_aggregation_mode == "max" else min(k_list)

            return k_decided

    def NFA_merge(self, state_id: int, verbose:bool = False) -> None:
        """
        eliminate NFA recursively
        rules:
        1. check if there are different targets under the same symbol (NFA)
        2. if ture, merge all the targets into the one with smallest id (keep_state_id), delete the others (del_id)
        3. after merge keep_state_id, recursively check keep_state_id again until no NFA on it
        4. untile the original state_id has no NFA, then return
        """

        if state_id not in self.states_Dict:
            if verbose: print(f"S({state_id} no exists, can't do NFA merge)")
            return 
        
        state = self.states_Dict[state_id]

        sym_groups = defaultdict(list)
        for sym, tgt_state in state.transitions:
            sym_groups[sym].append(tgt_state)


        for sym, target_states in sym_groups.items():
            if len(target_states) <= 1:
                if verbose: print(f"✅ S{state_id} [{sym}] has no repeted target")
                continue  
            if len(target_states) > 1:
                target_states_sorted = sorted(target_states, key=lambda x: x.id)
                target_ids_sorted = [t.id for t in target_states_sorted]
                if verbose: print(f"\n⚠️  NFA found ：S{state_id} -{sym} → {target_ids_sorted}")

                keep_state_id = target_states_sorted[0].id
                if verbose:print(f"!!!!!!!!!!!!!target_states[1:] = {target_states_sorted[1:]}")
                for tgt in target_states_sorted[1:]:
                    if state_id not in self.states_Dict:
                        continue
                    del_id = tgt.id
                    if verbose:print(f"   → merge NFA：S{keep_state_id} <- S{del_id}")
                    # print(f"acceptable:S{keep_state_id}={self.states_Dict[keep_state_id].is_accept} ; S{del_id}={self.states_Dict[del_id].is_accept}")

                    self.do_single_merge(keep_state_id, del_id)
                    
                    self.NFA_merge(keep_state_id)
        return 

    def simulate_NFA_merge(self, state_id: int, verbose:bool = False) -> None:
        """
        Simulate NFA elimination on the current dummy automaton (same structure as NFA_merge, but returns whether the whole process can complete successfully):
        1. If a symbol has several distinct targets, merge the later targets into the target with the smallest id, one after another;
        2. Before merging, if both states are still in states_Dict, their is_accept flags must match; otherwise return False;
        3. If one side is no longer in states_Dict (e.g. removed by an earlier merge), skip that merge — this does not count as failure;
        4. Recurse until the current state has no symbol with multiple targets;
        5. Return True if no failure occurred at any step.
        """
        if state_id not in self.states_Dict:
            if verbose: print(f"S({state_id} no exists, can't do NFA merge)")
            return 
        
        state = self.states_Dict[state_id]

        sym_groups = defaultdict(list)
        for sym, tgt_state in state.transitions:
            sym_groups[sym].append(tgt_state)


        for sym, target_states in sym_groups.items():
            if len(target_states) <= 1:
                if verbose: print(f"DUMMY:✅ S{state_id} [{sym}] has no repeted target")
                continue  
            if len(target_states) > 1:
                if verbose: print(f"DUMMY:now checking S{state_id}[{sym}], see if leading to multiple target state")
                target_states_sorted = sorted(target_states, key=lambda x: x.id)
                target_ids_sorted = [t.id for t in target_states_sorted]
                if verbose: print(f"\n⚠️  DUMMY:NFA found ：S{state_id} -{sym} → {target_ids_sorted}")

                keep_state_id = target_states_sorted[0].id
                if verbose: print(f"DUMMY:!!!!!!!!!!!!!target_states[1:] = {target_states_sorted[1:]}")
                for tgt in target_states_sorted[1:]:
                    if state_id not in self.states_Dict:
                        continue
                    del_id = tgt.id

                    if keep_state_id not in self.states_Dict or del_id not in self.states_Dict:
                        if verbose:print(f"DUMMY:⏭️ skip S{keep_state_id} <- S{del_id}: not both in states_Dict, continue")
                        continue
                    
                    keep_state = self.states_Dict[keep_state_id]
                    del_state = self.states_Dict[del_id]

                    if keep_state.is_accept != del_state.is_accept:
                        if verbose:print(f"DUMMY:❌ simulate_NFA_merge failed: S{keep_state_id}.is_accept={keep_state.is_accept} != S{del_id}.is_accept={del_state.is_accept}")
                        return False

                    if verbose: print(f"DUMMY:   → merge NFA：S{keep_state_id} <- S{del_id}")

                    self.do_single_merge(keep_state_id, del_id)
                    NFA_merge_succ = self.simulate_NFA_merge(keep_state_id,verbose=verbose)
                    if NFA_merge_succ == False:
                        return False
                    
        return True

    def Global_merge(self, verbose:bool = False, k_aggregation_mode: Literal["max", "min"] = "max",) -> None:
        """
        Global automatic merge algorithm (implemented exactly as specified).
        1. Iterate over all unordered pairs of states.
        2. First check whether k-tails match (overlap).
        3. If they match → then check whether can_merge allows the merge.
        4. If allowed → perform do_single_merge.
        5. After merging → call NFA_merge on the kept state to remove NFA nondeterminism.
        6. Repeat until a full pass finds no further mergeable pair.
        """
        if verbose: print(f"\n===== GLOBAL MERGE (k-vector = {self.k_vector} =====")

        if_merged = True
        round_count = 0

        while if_merged:
            if_merged = False 
            round_count += 1

            state_ids = list(self.states_Dict.keys())  
            state_total = len(state_ids)

            


            if verbose: print(f"\n===== {round_count}-th round | current state number :{state_total} =====")
            for i in range(state_total):
                state1_id = state_ids[i]
                for j in range(i + 1, state_total):
                    state2_id = state_ids[j]
                
                    if verbose: print(f"\n----------------------------------------")
                    if verbose: print(f"checking pairs to merge：S{state1_id} ↔ S{state2_id}")

                    if state1_id not in self.states_Dict or state2_id not in self.states_Dict:
                        if verbose: print(f"When providing two pairs:keep_state_id = {state1_id} or delete_state_id = {state2_id} not existed in Automaton.states_Dict, try next pair")
                        continue
                    
                    k = self.k_common_outgoing(state1_id,state2_id,k_aggregation_mode=k_aggregation_mode)
                    if k == None:   
                        continue 

                    kt_state1 = self.compute_state_k_tail(state1_id, k,verbose=verbose)
                    kt_state2 = self.compute_state_k_tail(state2_id, k,verbose=verbose)
                    if verbose: print(f"{k}-tail of S{state1_id}: {kt_state1}")
                    if verbose: print(f"{k}-tail of S{state2_id}: {kt_state2}")

                    if (kt_state1 is None) or (kt_state2 is None):
                        if verbose: print(f"S{state1_id} ↔ S{state2_id} ❌ skip: k-tail missing (None)")
                        continue
                    
                    common_k_tail = set(kt_state1) & set(kt_state2)
                    
                    if not common_k_tail:
                        if verbose: print(f"S{state1_id} ↔ S{state2_id} ❌ have NO common {k}-tail different, try next pair")
                        continue
                    if common_k_tail:
                        if verbose: print(f"S{state1_id} ↔ S{state2_id} ✅ HAVE COMMON {k}-tail : {common_k_tail}, \n checking can_merge validation")
                        canMerge = self.can_merge(state1_id, state2_id,verbose=verbose)
                        
                        if canMerge == False:
                            if verbose: print(f"❌ can_merge FAIL, try next pair")
                            continue
                        if canMerge == True:
                            if verbose: print(f"✅ can_merge PASS, doing single_merging")
                            self.do_single_merge(state1_id, state2_id)
                            if_merged = True  
                            if verbose: print(f"✅ single_merge success {state1_id} <- S{state2_id}")
                            if verbose: print(f" conduct NFA_merge S{state1_id}")
                            keep_state_id = min(state1_id, state2_id)
                            self.NFA_merge(keep_state_id,verbose=verbose)

                            break # exit j loop

                if if_merged == True:
                    break   # exit i loop

def single_infer(
        atm: Automaton,
        test_pos: List[List[str]],
        test_neg: List[List[str]],
        ATM_fileName: str,
        k_vector: Optional[Dict[str, int]] = None,
        all_k: int = 2,
        k_aggregation_mode: Literal["max", "min"] = "max",
        output_dir: str = "output",
        global_merge_verbose: bool = False,
        eval_verbose: bool = True,
) -> Dict[str, Any]:
    
    if k_vector is not None:
        atm.initialize_k_vector(values=k_vector)
    else:
        atm.initialize_k_vector(values=None, All_k=all_k)

    
    atm.Global_merge(verbose=global_merge_verbose, k_aggregation_mode=k_aggregation_mode)
    atm.export_to_dot(file_name=ATM_fileName)

    # ATM_BCR_fileName = f"{ATM_fileName}_ATM_BCR"
    # metrics = atm.evaluate_bcr(
    #     test_pos,
    #     test_neg,
    #     verbose=eval_verbose,
    #     filename=ATM_BCR_fileName,
    #     output_dir=output_dir,
    # )

    return 
    
def optimal_k_vector(
    raw_training_file: Tuple[List[List[str]], List[List[str]]],
    k_upper: int,
    *,
    train_ratio: float = 0.6,
    seed: int = 20,
    k_aggregation_mode: Literal["max", "min"] = "max",
    verbose: bool = True,
) -> Dict[str, Any]:
    
    if k_upper < 1:
        raise ValueError("k_upper must >= 1")
    
    raw_pos, raw_neg = parse_traces(raw_training_file)
    
    pos_cp = copy.deepcopy(raw_pos)
    neg_cp = copy.deepcopy(raw_neg)

    train_pos, train_neg, val_pos, val_neg = split_train_test(pos_cp,neg_cp,train_ratio,seed)

    base_atm  =  Automaton(name="optimal_k_search_base")
    base_atm.build_PTA_from_trace(train_pos, train_neg)
    base_atm.update_alphabet()
    alphabet = sorted(base_atm.alphabet)

    if len(alphabet) == 0:
        raise ValueError("alphabet empty, cannot search for k-vector")
    
    all_results: List[Dict[str, Any]] = []
    best_bcr = float("-inf")
    best_k_vector: Optional[Dict[str, int]] = None

    for ks in itertools.product(range(1, k_upper + 1), repeat=len(alphabet)):
        kv = {sym: int(k) for sym, k in zip(alphabet, ks)}

        atm = base_atm.copy_automaton()
        atm.initialize_k_vector(values=kv)
        atm.Global_merge(verbose=False, k_aggregation_mode=k_aggregation_mode)
        metrics = atm.evaluate_bcr(val_pos, val_neg, verbose=False)
        bcr = metrics["BCR"]
        single_result = {
            "k_vector": kv,
            "BCR": bcr,
            "sensitivity": metrics["sensitivity"],
            "specificity": metrics["specificity"],
        }
        if verbose: print(single_result)
        all_results.append(single_result)
        if bcr > best_bcr:
            best_bcr = bcr
            best_k_vector = kv
    result = {
        "best_k_vector": best_k_vector,
        "best_bcr": best_bcr,
        "num_candidates": len(all_results),
        "alphabet": alphabet,
        "all_results": all_results,
    }
    if verbose:
        print("=== optimal_k_vector result ===")
        print(f"alphabet: {alphabet}")
        print(f"num_candidates: {result['num_candidates']}")
        print(f"best_bcr: {best_bcr:.4f}")
        print(f"best_k_vector: {best_k_vector}")

    return result

def optimal_k_vector_cv(
    raw_training_file,
    k_upper: int,
    *,
    n_splits: int = 5,
    seed: int = 20,
    k_aggregation_mode: Literal["max", "min"] = "max",
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    use  K-fold cross validation to get optimal k-vector：
    for every candidate k-vector, compute the average BCR across K folds, and select the one with the highest average BCR
    """
    if k_upper < 1:
        raise ValueError("k_upper must >= 1")
    raw_pos, raw_neg = parse_traces(raw_training_file)
    folds = k_fold_split(raw_pos, raw_neg, n_splits=n_splits, seed=seed)

    t0 = time.perf_counter()
    base_atm = Automaton(name="optimal_k_search_base_cv")
    base_atm.build_PTA_from_trace(raw_pos, raw_neg)
    base_atm.update_alphabet()
    alphabet = sorted(base_atm.alphabet)
    if len(alphabet) == 0:
        raise ValueError("alphabet empty, cannot search for k-vector")
    all_results: List[Dict[str, Any]] = []
    best_mean_bcr = float("-inf")
    best_k_vector: Optional[Dict[str, int]] = None
    for ks in itertools.product(range(2, k_upper + 1), repeat=len(alphabet)):
        kv = {sym: int(k) for sym, k in zip(alphabet, ks)}
        fold_scores = []
        fold_sens = []
        fold_spec = []
        for fold_idx, (train_pos, train_neg, val_pos, val_neg) in enumerate(folds, start=1):
            atm = Automaton(name=f"cv_fold_{fold_idx}")
            atm.build_PTA_from_trace(train_pos, train_neg)
            atm.initialize_k_vector(values=kv)
            atm.Global_merge(verbose=False, k_aggregation_mode=k_aggregation_mode)
            m = atm.evaluate_bcr(val_pos, val_neg,timer=None, verbose=False)
            fold_scores.append(m["BCR"])
            fold_sens.append(m["sensitivity"])
            fold_spec.append(m["specificity"])
        mean_bcr = sum(fold_scores) / len(fold_scores)
        mean_sens = sum(fold_sens) / len(fold_sens)
        mean_spec = sum(fold_spec) / len(fold_spec)
        single_result = {
            "k_vector": kv,
            "mean_BCR": f"{mean_bcr:.4f}",
            "mean_sensitivity": f"{mean_sens:.4f}",
            "mean_specificity": f"{mean_spec:.4f}",
            "fold_BCRs": [f"{x:.4f}" for x in fold_scores],
        }
        all_results.append(single_result)
        if verbose:
            print(single_result)
        if mean_bcr > best_mean_bcr:
            best_mean_bcr = mean_bcr
            best_k_vector = kv
    
    result = {
        "best_k_vector": best_k_vector,
        "best_bcr": best_mean_bcr,  
        "num_candidates": len(all_results),
        "alphabet": alphabet,
        "n_splits": n_splits,
        "all_results": all_results,
    }
    elapsed = time.perf_counter() - t0
    print(f"⏱️ optimal_k_vector_cv completed in {round(elapsed, 2)} seconds")
    if verbose:
        print("=== optimal_k_vector_cv result ===")
        print(f"alphabet: {alphabet}")
        print(f"n_splits: {n_splits}")
        print(f"num_candidates: {result['num_candidates']}")
        print(f"best_bcr(mean cv): {best_mean_bcr:.4f}")
        print(f"best_k_vector: {best_k_vector}")
    return result

def infer_pipline(output_dir: str, raw_train_file: str, test_file: str) -> dict:
    t0 = time.perf_counter()
    train_pos, train_neg = parse_traces(raw_train_file)
    test_pos, test_neg = parse_traces(test_file)

    ATM_name = Path(raw_train_file).stem

    atm = Automaton(ATM_name)
    atm.build_PTA_from_trace(train_pos,train_neg)
    pta_metrics = atm.evaluate_PTA(test_pos, test_neg,output_dir=output_dir, filename=f"{ATM_name}_PTA_BCR")
    
    atm.export_pta_to_json(output_dir=output_dir, filename=f"{ATM_name}_PTA")
    
    # optimal_kv = optimal_k_vector(raw_train_file,2,train_ratio=0.7,verbose=False)["best_k_vector"]
    optimal_kv = optimal_k_vector_cv(raw_train_file, k_upper=3, n_splits=5, seed=20, verbose=True)["best_k_vector"]
    k_vector_to_json(optimal_kv,output_dir,f"{ATM_name}_optimal_kv")

    single_infer(atm,test_pos, test_neg, ATM_name,k_vector=optimal_kv,k_aggregation_mode="max",output_dir=output_dir,global_merge_verbose=False,eval_verbose=True)

    total_time_sec = time.perf_counter() - t0

    atm.evaluate_bcr(test_pos, test_neg, timer=total_time_sec, verbose=True, filename=f"{ATM_name}_ATM_BCR", output_dir=output_dir)

    print(f"✅ {ATM_name} finished in {round(total_time_sec, 2)} s")

    return {
        "ATM_name": ATM_name,
        "optimal_k_vector": optimal_kv,
        "pta_metrics": pta_metrics,
        # "infer_metrics": infer_metrics,
        "total_time_sec": round(total_time_sec, 4),
    }


            
# testing area
def single_infer_test():
    train_file = 'training_data/automaton_10_2_5_0~2.txt' 
    test_file  = 'training_data/automaton_10_2_5_0~99.txt'
    automaton_name = Path(train_file).name

    train_pos, train_neg = parse_traces(train_file)
    test_pos, test_neg = parse_traces(test_file)

    atm = Automaton(automaton_name)
    atm.build_PTA_from_trace(train_pos, train_neg)
    pta_result = atm.evaluate_PTA(test_pos,test_neg,filename=f"{automaton_name}_PTA")

    k_vector = {"L0":2,"L1":2,"L2":2,"L3":2,"L4":2}

    result = single_infer(atm,test_pos, test_neg, "test25_ATM", k_vector=k_vector,k_aggregation_mode="max",output_dir="./output/10_state", eval_verbose=False)
    print(result)


def main():
    # raw_train_file = 'training_data/automaton_10_2_5_0~0.txt' 
    # test_file      = 'training_data/automaton_10_2_5_0~99.txt'
    # output_dir = "output/10_state"

    # global infer pipeline for all datasets
    for i in range(5,6):
        raw_train_file = f"training_data/automaton_10_2_5_0~{i}.txt"
        test_file      = 'training_data/automaton_10_2_5_0~99.txt'
        output_dir = "output/10_state"
        infer_pipline(output_dir, raw_train_file, test_file)
    
    # single_infer_test()




    
if __name__ == "__main__":
    main()
