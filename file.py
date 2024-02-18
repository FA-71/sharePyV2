from hashlib import sha256
from pathlib import Path
import logging

from constants import CHUNK_SIZE


class File: 
    def __init__(self, path: str):
        self.path = Path(path)
        self.hash: bytes | None = None 
        self.file = None
        self.no_of_chunks = 0
    
    def read_file(self):
        """
        open file as read and make hash, no_of_chunks
        """
        self.file = self._file_read_open()
        self.hash = self._get_file_hash()
        self.no_of_chunks = self._get_no_of_chunks()

    def open_to_write(self):
        self._file_write_open()

    def close(self):
        self.file.close()
        logging.debug(f"{self.path}: file closed")

    def _file_read_open(self):
        """
        open file to read 
        """
        if (self.path.exists()):
            logging.debug(f"{self.path}: file exists")
            return open(self.path.resolve(), 'rb')

        logging.error(f"{self.path}: file doesn't exists")
        #TODO: handle error and raise exception 
        return None
    
    def _file_write_open(self): 
        """
        open file to write
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.path.resolve(), 'wb+') 
        logging.debug(f"{self.path} file open to write ")

    def write_chunk(self, index, chunk):
        """
        write chunk to the file 
        """
        self.file.seek(index * CHUNK_SIZE)
        self.file.write(chunk)


    def _get_file_hash(self):
        """
        return 256hash digest for the whole file 
        """
        file_hash = sha256() 
        self.file.seek(0)

        while True: 
            chunk = self.file.read(8192)
            if not chunk: 
                break 
            file_hash.update(chunk)

        logging.debug(f"{self.path}: file hash - {file_hash.digest()}")
        return file_hash.digest()
        
    def get_chunk(self, index):
        """
        return file chunk on given index  
        """
        if index >= self.no_of_chunks: 
            error_msg = f"{self.path}: get_chunks - index is out of range"
            logging.error(error_msg) 
            raise ValueError(error_msg)


        self.file.seek(index * CHUNK_SIZE)
        chunk = self.file.read(CHUNK_SIZE)
        return chunk

    def _get_no_of_chunks(self):
        """
        return no of chunks in the file 
        """
        file_size = self.path.stat().st_size
        no_chunks = file_size // CHUNK_SIZE

        if file_size % CHUNK_SIZE: 
            no_chunks += 1
        
        return no_chunks

    def check_hash(self):
        """
        return True if the existing hash matches 
        """
        file_hash = self._get_file_hash()
        if file_hash == self.hash: 
            logging.debug(f"{self.path}: hash matches")
            return True

        logging.error(f"{self.path}: hash doesn't match")
        return False 
        
        
