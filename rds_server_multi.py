#!/bin/python3
# Copyright Intelligent Compute LTD 2025
# SPDX-License-Identifier: GPL-3.0

import socket
import struct
import sys

# Default settings
HOST = '127.0.0.1'
MCAST_GRP = '224.0.0.251'  # Default multicast group
PORT = 5001
MCAST_TTL = 2

def main():
    # Parse command line arguments
    use_multicast = '--multicast' in sys.argv or '-m' in sys.argv
    
    if use_multicast:
        print("[Server] Multicast mode enabled")
        print(f"[Server] Note: RDS has limited multicast support, falling back to UDP")
        # Create UDP socket for multicast (RDS doesn't fully support multicast)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind to multicast group
        s.bind((MCAST_GRP, PORT))
        
        # Join multicast group
        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        bind_addr = MCAST_GRP
        print(f"[Server] UDP multicast socket bound to {MCAST_GRP}:{PORT}")
        print(f"[Server] Joined multicast group {MCAST_GRP}")
    else:
        # Create RDS socket for unicast
        s = socket.socket(socket.AF_RDS, socket.SOCK_SEQPACKET)
        bind_addr = HOST
        print(f"[Server] RDS unicast mode")
    
    try:
        if not use_multicast:
            # Bind to address for RDS
            s.bind((HOST, PORT))
            print(f"[Server] RDS socket bound to {HOST}:{PORT}")
            print(f"[Server] Listening for RDS datagrams...")
        else:
            print(f"[Server] Listening for UDP multicast datagrams...")
        
        while True:
            try:
                # Receive data with sender address
                data, addr = s.recvfrom(1024)
                
                if not data:
                    print("[Server] No data received.")
                    continue
                
                message = data.decode()
                if use_multicast:
                    print(f"[Server] Received multicast '{message}' from {addr}")
                else:
                    print(f"[Server] Received '{message}' from {addr}")
                
                if message.startswith("ping"):
                    # Extract stream identifier from the message for response
                    parts = message.split('-')
                    stream_id = parts[1] if len(parts) > 1 else "0"
                    reply = f"pong-{stream_id}"
                    
                    # Send reply back to the sender
                    if use_multicast:
                        # In multicast mode, reply via unicast to sender
                        s.sendto(reply.encode(), addr)
                        print(f"[Server] Sent unicast reply '{reply}' to {addr}")
                    else:
                        # RDS unicast mode
                        s.sendto(reply.encode(), addr)
                        print(f"[Server] Sent '{reply}' to {addr}")
                    
            except Exception as e:
                print(f"[Server] Error: {e}")
                break
                
    except Exception as e:
        print(f"[Server] Failed to bind or listen: {e}")
        if not use_multicast:
            print("[Server] Make sure RDS module is loaded: sudo modprobe rds")
            print("[Server] And check if RDS is supported on your system")
    finally:
        if use_multicast:
            # Leave multicast group
            try:
                s.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
            except:
                pass
        s.close()

if __name__ == "__main__":
    main()
