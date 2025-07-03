import hashlib
import secrets
import json
import struct
from gmpy2 import mpz

def serialize_ciphertext(ct):
    """Convert a labhe.Ciphertext object to a serializable dict."""
    return json.dumps({
        'label': ct.label,
        'ciphertext': str(ct.ciphertext)
    })

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def ot_sender(sock, m0, m1):
    """
    Simulated OT Sender: Sends two LabHE ciphertexts, and only one is revealed
    to receiver based on their choice bit (but sender doesn't learn the choice).
    """
    # Serialize the ciphertexts
    ct0 = serialize_ciphertext(m0).encode()
    ct1 = serialize_ciphertext(m1).encode()

    # Package both as a list and send
    payload = json.dumps([ct0.decode(), ct1.decode()])
    sock.sendall(struct.pack('>i', len(payload)) + payload.encode('utf-8'))

    print("[OT Sender] Sent OT message pair to receiver.")
