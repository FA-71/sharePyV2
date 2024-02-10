from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import datetime
import logging

from config import DEVICE_NAME


# class Keys: 
#     script_dir_path = Path(__file__).resolve().parent 
#     key_file = Path(script_dir_path) / "device.key" 
#     cert_file = Path(script_dir_path) / "device.cert"

#     @classmethod
#     def check_keys(cls):
#         """
#         check if key files exists and if not make them
#         """
#         logging.debug("keys: checking keys")
#         if cls.key_file.exists() and cls.cert_file.exists(): 
#             logging.debug("keys: files exists")
#             return

#         logging.debug("keys: making key files")
#         private_key = Keys._make_key() 
#         Keys._make_cert(private_key)
    
#     @classmethod
#     def _make_key(cls):
#         private_key = rsa.generate_private_key(
#             public_exponent=65537,
#             key_size=2048,
#             backend=default_backend()
#         )

#         with open(cls.key_file.resolve(), "wb") as file: 
#             file.write(private_key.private_bytes(
#                 encoding=serialization.Encoding.PEM,
#                 format=serialization.PrivateFormat.TraditionalOpenSSL,
#                 encryption_algorithm=serialization.NoEncryption()
#             ))
        
#         return private_key
    
#     @classmethod
#     def _make_cert(cls, private_key):
#         subject = issuer = x509.Name([
#             x509.NameAttribute(NameOID.COMMON_NAME, f"{DEVICE_NAME}")
#         ])

#         cert = x509.CertificateBuilder().subject_name(
#             subject
#         ).issuer_name(
#             issuer
#         ).public_key(
#             private_key.public_key()
#         ).serial_number(
#             x509.random_serial_number()
#         ).not_valid_before(
#             datetime.datetime.utcnow()
#         ).not_valid_after(
#             datetime.datetime.utcnow() + datetime.timedelta(days=365)
#         ).sign(private_key, hashes.SHA256(), default_backend())

#         with open(cls.cert_file.resolve(), "wb") as file: 
#             file.write(cert.public_bytes(serialization.Encoding.PEM))


class Keys:
    def __init__(self):
        self.private_key, self.public_key = self._generate_key_pair()

    def _generate_key_pair(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return  private_key, public_key

    def serialize_public_key(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def deserialize_public_key(self, public_key_bytes):
        return serialization.load_der_public_key(public_key_bytes, backend=default_backend())
