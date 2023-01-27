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

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        #defaults
        loc = ""
        path = " "
        code = str_200
        content_type = "Content-Type: text/html; charset=UTF-8"
        #html mostly copied from Hindle & Campbell's slides located here:
        #https://uofa-cmput404.github.io/cmput404-slides/04-HTTP.html#/20
        default_payload = "<html>\n\
                        <head><title>{http_code}</title></head>\n\
                        <body bgcolor=\"white\">\n\
                        <center><h1>{http_code}</h1></center>\n\
                        </body>\n\
                        </html>"

        #Check what data came in, convert to str for processing
        self.data = self.request.recv(1024).strip().decode('utf-8')
        print ("Got a request of: %s\n" % self.data)
        #Prevent empty requests from causing issues
        if self.data:
            split_data = self.data.split()
        else:
            return
        
        #Only allow GET requests
        if 'GET' != split_data[0]:
            code = str_405
        else:
            #Prevent relative paths
            if split_data[1][0:4] == "/../":
                code = str_404
            #Allow www folder in url only
            elif split_data[1][0:5] != "/www/":
                path = 'www' + split_data[1]
            else:
                path = split_data[1][1:]
            #Handle directories and missing end/
            if Path(path).is_dir():
                if path[-1] != '/':
                    code = str_301
                    loc = path + '/'
                else:
                    path = path + 'index.html'
            #Handle files
            if Path(path).is_file():
                f = open(path, "r")
                payload = f.read()
                f.close()
                #Specify mimetypes
                mime_types = mimetypes.read_mime_types(path)
                if mime_types != None:
                    split_path = path.split('.')
                    extension = '.' + split_path[-1]
                    content_type = "Content-Type: " + mime_types[extension] + "; charset=UTF-8" 
            #Make sure not 301 before calling 404
            elif code != str_301:
                code = str_404
        #Send 200 code and display file contents
        if code == str_200:
            self.request.sendall(bytearray(f"HTTP/1.1 {code}\r\n{content_type}\r\n\r\n" + payload, 'utf-8'))
        #Send 301 code with new location info
        elif code == str_301:
            self.request.sendall(bytearray(f"HTTP/1.1 {code}\r\n\
                Location: {base_url + loc}\r\n\
                {content_type}\r\n\r\n" + default_payload.format(http_code = code), 'utf-8'))
        #Send generic html page with code information         
        else:
            self.request.sendall(bytearray(f"HTTP/1.1 {code}\r\n\
                {content_type}\r\n\r\n" + default_payload.format(http_code = code), 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
