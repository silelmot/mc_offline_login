#!/usr/bin/python3

from tkinter import *
import mysql.connector
import hashlib
import configparser
import os
import subprocess
from tkinter import messagebox
import sys
import tkinter as tk
from pathlib import Path
import re
import requests
import random
import string
import shutil
import time
import smtplib, ssl
from threading import Thread
import socket
import argparse


# parsen Arguments
parser = argparse.ArgumentParser(description="Description of Script")
parser.add_argument("-debug", action="store_true", help="Debug-Modus")

args = parser.parse_args()

debug = 1 if args.debug else 0

version='2.0.6a'
print("Version:",version)
dir = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(dir + '/database.ini')

"""
Settings:
	(not in database.ini anymore because of passwords and credentials)

tried to have settings in database.ini - but everybody can read credentials , python can be compiled. save against noobs, 
have to find other solution, maybe first start setup-page with encrypted data and admin-password 

"""

#TelegramToken
TOKEN="bottoken"
chat_id="chatid"

#Email-Server-Settings
email_enabled = True
email_port = 465  
email_server = "example.example.net"
email_sender = "info@example.net"
email_password = "password"


#RemoteSaveServer
rss_enabled = True
rss_host = "minecraftdata@192.168.2.1"
rss_port = 22
rss_keyfile = "/home/minecraft/.ssh/mcdata"

#mysqlDB / if enabled
mysql_enabled = True
mysql_host = "192.168.2.1"
mysql_db = "minecraft"
mysql_user = "minecraft"
mysql_pass = "password"

mdir = config['Mountdir']['dir']
mcpath = Path("%s/mc_data" % mdir)

if rss_enabled:
    if not mcpath.is_mount():
        bashCommand = "sshfs -o allow_other,IdentityFile=%s,port=%s %s:data %s/mc_data/" % (rss_keyfile,rss_port,rss_host,mdir)
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        print("mounted")
    else:
        print("already mounted")
else:
    print("rss not enabled") 
    
resettry = 0;

standard = config['Standard']['standard']
mcvers = 'Standard'

vlist=[[],[],[],[]]

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
versions = config['Versions']['version'].split('\n')


connection = mysql.connector.connect(host = mysql_host,
                       database = mysql_db,
                       user = mysql_user,
                       password = mysql_pass)


window = Tk()
window.title("Minecraft Login Tool - V.%s" % version)
window.geometry('350x200')


window.iconphoto(window, PhotoImage(file=dir + "/mlt.png"))


for i in versions:
    
    v = re.findall(r'\[.*?\]', i)

    vlist[0].append(str(v[0]).replace('[','').replace(']','')) 
    vlist[1].append("%s %s" % ((str(v[0]).replace('[','').replace(']','')),v[1]))
    vlist[2].append(str(v[2]).replace('[','').replace(']',''))
    vlist[3].append(str(v[1]).replace('[','').replace(']',''))

vlist[0].append('Standard')
vlist[1].append('Standard')
vlist[2].append('release')
vlist[3].append('Vanilla')
clicked = StringVar()


if (standard in vlist[3]):
    vstand = (vlist[3].index(standard))
   
    stand = vlist[1][vstand]
   
    clicked.set( stand )
    mcvers = stand

else:
    clicked.set( 'Standard' )
    

def check(email):
        
        
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_mods(mcversion):
    print("getmods:")
    source_dir = os.path.join(mcpath, "mods", mcversion.lower())
    target_dir = os.path.join(os.path.expanduser("~"), ".minecraft", "mods", mcversion.lower(), "mods")

    if not os.path.isdir(source_dir):
        print("Der Mod-Unterordner existiert nicht!")
        return
        # create target folder if not exist
    os.makedirs(target_dir, exist_ok=True)

    # copy data (mods, configs)
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        target_item = os.path.join(target_dir, item)

        # test if data already there
        if not os.path.exists(target_item):
            try:
                if os.path.isdir(source_item):
                    shutil.copytree(source_item, target_item)
                else:
                    shutil.copy2(source_item, target_item)
                print(f"'{item}' wurde kopiert!")
            except Exception as e:
                print(f"Fehler beim Kopieren von '{item}': {e}")
   
