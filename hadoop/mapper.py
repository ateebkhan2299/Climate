#!/usr/bin/env python
"""
Hadoop Streaming Mapper for EarthScape Climate Agency
Extracts the 'State' field from incoming CSV stream of weather events and emits key-value pairs:
State \t 1
"""
import sys

def mapper():
    for line_idx, line in enumerate(sys.stdin):
        line = line.strip()
        if not line:
            continue
        
        # Skip header if present
        if line_idx == 0 and ("EventId" in line or "State" in line):
            continue
        
        parts = line.split(',')
        if len(parts) >= 13:
            # In WeatherEvents_Jan2016-Dec2022.csv, State is at index 12 (0-indexed)
            state = parts[12].strip()
            if state and state != 'State':
                print(f"{state}\t1")

if __name__ == "__main__":
    mapper()
