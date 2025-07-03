import hashlib

def prg(seed: bytes, length: int = 32) -> bytes:
    """
    Pseudorandom Generator (PRG) using SHA-256.
    
    Args:
        seed (bytes): The seed used as entropy input.
        length (int): The number of bytes to generate.
    
    Returns:
        bytes: A pseudorandom byte string of the specified length.
    """
    output = b''
    counter = 0
    while len(output) < length:
        counter_bytes = counter.to_bytes(4, 'big')
        output += hashlib.sha256(seed + counter_bytes).digest()
        counter += 1
    return output[:length]
