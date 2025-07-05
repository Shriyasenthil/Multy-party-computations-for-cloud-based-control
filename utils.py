import os
import labhe
from prg_utils import prg
from gmpy2 import mpz
import numpy as np

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def ot_send(msg0: bytes, msg1: bytes, seed0: bytes, seed1: bytes) -> tuple[bytes, bytes]:
    r0 = prg(seed0, len(msg0))
    r1 = prg(seed1, len(msg1))
    c0 = xor_bytes(msg0, r0)
    c1 = xor_bytes(msg1, r1)
    return c0, c1

def ot_receive(choice_bit: int, seed: bytes, c0: bytes, c1: bytes) -> bytes:
    r = prg(seed, len(c0))
    return xor_bytes(c0 if choice_bit == 0 else c1, r)

def generate_seed(seed_length: int = 16) -> bytes:
    return os.urandom(seed_length)


# LabHE
def encrypt_vector(vector, pubkey, label='default'):
    return [labhe.E(pubkey, pubkey, label, int(round(x))) for x in vector]


from gmpy2 import mpz

def decrypt_vector(enc_vec, privkey):
    plain = []
    for enc in enc_vec:
        if isinstance(enc, dict):
            cipher_obj = labhe.Ciphertext.from_json(enc)
        elif hasattr(enc, 'ciphertext'):
            cipher_obj = enc
        else:
            raise TypeError("Unknown ciphertext format in decrypt_vector()")
        plain.append(labhe.D(privkey, cipher_obj))
    return plain


def truncate(vec, lf):
    return [round(v, lf) for v in vec]

def project_on_Ubar(tk, Ubar):
    projected = []
    for i, v in enumerate(tk):
        li, lf = Ubar[i]
        projected.append(max(min(v, lf), li))
    return projected

def zero_vector(length, pubkey):
    try:
        zero_vec = []
        for i in range(length):
            zero_plaintext = labhe.Encode(0.0, pubkey)
            zero_ct = labhe.Encrypt(zero_plaintext, pubkey)
            zero_vec.append(zero_ct)
        return zero_vec
    except Exception as e:
        print(f"Error creating zero vector: {e}")
        raise

def he_add(vec1, vec2, pubkey):
    return [labhe.Eval_add(pubkey, c1, c2) for c1, c2 in zip(vec1, vec2)]


def he_scalar_mul(scalar, ciphertext, pubkey):
    """Multiply ciphertext(s) by a scalar value."""
    try:
        if isinstance(scalar, (int, float)):
            scalar = int(round(scalar))  

        if isinstance(ciphertext, list):
            return [labhe.Eval_mult_scalar(pubkey, ct, scalar) for ct in ciphertext]
        else:
            return labhe.Eval_mult_scalar(pubkey, ciphertext, scalar)

    except Exception as e:
        print(f"Error in he_scalar_mul: {e}")
        print(f"  scalar: {scalar}, ciphertext type: {type(ciphertext)}")
        raise


def he_matvec_mul(mat, enc_vector, pubkey):
    result = []
    for i, row in enumerate(mat):
        acc = None
        for j, scalar in enumerate(row):
            if scalar == 0:
                continue
            prod = labhe.Eval_mult(pubkey, scalar, enc_vector[j])
            prod.label = f"row_{i}"
            if acc is None:
                acc = prod
            else:
                acc = labhe.Eval_add(pubkey, acc, prod)
        if acc is None:
            acc = labhe.Eval_mult(pubkey, 0, enc_vector[0])
            acc.label = f"row_{i}"
        result.append(acc)
    return result

def he_vec_add(enc_vec1, enc_vec2):
    try:
        if len(enc_vec1) != len(enc_vec2):
            raise ValueError(f"Vector lengths don't match: {len(enc_vec1)} vs {len(enc_vec2)}")
        result = []
        for i in range(len(enc_vec1)):
            sum_ct = labhe.Eval_add(enc_vec1[i], enc_vec2[i])
            result.append(sum_ct)
        return result
    except Exception as e:
        print(f"Error in he_vec_add: {e}")
        raise

def load_matrix_from_file(filename):
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        matrix = []
        for line in lines:
            line = line.strip()
            if line:
                row = [float(x) for x in line.split(',')]
                matrix.append(row)
        return np.array(matrix)
    except Exception as e:
        print(f"Error loading matrix from {filename}: {e}")
        raise
