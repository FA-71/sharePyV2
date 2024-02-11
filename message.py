"""
 0 - public key 
"""

import json
from struct import pack, unpack
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric import rsa
from abc import abstractmethod, ABC




class BroadcastMessage: 
    identifier = "SharePyV2"

    @classmethod
    def pack_message(cls):
        return pack(f"!{len(cls.identifier)}s", cls.identifier.encode()) 
    
    @classmethod
    def check_message(cls, message): 
        return unpack(f"!{len(cls.identifier)}s", message)[0].decode() == cls.identifier 


class Message(ABC):
    @abstractmethod
    def pack_message(self):
        pass

    @abstractmethod
    def unpack_message(self):
        pass


class PublicKeyMessage(Message):
    id: int = 0

    @classmethod
    def pack_message(cls, public_key: bytes):
        """
        convert public key to hex and make json 
        """
        key_hex = public_key.hex()
        return json.dumps({"id": cls.id, "public_key": key_hex}).encode('utf-8')

    @classmethod
    def unpack_message(cls, data):
        """
        returns serialized public key 
        """
        return bytes.fromhex(data.get("public_key"))


MESSAGE_TYPE = {
    0 : PublicKeyMessage 
}
