"""async_client
Champlain College CSI-235, Spring 2018
Prof. Josh Auerbach
Bare bones example of asynchronously receiving
data from server and user input from stdin
    Author: Brian Nguyen and Jake Buzzell
    Class   : CSI-235
    Assignment: Final Project
    Date Assigned: April 11,2018
    Due Date: April 26, 2018  11:59pm
    Description:
        This code has been adapted from that provided by Prof. Joshua Auerbach:
        Champlain College CSI-235, Spring 2018
        The following code was provided by Prof. Joshua Auerbach
        and modified by Brian Nguyen and Jake Buzzell
"""
import asyncio
import argparse
import socket
import time
import ssl
import json
import struct

class AsyncClient(asyncio.Protocol):
    def __init__(self):
        self.username = ""
        self.logged_in = False
        self.header_struct = struct.Struct('!I')
        self.data = ""

    def connection_made(self,transport):
        self.transport = transport
        self.address = transport.get_extra_info("peername")
        print('accepted connection from {}'.format(self.address))

    def send_message(self, data):
        length = self.header_struct.pack(len(data))
        self.transport.write(length)
        message = data.encode('utf-8')
        self.transport.write(message)



    def data_received(self, data):
        """simply prints any data that is received"""

        print("Receive before setting: ", data,"\n\n\n\n")

        #json_data = data.replace("'", "\"")

        self.data += data.decode()
        #first need to get the first 4 bytes for the len(data)



#Clean this up later put it under handle user input function
#break it into 2 part b4 logged in and after logged in



    @asyncio.coroutine
    def handle_user_input(self, loop):
        """reads from stdin in separate thread
        if user inputs 'quit' stops the event loop
        otherwise just echos user input
        """
        while True:
            if(self.logged_in == False):
                message = yield from loop.run_in_executor(None, input, ">Enter Username to log in \n"
                                                                       ">or Enter quit to quit \n"
                                                                       ">input: ")
                if message == "quit":
                    loop.stop()
                    return
                #store message for your self and send the username

                my_dict = {"USERNAME": message}
                string_message = json.dumps(my_dict)
                self.send_message(string_message)

                yield from asyncio.sleep(1.0)

                print(self.data)#This is all the data together
                json_dict = json.dumps(self.data)
                print(json_dict)
                # make this a dictionary then sort data.

            #If user is logged in
            else:
                message = yield from loop.run_in_executor(None, input, ">")
                if message == "quit":
                    loop.stop()
                    return
                self.send_message(message)
                yield from asyncio.sleep(1.0)
                print("Test:logged in loop")

    def connection_lost(self, ex):
        print("Lost connection" + '\n')
        self.logged_in = False
        self.transport.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example client')
    parser.add_argument('host', help='IP or hostname')
    parser.add_argument('-p', metavar='port', type=int, default = 9000,
                        help='TCP port (default 9000)')
    parser.add_argument('-ca', dest='cafile', metavar='cafile', type=str, default=None,
                        help='CA File')
    #default for ca file can either be none or you can just leave it out it doesn't really matter
    args = parser.parse_args()



    loop = asyncio.get_event_loop()
    # we only need one client instance
    client = AsyncClient()

    # the lambda client serves as a factory that just returns
    # the client instance we just created
    #purpose = ssl.Purpose.CLIENT_AUTH
	#context = ssl.create_default_context(purpose, cafile=args.cafile)
    #context.load_cert_chain(certfile)
#Add ssl for certifacate later

    coro = loop.create_connection(lambda: client, args.host , args.p)

    loop.run_until_complete(coro)

    # Start a task which reads from standard input
    asyncio.async(client.handle_user_input(loop))

    try:
        loop.run_forever()
    finally:
        loop.close()
