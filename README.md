# SSH_Chat_Room
The purpose of this project is to design and use Socket Programming so that a communication
between clients and the server can be established and controlled through SSH and exchange messages between them.
The chat program uses the SSH (Secure Socket Shell) protocol in such a way that several users can chat with each other
as clients and through the server. Therefore, it is necessary to define at least one server and several clients.
By default, the SSH Chat Room server is be running and listening on a default IP and port.
The proposed scenario that is expressed in the following steps:

1-By default, the SSH Chat Room server is running and listening on a default IP and port.
(the local IP and port of system is used for that)
2- By calling the server, any user can send his/her bad words and passwords to the server.
3- Then on the server side, after the authentication of the user's authenticity is done correctly, SSH connection is established between each client and the server.
4- Now every user as a client can tell the server to which user he intends to send a message by entering his destination. After that, send a message to the server so that the server sends this message to the desired client.
5- Saving users' messages on the server, logging users' entry and exit from the sessions, and generally auditing users' activities should be done on the server side.
6- The required coding language can be one of Python, Java, C#, C/C++.

In this project, we use the paramiko library to create a chat room in such a way that 
there is a file called UserRecords.csv on the server side, 
where the username and password of the users are stored and the user authenticates themselves by using a username and password.

After creating each ssh channel, we set the channel name equal to the username and basically we assign a username to each of the channels. 

We also use two log files for logging. One of the files is server.log, where all the information and transactions 
related to the ssh protocol are stored (for this reason, it has a lower readability ) and the other is server_events.log, 
which stores the events that happened on the server side. (For example, transmitted messages,
who connected to the server or disconnected from it, and therefore is more readable.)
When a user connects to the server, we consider two threads for that user,
one of which is responsible for communicating with the user and the other implements the mailbox of that user,
so that if  the server broadcasts a message or another user sends a message, that message will be stored in the mailbox.

Users must enter the following command to access the server:

Login username password

Also, to send a message to someone, the following command must be entered:

msg username_of_receiver message

And to exit the server, you must enter the following command:

logout

Note: The server.py file must be executed first, and then client1.py and client2.py

Note: Python version 3.9 is used.
