from binascii import hexlify
import socket
import sys
import traceback
import paramiko
from paramiko.py3compat import b, u, decodebytes
import pandas as pd
import threading
import shlex

# setup logging
paramiko.util.log_to_file("server.log")

host_key = paramiko.RSAKey(filename="test_rsa.key")
# host_key = paramiko.DSSKey(filename='test_dss.key')

print("Read key: " + u(hexlify(host_key.get_fingerprint())))


class Server(paramiko.ServerInterface):
    # 'data' is the output of base64.b64encode(key)
    # (using the "user_rsa_key" files)
    data = (
        b"AAAAB3NzaC1yc2EAAAABIwAAAIEAyO4it3fHlmGZWJaGrfeHOVY7RWO3P9M7hp"
        b"fAu7jJ2d7eothvfeuoRFtJwhUmZDluRdFyhFY/hFAh76PJKGAusIqIQKlkJxMC"
        b"KDqIexkgHAfID/6mqvmnSJf0b5W8v5h2pI/stOSwTQ+pxVhwJ9ctYDhRSlF0iT"
        b"UWT10hcuO4Ks8="
    )
    good_pub_key = paramiko.RSAKey(data=decodebytes(data))

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        temp=user_records.query("user_id==@username and password==@password")
        if temp.empty:
            return paramiko.AUTH_FAILED
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_gssapi_with_mic(
        self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None
    ):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_keyex(
        self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None
    ):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def enable_auth_gssapi(self):
        return True

    def get_allowed_auths(self, username):
        return "gssapi-keyex,gssapi-with-mic,password,publickey"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        return True

def convert_arr_to_string(arr):
    temp=""
    for sring in arr:
        temp+=" "+sring
    return temp

def client_handler(chan):
    username=""
    channel_open=True
    f = chan.makefile("rU")
    while channel_open:
     command = f.readline().strip("\r\n")
     parsed_command = shlex.split(command)
     # print("name of channel is "+chan.get_name())
     # print(parsed_command)
     if username!="":
      if len(parsed_command) > 2 and parsed_command[0] == "msg":
          receiver_username=parsed_command[1]
          temp = user_records.query("user_id==@username")
          if not temp.empty and (receiver_username in messageBox.keys()):
              messageBox[receiver_username].append(f"[{username}]: "+convert_arr_to_string(parsed_command[2:len(parsed_command)]))
              print("message to "+receiver_username+" sent")
              # chan.send("message send\n")
              writer(command+"\n")

      elif len(parsed_command) > 0 and parsed_command[0] == "logout":
          print("loggin out "+username)
          del messageBox[chan.get_name()]
          broad_cast(f"[{username}] logged out")
          channel_open=False
          chan.close()
          writer("loggin out "+username + "\n")

     elif len(parsed_command) > 2 and parsed_command[0] == "login" and username=="":
         tempUserName=parsed_command[1]
         tempPassword=parsed_command[2]
         temp = user_records.query("user_id==@tempUserName and password==@tempPassword")
         if not temp.empty:
          username=tempUserName
          print("logging in "+username)
          chan.set_name(username)
          messageBox[username]=[]
          messageBoxHandler = threading.Thread(target=message_box_handler, args=(chan,))
          messageBoxHandler.start()
          broad_cast(f"[{username}] logged in")
          chan.send("\r\n\r\nWelcome!\r\n\r\n")
          writer(command + "\n")


def message_box_handler(chan):
      while chan.get_name() in messageBox.keys() :
          if len(messageBox[chan.get_name()])!=0:
              chan.send(messageBox[chan.get_name()].pop(0)+"\n")

def channel_maker(client):
    chan=None
    try:
        t = paramiko.Transport(client, gss_kex=DoGSSAPIKeyExchange)
        t.set_gss_host(socket.getfqdn(""))
        try:
            t.load_server_moduli()
        except:
            print("(Failed to load moduli -- gex will be unsupported.)")
            raise
        t.add_server_key(host_key)
        server = Server()
        try:
            t.start_server(server=server)
        except paramiko.SSHException:
            print("*** SSH negotiation failed.")

        # wait for auth
        chan = t.accept(20)
        if chan is None:
            print("*** No channel.")
        print("Authenticated!")

        server.event.wait(10)
        if not server.event.is_set():
            print("*** Client never asked for a shell.")
        return chan
    except Exception as e:
        print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
        traceback.print_exc()
        try:
            t.close()
        except:
            pass


def broad_cast(message):
 for key in messageBox.keys():
  messageBox[key].append(message)

def writer(message):
    server_events_log = open("server_events.log", "a")
    server_events_log.write(message)
    server_events_log.close()

DoGSSAPIKeyExchange = True
user_records=pd.read_csv("UserRecords.csv")
loggedInUsers=set()
messageBox=dict()
# now connect
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 22))
except Exception as e:
    print("*** Bind failed: " + str(e))
    traceback.print_exc()
    sys.exit(1)

while True:
 try:
     sock.listen(100)
     print("Listening for connection ...")
     client, addr = sock.accept()
 except Exception as e:
     print("*** Listen/accept failed: " + str(e))
     traceback.print_exc()


 print("Got a connection!")
 chan=channel_maker(client)
 clientHandler = threading.Thread(target=client_handler, args=(chan,))
 clientHandler.start()

