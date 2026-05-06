from collections import deque
from graphviz import Digraph

class PTAState:
    def __init__(self, state_id):
        self.id = state_id              # Unique identifier for the state
        self.transitions = {}           # Dictionary mapping input symbols to next states
        self.is_accepting = False       # True if this state is an accepting state (end of sequence), False otherwise
    
    def __str__(self):
        """Return a string representation of the state, showing its ID, whether it's accepting, and its transitions."""
        lines = []

        lines.append(f"State:\n\t q{self.id}")
        lines.append(f"Accepting:\n\t {self.is_accepting}")
        lines.append("Transitions:")

        if self.transitions:
            for symbol, next_state in self.transitions.items():
                lines.append(f"\t q{self.id}--{symbol}--> q{next_state.id}")
        else:
            lines.append("\t (no transitions)")

        return "\n".join(lines)

class PTA:
    def __init__(self):
        self.states = []                        # List of all states
        self.root = self._new_state()           # Create the root state (state 0)

    def _new_state(self):
        """Create a new state with a unique ID and add it to the list of states."""
        state = PTAState(len(self.states))      # Assign a unique ID based on the current number of states
        self.states.append(state)               # Add the new state to the list of states
        return state
    
    def __str__(self):
        """Return a string representation of the PTA, showing states and transitions."""
        lines = []

        # States
        state_line = ["States:"]
        for state in self.states:
            if state.is_accepting:
                state_line.append(f"[q{state.id}]\n")       # Enter new line when printed accepting state
            else:
                state_line.append(f"q{state.id}")

        lines.append(" ".join(state_line))

        # Transitions
        lines.append("Transitions:")
        for state_id, transitions in self.get_transition_dict().items():
            for symbol, next_state_id in transitions.items():
                lines.append(f"  q{state_id} --{symbol}--> q{next_state_id}")

        return "\n".join(lines)

    def add_trace(self, trace):
        """Add a trace to the PTA."""
        current = self.root                                         # Start from the root state
        for symbol in trace:
            if symbol not in current.transitions:
                current.transitions[symbol] = self._new_state()     # Create a new state if the transition does not exist
            current = current.transitions[symbol]                   # Move to the next state
        current.is_accepting = True                                 # Set the last state as accepting

    def get_alphabet(self):
        """Return the set of all symbols used in the PTA."""
        alphabet = set()
        for state in self.states:
            alphabet.update(state.transitions.keys())
        return alphabet
    
    def get_accepting_state_ids(self):
        """Return a set of IDs of all accepting states in the PTA."""
        return {state.id for state in self.states if state.is_accepting}
    
    def get_transition_dict(self):
        """Return a dictionary representation of the PTA transitions."""
        return {
                state.id: {symbol: next_state.id for symbol, next_state in state.transitions.items()}
                for state in self.states
            }

    def get_k_future(self, state_id, k):
        """Return the k future transitions of a state as (path, is_accepting) tuples."""
        if state_id < 0 or state_id >= len(self.states):
            raise ValueError(f"State ID {state_id} is out of bounds.")

        future = set()
        queue = deque([(self.states[state_id], tuple(), 0)])                          # (current_state, path, depth)

        while queue:
            current, path, depth = queue.popleft()

            if depth == k:
                future.add((path, current.is_accepting))
                continue

            for symbol, next_state in current.transitions.items():
                queue.append((next_state, path + (symbol,), depth + 1))

        return future

    def export_to_dot(self, file_path="diagram/pta", state_colors=None):
        """
        Export PTA using graphviz.
        
        state_colors: dict {state_id: color}
            e.g. {0: "red", 3: "blue"}
        """

        dot = Digraph(name="PTA", format="png")
        dot.attr(rankdir="LR")

        # Start node
        dot.node("__start__", shape="point")
        dot.edge("__start__", f"q{self.root.id}")

        # States
        for state in self.states:
            shape = "doublecircle" if state.is_accepting else "circle"
            color = state_colors.get(state.id) if state_colors else None
            if color:
                dot.node(
                    f"q{state.id}",
                    shape=shape,
                    style="filled",
                    fillcolor=color
                )
            else:
                dot.node(
                    f"q{state.id}",
                    shape=shape
                )

        # Transitions
        for state in self.states:
            for symbol, next_state in state.transitions.items():
                dot.edge(f"q{state.id}", f"q{next_state.id}", label=str(symbol))

        # Render
        dot.render(file_path, cleanup=True)

        print(f"[INFO] Graph saved to {file_path}")

def generate_pta(traces):
    pta = PTA()
    for trace in traces:
        pta.add_trace(trace)
    return pta
    
if __name__ == "__main__":
    from utils import read_traces

    file_path = "data/small.txt"
    # file_path = "data/automaton_5s/training_data/1_pos.txt"

    traces = read_traces(file_path)

    pta = generate_pta(traces)

    print("Input traces:")
    for t in traces:
        print(t)

    print("\nConstructed PTA:")
    print(pta)

    state_id = 4

    print("\nPrint individual state:")
    print(pta.states[state_id])

    print("\nAlphabet of the PTA:")
    print(pta.get_alphabet())

    print("\nIDs of accepting states of the PTA:")
    print(pta.get_accepting_state_ids())

    # print("\nTransition dictionary of the PTA:")
    # transition_dict = pta.get_transition_dict()
    # for state_id, transitions in transition_dict.items():
    #     print(f"  q{state_id}: {transitions}")

    print(f"\nK-future of state q{state_id} with k=2:")
    k_future = pta.get_k_future(state_id, k=2)
    for path, is_accepting in k_future:
        print(f"  Path: {path}, Accepting: {is_accepting}")

    state_colors = {
        0: "red",     # red fringe
        1: "blue",    # blue fringe
        5: "yellow"   # maybe merged or candidate
    }
    pta.export_to_dot("diagram/pta", state_colors=state_colors)
    