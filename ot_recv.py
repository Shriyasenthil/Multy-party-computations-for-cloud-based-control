import hashlib
import json
import secrets
import struct
from gmpy2 import mpz
from labhe import Ciphertext, D
from prg_utils import prg  # Ensure this is available

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def ot_receiver(sock, privkey, choice_bit):
    """
    Oblivious Transfer Receiver
    Receives only one of the two LabHE-encrypted messages (based on choice_bit)
    without revealing the choice to the sender.

    Parameters:
        sock        -- Connected socket to sender
        privkey     -- LabHE private key for decryption
        choice_bit  -- 0 or 1 (which ciphertext to receive)

    Returns:
        Decrypted integer message
    """

    # Step 1: Receive both messages (masked ciphertexts)
    msg_len = struct.unpack('>i', sock.recv(4))[0]
    payload = sock.recv(msg_len)
    messages = json.loads(payload.decode())

    msg0 = json.loads(messages[0])  # serialized ciphertext (label + ciphertext string)
    msg1 = json.loads(messages[1])

    ct0 = Ciphertext(msg0['label'], mpz(msg0['ciphertext']))
    ct1 = Ciphertext(msg1['label'], mpz(msg1['ciphertext']))

    # Step 2: Choose one based on choice_bit
    selected_ct = ct1 if choice_bit else ct0

    # Step 3: Decrypt and return the chosen message
    decrypted = D(privkey, selected_ct)
    return decrypted
