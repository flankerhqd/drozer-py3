from . import FtpException
from ..api.builders.file_transform_request import FileTransformRequestFactory


class Ftp:
    def __init__(self, session):
        self.__session = session

    def upload(self, filename: str, data: bytes):
        ret = self.__session.sendAndReceive(FileTransformRequestFactory(True, filename, data))
        if not ret.file_transform_response.success:
            raise FtpException("upload fail")

    def download(self, filename) -> bytes:
        ret = self.__session.sendAndReceive(FileTransformRequestFactory(False, filename))
        if not ret.file_transform_response.success:
            raise FtpException("download fail")
        return ret.file_transform_response.data
