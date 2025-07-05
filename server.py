import socket
import struct
import json
import numpy as np
from gmpy2 import mpz
import labhe
from utils import he_add, he_scalar_mul, he_matvec_mul, zero_vector, encrypt_vector


def send_data(sock, data):
    payload = json.dumps(data)
    sock.sendall(struct.pack('>i', len(payload)) + payload.encode('utf-8'))


def recv_data(sock):
    size_data = sock.recv(4)
    if not size_data:
        raise ConnectionError("Received empty header (connection closed).")
    size = struct.unpack('>i', size_data)[0]
    data = b''
    while len(data) < size:
        to_read = size - len(data)
        chunk = sock.recv(4096 if to_read > 4096 else to_read)
        if not chunk:
            raise ConnectionError("Incomplete message received.")
        data += chunk
    return json.loads(data.decode())


class FGDServer:
    def __init__(self, H_bar_f, F_bar_f, eta_bar, cold_start, Uw, m, pubkey, K):
        self.H_bar_f = H_bar_f
        self.F_bar_f = F_bar_f
        self.eta_bar = eta_bar
        self.cold_start = cold_start
        self.Uw = Uw
        self.m = m
        self.pubkey = pubkey
        self.K = K
        self.enc_Uk = None
        self.enc_xt = None

    def receive_encrypted_xt(self, enc_xt_strs):
        self.enc_xt = [
            labhe.Ciphertext.from_json({'label': 'xt', 'ciphertext': c})
            for c in enc_xt_strs
        ]
        print(f"Server: Received enc_xt with length {len(self.enc_xt)}")
        self.init_U0()

    def init_U0(self):
        N = self.H_bar_f.shape[0]
        print(f"Server: Initializing U0 with N={N}")
        if self.cold_start:
            self.enc_Uk = zero_vector(N, self.pubkey)
        else:
            tail = self.Uw[self.m:]
            self.enc_Uk = encrypt_vector(tail + [0] * self.m, self.pubkey, label='xt')
        self.enc_zk = self.enc_Uk
        print(f"Server: enc_Uk length: {len(self.enc_Uk)}")
        print(f"Server: enc_zk length: {len(self.enc_zk)}")

    def compute_tk(self):
        I_minus_H = np.eye(self.H_bar_f.shape[0]) - self.H_bar_f
        minus_F = -self.F_bar_f

        print(f"Server: Matrix shapes - I_minus_H: {I_minus_H.shape}, minus_F: {minus_F.shape}")
        print(f"Server: Vector lengths - enc_zk: {len(self.enc_zk)}, enc_xt: {len(self.enc_xt)}")

        try:
            enc_t1 = he_matvec_mul(I_minus_H, self.enc_zk, self.pubkey)
            print(f"Server: enc_t1 computed, length: {len(enc_t1)}")

            enc_t2 = he_matvec_mul(minus_F, self.enc_xt, self.pubkey)
            print(f"Server: enc_t2 computed, length: {len(enc_t2)}")

            if len(enc_t1) != len(enc_t2):
                raise ValueError(f"Vector length mismatch: enc_t1={len(enc_t1)}, enc_t2={len(enc_t2)}")
            if len(enc_t1) == 0 or len(enc_t2) == 0:
                raise ValueError(f"Empty vectors: enc_t1={len(enc_t1)}, enc_t2={len(enc_t2)}")

            tk = he_add(enc_t1, enc_t2, self.pubkey)

            print(f"Server: tk computed successfully, length: {len(tk)}")
            return tk

        except Exception as e:
            print(f"Server: Error in compute_tk: {e}")
            print(f"Server: enc_zk type: {type(self.enc_zk)}")
            print(f"Server: enc_xt type: {type(self.enc_xt)}")
            if hasattr(self, 'enc_zk') and self.enc_zk:
                print(f"Server: enc_zk[0] type: {type(self.enc_zk[0])}")
            if hasattr(self, 'enc_xt') and self.enc_xt:
                print(f"Server: enc_xt[0] type: {type(self.enc_xt[0])}")
            raise

    def update_uk_and_zk(self, enc_Uk_plus1_strs):
        enc_Uk_plus1 = [
            labhe.Ciphertext.from_json({'label': 'xt', 'ciphertext': c})
            for c in enc_Uk_plus1_strs
        ]

        for i in range(len(enc_Uk_plus1)):
            enc_Uk_plus1[i].label = self.enc_Uk[i].label

        enc_zk_new = he_add(
            he_scalar_mul(1 + self.eta_bar, enc_Uk_plus1, self.pubkey),
            he_scalar_mul(-self.eta_bar, self.enc_Uk, self.pubkey),
            self.pubkey
        )

        self.enc_Uk = enc_Uk_plus1
        self.enc_zk = enc_zk_new

    def get_final_UK(self):
        return [c.to_json() for c in self.enc_Uk]


def main():
    print("Server: Initializing LabHE...")
    privkey, pubkey = labhe.Init(512)
    upk, _ = labhe.KeyGen(pubkey)

    n, m, N = 5, 5, 35
    cold_start = True
    Uw = [0] * N
    eta_bar = 0.1
    K = 3

    H = np.loadtxt(f"Data/H{n}_{m}_{N}.txt", delimiter=',')
    F_full = np.loadtxt(f"Data/F{n}_{m}_{N}.txt", delimiter=',')
    F = np.zeros((N, N))
    F[:m, :] = F_full

    print(f"Server: Loaded matrices H: {H.shape}, F: {F.shape}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('localhost', 10001)
    server_socket.bind(server_address)
    server_socket.listen(1)
    print("Server: Listening on port 10001...")
    conn, client_address = server_socket.accept()
    print("Server: Connected to", client_address)

    server = FGDServer(H, F, eta_bar, cold_start, Uw, m, pubkey, K)

    try:
        msg = recv_data(conn)
        if msg['type'] == 'xt':
            print("Server: Received [[x(t)]]")
            server.receive_encrypted_xt(msg['data'])

        for k in range(K):
            print(f"Server: Sending [[tk]] for iteration {k}")
            tk = server.compute_tk()
            send_data(conn, {'type': 'tk', 'data': [c.to_json() for c in tk]})

            msg = recv_data(conn)
            if msg['type'] == 'Uk+1':
                print(f"Server: Received [[Uk+1]] at iteration {k}")
                server.update_uk_and_zk(msg['data'])

        print("Server: Sending final [[UK]] to client.")
        final_UK = server.get_final_UK()
        send_data(conn, {'type': 'final', 'data': final_UK})

    except Exception as e:
        print(f"Server: Error occurred - {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Server: Closing connection.")
        conn.close()
        server_socket.close()


if __name__ == '__main__':
    main()
