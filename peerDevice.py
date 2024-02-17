import socket 
import logging
from struct import unpack, pack
from cryptography.hazmat.primitives.asymmetric import rsa

from keys import Keys
from message import MESSAGE_TYPE
from config import DEVICE_ID
from message import DeviceInfoMessage
from message import PublicKeyMessage
from message import PairRequest
from message import PairResponse


class PeerDevice: 
    def __init__(
            self, 
            ip, 
            key_pair: Keys, 
            check_paired_before, 
            add_paired_device,
            peer_socket = None, 
            paired = False, 
            ):
        self.connected = False
        self.ip = ip
        self._handshake_done = False
        self.paired = paired 
        self.key_pair = key_pair
        self.peer_socket = peer_socket
        self._peer_public_key: rsa.RSAPublicKey | None = None
        self._buffer = b''
        self._key_sent = False
        self._info_sent = False
        self.check_paired_before = check_paired_before
        self.add_paired_device = add_paired_device
        self._has_pair_permission = False
    
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
                try: 
                    id = self._get_message_id(self._buffer[4:])
                    if id == 0:
                        self._handle_public_key_message(self._buffer)
                except Exception as e: 
                    logging.error(f"peerDevice: {self.ip}: invalid message")

                self._update_buffer(len(self._buffer))
                #TODO: send invalid message to the peer 
                return
            else:
                # handle messages with encryption
                encrypted_message = unpack(f"!{length - 4}s", self._buffer[4:length])[0]
                message = self._get_decrypted_message(encrypted_message)
                id = self._get_message_id(message)

                if (id == 1):
                    self._handle_info_message(message)
                elif (id == 2):
                    self._handle_pair_request()
                elif (id == 3): 
                    self._handle_pair_response(message)

            self._update_buffer(length)

    def _handle_pair_response(self, message):
        """
        handle pair response 
        """
        response = PairResponse.unpack_message(message)
        if response and self._has_pair_permission:
            self.paired = True
            self.connected = True
            self.add_paired_device(self.device_id, self.device_name)
            message = PairResponse.pack_message()
            self._send_encrypted_message(message)
            logging.debug(f"{self.device_name}: sending pair response")
            logging.debug(f"{self.device_name}: paired and connected ")
        else: 
            self._has_pair_permission = False
            logging.debug(f"{self.device_name}: failed to pair ")

    def _handle_pair_request(self): 
        """
        handle pair request and if user wants pairs and send pair response 
        """
        if (input("Do you wanna pair?: ") == "yes"):
            self._has_pair_permission = True
            message = PairResponse.pack_message()
            self._send_encrypted_message(message)
            logging.debug(f"{self.device_name}: sending pair response")
        
                    
    def _handle_info_message(self, message):
        """
        return device id and name
        """
        device_id, device_name = DeviceInfoMessage.unpack_message(message)
        logging.debug(f"peerDevice: {device_id}: {device_name}")
        self.device_id = device_id
        self.device_name = device_name 

        if not self._info_sent: 
            self._send_device_info()

        #TODO: check if device info is received to the peer 
        logging.debug(f"{self.device_name}: handshake done ")
        self._handshake_done = True

        if (self.check_paired_before(device_id)):
            #TODO: send a connnected message
            logging.debug(f"{self.device_name}: - connected")
            self.paried = True
            self._has_pair_permission = True
            self.connected = True

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
        self._send_encrypted_message(device_info_message) 
        self._info_sent = True
    
    def _send_encrypted_message(self, message):
        """
        encrypt and send the message to the peer 
        """
        encrypted_message = self._get_packed_ciphertext(message)
        self._send_message(encrypted_message)


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
        