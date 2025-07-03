import socket
import struct
import json
import labhe
from gmpy2 import mpz

def send_data(sock, data):
    payload = json.dumps(data)
    sock.sendall(struct.pack('>i', len(payload)) + payload.encode('utf-8'))

def recv_data(sock):
    data = b''
    size_data = sock.recv(4)
    size = struct.unpack('>i', size_data)[0]
    while len(data) < size:
        to_read = size - len(data)
        data += sock.recv(4096 if to_read > 4096 else to_read)
    return data

def main():
    print("Client: Initializing LabHE keys...")
    privkey, pubkey = labhe.Init(512)
    upk, _ = labhe.KeyGen(pubkey)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10001)
    print("Client: Connecting to Server1...")
    sock.connect(server_address)

    # Encrypt one value as example
    val = 12345
    label = "x0_0"
    print(f"Client: Encrypting value {val} with label '{label}'")
    cipher = labhe.E(pubkey, upk, label, val)
    data_to_send = {'label': cipher.label, 'ciphertext': str(cipher.ciphertext)}
    print("Client: Encrypted value sent to Server1")
    send_data(sock, data_to_send)

    print("Client: Waiting for Server1's response...")
    resp = recv_data(sock)
    result = json.loads(resp.decode())
    print("Client: Received result from Server1:", result)
    sock.close()

if __name__ == '__main__':
    main()
