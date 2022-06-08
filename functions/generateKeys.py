from email.mime import base
import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64


def generate_keys(): #generate the keys and saved in current folder named private_noshare and public_shared .pem

#############generate public and private keys###################

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()


    print("private key:",private_key)
    print("public key:",public_key)

    #############serializing and saving the keys################

    serial_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open('private_noshare.pem', 'wb') as f: f.write(serial_private)

    serial_pub = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open('public_shared.pem', 'wb') as f: f.write(serial_pub)

##############reading the saved keys#########################

def read_private (filename = "private_noshare.pem"): #to read the private key
    with open(filename, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

def read_public (filename = "public_shared.pem"): #to read the public key
    with open(filename, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key

###############encryption########################

def encryption(data, public_key):  # data has to be binary type
    encrypted = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return base64.b64encode(encrypted)  # encode in base 64

##############decryption#################################
def decryption(data, private_key): #data needs to be b64 encrypted
    return private_key.decrypt(
        base64.b64decode(data),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


#########EJEMPLO DE USO#################
""" 
cypher_text =  encryption(b'password',read_public())

print(cypher_text)
print(decryption(cypher_text,read_private())) """