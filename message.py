"""
 0 - public key 
"""

import json
from struct import pack, unpack
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric import rsa
from abc import abstractmethod, ABC

from config import DEVICE_ID, DEVICE_NAME

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
        convert serialize public key to hex then bytes and pack the message 
        message: length, id, key
        """
        key_bytes = public_key.hex().encode()
        return pack(f"!IB{len(key_bytes)}s", len(key_bytes) + 5, cls.id, key_bytes)

    @classmethod
    def unpack_message(cls, data):
        """
        returns serialized public key 
        """
        length = unpack("!I", data[:4])[0]
        key_hex = unpack(f"{length - 5}s", data[5: length])[0].decode()
        return bytes.fromhex(key_hex) 


class DeviceInfoMessage(Message):
    id: int = 1

    @classmethod
    def pack_message(cls):
        """
        return packed device info message
        """
        return pack(f"!B32s{len(DEVICE_NAME)}s", cls.id, DEVICE_ID, DEVICE_NAME.encode())

    @classmethod 
    def unpack_message(cls, data):
        """
        return device id, name
        """
        length = len(data)
        device_id, device_name = unpack(f"!32s{length - 33}s", data[1:])
        return device_id, device_name.decode() 


class PairRequest(Message): 
    id: int = 2

    @classmethod
    def pack_message(cls):
        return pack("!B", cls.id)
    

class PairResponse(Message):
    id: int = 3

    @classmethod
    def pack_message(cls, response):
        if (response): 
            response = 1
        else: 
            response = 0
        return pack("!BI", cls.id, response)
    
    @classmethod
    def unpack_message(cls, message):
        response = unpack("!I", message[1:])
        if response: return True
        return False
    
class PairCancel(Message):
    id: int = 4

    @classmethod 
    def pack_message(cls):
        return pack("!B", cls.id)
# class EncryptedMessage():
#     @classmethod 
#     def pack_message(message):
#         return pack(f"!I{len(message)}s", len(message), message)
    
#     @classmethod
#     def unpack_message(message):
#         pass 
        

MESSAGE_TYPE = {
    0 : PublicKeyMessage, 
    1 : DeviceInfoMessage,
    2 : PairRequest, 
    3 : PairResponse, 
    4 : PairCancel,
    # 5 : Connected
}


