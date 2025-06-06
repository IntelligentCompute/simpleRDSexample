#!/bin/python3
# Copyright Intelligent Compute LTD 2025
# SPDX-License-Identifier: GPL-3.0

import socket

HOST = '127.0.0.1'
PORT = 5001

def main():
    # Create RDS socket - note: RDS uses SOCK_SEQPACKET for reliable ordered delivery
    s = socket.socket(socket.AF_RDS, socket.SOCK_SEQPACKET)
    
    try:
        # Bind to address
        s.bind((HOST, PORT))
        print(f"[Server] RDS socket bound to {HOST}:{PORT}")
        print(f"[Server] Listening for RDS datagrams...")
        
        while True:
            try:
                # RDS recv - gets data with sender address
                # RDS preserves message boundaries and provides reliable delivery
                data, addr = s.recvfrom(1024)
                
                if not data:
                    print("[Server] No data received.")
                    continue
                
                message = data.decode()
                print(f"[Server] Received '{message}' from {addr}")
                
                if message.startswith("ping"):
                    # Extract stream identifier from the message for response
                    parts = message.split('-')
                    stream_id = parts[1] if len(parts) > 1 else "0"
                    reply = f"pong-{stream_id}"
                    
                    # Send reply back to the sender
                    # RDS guarantees reliable delivery to the destination
                    s.sendto(reply.encode(), addr)
                    print(f"[Server] Sent '{reply}' to {addr}")
                    
            except Exception as e:
                print(f"[Server] Error: {e}")
                break
                
    except Exception as e:
        print(f"[Server] Failed to bind or listen: {e}")
        print("[Server] Make sure RDS module is loaded: sudo modprobe rds")
        print("[Server] And check if RDS is supported on your system")
    finally:
        s.close()

if __name__ == "__main__":
    main()
