import random
import hashlib
from gmpy2 import mpz, powmod, invert, mpz_urandomb, random_state, next_prime, lcm

class PublicKey:
    def __init__(self, n):  # ✅ Fixed here
        self.n = n
        self.nsquare = n * n
        self.g = n + 1

class PrivateKey:
    def __init__(self, pub, p, q):  # ✅ Fixed here
        self.pub = pub
        self.p = p
        self.q = q
        self.n = pub.n
        self.nsquare = self.n * self.n
        self.lambda_param = lcm(p - 1, q - 1)
        self.mu = invert(self.L_function(powmod(pub.g, self.lambda_param, self.nsquare)), self.n)

    def L_function(self, x):
        return (x - 1) // self.n

def Init(keysize):
    rng = random_state(42)
    while True:
        p = next_prime(mpz_urandomb(rng, keysize // 2))
        q = next_prime(mpz_urandomb(rng, keysize // 2))
        if p != q:
            break
    n = p * q
    pub = PublicKey(n)
    priv = PrivateKey(pub, p, q)
    return priv, pub

def KeyGen(pub):
    return pub, pub  # Dummy keypair for compatibility

class Ciphertext:
    def __init__(self, label, ciphertext):  # ✅ Fixed here
        self.label = label
        self.ciphertext = ciphertext

    def to_json(self):
        return {'label': self.label, 'ciphertext': str(self.ciphertext)}

    @staticmethod
    def from_json(obj):
        return Ciphertext(obj['label'], mpz(obj['ciphertext']))

def hash_label(label):
    return int(hashlib.sha256(label.encode()).hexdigest(), 16)

def E(pub, upk, label, m):
    """ Encrypt integer m with label using LabHE """
    r = random.randint(1, pub.n - 1)
    L = hash_label(label)
    gm = powmod(pub.g, m, pub.nsquare)
    gL = powmod(pub.g, L, pub.nsquare)
    rn = powmod(r, pub.n, pub.nsquare)
    c = (gm * gL * rn) % pub.nsquare
    return Ciphertext(label, c)

def D(priv, ct):
    """ Decrypt ciphertext and remove label-based mask """
    L = hash_label(ct.label)
    u = powmod(ct.ciphertext, priv.lambda_param, priv.nsquare)
    l = priv.L_function(u)
    mL = (l * priv.mu) % priv.n
    m = mL - L
    return m % priv.n

def Eval_add(pub, ct1, ct2):
    assert ct1.label == ct2.label, "Labels must match for Eval_add"
    c = (ct1.ciphertext * ct2.ciphertext) % pub.nsquare
    return Ciphertext(ct1.label, c)

def Eval_mult_scalar(pub, ct, scalar):
    """ Homomorphic multiplication by plaintext scalar """
    c = powmod(ct.ciphertext, scalar, pub.nsquare)
    return Ciphertext(ct.label, c)
