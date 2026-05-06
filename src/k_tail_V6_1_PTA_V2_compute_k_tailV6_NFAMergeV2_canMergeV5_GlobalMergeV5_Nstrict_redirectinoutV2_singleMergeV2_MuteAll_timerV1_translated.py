from function import * 
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
from pathlib import Path
import json
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

    def copy_automaton(self) -> "Automaton":
        old_ids = sorted(self.states_Dict.keys())
        if not old_ids:
            return Automaton(name=self.name + "_copy")
        new_atm = Automaton(name=self.name + "_copy")
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

    def _add_state(self):
        state_id=len(self.states_Dict)
        new_state = State(state_id)  
        self.states_Dict[state_id] =new_state
        return new_state

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
        k=None,
        timer=None,
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
            **({"elapsed_time_sec": timer} if timer is not None else {})
        }
        lines = [
            f"=== BCR evaluation k={k}===",
            f"ATM states num = {len(self.states_Dict)}",
            f"Positive traces: {len(pos_traces)} | Negative traces: {len(neg_traces)}",
            f"TP={tp}  FN={fn}  TN={tn}  FP={fp}",
            f"Sensitivity (TPR): {sens:.4f}",
            f"Specificity (TNR): {spec:.4f}",
            f"BCR:               {bcr:.4f}",
            f"Elapsed time:      {result['elapsed_time_sec']:.2f} seconds" if timer is not None else "",
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
        verbose: bool = False,
        filename: Optional[str] = None,
        output_dir: str = "output",
    ) -> None:
        res = self.evaluate_bcr(test_pos, test_neg, verbose=False,k=None)
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
        """
        Compute the k-tail of a state:
        1. Only return paths of length exactly k (not paths of length ≤ k).
        2. At the end of each path, indicate whether the final state is accepting.
        3. If there is no path of length k → return None.
        """
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
        
        print(f"✅ DOT saved：{final_path}")

    def can_merge(self, state1_id: int, state2_id: int, verbose: bool = False) -> bool:
        """Helper that checks whether two states can be merged.
            It runs several checks: return False as soon as any check fails; if all checks pass, return True at the end.
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

    def do_single_merge(self, state1_id: int, state2_id: int, verbose: bool = False) -> bool:

        keep_state_id = min(state1_id, state2_id)
        delete_state_id = max(state1_id, state2_id)

        if delete_state_id not in self.states_Dict or keep_state_id not in self.states_Dict:
            if verbose:print(f"When checking do_singale_merge:keep_state_id = {keep_state_id} or delete_state_id = {delete_state_id} not existed in Automaton.states_Dict")
            return False
        self.redirect_incoming(keep_state_id, delete_state_id)
        self.redirect_outgoing(keep_state_id, delete_state_id)

        keep_state = self.states_Dict[keep_state_id]
        delete_state = self.states_Dict[delete_state_id]
        keep_state.is_accept = keep_state.is_accept or delete_state.is_accept

        del self.states_Dict[delete_state_id]

        if verbose :print(f"✅ Keep_S{keep_state_id} <- Delete_S{delete_state_id} merged")
        return True
        
    def redirect_outgoing(self, keep_state_id: int, delete_state_id: int) -> None:
        """
        Move **all outgoing transitions** of `delete_state` onto `keep_state`.
        Then clear the outgoing transitions of `delete_state`.
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
        Visit **every** state and retarget every incoming edge that points to `delete_state`
        so that it points to `keep_state` instead.
        For each (state, symbol) pair, at most one edge is kept—no duplicates.
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

    def NFA_merge(self, state_id: int, verbose:bool = False) -> None:
        """
        【Pure recursive NFA elimination】
        Rules:
        1. Check whether, under `state_id`, some symbol `sym` leads to more than one distinct target state.
        2. If so → merge those target states directly (no k-tail check, no extra predicate).
        3. After merging, recursively check whether the current state still has NFA nondeterminism.
        4. Continue until there is no NFA left.
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
                if verbose: print(f"!!!!!!!!!!!!!target_states[1:] = {target_states_sorted[1:]}")
                for tgt in target_states_sorted[1:]:
                    if state_id not in self.states_Dict:
                        continue
                    del_id = tgt.id
                    if verbose: print(f"   → merge NFA：S{keep_state_id} <- S{del_id}")

                    self.do_single_merge(keep_state_id, del_id)
                    
                    self.NFA_merge(keep_state_id)
        return 
    
    def simulate_NFA_merge(self, state_id: int, verbose:bool = False) -> None:
        """
        On the current dummy automaton, simulate NFA elimination (same structure as NFA_merge, but returns whether the whole process completes successfully):
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
                    NFA_merge_succ = self.simulate_NFA_merge(keep_state_id)
                    if NFA_merge_succ == False:
                        return False
                    
        return True

    def Global_merge(self, k: int, verbose:bool = False) -> None:
        """
        Global automatic merge algorithm (implemented exactly as specified).
        1. Iterate over all unordered pairs of states.
        2. First check whether the k-tails match (overlap).
        3. If they match → then check whether can_merge allows the merge.
        4. If allowed → perform do_single_merge.
        5. After merging → call NFA_merge on the kept state to remove NFA nondeterminism.
        6. Repeat until a full pass finds no further mergeable pair.
        """
        if verbose:print(f"\n===== GLOBAL MERGE (k={k}) =====")

        if_merged = True
        round_count = 0

        while if_merged:
            if_merged = False  
            round_count += 1

            state_ids = list(self.states_Dict.keys()) 
            state_total = len(state_ids)

            


            if verbose:print(f"\n===== {round_count}-th round | current state number :{state_total} =====")
            for i in range(state_total):
                state1_id = state_ids[i]
                for j in range(i + 1, state_total):
                    state2_id = state_ids[j]
                
                    if verbose:print(f"\n----------------------------------------")
                    if verbose:print(f"checking pairs to merge：S{state1_id} ↔ S{state2_id}")

                    if state1_id not in self.states_Dict or state2_id not in self.states_Dict:
                        print(f"When providing two pairs:keep_state_id = {state1_id} or delete_state_id = {state2_id} not existed in Automaton.states_Dict, try next pair")
                        continue

                    kt_state1 = self.compute_state_k_tail(state1_id, k,verbose=verbose)
                    kt_state2 = self.compute_state_k_tail(state2_id, k,verbose=verbose)
                    if verbose:print(f"{k}-tail of S{state1_id}: {kt_state1}")
                    if verbose:print(f"{k}-tail of S{state2_id}: {kt_state2}")

                    if (kt_state1 is None) or (kt_state2 is None):
                        if verbose:print(f"S{state1_id} ↔ S{state2_id} ❌ skip: k-tail missing (None)")
                        continue
                    
                    common_k_tail = set(kt_state1) & set(kt_state2)
                    
                    if not common_k_tail:
                        if verbose:print(f"S{state1_id} ↔ S{state2_id} ❌ have NO common {k}-tail different, try next pair")
                        continue
                    if common_k_tail:
                        if verbose:print(f"S{state1_id} ↔ S{state2_id} ✅ HAVE COMMON {k}-tail : {common_k_tail}, \n checking can_merge validation")
                        canMerge = self.can_merge(state1_id, state2_id,verbose=verbose)
                        
                        if canMerge == False:
                            if verbose:print(f"❌ can_merge FAIL, try next pair")
                            continue
                        if canMerge == True:
                            if verbose:print(f"✅ can_merge PASS, doing single_merging")
                            self.do_single_merge(state1_id, state2_id)
                            if_merged = True 
                            if verbose:print(f"✅ single_merge success {state1_id} <- S{state2_id}")
                            if verbose:print(f" conduct NFA_merge S{state1_id}")
                            keep_state_id = min(state1_id, state2_id)
                            self.NFA_merge(keep_state_id,verbose=verbose)

                            break # exit j loop

                if if_merged == True:
                    break   # exit i loop





            
# testing area





def main():
    t0 = time.perf_counter()
    train_file = 'training_data/automaton_10_2_5_0~6.txt' 
    test_file  = 'training_data/automaton_10_2_5_0~99.txt'
    automaton_name = Path(train_file).name

    train_pos, train_neg = parse_traces(train_file)
    test_pos, test_neg = parse_traces(test_file)

    atm = Automaton(automaton_name)
    atm.build_PTA_from_trace(train_pos, train_neg)
    atm.export_to_dot(file_name=f"{automaton_name}_PTA")
    atm.evaluate_PTA(test_pos,test_neg,filename=f"{automaton_name}_PTA_BCR_Ktail")
    atm.export_pta_to_json()
    atm.Global_merge(k=2,verbose=False)
    elapsed = time.perf_counter() - t0
    atm.evaluate_bcr(test_pos,test_neg, filename=f"{automaton_name}_ATM_BCR_Ktail",k=2,timer=elapsed)
    atm.export_to_dot(file_name=automaton_name)
    
    print(f"\nTotal elapsed time: {elapsed:.2f} seconds")




    
if __name__ == "__main__":
    main()
