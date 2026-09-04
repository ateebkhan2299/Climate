import sys
import subprocess
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_local_mapreduce_simulation(sample_size: int = 50000):
    """
    Simulate Hadoop Streaming MapReduce locally using Python subprocess pipes.
    Flow: CSV Stream -> mapper.py -> sort -> reducer.py -> Output
    """
    print("=" * 60)
    print("[INFO] Running Hadoop Streaming MapReduce (Local Streaming Pipe)")
    print("=" * 60)
    
    csv_file = "d:/climate/WeatherEvents_Jan2016-Dec2022.csv"
    if not os.path.exists(csv_file):
        print(f"Error: Dataset {csv_file} not found.")
        return

    # Read top N lines from CSV to stream into mapper
    print(f"[*] Reading sample stream of {sample_size:,} records from {csv_file}...")
    lines = []
    with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f):
            if i >= sample_size:
                break
            lines.append(line)
    
    input_text = "".join(lines)

    # Stage 1: Mapper
    print("[*] Executing Mapper: Mapping events to (State, 1)...")
    mapper_proc = subprocess.Popen(
        [sys.executable, "d:/climate/hadoop/mapper.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    mapped_out, mapper_err = mapper_proc.communicate(input=input_text)

    # Stage 2: Shuffle & Sort
    print("[*] Executing Shuffle & Sort stage...")
    mapped_lines = [line.strip() for line in mapped_out.strip().split('\n') if line.strip()]
    sorted_lines = sorted(mapped_lines)
    sorted_input = "\n".join(sorted_lines) + "\n"

    # Stage 3: Reducer
    print("[*] Executing Reducer: Aggregating total weather events by state...")
    reducer_proc = subprocess.Popen(
        [sys.executable, "d:/climate/hadoop/reducer.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    reduced_out, reducer_err = reducer_proc.communicate(input=sorted_input)

    print("\n" + "=" * 60)
    print("[RESULT] MapReduce Output (Top 15 States by Weather Event Frequency):")
    print("=" * 60)
    results = []
    for line in reduced_out.strip().split('\n'):
        if line and '\t' in line:
            st, cnt = line.split('\t')
            results.append((st, int(cnt)))
    
    results.sort(key=lambda x: x[1], reverse=True)
    print(f"{'State':<10} {'Total Events':<15}")
    print("-" * 25)
    for st, cnt in results[:15]:
        print(f"{st:<10} {cnt:<15,}")
    print("-" * 25)
    print(f"Total Unique States Processed: {len(results)}")
    print("=" * 60)

def print_hdfs_cluster_commands():
    """Display production Hadoop HDFS cluster commands."""
    print("\n[INFO] Production Hadoop HDFS Cluster Execution Commands:")
    print("-" * 60)
    print("""
# 1. Create HDFS Directory Structure
hdfs dfs -mkdir -p /climate/raw /climate/processed /climate/ml /climate/output

# 2. Upload Raw Weather Dataset to HDFS
hdfs dfs -put WeatherEvents_Jan2016-Dec2022.csv /climate/raw/

# 3. Submit Hadoop Streaming MapReduce Job to YARN Cluster
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \\
  -files d:/climate/hadoop/mapper.py,d:/climate/hadoop/reducer.py \\
  -input /climate/raw/WeatherEvents_Jan2016-Dec2022.csv \\
  -output /climate/output/state_events_summary \\
  -mapper "python3 mapper.py" \\
  -reducer "python3 reducer.py"

# 4. View Processed Results from HDFS
hdfs dfs -cat /climate/output/state_events_summary/part-00000 | head -n 20
""")

if __name__ == "__main__":
    run_local_mapreduce_simulation(sample_size=100000)
    print_hdfs_cluster_commands()
