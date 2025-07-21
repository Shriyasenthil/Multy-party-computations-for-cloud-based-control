
# Utility functions 
import random
import math

def invert(a, b):
    #Compute modular inverse 
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % b, b)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % b + b) % b

def powmod(base, exp, mod):
    #Compute (base^exp) % mod 
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result

def getprimeover(n):
    #Generate a prime number with bit length > n
    def is_prime(num):
        if num < 2:
            return False
        if num == 2:
            return True
        if num % 2 == 0:
            return False
        
        # Miller-Rabin primality test
        r = 0
        d = num - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        # Witness loop
        for _ in range(5):  
            a = random.randrange(2, num - 1)
            x = powmod(a, d, num)
            if x == 1 or x == num - 1:
                continue
            
            for _ in range(r - 1):
                x = powmod(x, 2, num)
                if x == num - 1:
                    break
            else:
                return False
        return True
    
    # Generate random odd number with desired bit length
    while True:
        candidate = random.getrandbits(n)
        candidate |= (1 << (n - 1))  # Set the highest bit
        candidate |= 1  # Make it odd
        
        if is_prime(candidate):
            return candidate

def isqrt(n):
    #Integer square root
    if n < 0:
        raise ValueError("Cannot compute square root of negative number")
    if n == 0:
        return 0
    
    # Newton's method for integer square root
    x = n
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y