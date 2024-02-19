import socket 
import logging
from struct import unpack, pack
from cryptography.hazmat.primitives.asymmetric import rsa

from keys import RsaKeys
from keys import AseKey
from message import MESSAGE_TYPE
from config import DEVICE_ID
from file import File 
from message import *


class PeerDevice: 
    def __init__(
            self, 
            ip, 
            key_pair: RsaKeys, 
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
        self._current_file = None
        self._ase_key = None
        self._rsa_key_shared = False
    
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
            elif self._rsa_key_shared and not self.connected:
                # handle messages with encryption
                encrypted_message = unpack(f"!{length - 4}s", self._buffer[4:length])[0]
                message = self._get_decrypted_message(encrypted_message)
                id = self._get_message_id(message)

                if id == 1:
                    self._handle_info_message(message)
                elif id == 2:
                    self._handle_pair_request()
                elif id == 3: 
                    self._handle_pair_response(message)
                elif id == 4: 
                    self._handle_pair_cancel()
                elif id == 5: 
                    self._handle_ase_key_message(message)
            else:
                if not self.paired and not self.connected:
                    #TODO: handle the exception
                    return 

                encrypted_message = unpack(f"!{length - 4}s", self._buffer[4:length])[0]
                message = self._ase_key.decrypt_data(encrypted_message)
                id = self._get_message_id(message) 
                
                #TODO: handle the ase key 
                if id == 6:
                    self._handle_file_info_message(message)
                elif id == 7: 
                    self._handle_file_chunk_message(message)
                elif id == 8:
                    self._handle_file_done_message()


            self._update_buffer(length)


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
            self._set_paired()
            self._send_ase_key()
            return 
    
    def _send_ase_key(self):
        """
        make and send the ase key 
        """
        self._ase_key = AseKey()
        logging.debug(f"{self.device_name}: ase key - {self._ase_key}")

        key_message = AseKeyMessage.pack_message(self._ase_key.key)
        self._send_rsa_encrypted_message(key_message)
        logging.debug(f"{self.device_name}: ase key sent")

        logging.debug(f"{self.device_name}: connected")
        self.connected = True
    
    def _handle_ase_key_message(self, message):
        """
        """
        key = AseKeyMessage.unpack_message(message)
        logging.debug(f"{self.device_name}: got ase key - {key}")

        self._ase_key = AseKey(key)
        self.connected = True

    def pair(self):
        """
        do the pairing process
        """
        self._send_pair_request()

    def _send_pair_request(self):
        """
        send the pair request 
        """
        if (input("Do you wanna pair?: ") == "yes"):
            self._has_pair_permission = True
            message = PairRequest.pack_message()
            self._send_rsa_encrypted_message(message)
            logging.debug(f"{self.device_name}: sending pair request")
            logging.info(f"{self.device_name}: pairing")
        
    def _handle_pair_request(self): 
        """
        handle pair request and if user wants pairs and send pair response 
        """
        if (input("Do you wanna pair?: ") == "yes"):
            self._has_pair_permission = True
            message = PairResponse.pack_message(True)
            self._send_rsa_encrypted_message(message)
            logging.debug(f"{self.device_name}: sending pair response")

    def _handle_pair_response(self, message):
        """
        handle pair response 
        """
        response = PairResponse.unpack_message(message)

        # if paired doesn't do anything 
        if response and self.paired: 
            return 

        #TODO: if response is 0 cancel the pair
        if response and self._has_pair_permission:
            self._set_paired()
            self.add_paired_device(self.device_id, self.device_name)

            message = PairResponse.pack_message(True)
            self._send_rsa_encrypted_message(message)
            logging.debug(f"{self.device_name}: sending pair response")

            self._send_ase_key()
        else: 
            self._has_pair_permission = False
            logging.info(f"{self.device_name}: failed to pair ")

    def _set_paired(self):
        """
        set variables to paired and connected
        """
        self.paried = True
        self._has_pair_permission = True
        logging.info(f"{self.device_name}: - paired")

    def unpair(self):
        """
        do the unpairing process
        """
        self.paired = False
        self._has_pair_permission = False
        self.connected = False
        self._send_pair_cancel()
        logging.info(f"{self.device_name}: pair canceled")

    def _send_pair_cancel(self):
        """
        send encrypted pair cancel message 
        """
        message = PairCancel.pack_message()
        self._send_rsa_encrypted_message(message)
                    
    def _handle_pair_cancel(self):
        """
        handle the pair cancel message
        """
        self.paired = False
        self._has_pair_permission = False
        self.connected = False
        logging.info(f"{self.device_name}: pair canceled")

    def send_file(self, path: str):
        """
        send file to the peer
        """
        file = File(path)
        file.read_file()

        # send the file info 
        file_info_message = FileInfoMessage.pack_message(file.__str__(), file.hash) 
        self._send_ase_encrypted_message(file_info_message)

        logging.info(f"{file.path}: sending the file")
        for i in range(0, file.no_of_chunks):
            chunk = file.get_chunk(i)
            file_chunk_message = FileChunkMessage.pack_message(i, chunk)
            print(file_chunk_message)
            self._send_ase_encrypted_message(file_chunk_message)

    def _handle_file_info_message(self, message):
        """
        unpack message and make a file object
        """
        path, hash = FileInfoMessage.unpack_message(message)
        self._current_file = File(path)
        self.hash = hash 
        self._current_file.open_to_write()

    def _handle_file_chunk_message(self, message):
        """
        unpack message and write to the file 
        """
        index, chunk = FileChunkMessage.unpack_message(message)
        self._current_file.write_chunk(index, chunk)

    def _handle_file_done_message(self):
        """
        check hash and close file 
        """
        if (self._current_file.check_hash()): 
            logging.info(f"{self._current_file}: file received")
        self._current_file.close()
    
    def _get_packed_ciphertext(self, encrypted_message):
        """
        encrypt message with peer public key and pack it with length of the message
        """
        return pack(f"!I{len(encrypted_message)}s", len(encrypted_message) + 4, encrypted_message) 

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
        self._peer_public_key = RsaKeys.deserialize_public_key(PublicKeyMessage.unpack_message(message)) 
        logging.debug(f"peer:{self.ip}: got public key")
        if not self._key_sent: 
            self.send_key()
        else:
            self._send_device_info()

        self._rsa_key_shared = True

    def _send_device_info(self):
        """
        send device info to the peer 
        """
        device_info_message = DeviceInfoMessage().pack_message()
        self._send_rsa_encrypted_message(device_info_message) 
        self._info_sent = True
    
    def _send_rsa_encrypted_message(self, message):
        """
        encrypt and send the message to the peer 
        """
        encrypted_message = RsaKeys.get_ciphertext(message, self._peer_public_key)
        data = self._get_packed_ciphertext(encrypted_message)
        self._send_message(data)

    def _send_ase_encrypted_message(self, message):
        """
        send ase encrypted message 
        """
        encrypted_message = self._ase_key.encrypt_data(message)
        data = self._get_packed_ciphertext(encrypted_message)
        self._send_message(data)

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
        