def get_shaders(mcversion):
    source_dir = os.path.join(mcpath, "shaders", mcversion.lower())
    target_dir = os.path.join(os.path.expanduser("~"), ".minecraft", "mods", mcversion.lower(), "shaderpacks")

    # test if source folder exists
    if not os.path.isdir(source_dir):
        print("Der Shader-Unterordner existiert nicht!")
        return

    # create source folder if not
    os.makedirs(target_dir, exist_ok=True)

    # copy data
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        target_item = os.path.join(target_dir, item)

        # test if data already there
        if not os.path.exists(target_item):
            try:
                if os.path.isdir(source_item):
                    shutil.copytree(source_item, target_item)
                else:
                    shutil.copy2(source_item, target_item)
                print(f"'{item}' wurde kopiert!")
            except Exception as e:
                print(f"Fehler beim Kopieren von '{item}': {e}")


def get_servers(mcversion):
    source_dir = os.path.join(mcpath, "servers")
    target_dir = os.path.join(os.path.expanduser("~"), ".minecraft", "mods", mcversion.lower())

    # test if source folder exists
    if not os.path.isdir(source_dir):
        print("Der 'servers' Unterordner existiert nicht!")
        return
    if not os.path.isdir(target_dir):
        print("Der 'servers' Targetordner existiert nicht!")
        return        

    # copy data and subfolder
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        target_item = os.path.join(target_dir, item)

        if os.path.isdir(source_item):
            shutil.copytree(source_item, target_item)
        else:
            shutil.copy2(source_item, target_item)


def get_userdata(Name,game):
    max_attempts = 5
    failed_attempts = 0
    success = False

#if remot system is installed and enabled:
    if rss_enabled:    
       if os.path.islink("%s/%s/saves" % (os.path.expanduser("~/.minecraft/mods"),game.lower())):
           bashCommand = "rm %s/%s/saves" % (os.path.expanduser("~/.minecraft/mods"),game.lower())
       elif not os.path.exists("%s/%s/saves" % (os.path.expanduser("~/.minecraft/mods"),game.lower())):
           create_mcfolders(Name.lower(),game.lower())
           bashCommand = "echo "
       else:
           for save in os.listdir("%s/%s/saves/" % (os.path.expanduser("~/.minecraft/mods"),game.lower())):
              world_path = os.path.join(("%s/%s/saves/" % (os.path.expanduser("~/.minecraft/mods"),game.lower())),save)
              remote_world = os.path.join(("%s/users/%s/saves" % (mcpath,Name.lower())),save)
    	  	  
              if os.path.exists(remote_world):
                 current_date = time.strftime('%Y%m%d')
                 new_save_name = f"{save}_{current_date}"
                 remote_world = os.path.join(("%s/users/%s/saves" % (mcpath,Name.lower())), new_save_name)
                 print(f"Renaming world '{save}' to '{new_save_name}' on remote server.")
              shutil.move(world_path, remote_world)
              print(f"Moved world '{save}' to remote saves for user '{Name}'.")
	           
	
           bashCommand = "rm -r %s/%s/saves/" % (os.path.expanduser("~/.minecraft/mods"),game.lower())
       p = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
       out,err = p.communicate()	
       while failed_attempts < max_attempts and not success:
           bashCommand = "ln -sf %s/users/%s/saves %s/%s/" % (mcpath,Name.lower(),os.path.expanduser("~/.minecraft/mods/"),game.lower())
           try:
               subprocess.run(bashCommand.split(), check=True)
               success = True
           except subprocess.CalledProcessError:
               failed_attempts += 1
	
   # if symlink is successfull:
       if success:
           print("Symlink erfolgreich erstellt.")
       else:
           print(f"Symlink konnte nach {max_attempts} Versuchen nicht erstellt werden.")
           # message via telegram
           message = f"Symlink-Erstellung fehlgeschlagen nach {max_attempts} Versuchen."
           telegram = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
           requests.post(telegram).json()
	    
       bashCommand = "ln -sf %s/users/%s/options.txt %s/%s/" % (mcpath,Name.lower(),os.path.expanduser("~/.minecraft/mods/"),game.lower())
       p = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
       out,err = p.communicate()	   
    else:
       print("rss not enabled") 
	
