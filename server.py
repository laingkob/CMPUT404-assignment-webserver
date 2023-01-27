#  coding: utf-8 
import socketserver
from pathlib import Path
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Courtenay Laing-Kobe
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

str_200 = "200 OK"
str_301 = "301 Moved Permanently"
str_405 = "405 Method Not Allowed"
str_404 = "404 Path Not Found"
base_url = "http://127.0.0.1:8080/"

#TODO:
# -MIME for css & html
# -Fix 301 redirect
# /Test on Lab Machine, check curl for 405 testing
# /Make sure script runs ^
# -More basic html error page
# -Should add dates and content lengths to headers
# -Check licensing
# -Screenshots in reqs (& test in Firefox)

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        #default content type
        content_type = "Content-Type: application/octet-stream"

        self.data = self.request.recv(1024).strip().decode('utf-8')
        print ("Got a request of: %s\n" % self.data)
        if self.data:
            split_data = self.data.split()
        else:
            return
        self.code = str_200

        if 'GET' != split_data[0]:
            self.code = str_405
        else:
            if split_data[1][0:3] != "/www":
                path = 'www' + split_data[1]
            else:
                path = split_data[1]

            if Path(path).is_dir():
                if path[-1] != '/':
                    self.code = str_301
                    loc = path + '/'
                path = path + 'index.html'

            if Path(path).is_file():
                f = open(path, "r")
                html = f.read()
                f.close()
            elif self.code != str_301:
                self.code = str_404

        mime_types = mimetypes.read_mime_types(path)
        if mime_types != None:
            split_path = path.split('.')
            extension = '.' + split_path[-1]
            content_type = "Content-Type: " + mime_types[extension] 

        if self.code == str_200:
            self.request.sendall(bytearray(f"HTTP/1.1 {self.code}\r\n\r\n" + html, 'utf-8'))
        
        elif self.code == str_301:
            self.request.sendall(bytearray(f"HTTP/1.1 {self.code}\r\n\
                Location: {base_url + loc}\r\n\
                \r\n\
                <html>\n\
                <head><title>{self.code}</title></head>\n\
                <body bgcolor=\"white\">\n\
                <center><h1>{self.code}</h1></center>\n\
                </body>\n\
                </html>", 'utf-8'))         
        else:
            self.request.sendall(bytearray(f"HTTP/1.1 {self.code}\r\n\
                {content_type}\r\n\
                \r\n\
                <html>\n\
                <head><title>{self.code}</title></head>\n\
                <body bgcolor=\"white\">\n\
                <center><h1>{self.code}</h1></center>\n\
                </body>\n\
                </html>", 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
