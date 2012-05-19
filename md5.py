#!/usr/bin/python
import argparse, numpy as np
from bitstring import BitArray
from copy import copy
from math import floor, sin
parser = argparse.ArgumentParser(description='Calculate the MD5 hash of a HEX string')
parser.add_argument('hexstring')
args = parser.parse_args()

# will take an int and create a binary list, big endian
def int2bin(i, bitformat = None):
    bs = bin(i).lstrip('-0b')
    if bitformat is not None:
        bs = bs.zfill(bitformat)
    return map(int, bs)

def chunk(iterable, count):
    pos = 0
    end = len(iterable)
    while pos < end:
        yield iterable[pos:pos+count]
        pos+=count


def hex2bin(string, bitformat = None):
    try:
        return int2bin(int(string, 16), bitformat)
    except ValueError:
        return []

def hexle2hexbe(hexstring):
    ''' return the true hexstring represented by a loworder hex string'''
    return ''.join(hexstring.split(' ')[::-1])


#original_bitstring = hex2bin(args.hexstring)
original_bitstring = BitArray(bin(int(args.hexstring, 16)))
modifiable_bitstring = BitArray(bin(int(args.hexstring, 16)))

# Step 1. Append Padding Bits
# append single '1'
modifiable_bitstring.append(1)
# append number of 0s needed to make the length of the message congruent to 448
modifiable_bitstring.append([0]*((448 - (len(modifiable_bitstring) % 512)) % 512))

# should by 64 bits shy of being a multiple of 512
assert len(modifiable_bitstring)%512 == 448

# Step 2. Append Length
# length of original msg as little-endian 64-bit binary string
msglength64bit = BitArray(intle=len(original_bitstring), length=64)
modifiable_bitstring.append(msglength64bit)

# should be a multiple of 512 bits now
assert len(modifiable_bitstring)%512 == 0

# Step 3. Initialize MD Buffer
# each word is a 32-bit register
# intialised using hexadecimal, low-order bytes first
# Therefore: string...
A = BitArray(hex=hexle2hexbe('01 23 45 67'))
B = BitArray(hex=hexle2hexbe('89 ab cd ef'))
C = BitArray(hex=hexle2hexbe('fe dc ba 98'))
D = BitArray(hex=hexle2hexbe('76 54 32 10'))

# Step 4. Auxilliary functions brackets are for clarity
F = lambda X, Y, Z: (X & Y) | (~X & Z)
G = lambda X, Y, Z: (X & Z) | (Y & ~Z)
H = lambda X, Y, Z: X ^ Y ^ Z
I = lambda X, Y, Z: Y ^ (X | ~Z)

X = modifiable_bitstring
#    4294967296 == 2**32
T = [int(floor(4294967296 * abs(sin(i)))) for i in range(0, 65)]

AA = copy(A)
BB = copy(B)
CC = copy(C)
DD = copy(D)

def op(a, b, c, d, k, s, i, f):
    # a +F(b,c,d) + X[k] + T[i]
    inner_sum = (a.int + F(b,c,d).int + X[k] + T[i]) % 2^32
    inner_array = BitArray(uint=inner_sum, length=32)
    # <<< s
    inner_array.rol(s)
    # + b
    result = (b.int + inner_array.int)% 2^32
    # assign the result into A
    return BitArray(uint=result, length=32)

# round 1
A = op(A,B,C,D, k=0, s=7 , i=1, f=F)
D = op(D,A,B,C, k=1, s=12, i=2, f=F)
C = op(C,D,A,B, k=2, s=17, i=3, f=F)
B = op(B,C,D,A, k=3, s=22, i=4, f=F)

A = op(A,B,C,D, k=4, s=7 , i=5, f=F)
D = op(D,A,B,C, k=5, s=12, i=6, f=F)
C = op(C,D,A,B, k=6, s=17, i=7, f=F)
B = op(B,C,D,A, k=7, s=22, i=8, f=F)

A = op(A,B,C,D, k=8 , s=7 , i=9, f=F)
D = op(D,A,B,C, k=9 , s=12, i=10, f=F)
C = op(C,D,A,B, k=10, s=17, i=11, f=F)
B = op(B,C,D,A, k=11, s=22, i=12, f=F)

