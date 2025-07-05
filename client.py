import socket
import struct
import json
import labhe
from gmpy2 import mpz
from utils import encrypt_vector, decrypt_vector, truncate, project_on_Ubar
import numpy as np  

def send_data(sock, data):
    payload = json.dumps(data)
    sock.sendall(struct.pack('>i', len(payload)) + payload.encode('utf-8'))

def recv_data(sock):
    size_data = sock.recv(4)
    if not size_data or len(size_data) < 4:
        raise ConnectionError("Incomplete or no message header received from server.")
    size = struct.unpack('>i', size_data)[0]
    data = b''
    while len(data) < size:
        chunk = sock.recv(min(4096, size - len(data)))
        if not chunk:
            raise ConnectionError("Incomplete message body received.")
        data += chunk
    return json.loads(data.decode())

class FGDClient:
    def __init__(self, lf, pubkey, privkey, sock):
        self.lf = lf
        self.pubkey = pubkey
        self.privkey = privkey
        self.sock = sock

    def run_protocol(self, x_t, Ubar, K):
       
        encrypted_xt = encrypt_vector(x_t, self.pubkey, label='xt')
        print("Client: Sending encrypted x(t)...")
        send_data(self.sock, {'type': 'xt', 'data': [str(c.ciphertext) for c in encrypted_xt]})

        for k in range(K):
            
            print(f"Client: Waiting for tk at iteration {k}...")
            msg = recv_data(self.sock)
            if msg['type'] != 'tk':
                raise ValueError("Unexpected message type")

            enc_tk = msg['data']
            tk_plain = decrypt_vector(enc_tk, self.privkey)
            tk_trunc = truncate(tk_plain, self.lf)

            Uk_plus1 = project_on_Ubar(tk_trunc, Ubar)

            encrypted_Uk_plus1 = encrypt_vector(Uk_plus1, self.pubkey, label='xt')
            send_data(self.sock, {'type': 'Uk+1', 'data': [str(c.ciphertext) for c in encrypted_Uk_plus1]})

        
        print("Client: Waiting for final UK...")
        msg = recv_data(self.sock)
        if msg['type'] != 'final':
            raise ValueError("Unexpected message type")
        encrypted_final_UK = msg['data']
        final_UK = decrypt_vector(encrypted_final_UK, self.privkey)
        return final_UK[:len(Ubar)]

def main():
    print("Client: Initializing LabHE keys...")
    privkey, pubkey = labhe.Init(512)
    upk, _ = labhe.KeyGen(pubkey)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10001)
    print("Client: Connecting to Server1...")
    sock.connect(server_address)

    
    x_t = np.random.uniform(-10, 10, size=35).tolist()
    Ubar = [(-10, 10) for _ in range(35)]  
    K = 3   
    lf = 2  

    
    client = FGDClient(lf, pubkey, privkey, sock)
    result = client.run_protocol(x_t, Ubar, K)
    print("Client: Final projected result:", result)
    sock.close()

if __name__ == '__main__':
    main()
