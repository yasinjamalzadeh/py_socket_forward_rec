# This script forwards a number of configured local ports
# to local or remote socket servers.
#
# Configuration:
# Add to the config file pyrec.config lines with
# contents as follows:
#   <local incoming port> <dest hostname> <dest port>
#
# Start the application at command line with 'python pyrec.py'
# and stop the application by keying in <ctrl-c>.
#
#

import socket
import sys
import _thread
import time
import base64
import struct

def main(setup,  args):
    # if args
    if (len(args) > 0):
        for settings in parse_args(args):
            _thread.start_new_thread(server, settings)
    else:
        # read settings for port forwarding
        for settings in parse(setup):
            _thread.start_new_thread(server, settings)
    _thread.start_new_thread(heartbeat, ())
    while True:
       time.sleep(60)

def heartbeat():
    while True:
        print("Heartbeat...")
        time.sleep(10)

def parse(setup):
    settings = list()
    for line in file(setup):
        # skip comment line
        if line.startswith('#'):
            continue

        parts = line.split()
        settings.append((int(parts[0]), parts[1], int(parts[2])))
    return settings

def parse_args(args):
    settings = list()
    for line in args:
        parts = line.split(":")
        settings.append((int(parts[0]), parts[1], int(parts[2])))
    return settings

def server(*settings):
    try:
        dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        dock_socket.bind(('', settings[0]))
        dock_socket.listen()
        while True:
            client_socket = dock_socket.accept()[0]
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((settings[1], settings[2]))
            _thread.start_new_thread(forward, (client_socket, server_socket))
            _thread.start_new_thread(forward, (server_socket, client_socket))
    finally:
        _thread.start_new_thread(server, settings)

def forward(source, destination):
    source.settimeout(10)
    destination.settimeout(10)

    try:
        while True:
            try:
                string = source.recv(1024)
                if not string:
                    break
                destination.sendall(string)
            except (ConnectionResetError, BrokenPipeError) as e:
                print(f"Socket error: {e}")
                break
            except OSError as e:
                if e.errno == 9:
                    print("[!] Bad file descriptor. Closing thread.")
                    return 
                else:
                    print(f"OSError: {e}")
                    break
            except socket.timeout:
                print("Socket timeout")
                break
    finally:
        try:
            source.shutdown(socket.SHUT_RD)
        except Exception:
            pass
        try:
            destination.shutdown(socket.SHUT_WR)
        except Exception:
            pass
        source.close()
        destination.close()


if __name__ == '__main__':
    main('pyrec.config', sys.argv[1:])
