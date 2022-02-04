import secrets, hashlib, codecs
from pprint import pprint
from Crypto.Hash import keccak



'''
chars = []
#print(secrets.token_hex(32))
numkeys = 20
print(f"Generating {numkeys} random keys...")
for i in range(numkeys):
    #chars.append(secrets.token_hex(32))
    chars.append(hex(secrets.randbits(256)))
pprint(chars)
del chars[:]
'''
# priv key -> pub key -> address
# Example of generated values
#0x56f08e6b45C00bb4dB2DBd50565C30EF0Fd22baA
#f3fed54f057483e3d829c9da483315f2484569e472b763595fc2ecf7fea6d739


'''
ECDSA = Elliptic Curve Digital Signature Algorithm
The order of secp256k1 is FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Secp256k1 is the name of the elliptic curve we are using 
y² = x³ + ax + b
a=0, b=7, ==> y^2=x^3+7

Because the y component of the equation is squared, secp256k1 is symmetric across the x-axis, 
and for each value of x, there are two values of y, one of which is odd while the other is even. 
This allows public keys to be identified simply by the x-coordinate and the parity of the y-coordinate, 
saving significant data usage on the blockchain.


An ECDSA key pair is needed for Bitcoin address generation. Both the public and private ECDSA key are a 
256-bit integer and you keep the private key in a secret place first. Then you take out the public key and 
perform the first round of SHA256 + RIPEMD160 hash on it. Prepend 0x00 to the bits assuming you are 
working with BTC main network. Two more rounds of SHA256 on the bit sequence. Take the first 4 bytes 
from output and append them onto the previous RIPEMD160 output. Encode the final sequence into a base58 
string, which is your Bitcoin address to receive payments from others.

# encrypted public key = ripemd160(sha256(public key))



'''
