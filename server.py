#  coding: utf-8 
import SocketServer
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
        #Takes the message and parses out and removes the file the client is interested in. Should always be second word in.
        data = data.split(" ")
        return data[1]

    def get_file_location(self, file):
        #Gets the location of the file. Should be the same unless it's a directory (ends in /). Then append index.html to the end.
        last_character = file[-1:]
        if last_character == "/":
            file = file + "index.html"

        #Return file location, remove the slash at the beginning
        return file[1:]

    def send_page(self, file_location):
        #Sends a page to the client.

        #Check if its a .css file. If so, set its mime type to CSS.
        try:
            if file_location[-4:] == ".css":
                mime_type = "text/css"
            else:
                mime_type = "text/html"
        except:
            mime_type = "text/html"
        
        #Dump the contents of the file to page.
        with open (file_location, "r") as page_file:
            page = page_file.read()

        #Generate the header.
        header = "HTTP/1.1 200 OK\r\nContent-Type: " + mime_type + "\r\nContent-Length: " + str(len(page)) + "\r\n\r\n"
        
        #Send to client.
        self.request.sendall(header + page)

    def send_404(self):
        #Send a 404 page (page not found)

        page = "<html><body><h1>404 - Not Found</h1></body></html>"

        header = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: " + str(len(page)) + "\r\n\r\n"

        #print header and page
        self.request.sendall(header + page)


    def check_ifValidFile(self, file):
        #Check to see if the file is inside the www directory. If outside, will return false.
        
        #Get the actual location of the www folder on disk.
        location = os.path.realpath("www/" + file)

        #Get the location of the python script and append the www folder to it.
        script_location = os.path.dirname(os.path.realpath(__file__)) + "/www/"

        #Check if the file is inside the www directory.
        if location[:len(script_location)] == script_location:
            return True
        else:
            return False

    def handle(self):
        self.data = self.request.recv(1024).strip()

        #Sometimes the server recieves empty messages. If the message can't be parsed, do nothing.
        valid_request = True

        try:
            #Parse the file wanted, and get the location of the file.
            file_requested = self.get_file_requested(self.data)
            file_location = self.get_file_location(file_requested)
        except:
            valid_request = False

        if valid_request:
            #Check to see if the file physically exists and is not outside of the www folder.
            if os.path.isfile('www/' + file_location) and self.check_ifValidFile(file_location):
                #If so, send the file to the client.
                self.send_page('www/' + file_location)
            else:
                #Either not found or is outside of the www directory. Send 404.
                self.send_404()
                
        #Debugging.
        print ("Got a request of: %s\n" % self.data)
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
