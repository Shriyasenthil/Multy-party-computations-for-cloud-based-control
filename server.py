import socket
import struct
import json
import numpy as np
import labhe

def recv_data(conn):
    data = b''
    size_data = conn.recv(4)
    size = struct.unpack('>i', size_data)[0]
    while len(data) < size:
        to_read = size - len(data)
        data += conn.recv(4096 if to_read > 4096 else to_read)
    return data

def main():
    print("Server: Initializing LabHE...")
    privkey, pubkey = labhe.Init(512)
    upk, _ = labhe.KeyGen(pubkey)

    # Example parameters (update if needed)
    n, m, N = 5, 5, 7

    # Corrected file loading with underscores
    H = np.loadtxt(f"Data/H{n}_{m}_{N}.txt", delimiter=',')
    F = np.loadtxt(f"Data/F{n}_{m}_{N}.txt", delimiter=',')
    G = np.loadtxt(f"Data/G0{n}_{m}_{N}.txt", delimiter=',')
    K = np.loadtxt(f"Data/K{n}_{m}_{N}.txt", delimiter=',')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10001)
    sock.bind(server_address)
    sock.listen(1)
    print("Server: Listening on port 10001...")
    connection, client_address = sock.accept()
    print("Server: Connection established with Client", client_address)

    try:
        data = recv_data(connection)
        payload = json.loads(data.decode())
        print("Server: Received encrypted x0 from Client")

        # Dummy secure computation result
        result = [1, 0]
        result_json = json.dumps(result)
        connection.sendall(struct.pack('>i', len(result_json)) + result_json.encode('utf-8'))
        print("Server: Sent result to Client")

    finally:
        print("Server: Closing connection")
        connection.close()

if __name__ == '__main__':
    main()
