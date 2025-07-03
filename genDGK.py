# genDGK.py
from gmpy2 import mpz, mpz_urandomb, random_state, next_prime, powmod

DEFAULT_KEYSIZE = 512
DEFAULT_MSGSIZE = 20
DEFAULT_SECURITYSIZE = 160

rand = random_state()


def getprimeover(bits):
    candidate = mpz_urandomb(rand, bits)
    return next_prime(candidate)


def keysDGK(n_length=DEFAULT_KEYSIZE, u_length=DEFAULT_MSGSIZE, t=DEFAULT_SECURITYSIZE):
    """
    Generate DGK keys.
    Returns: p, q, u, vp, vq, fp, fq, g, h
    """
    u = getprimeover(u_length)      # small plaintext space prime
    vp = getprimeover(t)            # prime such that g^vp ≡ 1 mod p
    vq = getprimeover(t)
    fp = getprimeover(t)
    fq = getprimeover(t)

    while True:
        p = u * vp * fp + 1
        if p % u == 1 and p % vp == 1 and p % fp == 1 and p.bit_length() >= n_length // 2:
            break

    while True:
        q = u * vq * fq + 1
        if q % u == 1 and q % vq == 1 and q % fq == 1 and q.bit_length() >= n_length // 2:
            break

    n = p * q

    # Generator g ∈ Z*_n with order u
    while True:
        g = getprimeover(n_length)
        if powmod(g, u, p) != 1 and powmod(g, u, q) != 1:
            break

    # Generator h ∈ Z*_n with order vp
    while True:
        h = getprimeover(n_length)
        if powmod(h, vp, p) != 1 and powmod(h, vq, q) != 1:
            break

    return mpz(p), mpz(q), mpz(u), mpz(vp), mpz(vq), mpz(fp), mpz(fq), mpz(g), mpz(h)
