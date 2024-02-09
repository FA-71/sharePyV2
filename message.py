"""
"""


from struct import pack, unpack

class BroadcastMessage: 
    identifier = "SharePyV2"

    @classmethod
    def pack_message(cls):
        return pack(f"!{len(cls.identifier)}s", cls.identifier.encode()) 
    
    @classmethod
    def check_message(cls, message): 
        return unpack(f"!{len(cls.identifier)}s", message) == cls.identifier 


