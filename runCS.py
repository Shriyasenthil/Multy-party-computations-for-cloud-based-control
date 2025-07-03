#!/usr/bin/env python3
import subprocess
import time
import sys

"""
Run the Model Predictive Control problem using Client-Server simulation.
Based on: https://arxiv.org/pdf/1803.09891.pdf
"""

if __name__ == '__main__':
    try:
        print("Starting Server...", flush=True)
        proc_server = subprocess.Popen(['python3', 'server.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        time.sleep(1)  # Give the server time to start

        print("Starting Client...", flush=True)
        proc_client = subprocess.Popen(['python3', 'client.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        stdout_client, stderr_client = proc_client.communicate()
        stdout_server, stderr_server = proc_server.communicate()

        print("\n--- Server Output ---\n", stdout_server)
        print("--- Server Errors ---\n", stderr_server)
        print("\n--- Client Output ---\n", stdout_client)
        print("--- Client Errors ---\n", stderr_client)

    except Exception as e:
        print("An error occurred while running Client-Server:", str(e))
