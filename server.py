#  coding: utf-8 
import SocketServer
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Peter Sterling
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


class MyWebServer(SocketServer.BaseRequestHandler):	

    def get_file_requested(self, data):
        #Split by space and return the second argument to get the file requested
        data = data.split(" ")
        return data[1]

    def get_file_location(self, file):
        #If ending in '/', append .index.html and return it
        last_character = file[-1:]
        if last_character == "/":
            file = file + "index.html"

        return file[1:]

    def send_page(self, file_location):
        #Send a page to the client
        
        #Assign mime-type, default .html
        try:
            if file_location[-4:] == ".css":
                mime_type = "text/css"
            else:
                mime_type = "text/html"
        except:
            mime_type = "text/html"
        
        #Read file
        with open (file_location, "r") as page_file:
            page = page_file.read()

        #Generate header, and then send
        header = "HTTP/1.1 200 OK\r\nContent-Type: " + mime_type + "\r\nContent-Length: " + str(len(page)) + "\r\n\r\n"
        self.request.sendall(header + page)
        

    def send_404(self):
        #Send 404 not found page

        page = "<html><body><h1>404 - Not Found</h1></body></html>"

        header = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: " + str(len(page)) + "\r\n\r\n"

        self.request.sendall(header + page)

    def send_redirect(self, file):
        #If trying to access a directory without a trailing slash, redirect to the location with a trailing slash

        header = "HTTP/1.1 302 Found\r\nLocation: http://127.0.0.1:8080/" + file + "/\r\n\r\n"

        self.request.sendall(header)
        

    def check_ifValidLocation(self, file):
        #Returns true if is inside the 'www' folder, otherwise return false

        #Get the real path of the file.
        location = os.path.realpath("www/" + file)

        #Get the real path of where the script is located, append www to the end.
        script_location = os.path.dirname(os.path.realpath(__file__)) + "/www/"

        #Check if is in the www folder.
        if location[:len(script_location)] == script_location:
            return True
        else:
            return False

    def handle(self):
        self.data = self.request.recv(1024).strip()

        valid_request = True

        try:
            #Parse the file requested out of the message sent
            file_requested = self.get_file_requested(self.data)

            #Get the file location (add /index.html to the end if requesting a directory)
            file_location = self.get_file_location(file_requested)
        except:
            valid_request = False

        if valid_request:

            if os.path.isdir('www/' + file_location) and self.check_ifValidLocation(file_location):
                #If this directory exists and client didnt request with a trailing slash, redirect to a trailing slash
                self.send_redirect(file_location)
            elif os.path.isfile('www/' + file_location) and self.check_ifValidLocation(file_location):
                #Otherwise, if it exists, send the actual file
                self.send_page('www/' + file_location)
            else:
                #Else case: send a 404
                self.send_404()
                

        print ("Got a request of: %s\n" % self.data)
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
