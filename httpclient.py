#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Michael Stensby
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
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    CRLF = "\r\n\r\n"
    def get_host_port_path(self,url):
        url_split =  url.split(":")
        if len(url_split) == 2:
            url_split[1] = url_split[1].strip("/")
            if "/" in url_split[1]: # has path
                host_path = url_split[1].split("/")
                host = host_path.pop(0)
                path = "/"+"/".join(host_path)
            else: # default path
                host = url_split[1]
                path = "/"

            port = 80
        elif len(url_split) == 3:
            host = url_split[1].strip("/")
            port_path = url_split[2].split("/")
            port = int(port_path[0])
            path = "/"+"/".join(port_path[1:])

        return host, port, path

    def connect(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host,port))
        return sock

    def get_code(self, data):
        return int(data.split()[1])

    # header and body separated by CRLF
    def get_headers(self,data):
        return data.split(self.CRLF)[0]

    def get_body(self, data):
        return data.split(self.CRLF)[1]

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
        return str(buffer)

    # send GET request to url with args, return HTTPResponse
    def GET(self, url, args=None):
        host, port, path = self.get_host_port_path(url)
        sock = self.connect(host,port)
        if args != None:
            body = urllib.urlencode(args)
        else:
            body = ""

        request = "GET %s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\nContent-Length: %s\r\nConnection: close%s%s%s" %(path, host, len(body),self.CRLF,body,self.CRLF)
        sock.sendall(request)
        response = self.recvall(sock)
        sock.close()

        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.get_host_port_path(url)
        sock = self.connect(host,port)
        if args != None:
            body = urllib.urlencode(args)
        else:
            body = ""
        request = "POST %s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\nContent-Length: %s\r\nConnection: close%s%s%s" %(path, host, len(body),self.CRLF,body,self.CRLF)
        sock.sendall(request)
        response = self.recvall(sock)
        sock.close()

        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )
