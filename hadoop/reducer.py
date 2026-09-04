#!/usr/bin/env python
"""
Hadoop Streaming Reducer for EarthScape Climate Agency
Aggregates occurrence counts for each State from sorted (Key, Value) stream.
Emits:
State \t Total_Events
"""
import sys

def reducer():
    current_state = None
    current_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            state, count = line.split('\t', 1)
            count = int(count)
        except ValueError:
            continue

        if current_state == state:
            current_count += count
        else:
            if current_state is not None:
                print(f"{current_state}\t{current_count}")
            current_state = state
            current_count = count

    # Output final state
    if current_state is not None:
        print(f"{current_state}\t{current_count}")

if __name__ == "__main__":
    reducer()