A = op(A,B,C,D, k=12, s=7 , i=13, f=F)
D = op(D,A,B,C, k=13, s=12, i=14, f=F)
C = op(C,D,A,B, k=14, s=17, i=15, f=F)
B = op(B,C,D,A, k=15, s=22, i=16, f=F)

# round 2
A = op(A,B,C,D, k=1 , s=5 , i=17, f=G)
D = op(D,A,B,C, k=6 , s=9 , i=18, f=G)
C = op(C,D,A,B, k=11, s=14, i=19, f=G)
B = op(B,C,D,A, k=0 , s=20, i=20, f=G)

A = op(A,B,C,D, k=5 , s=5 , i=21, f=G)
D = op(D,A,B,C, k=10, s=9 , i=22, f=G)
C = op(C,D,A,B, k=15, s=14, i=23, f=G)
B = op(B,C,D,A, k=4 , s=20, i=24, f=G)

A = op(A,B,C,D, k=9 , s=5 , i=25, f=G)
D = op(D,A,B,C, k=14, s=9 , i=26, f=G)
C = op(C,D,A,B, k=3 , s=14, i=27, f=G)
B = op(B,C,D,A, k=8 , s=20, i=28, f=G)

A = op(A,B,C,D, k=13, s=5 , i=29, f=G)
D = op(D,A,B,C, k=2 , s=9 , i=30, f=G)
C = op(C,D,A,B, k=7 , s=14, i=31, f=G)
B = op(B,C,D,A, k=12, s=20, i=32, f=G)

# round 3
A = op(A,B,C,D, k=5 , s=4 , i=33, f=H)
D = op(D,A,B,C, k=8 , s=11, i=34, f=H)
C = op(C,D,A,B, k=11, s=16, i=35, f=H)
B = op(B,C,D,A, k=14, s=23, i=36, f=H)

A = op(A,B,C,D, k=1 , s=4 , i=37, f=H)
D = op(D,A,B,C, k=4 , s=11, i=38, f=H)
C = op(C,D,A,B, k=7 , s=16, i=39, f=H)
B = op(B,C,D,A, k=10, s=23, i=40, f=H)

A = op(A,B,C,D, k=13, s=4 , i=41, f=H)
D = op(D,A,B,C, k=0 , s=11, i=42, f=H)
C = op(C,D,A,B, k=3 , s=16, i=43, f=H)
B = op(B,C,D,A, k=6 , s=23, i=44, f=H)

A = op(A,B,C,D, k=9 , s=4 , i=45, f=H)
D = op(D,A,B,C, k=12, s=11, i=46, f=H)
C = op(C,D,A,B, k=15, s=16, i=47, f=H)
B = op(B,C,D,A, k=2 , s=23, i=48, f=H)

# round 4
A = op(A,B,C,D, k=0 , s=5 , i=49, f=I)
D = op(D,A,B,C, k=7 , s=9 , i=50, f=I)
C = op(C,D,A,B, k=14, s=14, i=51, f=I)
B = op(B,C,D,A, k=5 , s=20, i=52, f=I)

A = op(A,B,C,D, k=12, s=5 , i=53, f=I)
D = op(D,A,B,C, k=3 , s=9 , i=54, f=I)
C = op(C,D,A,B, k=10, s=14, i=55, f=I)
B = op(B,C,D,A, k=1 , s=20, i=56, f=I)

A = op(A,B,C,D, k=8 , s=5 , i=57, f=I)
D = op(D,A,B,C, k=15, s=9 , i=58, f=I)
C = op(C,D,A,B, k=6 , s=14, i=59, f=I)
B = op(B,C,D,A, k=13, s=20, i=60, f=I)

A = op(A,B,C,D, k=4 , s=5 , i=61, f=I)
D = op(D,A,B,C, k=11, s=9 , i=62, f=I)
C = op(C,D,A,B, k=2 , s=14, i=63, f=I)
B = op(B,C,D,A, k=9 , s=20, i=64, f=I)

A = A + AA
B = B + BB
C = C + CC
D = D + DD
print "{} {} {} {}".format(A,B,C,D)
