# MC Offline Login

This repository contains a login script that provides the possibility to offer Minecraft in offline mode in an environment with multiple PCs. However, the usernames, with which inventory, buildings, etc., are assigned in the offline mode, are secured by a username/password entry in a database.

## Features:

- Secure login with username and password to protect user data in offline Minecraft environments.
- Integration with a MySQL database for storing username and password information.
- Admin receives an auth code via Telegram during user registration, and the account is only activated after the admin enters the auth code. This prevents users from creating numerous accounts.
- Account information is linked to the storage of settings and additional Fabric mods, which are then automatically loaded from a server.
- Multiple Minecraft versions can be set up for user selection.

## System Requirements:

- All code is written for Debian-based Linux systems.

## Configuration Instructions:

### Step 1: Create MYSQL-Table:

To create the necessary table, import the create_table.sql file into your MySQL database.

### Step 2: Edit database.ini:

#### 2.1: MySQL Database Configuration
The script relies on a MySQL database. Configure the `database.ini` file with the following information:

```ini
[mysqlDB]
host = <MySQL_Hostname_or_IP>
db = <Database_Name>
user = <MySQL_Username>
pass = <MySQL_Password>
```

#### 2.2: Directory Settings
Specify the directory settings in the database.ini file:

```ini
[Mountdir]
dir = <Absolute_Path_to_Script_Folder>
home = <Absolute_Path_to_User_Home_Directory>
```

#### 2.3: Minecraft Versions
Under the [Versions] section of database.ini, specify the available Minecraft versions in the following format:

```ini
[Vanilla/Fabric][Your_Game_Name][Version, vanilla: for the latest, otherwise vanilla:version_number or fabric:version_number]
```

Example:

```ini
[Vanilla][MyAdventure][vanilla:1.19.2]
[Fabric][MyAdventure][fabric:1.19.2]
```

#### 2.4: Default Version
In the [Standard] section of database.ini, specify the default Minecraft version by entering the name of the game.

#### 2.5: Telegram Integration (Required)
Telegram integration is necessary for receiving login tokens. Fill in the [telegram] section of database.ini:

```ini
[telegram]
token = <Your_Telegram_Bot_Token>
id = <Your_Telegram_Chat_ID>
```

#### 2.6: Email Configuration (Optional - Password Recovery)
To enable password recovery via email, fill in the [email] section of database.ini with your email server details:

```ini
[email]
host = <SMTP_Server_Hostname>
port = <SMTP_Port>
user = <Your_Email_Username>
pass = <Your_Email_Password>
```

Important: Keep your database.ini file secure, as it contains sensitive information.


Usage:

    After configuring database.ini, users can use the script for secure offline Minecraft login with the specified settings and versions.
    Telegram integration allows users to receive login tokens via Telegram.
    Email can be used for password recovery if configured.

For any questions or assistance, please refer to the documentation or contact the project administrator.


### Step 3: Setting Up the Remote Server Folder and Folder Structure
To make the most of this tool's features, you'll need to set up a remote server folder and create the required folder structure. This folder will be mounted by the script as "mc_data." Here are the steps you need to follow:

#### 3.1. Create the Remote Server Folder:
Ensure that you have access to a remote server where you can store files. In most cases, this will be a server you can access via SSH.

#### 3.2. Install SSHFS:
To mount the remote server folder, you'll need SSHFS. If you haven't already installed it, you can do so using your package management system. For example, on a Debian-based system, you can install it with the following command:

```bash
sudo apt-get install sshfs
```

#### 3.3. Installing Python Libraries:
To ensure you have the required Python libraries, run the following command in your terminal:

```bash
pip install -r requirements.txt
```
This will install all the necessary libraries specified in the requirements.txt file.


#### 3.4. Understanding the Folder Structure (Automatically Created):
The script will automatically generate the necessary folder structure inside the "mc_data" directory. Here's an explanation of what each folder is used for:

    mods: Inside this folder, the script creates subfolders for each game version you want to install mods for. You can place compatible mods inside these version-specific folders.

    servers: You can use this folder to store a servers.dat file, which allows you to add dedicated Minecraft servers. These servers will then appear in the multiplayer server list within the Minecraft game.

    shaders: Within this folder, the script generates subfolders corresponding to different game versions. You can place shader files inside these version-specific folders. To use shaders, you'll only need to enable them in Minecraft; the script takes care of the rest.

    users: This folder is where individual user folders are created. Each user folder is named after the respective Minecraft username and contains maps and settings specific to that user.

The script streamlines the creation of this folder structure, so you don't need to manually set it up. Simply follow the previous steps to mount the remote server folder, and the script will handle the rest.


## ToDo:
These are reminders for me for future improvements to the code:

    Make Telegram integration optional.
    Editable Screen-Messages
    Allow the script to run without a remote save server.