def get_vers():
    bashCommand = "portablemc search"
    p = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    out,err = p.communicate()
    vvers=''
    snapfirst = 0
    a=0
    t=0
    for v in vlist[0]:
        a+=1
        i=2
        for e in out.split():         
            if e.decode("utf-8") == 'Release'.lower() and snapfirst == 0:
                snapfirst = 2
                relfirst = 1
            elif e.decode("utf-8") == 'Snapshot'.lower() and snapfirst != 2:
                snapfirst = 1
                relfirst = 0

            if e.decode("utf-8") == v.lower():
                
                
                vvers = out.split()[i].decode("utf-8")
                break
            i += 1
            t += 1
        vlist[1]
        
        if relfirst == 1:
            try:
                vlist[0].remove("Snapshot")
            except:
                print("no Snapshot in list")

def is_connected():
    try:
        socket.create_connection(("www.google.com",80))
        returnTrue
    except OSError:
        pass
    return False
    
def change_dropdown(*args):
    global mcvers
    mcvers = clicked.get()
    
    print("this:%s" % mcvers)

def extract_version(output):
    lines = output.splitlines()
    for line in lines:
        if not line.strip():
            continue
        # first not empty line here:
        match = re.search(r'(\d+(\.\d+)+)', line)
        if match:
            return match.group(1)
    return None
    

def clear():
    list = window.grid_slaves()
    for l in list:
        l.destroy()

def command(do,command):
    print(do)
    print(command)
    bashcommand = "%s %s" % (do,command)
    if do=="mkdir":
        if not os.path.exists(command):
             subprocess.Popen(bashcommand.split(),stdout=subprocess.PIPE)
             while not os.path.exists(command):
                  time.sleep(1)
    elif do=="touch":
        if not os.path.isfile(command):
             subprocess.Popen(bashcommand.split(),stdout=subprocess.PIPE)
    else:
        subprocess.Popen(bashcommand.split(),stdout=subprocess.PIPE)
    
def cl_login(arg, txt1, txt2, mcvers):
    if arg == 0:
        if txt1.get() == "":
            messagebox.showerror("Error", "Kein Name eingegeben!")
            return
        elif txt2.get() == "":
            messagebox.showerror("Error", "Kein Passwort eingegeben!")
            return

        else:
            Name = txt1.get()
            
            Passwort = (hashlib.md5(txt2.get().encode('utf-8')).hexdigest());

        sql_Query = """ SELECT * FROM users WHERE LOWER(Name) = LOWER('%s') """ % (Name);
        cursor = connection.cursor()
        cursor.execute(sql_Query)
        record_name = cursor.fetchone()

        sql_Query = """ SELECT * FROM users WHERE LOWER(Name) = LOWER('%s') AND Password = '%s' """ % (Name, Passwort);
        
        cursor.execute(sql_Query)
        record = cursor.fetchone()
        if record:
            Name = record[0]

        else:
            if not record_name:
                messagebox.showerror("Error", "Nutzername nicht gefunden!")
                return
            elif email_enabled:
                MsgBox = messagebox.askquestion("Error", "Passwort falsch! Willst du es zurücksetzen?")
                if MsgBox == 'yes':
                    sendemail(Name)
                return
            else:
                MsgBox = messagebox.showerror("Error", "Das Passwort ist falsch!")
                return
    else:
        Name = txt1     
  
    create_remotefolders(Name.lower(),mcvers)
    vnum = (vlist[1].index(mcvers))
    rungame = vlist[2][vnum]
    typeogame =  (vlist[0][vnum])
    gamename = vlist[3][vnum]
    cmd = "portablemc start --dry %s" % rungame  
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    output, errors = p.communicate()
    mcversion = extract_version(output)

    game = "%s_%s" % (typeogame,mcversion)#game.replace(":", "_")
    print("game is: %s" % game)
    print("version: %s"% mcversion) 
 
    if typeogame == "Fabric":
      get_mods(game)
      get_shaders(game)
    get_userdata(Name,game) 
    get_servers(game)
 
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    sql_query = """ UPDATE `users` SET `lastlogin` = '%s' WHERE `Name` = '%s' """ % (now,Name);

    cursor = connection.cursor()
    try:
      cursor.execute(sql_query)
    except mysql.connector.Error as e:
      print(e)
    connection.commit()
    if is_connected:
        cmd = "portablemc  --work-dir ~/.minecraft/mods/%s start %s -u %s" % (game.lower(),rungame,Name)
    clear()    
    
    textfield = Text(window,bg="black",fg="white",font = "Arial 7")
    textfield.pack(fill="both",expand=TRUE)
    t = Thread( target = lambda: terminal(cmd,textfield,debug))
    t.start()
    window.after(800, check_if_ready,t)
    window.mainloop()

    sys.exit(0)


