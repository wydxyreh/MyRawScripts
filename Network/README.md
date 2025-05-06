Unreal TCP Network Client
========================

This is a simple TCP client for the Unreal platform, written in python using python sockets.

What is it for?
---------------

This is just a starter script for more complex networking applications.

How does it work?
-----------------

The package comes with a simple echo server, written in python.
The server runs on port 50000, it will echo back packets received and will close the connection when receiving a "quit" command.

Execute the server, uncomment socket related code in `ue_site.py` and run the default scene.

The program will send heart beat string to server continuously.
When received, the server will reply accordingly.

If a "quit" command is submitted, the server will close the connection, and further packet requests will return an exception (the socket has been closed)
