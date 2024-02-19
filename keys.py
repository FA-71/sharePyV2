from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet 

from config import DEVICE_NAME


class RsaKeys:
    def __init__(self):
        self.private_key, self.public_key = self._generate_key_pair()

    def _generate_key_pair(self):
        """
        generate public and private key pair
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048, 
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return  private_key, public_key

    def serialize_public_key(self):
        """
        serialize public key to send 
        """
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @staticmethod
    def deserialize_public_key(public_key_bytes):
        """
        deserialize public key
        """
        return serialization.load_pem_public_key(public_key_bytes, backend=default_backend())

    @staticmethod
    def get_ciphertext(message, public_key: rsa.RSAPublicKey):
        """
        use peer public key to encrypt message
        """
        return public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def decrypt_ciphertext(self, ciphertext: bytes):
        """
        use own private key to decrypt message
        """
        return self.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )  


class AseKey:
    def __init__(self, key = Fernet.generate_key()):
        self.key = key 
        self.cipher_suit = Fernet(self.key)

    def encrypt_data(self, data):
        """
        return encrypted data using ase key 
        """
        return self.cipher_suit.encrypt(data)

    def decrypt_data(self, data):
        """
        return decrypted bytes
        """
        return self.cipher_suit.decrypt(data)
