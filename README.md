# Computational Thinking Assignment 2 Role-Based Notification System

This is a simple client-server notification system built using Python.
We wanted to apply the TCP socket programming concepts learned from Data Communications class.
The server manages user logins, roles, and inactivity timeouts.  
Clients can log in, receive and view automatic messages based on their role

---

## Features

- User authentication (admin, editor, viewer)
- Checks for user subscription (user must be subscribed to recieve and view notifications)
- Automatic role-based notifications sent to client inboxes
- Users messages are cleared after viewing
- Inactivity timeout auto-logout
- Simple text-based menu
- Multi-client support using threads

--- 
## How to Run

### 1. Start the Server

python server.py

### 2. Start the Client

pyhton client.py
