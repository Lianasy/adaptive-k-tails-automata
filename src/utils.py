def read_traces(file_path):
    """Read traces from a file and return them as a 2d list."""
    traces = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()                                             # Remove spaces and newlines
            if not line:                                                    # Skip empty lines
                continue
            trace = [x.strip() for x in line.split(",") if x.strip()]       # Split by comma and remove extra spaces
            traces.append(trace)                                            # Add to the list of traces
    return traces