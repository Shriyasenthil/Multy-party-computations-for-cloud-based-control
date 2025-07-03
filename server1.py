import socket
import struct
import json
import labhe
from gmpy2 import mpz

def recv_size(sock):
    total_len = 0
    total_data = []
    size = struct.unpack('>i', sock.recv(4))[0]
    while total_len < size:
        packet = sock.recv(min(4096, size - total_len))
        if not packet:
            break
        total_data.append(packet)
        total_len += len(packet)
    return b''.join(total_data)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 10001
    sock.bind(('localhost', port))
    sock.listen(1)
    print(f"Server1: Listening on port {port}...")

    connection, client_address = sock.accept()
    print(f"Server1: Connection established with Client {client_address}")

    enc_payload = recv_size(connection)
    data = json.loads(enc_payload.decode())
    ct = labhe.Ciphertext(data['label'], mpz(data['ciphertext']))

    print("Server1: Received encrypted x0 from Client")
    print("Server1: Connecting to Server2...")

    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(('localhost', 10000))  # Server2 is listening here
    sock2.sendall(struct.pack('>i', len(enc_payload)) + enc_payload)
    print("Server1: Sent encrypted x0 to Server2")

    result_len = struct.unpack('>i', sock2.recv(4))[0]
    result = sock2.recv(result_len)
    connection.sendall(result)
    print("Server1: Forwarded result to Client")

    connection.close()
    sock2.close()
    sock.close()

if __name__ == '__main__':
    main()
