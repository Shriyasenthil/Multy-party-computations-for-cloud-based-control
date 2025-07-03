import socket
import sys
import struct
import json
from gmpy2 import mpz
import labhe
import DGK
import genDGK
import time

def recv_size(sock):
    total_len = 0
    total_data = []
    size = sys.maxsize
    recv_size = 4096
    while total_len < size:
        sock_data = sock.recv(recv_size)
        if not total_data:
            if len(sock_data) > 4:
                size = struct.unpack('>i', sock_data[:4])[0]
                total_data.append(sock_data[4:])
            else:
                continue
        else:
            total_data.append(sock_data)
        total_len = sum(len(i) for i in total_data)
    return b''.join(total_data)

def get_enc_data(data):
    return [labhe.Ciphertext(label="default", ciphertext=mpz(x)) for x in data]

def main():
    print("Server2: Initializing...")
    privkey, pubkey = labhe.Init(512)
    DGK_pubkey = DGK.DGKpubkey(123, 2, 3, 20)  # placeholder values

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 10000
    sock.bind(('localhost', port))
    sock.listen(1)
    print(f"Server2: Listening on port {port}...")

    connection, addr = sock.accept()
    print(f"Server2: Connection established with Server1.")

    try:
        print("Server2: Waiting for encrypted x0 from Server1...")
        enc_data = recv_size(connection)
        enc_x0 = json.loads(enc_data.decode())
        print("Server2: Received encrypted x0:", enc_x0)

        # Simulate comparison
        t_comp = [1 if i % 2 == 0 else 0 for i in range(len(enc_x0))]
        t_comp_json = json.dumps(t_comp)
        print("Server2: Sending t_comp:", t_comp)
        connection.sendall(struct.pack('>i', len(t_comp_json)) + t_comp_json.encode('utf-8'))

        # Wait for OT messages
        print("Server2: Waiting for OT messages from Server1...")
        ot_raw = recv_size(connection)
        ot_pair = json.loads(ot_raw.decode())
        msg0 = json.loads(ot_pair[0])
        msg1 = json.loads(ot_pair[1])
        print("Server2: OT Message 0:", msg0)
        print("Server2: OT Message 1:", msg1)

        # Select based on t_comp[0]
        selected = msg1 if t_comp[0] else msg0
        ct = labhe.Ciphertext(selected['label'], mpz(selected['ciphertext']))
        decrypted = labhe.D(privkey, ct)
        print("Server2: OT selected value:", decrypted)

    finally:
        print("Server2: Closing socket.")
        connection.close()

if __name__ == '__main__':
    main()
