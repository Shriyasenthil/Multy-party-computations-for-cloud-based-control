#!/usr/bin/env python3
from subprocess import Popen, PIPE
import time

"""
Run the Model Predictive Control problem on encrypted data in a Two-Server architecture.
This launches server1.py and server2.py as separate subprocesses.
"""

def run_script(name, path):
    print(f"Starting {name}...", flush=True)
    return Popen(['python3', path], stdout=PIPE, stderr=PIPE, universal_newlines=True)

if __name__ == '__main__':
    try:
        # Start Server1
        proc1 = run_script("Server1", "server1.py")

        time.sleep(2)  # Give Server1 time to initialize

        # Start Server2
        proc2 = run_script("Server2", "server2.py")

        # Wait for Server2 to finish
        stdout2, stderr2 = proc2.communicate()

        # If Server2 is done, assume Server1 is also done
        stdout1, stderr1 = proc1.communicate()

        # Print collected outputs
        print("\n====== Server1 Output ======")
        print(stdout1)
        print("====== Server1 Errors ======")
        print(stderr1)

        print("\n====== Server2 Output ======")
        print(stdout2)
        print("====== Server2 Errors ======")
        print(stderr2)

    except Exception as e:
        print("An error occurred while running the servers:", e)
