all code is written for debian-based linux systems
# MC Offline Login

This repository contains a login script that provides the possibility to offer Minecraft in offline mode in an environment with multiple PCs. However, the usernames, with which inventory, buildings, etc., are assigned in the offline mode, are secured by a username/password entry in a database.

## Features:

- Secure login with username and password to protect user data in offline Minecraft environments.
- Integration with a MySQL database for storing username and password information.
- Admin receives an auth code via Telegram during user registration, and the account is only activated after the admin enters the auth code. This prevents users from creating numerous accounts.
- Account information is linked to the storage of settings and additional Fabric mods, which are then automatically loaded from a server.
- Multiple Minecraft versions can be set up for user selection.
