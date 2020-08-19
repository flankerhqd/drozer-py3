"""
A library of fileystem functions.
"""

from hashlib import md5
from typing import Union


def read(path) -> bytes:
    """
    Utility method to read a file from the filesystem into a string.
    """
    
    try:
        f = open(path, 'rb')
        data = f.read()
        f.close()
        
        return data
    except IOError as e:
        return None
    
def touch(path):
    """
    Utility method to touch a file on the filesystem.
    """
    
    open(path, 'w').close()

def write(path, data: Union[bytes, str]):
    """
    Utility method to write a string into a filesystem file.
    """
    
    try:
        f = open(path, 'wb')
        if isinstance(data, bytes):
            f.write(data)
        else:
            f.write(data.encode())
        f.close()
        
        return len(data)
    except IOError:
        return None
        
def md5sum(path):
    """
    Utility method to get the md5sum of a file on the filesystem
    """
    
    try:
        f = open(path, 'rb')
        line = data = f.read()

        while line != "":
            line = f.read()
            
            data += line
        
        f.close()
        
        return md5.new(data).digest().encode("hex")
    except IOError:
        return None
        
