import socket
import pickle
import threading
from paillier import EncryptedNumber

class Server2:
    def __init__(self, host='localhost', port=8002):
        self.host = host
        self.port = port
        self.server_socket = None
        
    def handle_client(self, client_socket, address):
        #Handle incoming client connection
        try:
            print(f"Server2: Connection from {address}")
            
            # Receive data length
            data_length = int.from_bytes(client_socket.recv(4), 'big')
            
            # Receive data
            data = b''
            while len(data) < data_length:
                chunk = client_socket.recv(data_length - len(data))
                if not chunk:
                    break
                data += chunk
            
            # Deserialize data
            request = pickle.loads(data)
            
            print(f"Server2: Received encrypted value and gain k1 = {request['gain']}")
            
            # Extract components
            public_key = request['public_key']
            encrypted_value = request['encrypted_value']
            gain = request['gain']
            
            # Perform homomorphic multiplication: k1 * x1
            encrypted_result = encrypted_value * gain
            
            print(f"Server2: Computed k1 * x1 homomorphically")
            
            # Send result back to client
            response = encrypted_result
            serialized_response = pickle.dumps(response)
            
            client_socket.sendall(len(serialized_response).to_bytes(4, 'big'))
            client_socket.sendall(serialized_response)
            
            print(f"Server2: Sent encrypted result back to client")
            
        except Exception as e:
            print(f"Server2: Error handling client: {e}")
        finally:
            client_socket.close()
    
    def start(self):
        #Start the server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Server2: Listening on {self.host}:{self.port}")
            
            while True:
                client_socket, address = self.server_socket.accept()
                
                # Handle each client in separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\nServer2: Shutting down...")
        except Exception as e:
            print(f"Server2: Error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

if __name__ == "__main__":
    server = Server2()
    server.start()