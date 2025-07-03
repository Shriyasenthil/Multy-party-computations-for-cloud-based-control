# util.py
import os
from prg_utils import prg

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings"""
    return bytes(x ^ y for x, y in zip(a, b))

def ot_send(msg0: bytes, msg1: bytes, seed0: bytes, seed1: bytes) -> tuple[bytes, bytes]:
    """OT Sender: Mask msg0 and msg1 using PRG seeded with seed0 and seed1"""
    r0 = prg(seed0, len(msg0))
    r1 = prg(seed1, len(msg1))
    c0 = xor_bytes(msg0, r0)
    c1 = xor_bytes(msg1, r1)
    return c0, c1

def ot_receive(choice_bit: int, seed: bytes, c0: bytes, c1: bytes) -> bytes:
    """OT Receiver: Retrieve msg_b using the chosen bit and PRG(seed)"""
    r = prg(seed, len(c0))
    return xor_bytes(c0 if choice_bit == 0 else c1, r)

def generate_seed(seed_length: int = 16) -> bytes:
    """Generate secure random seed of given length (default 16 bytes)"""
    return os.urandom(seed_length)
