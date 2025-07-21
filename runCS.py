#!/usr/bin/env python3

import subprocess
import sys
import time
import os
from threading import Thread

def run_server(server_name, script_name):
    print(f"Starting {server_name}...")
    try:
        process = subprocess.Popen([sys.executable, script_name])
        return process
    except Exception as e:
        print(f"Error starting {server_name}: {e}")
        return None

def main():

    
    print("Step 1: Starting servers...")
    
    # Start servers
    server1_process = run_server("Server1", "server1.py")
    server2_process = run_server("Server2", "server2.py")
    
    if not server1_process or not server2_process:
        print("Failed to start servers!")
        return
    
    # Wait for servers to start
    print("Waiting for servers to initialize...")
    time.sleep(2)
    
    print("\nStep 2: Running client...")
    #Client will: Encrypt state vector x0 = [1, 2]. Send encrypted x0=1 to Server1 with gain k0=5.
    # Send encrypted x1=2 to Server2 with gain k1=10. Receive encrypted results and compute u = k0*x0 + k1*x1 and finally decrypt final result (expected: 5*1 + 10*2 = 25)
    print()
    
    try:
        # Run client
        client_process = subprocess.run([sys.executable, "client.py"], 
                                       capture_output=False, text=True)
        
        if client_process.returncode == 0:
            print("\n System execution completed successfully!")
        else:
            print(f"\n Client execution failed with return code: {client_process.returncode}")
            
    except KeyboardInterrupt:
        print("\n\nShutting down system...")
    except Exception as e:
        print(f"\nError running client: {e}")
    finally:
        
        print("\nStopping servers...")
        if server1_process:
            server1_process.terminate()
        if server2_process:
            server2_process.terminate()
        
        # Wait for processes to terminate
        time.sleep(1)
        
        # Force kill if still running
        if server1_process and server1_process.poll() is None:
            server1_process.kill()
        if server2_process and server2_process.poll() is None:
            server2_process.kill()
        
        print("System shutdown complete.")

if __name__ == "__main__":
    main()