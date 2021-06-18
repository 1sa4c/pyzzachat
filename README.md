# pyzzachat

Python + Pizza + Bored network student + free time = Pyzzachat!

Pyzzachat is an easy to setup, multi-platform, client-server, terminal based chatting software using python and sockets.
Users can register their name on the server with passwords during an initial "handshake process".
Messages are sent with headers using the format [X-x]. Headers and their usage are explained in the `codes.txt` file.
The lenght of a message is sent before it to better manage the resources and separate messages from one another.

## How to use

Clone the repo to your machine and setup the database:

`python3 server/database/setup.py`

And run the server:

`python3 server/main.py`

Then, run the client on each user's machine:

`python3 client/main.py`

The client will ask for the server's IP address and port. The defaults are `127.0.0.1` (localhost) and `7777`, but this can be changed on the code.

After the connection, follow the instructions provided to register you user, or login using your name and password (if the server stops, users are not saved).

That's it! To disconnect from the server just type `/quit`.