def check_if_ready(thread):
    
    if thread.is_alive():
        
        window.after(800, check_if_ready, thread)
    else:        
        sys.exit(0)

def terminal(cmd, terminal, debug=0):

    if debug:
         p = subprocess.Popen(cmd, shell=True)
         p.communicate()
    else:
         p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE , bufsize=1, universal_newlines=True, shell = True)
         p.poll()

         while True:
             line = p.stdout.readline()
             terminal.insert(tk.END, line)
             terminal.see(tk.END)
             if not line and p.poll is not None: break
             if "Sound engine started" in line:
                sys.exit(0)
           
         while True:
             err = p.stderr.readline()
             terminal.insert(tk.END, err)
             terminal.see(tk.END)
             if not err: break

def create_mcfolders(Name,mcvers):
    vers_folder = os.path.join(os.path.expanduser("~/.minecraft/mods"),mcvers)
    print(f"vers_folder: '{vers_folder}'")
    
    if not os.path.exists(vers_folder):
        os.makedirs(vers_folder)

def create_remotefolders(Name,mcvers):
    user_folder = os.path.join(mcpath, "users", Name)

    # test if folder exists
    if not os.path.exists(user_folder):
         # if not create
         os.makedirs(user_folder)
         print(f"Ordner '{user_folder}' wurde erstellt.")
    else:
         print(f"Ordner '{user_folder}' existiert bereits.")
    # create "saves"-folder
    saves_folder = os.path.join(user_folder, "saves")
    if not os.path.exists(saves_folder):
        os.makedirs(saves_folder)
        print(f"Ordner '{saves_folder}' wurde erstellt.")
    else:
        print(f"Ordner '{saves_folder}' existiert bereits.")

    # create "options.txt"
    options_file_path = os.path.join(user_folder, "options.txt")
    if not os.path.exists(options_file_path):
        with open(options_file_path, "w") as f:
            f.write("")  # Leere Datei erstellen
        print(f"Datei '{options_file_path}' wurde erstellt.")
    else:
        print(f"Datei '{options_file_path}' existiert bereits.")
        
        
def sendemail(Name):
    email_code = id_generator()
    sql_Query = """ SELECT email FROM users WHERE LOWER(Name) = LOWER('%s') """ % Name;
    cursor = connection.cursor()
    cursor.execute(sql_Query)
    email = cursor.fetchone()
    message = """\
Subject: Jugendhaus - MC Passwort-Code: %s

Hey du Pflaume,
du hast also dein Passwort verschlampt?
Gut gemacht! (Aplaus)

Hier der Code, dass du ein neues vergeben kannst!

%s""" % (email_code,email_code)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(email_server, email_port, context=context) as server:
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email, message)
    resetcodeconfirm(Name,email_code)

def resetcodeconfirm(Name,email_code):
    global resettry
    resettry = resettry + 1
    if (resettry < 4):
        clear()
        lbl0 = Label(window,text="%s. Versuch von 3" % resettry)
        lbl0.grid(column=3, row=0)
        lbl1 = Label(window, text="Den Wiederherstellungs-Code")
        lbl2 = Label(window, text="aus deiner Email eingeben:")
        lbl1.grid(column=1, row=1, columnspan = 2)
        lbl2.grid(column=1, row=2, columnspan = 2)
        lbl2 = Label(window, text="Verification-Code:")
        lbl2.grid(column=1, row=4)
        txt1 = Entry(window,width=16)
        txt1.grid(column=2, row=4)
        txt1.focus()

        btn = Button(window, text="Enter", command= lambda: cl_pwreset(txt1,email_code,Name))
        btn.grid(column=2, row=6)
        window.bind('<Return>',lambda event: cl_pwreset(txt1,email_code,Name))
    else:
        messagebox.showerror("Error", "Code 3x falsch eingegeben!")
        resettry = 0;
        cl_loginpage()

