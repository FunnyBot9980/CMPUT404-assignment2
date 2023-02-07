#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, John Macdonald
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def get_host_port(self, url):
        parsed_url = urlparse(url)

        if parsed_url.scheme != 'http':
            raise ValueError("Client cannot handle any scheme other than http")

        host = parsed_url.hostname

        if parsed_url.port == None:
            port = 80
        else:
            port = parsed_url.port
        return (host, port)


    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self, data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = "empty body"
        host, port = self.get_host_port(url)
        self.connect(host, port)
        request = "GET / HTTP/1.1\r\n"
        request += "Host: {}:{}\r\n".format(host, port)
        request += "User-Agent: http-client/1.0\r\n"
        request += "Accept: */*\r\n"
        request += "\r\n"
        print(request)
        self.sendall(request)
        data = self.recvall(self.socket)
        print(data)
        self.close()
        # print(host, port)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = "empty body"
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        response = client.command( sys.argv[2], sys.argv[1] )
        # print(response.code, response.body)
    else:
        response = client.command( sys.argv[1] )
        # print(response.code, response.body)
