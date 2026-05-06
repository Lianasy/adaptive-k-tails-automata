import os
import re

def split_samples(input_file):
    filename = os.path.basename(input_file)
    match = re.search(r'~(\d+)', filename)

    if not match:
        raise ValueError("Filename must contain ~n (e.g. automaton~1.txt)")

    n = match.group(1)

    pos_file = f"{int(n)+1}_pos.txt"
    neg_file = f"{int(n)+1}_neg.txt"

    pos_lines = []
    neg_lines = []

    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("+"):
                # remove "+ "
                pos_lines.append(line[2:])
            elif line.startswith("-"):
                # remove "- "
                neg_lines.append(line[2:])

    with open(pos_file, "w") as f:
        f.write("\n".join(pos_lines))

    with open(neg_file, "w") as f:
        f.write("\n".join(neg_lines))

    print(f"Created {pos_file} with {len(pos_lines)} samples")
    print(f"Created {neg_file} with {len(neg_lines)} samples")

    os.remove(input_file)


for file in os.listdir():
    if "~" in file and file.endswith(".txt"):
        split_samples(file)