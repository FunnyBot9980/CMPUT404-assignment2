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

# try these for testing:
# curl -v -X GET http://127.0.0.1:8080/
# py httpclient.py GET http://127.0.0.1:8080/
# py httpclient.py GET http://www.example.com/
# curl -v -X GET http://www.example.com/


import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, parse_qs, urlencode

USER_AGENT = 'mini-curl/1.0'
HTTP_VERSION = 'HTTP/1.1'
URL_ENCODE = "application/x-www-form-urlencoded"
codes = {
        200: 'Ok',
        404: 'Not Found',
        }

def help():
    print("httpclient.py [GET/POST] [URL]\n")



class HTTPRequest(object):
    def __init__(self, ip, host, port, method="GET", path="/", accept="text/html; application/json", content_type=URL_ENCODE, content_length=0, body=""):
        self.method = method
        self.path = path
        self.ip = ip
        self.host = host
        self.port = port
        self.accept = accept
        self.content_type = content_type
        self.content_length = content_length
        self.body = body


    def request_to_str(self):
        request = "{} {} {}\r\n".format(self.method, self.path, HTTP_VERSION)
        if self.ip != self.host:
            request += "Host: {}\r\n".format(self.host) 
        else:
            request += "Host: {}:{}\r\n".format(self.ip, self.port) 
        request += "User-Agent: {}\r\n".format(USER_AGENT)
        request += "Accept: {}\r\n".format(self.accept)
        request += "\r\n"
        return request


    def post_request_to_str(self):
        request = "{} {} {}\r\n".format(self.method, self.path, HTTP_VERSION)
        if self.ip != self.host:
            request += "Host: {}\r\n".format(self.host) 
        else:
            request += "Host: {}:{}\r\n".format(self.ip, self.port) 
        request += "User-Agent: {}\r\n".format(USER_AGENT)
        request += "Content-Type: {}\r\n".format(self.content_type)
        self.content_length = len(self.body.encode())
        request += "Content-Length: {}\r\n".format(self.content_length)
        request += "Accept: {}\r\n".format(self.accept)
        request += "\r\n"
        request += self.body
        return request


class HTTPResponse(object):
    def __init__(self, code=404, headers_dict="", headers="", body=""):
        self.code = code
        self.headers = headers
        self.headers_dict = headers_dict
        self.body = body


class HTTPClient(object):
    def get_host_port(self, url):
        parsed_url = urlparse(url)

        if parsed_url.scheme != 'http':
            raise ValueError("Client cannot handle any scheme other than http")

        host = parsed_url.hostname
        ip = socket.gethostbyname(host)
        if parsed_url.port == None:
            port = 80
        else:
            port = parsed_url.port
        return (host, ip, port, parsed_url)


    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None


    def parse_headers(self, headers_data):
        headers = headers_data.decode('utf-8')
        headers = headers.split('\r\n')
        headers_dict = {}
        for line in range(1, len(headers)):
            if headers[line] != '':
                parts = headers[line].split(':', 1)
                headers_dict[parts[0]] = parts[1].strip()
        statusline = headers[0].split()
        return (statusline, headers_dict)

    

    def get_body(self, sock, content_length):
        if content_length != None:
            recv_buffer = 1024
            while content_length > recv_buffer:
                recv_buffer += 1024
            body = sock.recv(recv_buffer)
        else:
            body = bytearray()
            sock.settimeout(15)
            while True:
                try:
                    part = sock.recv(1024)
                    if not part:
                        break
                    body.extend(part)
                except socket.timeout:
                    break
        return body.decode('utf-8')


    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))


    def close(self):
        self.socket.close()


    # read everything from the socket
    def recvall(self, sock):
        response = HTTPResponse()
        headers = b''
        while b'\r\n\r\n' not in headers:
            headers += sock.recv(1)
        parsed_headers = self.parse_headers(headers)
        statusline = parsed_headers[0]

        response.code = int(statusline[1])
        response.headers = headers.decode('utf-8')
        response.headers_dict = parsed_headers[1]
        try:
            content_length = int(response.headers_dict['Content-Length'])
        except KeyError:
            content_length = None

        response.body = self.get_body(sock, content_length)
        return response 


    def GET(self, url, args=None):
        host, ip, port, parsed_url = self.get_host_port(url)
        self.connect(ip, port)

        request = HTTPRequest(ip, host, port, path=parsed_url.path)
        request = request.request_to_str()
        # print(request)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()
        # print(response.headers)
        # print(response.body)
        return response 


    def POST(self, url, args=None):
        host, ip, port, parsed_url = self.get_host_port(url)
        self.connect(ip, port)

        # args = {'a':'aaaaaaaaaaaaa',
        #         'b':'bbbbbbbbbbbbbbbbbbbbbb',
        #         'c':'c',
        #         'd':'012345\r67890\n2321321\n\r'}
        
        request = HTTPRequest(ip, host, port, path=parsed_url.path, method='POST', body=parsed_url.query)
        if args != None:
            parsed_args = urlencode(args)
            print(parsed_args)
            if request.body == "":
                request.body += parsed_args
            else:
                request.body += "&" + parsed_args
        request = request.post_request_to_str()
        print(request)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()
        print(response.headers)
        print(response.body)
        return response


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
