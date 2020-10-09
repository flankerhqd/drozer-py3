import socket
import ssl
from typing import Optional, List, Tuple

from .. import Frame
from .exceptions import ConnectionError
from .transport import Transport

from drozer.ssl.provider import Provider # TODO: eugh

class SocketTransport(Transport):
    AdbHost = "127.0.0.1"
    AdbPort = 5037
    DefaultPort = 31415

    def __init__(self, arguments, trust_callback=None):
        Transport.__init__(self)
        self.choice = None
        if arguments.ssl:
            provider = Provider()
            self.__socket = ssl.wrap_socket(self.__socket, cert_reqs=ssl.CERT_REQUIRED, ca_certs=provider.ca_certificate_path())

        # connect adb 31415
        success = False
        e_msg = self.connect_via_adb(self.DefaultPort)
        if e_msg is None:
            success = True
        else:
            print(e_msg)
        if not success:
            # connect adb custom-port
            endpoint = self.__getEndpoint(arguments)
            if endpoint is None:
                raise ConnectionError("Connect via adb fail and arguments.server is not configured")
            if self.DefaultPort != endpoint[1]:
                print("tcp(%d) over adb fail, then try tcp(%d) over adb" % (self.DefaultPort, endpoint[1]))
                e_msg = self.connect_via_adb(endpoint[1])
        if e_msg is None:
            success = True
        else:
            print(e_msg)

        if not success:
            # connect custom host:port
            print("Connect via adb fail, then try tcp connect")
            self.__socket = socket.socket()
            self.setTimeout(90.0)
            self.__socket.connect(endpoint)
        
        if arguments.ssl:
            trust_callback(provider, self.__socket.getpeercert(True), self.__socket.getpeername())
            
    def close(self):
        """
        Close the connection to the Server.
        """

        self.__socket.close()
        
    def receive(self):
        """
        Receive a Message from the Server.

        If not frame is available, None is returned.
        """

        try:
            frame = Frame.readFromSocket(self.__socket)
    
            if frame is not None:
                return frame.message()
            else:
                return None
        except socket.timeout as e:
            raise ConnectionError(e)
        except ssl.SSLError as e:
            raise ConnectionError(e)

    def send(self, message):
        """
        Send a Message to the Server.

        The Message is automatically assigned an identifier, and this is
        returned.
        """

        try:
            message_id = self.nextId()
    
            frame = Frame.fromMessage(message.setId(message_id).build())
    
            self.__socket.sendall(frame.bytes())
    
            return message_id
        except socket.timeout as e:
            raise ConnectionError(e)
        except ssl.SSLError as e:
            raise ConnectionError(e)

    def sendAndReceive(self, message):
        """
        Send a Message to the Server, and wait for the response to be received.
        """

        message_id = self.send(message)

        while True:
            response = self.receive()

            if response is None:
                raise ConnectionError(RuntimeError('Received an empty response from the Agent.'))
            elif response.id == message_id:
                return response
            
    def setTimeout(self, timeout):
        """
        Change the read timeout on the socket.
        """
        
        self.__socket.settimeout(timeout)

    def __getEndpoint(self, arguments) -> Optional[Tuple[str, int]]:
        """
        Decode the Server endpoint parameters, from an ArgumentParser arguments
        object with a server member.

        This extracts the hostname and port, assigning a default if they are
        not provided.
        """

        if arguments.server is not None:
            endpoint = arguments.server
        else:
            return None

        if ":" in endpoint:
            host, port = endpoint.split(":")
        else:
            host = endpoint
            port = self.DefaultPort
        
        return host, int(port)

    def adb(self, s: str):
        return ('%04x' % len(s)).encode('ascii') + s.encode()

    def connect_via_adb(self, port: int) -> Optional[str]:
        # adb devices
        _tmp_socket = socket.socket()
        try:
            _tmp_socket.connect((self.AdbHost, self.AdbPort))
        except Exception:
            return "adb server seems not alive"
        _tmp_socket.send(self.adb('host:devices'))
        if _tmp_socket.recv(4) != b'OKAY':
            _tmp_socket.close()
            return "adb(host:devices) fail"
        devices = _tmp_socket.recv(int(_tmp_socket.recv(4).decode('ascii'), 16)).decode().strip().split('\n')
        _tmp_socket.close()

        # adb -s
        self.__socket = socket.socket()
        try:
            self.__socket.connect((self.AdbHost, self.AdbPort))
        except Exception:
            return "adb server seems not alive"
        if len(devices) == 1:
            self.__socket.send(self.adb('host:transport-any'))
        else:
            self.__socket.send(self.adb('host:transport:%s' % self.choose_device(devices)))
        if self.__socket.recv(4) != b'OKAY':
            self.__socket.close()
            return "adb(host:transport-any) fail"
        # connect via tcp:<port>
        self.__socket.send(self.adb('tcp:%d' % port))
        if self.__socket.recv(4) != b'OKAY':
            self.__socket.close()
            return "adb(tcp:%d) fail" % port

    def choose_device(self, devices: List[str]) -> str:
        if self.choice is None:
            for i in range(len(devices)):
                print('[%d]' % i, devices[i])
            self.choice = devices[int(input("Input your choice\n"))].split('\t')[0]
        return self.choice
