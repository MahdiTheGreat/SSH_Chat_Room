import os
import socket
import sys
import traceback
from paramiko.py3compat import input
import interactive
import paramiko
import shlex


def manual_auth(username, password):
    # pw = getpass.getpass("Password for %s@%s: " % (username, hostname))
    print(username + ":" + password + "\n")
    t.auth_password(username, password)


# setup logging
paramiko.util.log_to_file("client1.log")

hostname = "127.0.0.1"
port = 22
# now connect
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port))
except Exception as e:
    print("*** Connect failed: " + str(e))
    traceback.print_exc()
    sys.exit(1)

try:
    t = paramiko.Transport(sock)
    try:
        t.start_client()
    except paramiko.SSHException:
        print("*** SSH negotiation failed.")
        sys.exit(1)
    try:
        keys = paramiko.util.load_host_keys(
            os.path.expanduser("~/.ssh/known_hosts")
        )
    except IOError:
        try:
            keys = paramiko.util.load_host_keys(
                os.path.expanduser("~/ssh/known_hosts")
            )
        except IOError:
            print("*** Unable to open host keys file")
    # check server's host key -- this is important.

    key = t.get_remote_server_key()
    loggedOn = False
    while not loggedOn:
        command = input("login please\n")
        parsed_command = shlex.split(command)
        if len(parsed_command) > 0 and parsed_command[0] == "login":
            username = parsed_command[1]
            password = parsed_command[2]
            manual_auth(username, password)
            if not t.is_authenticated():
                print("*** Authentication failed. :(")
            else:
                loggedOn = True
    print("opened channel")
    chan = t.open_session()
    chan.get_pty()
    chan.invoke_shell()
    chan.send(command + "\n")
    print("*** Here we go!\n")
    while True:
        interactive.interactive_shell(chan)
    chan.close()
    t.close()

except Exception as e:
    print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
    traceback.print_exc()
    try:
        t.close()
    except:
        pass
    sys.exit(1)