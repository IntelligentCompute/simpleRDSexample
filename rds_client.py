#!/bin/python3
# Copyright Intelligent Compute LTD 2025
# SPDX-License-Identifier: GPL-3.0

import socket
import time

HOST = '127.0.0.1'
PORT = 5001
NUM_STREAMS = 5  # Simulated streams using message identifiers

def main():
    # Create RDS socket
    s = socket.socket(socket.AF_RDS, socket.SOCK_SEQPACKET)
    
    try:
        # For RDS, we need to bind to a local address first
        # RDS requires both endpoints to have bound addresses
        s.bind(('127.0.0.1', 0))  # Bind to any available port
        print(f"[Client] Created and bound RDS socket")
        print(f"[Client] Simulating {NUM_STREAMS} streams using message identifiers")
        print(f"[Client] RDS provides reliable, ordered delivery like SCTP")
        
        stream = 0
        while True:
            try:
                # Create message with stream identifier
                msg = f"ping-{stream}"
                
                # Send datagram to server
                # RDS handles reliable delivery automatically
                s.sendto(msg.encode(), (HOST, PORT))
                print(f"[Client] Sent '{msg}' (simulated stream {stream})")
                
                # Set timeout for response
                s.settimeout(5.0)
                
                # Receive response
                # RDS guarantees message will arrive reliably and in order
                data, addr = s.recvfrom(1024)
                
                if not data:
                    print("[Client] No data received.")
                    break
                
                response = data.decode()
                print(f"[Client] Received '{response}' from {addr}")
                
                # Move to next simulated stream
                stream = (stream + 1) % NUM_STREAMS
                time.sleep(1)
                
            except socket.timeout:
                print("[Client] Timeout waiting for response")
                break
            except Exception as e:
                print(f"[Client] Error: {e}")
                break
                
    except Exception as e:
        print(f"[Client] Failed to create or use RDS socket: {e}")
        print("[Client] Make sure RDS module is loaded: sudo modprobe rds")
        print("[Client] And check if RDS is supported on your system")
    finally:
        s.close()

if __name__ == "__main__":
    main()
