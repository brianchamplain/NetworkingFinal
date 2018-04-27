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
import ast
import datetime
import calendar

class AsyncClient(asyncio.Protocol):
    def __init__(self):
        self.username = ""
        self.logged_in = False
        self.header_struct = struct.Struct('!I')
        self.data = b''
        self.tuple = ()

    def connection_made(self,transport):
        self.transport = transport
        self.address = transport.get_extra_info("peername")
        print('accepted connection from {}'.format(self.address))

    def send_message(self, data):

        length = self.header_struct.pack(len(data))
        self.transport.write(length)
        message = data.encode('ascii')
        self.transport.write(message)



    def data_received(self, data):
        """simply prints any data that is received"""
        self.data += data
        if(self.logged_in == True):
            print(data)





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


                self.data = self.data[4:]
                self.data.decode()
                json_dict = json.loads(self.data)
                if json_dict.get("USERNAME_ACCEPTED") == False:
                    print("\n", json_dict.get("INFO"), "\n")
                elif json_dict.get("USERNAME_ACCEPTED") == True:
                    print("\n", json_dict.get("INFO"), "\n")
                    print("\n", json_dict.get("USER_LIST"), "\n")
                    print("\n", json_dict.get("MESSAGES"), "\n")
                    self.username = message
                    self.logged_in = True

            #If user is logged in
            else:
                message = yield from loop.run_in_executor(None, input, ">")
                if message == "quit":
                    loop.stop()
                    return
                if message[0] == "@":
                    #Send to an individual person
                    first_white_space = message.find(" ")
                    timestamp = calendar.timegm(time.gmtime())
                    tuple = ()
                    tuple = tuple +(self.username, message[0:first_white_space],
                                              timestamp, message[first_white_space:])
                    send_message = json.dumps({'MESSAGES' : [tuple]})
                    self.send_message(send_message)
                else:
                    timestamp = calendar.timegm(time.gmtime())
                    tuple = ()
                    tuple = tuple + (self.username, "ALL",
                                               timestamp, message)
                    send_message = json.dumps({'MESSAGES': [tuple]})
                    self.send_message(send_message)

                yield from asyncio.sleep(1.0)
                if json_dict.get("USERS_JOINED") is not None:
                    print("\n", json_dict.get("USERS_JOINED"), "\n")
                if json_dict.get("USERS_LEFT") is not None:
                    print("\n", json_dict.get("USERS_LEFT"), "\n")

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
