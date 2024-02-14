import socket 
import logging
from struct import unpack, pack
from cryptography.hazmat.primitives.asymmetric import rsa

from keys import Keys
from message import MESSAGE_TYPE
from message import PublicKeyMessage
from message import DeviceInfoMessage
from config import DEVICE_ID


class PeerDevice: 
    def __init__(
            self, 
            ip, 
            key_pair: Keys, 
            peer_socket = None, 
            paired = False
            ):
        self.ip = ip
        self._handshake_done = False
        self.paired = paired 
        self.key_pair = key_pair
        self.peer_socket = peer_socket
        self._peer_public_key: rsa.RSAPublicKey | None = None
        self._buffer = b''
        self._key_sent = False
        self._info_sent = False
    
    def handle_peer_messages(self, peer_socket: socket.socket):
        """
        handle peer responses
        """
        data = peer_socket.recv(4096) 
        self._buffer += data

        if self._buffer: 
            logging.debug(f"client: {peer_socket.getsockname()}: buffer - {self._buffer}")

            # if the buffer length is smaller than message length it returns
            length = self._get_message_length()
            if (length > len(self._buffer)):
                return

            # if peer public key hasn't received, doesn't use decryption
            if not self._key_sent or self._peer_public_key == None:
                id = self._get_message_id(self._buffer[4:])
                if id == 0:
                    self._handle_public_key_message(self._buffer)
            else:
                # handle messages with encryption
                print(length)
                print(len(self._buffer))
                print(len(self._buffer[4:length]))
                encrypted_message = unpack(f"!{length - 4}s", self._buffer[4:length])[0]
                message = self._get_decrypted_message(encrypted_message)
                id = self._get_message_id(message)
                if (id == 1):
                    self._handle_info_message(length - 4, message)

            self._update_buffer(length)
                    
    def _handle_info_message(self, length, message):
        """
        return device id and name
        """
        print(length)
        print(message)
        device_id, device_name = DeviceInfoMessage.unpack_message(length, message)
        logging.debug(f"peerDevice: {device_id}: {device_name}")
        self.device_id = device_id
        self.device_name = device_name 

        if not self._info_sent: 
            self._send_device_info()

        #TODO: check if device info is received to the peer 
        self._handshake_done = True

    def _get_packed_ciphertext(self, message):
        """
        encrypt message with peer public key and pack it with length of the message
        """
        encrypted_messsage = Keys.get_ciphertext(message, self._peer_public_key)
        return pack(f"!I{len(encrypted_messsage)}s", len(encrypted_messsage) + 4, encrypted_messsage) 

    def _get_decrypted_message(self, ciphertext):
        """
        return decrypted cipher message
        """
        return self.key_pair.decrypt_ciphertext(ciphertext)

    def _update_buffer(self, length):
        """
        remove length number of bytes from the buffer
        """
        self._buffer = self._buffer[length:]

    def _get_message_id(self, data):
        """
        return message length, id
        """
        # print(data[0])
        # return unpack("!B", data[0])[0]
        return data[0]

    def _get_message_length(self):
        """
        return message length
        """ 
        return unpack("!I", self._buffer[:4])[0]

    def _handle_public_key_message(self, message):
        """
        handle peer public key 
        """
        self._peer_public_key = Keys.deserialize_public_key(PublicKeyMessage.unpack_message(message)) 
        logging.debug(f"peer:{self.ip}: got public key")
        if not self._key_sent: 
            self.send_key()
        else:
            self._send_device_info()

    def _send_device_info(self):
        """
        send device info to the peer 
        """
        device_info_message = DeviceInfoMessage().pack_message()
        message = self._get_packed_ciphertext(device_info_message)
        self._send_message(message)
        self._info_sent = True

    def _send_message(self, data):
        """
        send messages to peer
        """
        self.peer_socket.sendall(data)

    def send_key(self):
        """
        send device public key 
        """
        logging.debug(f"peer:{self.ip}: sending public key")
        self._send_message(PublicKeyMessage.pack_message(self.key_pair.serialize_public_key()))
        self._key_sent = True
        