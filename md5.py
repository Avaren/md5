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
T = [int(floor(4294967296 * abs(sin(i)))) for i in range(1, 65)]

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
A = op(A,B,C,D, k=0, s=7, i=1, f=F)
D = op(D,A,B,C, k=0, s=7, i=1, f=F)
C = op(C,D,A,B, k=0, s=7, i=1, f=F)
B = op(B,C,D,A, k=0, s=7, i=1, f=F)

A = op(A,B,C,D, k=0, s=7, i=1, f=F)
D = op(D,A,B,C, k=0, s=7, i=1, f=F)
C = op(C,D,A,B, k=0, s=7, i=1, f=F)
B = op(B,C,D,A, k=0, s=7, i=1, f=F)

A = op(A,B,C,D, k=0, s=7, i=1, f=F)

D = op(D,A,B,C, k=0, s=7, i=1, f=F)
C = op(C,D,A,B, k=0, s=7, i=1, f=F)
B = op(B,C,D,A, k=0, s=7, i=1, f=F)
A = op(A,B,C,D, k=0, s=7, i=1, f=F)
D = op(D,A,B,C, k=0, s=7, i=1, f=F)
C = op(C,D,A,B, k=0, s=7, i=1, f=F)
B = op(B,C,D,A, k=0, s=7, i=1, f=F)
