import random
import signal
import socket
import sys

# Constants used in the program.
DEFAULT_PORT = 8080
PASSWORDS_FILE_NAME = "passwords.txt"
SECRETS_FILE_NAME = "secrets.txt"

# Basic credentials of users (username, password, secret) are stored here
credentials = {}

# A dictionary to store cookie tokens for authorized users
tokens = {}


# Helper functions

# Printing.
def print_value(tag, message):
    print "Here is the", tag
    print "\"\"\""
    print message
    print "\"\"\""
    print


# Signal handler for graceful exit
def sigint_handler(sig, frame):
    print 'Finishing up by closing listening socket...'
    sock.close()
    sys.exit(0)


# Read a command line argument for the port where the server must run.
if len(sys.argv) > 1:
    port = int(sys.argv[1].strip())
    print "Using port {}".format(port)
else:
    port = DEFAULT_PORT
    print "Using default port {}".format(DEFAULT_PORT)

# Contents of pages we will serve.
# Login form
login_form = """
   <form action = "http://localhost:%d" method = "post">
   Name: <input type = "text" name = "username">  <br/>
   Password: <input type = "text" name = "password" /> <br/>
   <input type = "submit" value = "Submit" />
   </form>
""" % port

# Default: Login page.
login_page = "<h1>Please login</h1>" + login_form

# Error page for bad credentials
bad_creds_page = "<h1>Bad user/pass! Try again</h1>" + login_form

# Successful logout
logout_page = "<h1>Logged out successfully</h1>" + login_form

# A part of the page that will be displayed after successful
# login or the presentation of a valid cookie
success_page = """
   <h1>Welcome!</h1>
   <form action="http://localhost:%d" method = "post">
   <input type = "hidden" name = "password" value = "new" />
   <input type = "submit" value = "Click here to Change Password" />
   </form>
   <form action="http://localhost:%d" method = "post">
   <input type = "hidden" name = "action" value = "logout" />
   <input type = "submit" value = "Click here to logout" />
   </form>
   <br/><br/>
   <h1>Your secret data is here:</h1>
""" % (port, port)

new_password_page = """
   <form action="http://localhost:%d" method = "post">
   New Password: <input type = "text" name = "NewPassword" /> <br/>
   <input type = "submit" value = "Submit" />
</form>
""" % port

# Start a listening server socket on the port
sock = socket.socket()
sock.bind(('', port))
sock.listen(2)

# Register the signal handler
signal.signal(signal.SIGINT, sigint_handler)

# TODO: put your application logic here!

# Read login credentials for all the users
with open(PASSWORDS_FILE_NAME, "r") as passwords_file:
    for line in passwords_file:
        columns = line.strip().split()
        if len(columns) == 2:
            username, password = columns
            credentials[username] = {"password": password}

# Read secret data of all the users
with open(SECRETS_FILE_NAME, "r") as secrets_file:
    for line in secrets_file:
        columns = line.strip().split()
        if len(columns) == 2:
            username, secret = columns
            if username in credentials:
                credentials[username]["secret"] = secret
            else:
                credentials[username] = {"secret": secret}

# Loop to accept incoming HTTP connections and respond.
while True:
    client, addr = sock.accept()
    request = client.recv(1024)

    # Let's pick the headers and entity body apart
    header_body = request.split('\r\n\r\n')
    headers = header_body[0]
    body = '' if len(header_body) == 1 else header_body[1]
    print_value('headers', headers)
    print_value('entity body', body)

    # TODO: Put your application logic here!
    # Parse headers and body and perform various actions

    # Parse headers to extract the "Cookie"s
    cookies = {}
    for header in headers.split('\r\n'):
        if header.startswith('Cookie:'):
            # Loop through the cookies to find the "token" cookie.
            for cookie in header.split(';'):
                key_value = cookie.strip().split(':')[1].split('=')
                key = key_value[0].strip()
                value = key_value[1].strip() if len(key_value) > 1 else ''
                cookies[key] = value
    token = cookies["token"] if "token" in cookies else ''

    # Parse body to extract the request parameters and their values.
    request_parameters = {}
    if body:
        for pair in body.split('&'):
            key_value = pair.split('=')
            key = key_value[0].strip()
            value = key_value[1] if len(key_value) > 1 else ''
            request_parameters[key] = value

    # You need to set the variables:
    # (1) `html_content_to_send` => add the HTML content you'd
    # like to send to the client.
    # Right now, we just send the default login page.
    html_content_to_send = login_page

    # But other possibilities exist, including
    # html_content_to_send = success_page + <secret>
    # html_content_to_send = bad_creds_page
    # html_content_to_send = logout_page

    # (2) `headers_to_send` => add any additional headers
    # you'd like to send the client?
    # Right now, we don't send any extra headers.
    headers_to_send = ""

    if len(request_parameters) == 1:
        if token and (token in tokens):
            if ("password" in request_parameters) and (request_parameters["password"] == "new"):
                html_content_to_send = new_password_page

            elif "NewPassword" in request_parameters:
                username = tokens[token]
                credentials[username]["password"] = request_parameters["NewPassword"]
                html_content_to_send = success_page + credentials[username]["secret"]

            # Logout ... Extra credit
            elif ("action" in request_parameters) and (request_parameters["action"] == "logout"):
                html_content_to_send = logout_page
                del tokens[token]
                headers_to_send = "Set-Cookie: token=; expires=Thu, 01 Jan 1970 00:00:00 GMT\r\n"
        else:
            html_content_to_send = bad_creds_page

    else:
        if token and (token in tokens):
            username = tokens[token]
            password = credentials[username]["password"]
            html_content_to_send = success_page + credentials[username]["secret"]
        else:
            username = request_parameters["username"] if "username" in request_parameters else ""
            password = request_parameters["password"] if "password" in request_parameters else ""

            if not username and not password:
                html_content_to_send = login_page
            else:
                if username and password:
                    if username in credentials:
                        if credentials[username]["password"] == password:
                            # Create a new token.
                            new_token = str(random.getrandbits(64))

                            # Store the new token.
                            tokens[new_token] = username

                            html_content_to_send = success_page + credentials[username]["secret"]
                            headers_to_send = "Set-Cookie: token=" + new_token + "\r\n"
                        else:
                            html_content_to_send = bad_creds_page
                    else:
                        html_content_to_send = bad_creds_page
                else:
                    html_content_to_send = bad_creds_page

    # Construct and send the final response
    response = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    print_value('response', response)
    client.send(response)
    client.close()

    print "Served one request/connection!"
    print

# We will never actually get here.
# Close the listening socket
sock.close()