def cl_pwreset(txt1,email_code,Name): 
    if not (type(txt1) == str):
        txt1 = txt1.get()
    
    if (email_code == txt1):
        clear()
        lbl0 = Label(window, text="Gib ein neues Passwort ein:")
        lbl0.grid(column=1, row=1, columnspan = 2)
        lbl1 = Label(window, text="Passwort:")
        lbl1.grid(column=1, row=3)
        lbl2 = Label(window, text="Passwort-Bestätigung:")
        lbl2.grid(column=1, row=4)
        txt2 = Entry(window,width=16)
        txt2.config(show="*");
        txt2.grid(column=2, row=3)
        txt3 = Entry(window,width=16)
        txt3.config(show="*");
        txt3.grid(column=2, row=4)
        txt2.focus()

        btn = Button(window, text="Enter", command= lambda: cl_pwsave(Name,txt1,email_code,txt2,txt3))
        btn.grid(column=2, row=6)
        window.bind('<Return>',lambda event: cl_pwsave(Name,txt1,email_code,txt2,txt3))
    else:
        resetcodeconfirm(Name,email_code)

def cl_pwsave(Name,txt1,email_code,txt2,txt3): 
    txt2 = txt2.get()
    txt3 = txt3.get()
    if (txt3 == txt2):
        password1 = txt3
        Passwort = (hashlib.md5(password1.encode('utf-8')).hexdigest());
        sql_insert_query = """ UPDATE `users` SET `Password` = %s WHERE `Name` = %s """ % (Passwort,Name);
        cursor = connection.cursor()
        try:
          cursor.execute(sql_insert_query)
          messagebox.showinfo("Erfolg","Das Passwort wurde geändert!")
        except mysql.connector.Error as e:
          print(e)
        connection.commit()

        cl_loginpage()
    else:
        messagebox.showerror("Error", "Die Emails stimmen nicht überein")
        cl_pwreset(txt1,email_code,Name)

def cl_register():
    clear()
    lbl1 = Label(window, text="Nickname: ")
    lbl1.grid(column=1, row=1)
    lbl2 = Label(window, text="Passwort: ")
    lbl2.grid(column=1, row=2)
    lbl3 = Label(window, text="Passwort bestätigen: ")
    lbl3.grid(column=1, row=3)
    lbl4 = Label(window, text="E-Mail: *optional")
    lbl4.grid(column=1, row=4)

    txt1 = Entry(window,width=16)
    txt1.grid(column=2, row=1)
    txt1.focus()
    txt2 = Entry(window,width=16)
    txt2.config(show="*");
    txt2.grid(column=2, row=2)
    txt3 = Entry(window,width=16)
    txt3.config(show="*");
    txt3.grid(column=2, row=3)
    txt4 = Entry(window,width=16)
    txt4.grid(column=2, row=4)

    btn = Button(window, text="Zurück", command= lambda: cl_loginpage())
    btn.grid(column=1, row=5)

    btn = Button(window, text="Enter", command= lambda: cl_regenter(txt1.get(), txt2.get(), txt3.get(), txt4.get()))
    btn.grid(column=2, row=5)
    window.bind('<Return>',lambda event: cl_regenter(txt1.get(), txt2.get(), txt3.get(), txt4.get()))
    window.grid_rowconfigure(4, minsize=20)

