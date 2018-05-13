#!/usr/bin/python3
from Crypto.Cipher import AES
import base64
import sys
import time
import socket
from socket import SHUT_RDWR

class Encrypt:
    def __init__(self,blockSize,padding):
        self.BLOCK_SIZE = blockSize #32
        self.PADDING = padding #'~'

    def pad(self, s):
        return s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * self.PADDING

    def EncodeAES(self, plaindata, key):
        key = self.pad(key)
        cipher = AES.new(key)
        enc = cipher.encrypt(self.pad(plaindata))
        return base64.b64encode(enc)

    def DecodeAES(self, encodeddata, key):
        key = self.pad(key)
        cipher = AES.new(key)
        b64 = base64.b64decode(encodeddata)
        return cipher.decrypt(b64).decode().replace(self.PADDING,"")


class communication():
    def __init__(self,ip,port,encryptionKey):
        self.port = port
        self.ip = ip
        self.encryption = Encrypt(32,'~')
        self.encryptionKey = encryptionKey
        self.deadConnection = True

    def isAlive(self):
        # checks if the connection is alive or not 
        return(not self.deadConnection)

    def send_data(self,data):
        # assumes there is a connection established
        # uses self.conn to send data over
        while (self.deadConnection):
            print("Waiting 5 seconds for connection before sending")
            time.sleep(5)

        self.conn.sendall(self.encryption.EncodeAES(data,self.encryptionKey))

    def receive_data(self):
        while (self.deadConnection):
            print("Waiting 5 seconds for connection")
            time.sleep(5)

        data = self.encryption.DecodeAES(self.conn.recv(1024), self.encryptionKey)

        if data == '':
            self.deadConnection = True
            self.conn.shutdown(SHUT_RDWR)
            self.conn.close()
            return

        return data

    def restart_server(self):
        self.sock.listen(1)
        self.conn, self.address = self.sock.accept()
        self.deadConnection = False

    def restart_client(self):
        self.conn.connect((self.ip, self.port))
        self.deadConnection = False

    def start_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1) #listen for max 1 connection only

        self.conn, self.address = self.sock.accept()
        self.deadConnection = False

    def start_client(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.conn.connect((self.ip, self.port))
        self.deadConnection = False

    def terminate(self):
        try:
            self.conn.close()
        except AttributeError:
            self.sock.shutdown(SHUT_RDWR)
            self.sock.close()
        except Exception as e:
            print("Exception on termination: {}".format(e))

    def printInfo(self):
        print("\nRemote ip: {}".format(self.ip))
        print("\nRemote port: {}".format(self.port))
        print("\nEncryption Key: {}".format(self.encryptionKey))


def unit_test():
    print('Unit testing is running\n')
    conn = communication('localhost',8082,'thisisthekey')
    try:
        # UNCOMMENT BELOW FOR SERVER TEST #
        # =============================== #
        # conn.start_server()
        # while True:
        #     print("Data received: {}".format(conn.receive_data()))
        #     if (not conn.isAlive()):
        #         conn.restart_server()
        # =============================== #
        
        # UNCOMMENT BELOW FOR CLIENT TEST #
        # =============================== #
        conn.start_client()
        while True:
            conn.send_data("Hello world!")
            print(conn.receive_data())

            if (not conn.isAlive()):
            #     conn.restart_client()
            #     time.sleep(20)
                sys.exit(1)
        # =============================== #

    except KeyboardInterrupt:
        conn.terminate()


if __name__ == '__main__':
    unit_test()