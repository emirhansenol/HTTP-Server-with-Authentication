# HTTP Server with Authentication

------------

Implementation of an HTTP server in Python language that serves secret user data via either name-password or cookies from successful prior authentication.

This project demonstrates the use of the HTTP protocol to build a simple version of authentication mechanisms (username-password, and cookies) to render browser-readable data.

While the `server.py` is running, access to it via a web browser would display the following login page:

<img width="222" alt="image" src="https://user-images.githubusercontent.com/107651391/226140560-ddec4127-79b8-4dfd-90d1-06c9838ed350.png">

## Features

- Login
- Modify password
- Logout (Removes cookie stored for authenticated username)