def cl_regenter(Name, password1, password2, Email=None):
    
    sql_Query = """ SELECT * FROM users WHERE LOWER(Name) = LOWER('%s') """ % Name;
    cursor = connection.cursor()
    cursor.execute(sql_Query)
    cursor_name = cursor.fetchone()

    if ' ' in Email:
        sql_Query = """ SELECT * FROM users WHERE LOWER(Email) = LOWER('%s') """ % Email;
        cursor = connection.cursor()
        cursor.execute(sql_Query)
        cursor_email = cursor.fetchone()

    if cursor_name:
        messagebox.showerror("Error", "Der Name existiert bereits!")   
    elif ' ' in Email and cursor_email:
        messagebox.showerror("Error", "Die Email wurde schon registriert!")
    elif ' ' in Name:
        messagebox.showerror("Error", "Der Name darf kein Leerzeichen enthalten!")
    elif ' ' in Email and not check(Email):
        messagebox.showerror("Error", "Keine gültige Email!")
    else:
        if password1 == password2:
            Passwort = (hashlib.md5(password1.encode('utf-8')).hexdigest());
            code = id_generator()
            message = "Nick: "+Name+"\nEmail: "+Email+"\nCode: "+code
            
            telegram = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
            requests.post(telegram).json()
            cl_confirmcode(Name,Passwort,Email,code)
        else:
            messagebox.showerror("Error", "Die Passwörter stimmen nicht überein!")
            
def cl_confirmcode(Name,Passwort,Email,code):
    clear()
    lbl0 = Label(window, text="Den Registrierungs-Code bekommst du bei den")
    lbl1 = Label(window, text="Mitarbeitern des Jugendhauses")
    lbl0.grid(column=1, row=1, columnspan = 2)
    lbl1.grid(column=1, row=2, columnspan = 2)
    lbl2 = Label(window, text="Verification-Code:")
    lbl2.grid(column=1, row=4)
    txt1 = Entry(window,width=16)
    txt1.grid(column=2, row=4)
    txt1.focus()

    btn = Button(window, text="Enter", command= lambda: cl_confirmed(Name, Passwort, Email, code, txt1))
    btn.grid(column=2, row=6)
    window.bind('<Return>',lambda event: cl_confirmed(Name, Passwort, Email, code, txt1))

def cl_confirmed(Name,Passwort,Email,code,code2):
    code2 = code2.get()    
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    if code == code2.upper():
        sql_insert_query = """ INSERT INTO `users`
                                     (`Name`, `Password`, `Set_`, `Email`, `lastlogin`) VALUES ('%s', '%s', 1, '%s', '%s')""" % (Name,Passwort,Email,now)

        cursor = connection.cursor()
        try:
          cursor.execute(sql_insert_query)
          messagebox.showinfo("Erfolg", "Der Account '" + Name + "' wurde angelegt!")  
        except mysql.connector.Error as e:
          print(e)
        connection.commit()                                 
    
        create_remotefolders(Name.lower(),mcvers) 
        cl_login(1, Name, Passwort, mcvers)
    else:
        messagebox.showerror("Error", "Der Code war falsch!")

def cl_loginpage():
    clear()
    lbl1 = Label(window, text="Nutzername: ")
    lbl1.grid(column=1, row=1)
    lbl2 = Label(window, text="Passwort: ")
    lbl2.grid(column=1, row=2)

    txt1 = Entry(window,width=16)
    txt1.grid(column=2, row=1)
    txt1.focus()
    txt2 = Entry(window,width=16)
    txt2.config(show="*");
    txt2.grid(column=2, row=2)
    
    drop = OptionMenu( window, clicked, *vlist[1])    
    drop.grid(column=1, row=5, columnspan = 2)
    clicked.trace('w', change_dropdown)

    btn = Button(window, text="Login", command= lambda: cl_login(0, txt1, txt2, mcvers))
    btn.grid(column=3, row=5)
    window.bind('<Return>',lambda event: cl_login(0, txt1, txt2, mcvers))

    btn = Button(window, text="Register", command=cl_register, font=('Arial', 8))
    btn.grid(column=3, row=8)


get_vers()



    
if config.has_option('Autologin','Version'):
    a_version = config['Autologin']['Version']
    a_name = config['Autologin']['Name']
    a_pw = config['Autologin']['Password']
    cl_login(1,a_name,a_pw,a_version)

filename = PhotoImage(file=dir + "/mineback.gif")
background_label = Label(window, image=filename)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

window.grid_rowconfigure(0, minsize=10)
window.grid_rowconfigure(4, minsize=20)
window.grid_rowconfigure(6, minsize=12)
window.grid_columnconfigure(0, minsize=20)

cl_loginpage()
window.mainloop()
