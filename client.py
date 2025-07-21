import socket
import pickle
import threading
import time
from paillier import generate_paillier_keypair, PaillierPublicKey, PaillierPrivateKey

class Client:
    def __init__(self):
        # Initial state vector x0 = [1, 2]
        self.x0 = [1, 2]
        
        # Generate Paillier key pair
        self.public_key, self.private_key = generate_paillier_keypair()
        
        # Server addresses
        self.server1_address = ('localhost', 8001)
        self.server2_address = ('localhost', 8002)
        
        # Storage for encrypted results
        self.encrypted_results = {}
        
    def send_to_server(self, server_address, data):
        #Send data to specific server
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(server_address)
                
                # Send data
                serialized_data = pickle.dumps(data)
                sock.sendall(len(serialized_data).to_bytes(4, 'big'))
                sock.sendall(serialized_data)
                
                # Receive response
                response_length = int.from_bytes(sock.recv(4), 'big')
                response_data = b''
                while len(response_data) < response_length:
                    chunk = sock.recv(response_length - len(response_data))
                    if not chunk:
                        break
                    response_data += chunk
                
                return pickle.loads(response_data)
        except Exception as e:
            print(f"Error communicating with server {server_address}: {e}")
            return None
    
    def process_server_response(self, server_id, response):
        #Process server response
        if response is not None:
            self.encrypted_results[server_id] = response
            print(f"Received encrypted result from server {server_id}")
    
    def run(self):
        print("Client starting...")
        print(f"Initial state: x0 = {self.x0}")
        
        # Encrypt the state components
        encrypted_x0 = self.public_key.encrypt(self.x0[0])
        encrypted_x1 = self.public_key.encrypt(self.x0[1])
        
        print(f"Encrypted x0: {encrypted_x0}")
        print(f"Encrypted x1: {encrypted_x1}")
        
        # Prepare data for servers
        server1_data = {
            'public_key': self.public_key,
            'encrypted_value': encrypted_x0,
            'gain': 5  # k0 = 5
        }
        
        server2_data = {
            'public_key': self.public_key,
            'encrypted_value': encrypted_x1,
            'gain': 10  # k1 = 10
        }
        
        # Send to servers 
        def send_to_server1():
            response = self.send_to_server(self.server1_address, server1_data)
            self.process_server_response(1, response)
        
        def send_to_server2():
            response = self.send_to_server(self.server2_address, server2_data)
            self.process_server_response(2, response)
        
        # Start threads for communication
        thread1 = threading.Thread(target=send_to_server1)
        thread2 = threading.Thread(target=send_to_server2)
        
        thread1.start()
        thread2.start()
        
        # Wait for threads to complete
        thread1.join()
        thread2.join()
        
        # Check received responses from both servers
        if 1 in self.encrypted_results and 2 in self.encrypted_results:
            print("\nReceived responses from both servers")
            
            # Sum the encrypted results: u = k0*x0 + k1*x1
            encrypted_sum = self.encrypted_results[1] + self.encrypted_results[2]
            
            # Decrypt the final result
            u = self.private_key.decrypt(encrypted_sum)
            
            print(f"Final control input u = {u}")
            print(f"Expected result: {5*1 + 10*2} = {5*1 + 10*2}")
            
            if u == 5*1 + 10*2:
                print(" Homomorphic computation successful!")
            else:
                print(" Homomorphic computation failed!")
        else:
            print("Failed to receive responses from both servers")

if __name__ == "__main__":
    client = Client()
    client.run()