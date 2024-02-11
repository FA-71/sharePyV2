import socket 
import logging
import json

from keys import Keys
from message import MESSAGE_TYPE
from message import PublicKeyMessage


class PeerDevice: 
    def __init__(
            self, 
            ip, 
            key_pair: Keys, 
            peer_socket: socket.socket | None = None, 
            paired = False
            ):
        self.ip = ip
        self._key_shared = False
        self.paired = paired 
        self.key_pair = key_pair
        self.peer_socket = peer_socket
        self._derived_key: bytes | None = None
    
    def handle_peer_messages(self, peer_socket: socket.socket):
        """
        handle peer responses
        """
        data = peer_socket.recv(4096) 
        if data: 
            logging.debug(f"client: {peer_socket.getsockname()}: data - {data}")
            message = json.loads(data).decode()
            id = message["id"] 
            if id == 0:
                self._handle_public_key_message(message)
            #TODO: send public key 
            #TODO: make a shared key 
            #TODO: store shared key in peerDevice
        
    def _handle_public_key_message(self, message):
        peer_public_key = Keys.deserialize_public_key(PublicKeyMessage.unpack_message(message))    
        if not self._key_shared: self.send_key()
        shared_key = self.key_pair.private_key.exchange(peer_public_key) 
        self._derived_key = Keys.get_derived_key(shared_key)
        print("dervied key", self._derived_key)

    def _send_message(self, message):
        self.peer_socket.sendall(message)

    def send_key(self):
        self._send_message(PublicKeyMessage.pack_message(self.key_pair.serialize_public_key()))
        self._key_shared = True
        