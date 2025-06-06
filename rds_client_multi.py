#!/bin/python3
# Copyright Intelligent Compute LTD 2025
# SPDX-License-Identifier: GPL-3.0

import socket
import struct
import time
import sys

# Default settings
HOST = '127.0.0.1'
MCAST_GRP = '224.0.0.251'  # Default multicast group
PORT = 5001
NUM_STREAMS = 5  # Simulated streams using message identifiers
MCAST_TTL = 2

def main():
    # Parse command line arguments
    use_multicast = '--multicast' in sys.argv or '-m' in sys.argv
    
    if use_multicast:
        print("[Client] Multicast mode enabled")
        print(f"[Client] Note: RDS has limited multicast support, using UDP for multicast")
        # Create UDP socket for multicast
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Set multicast TTL
        ttl = struct.pack('b', MCAST_TTL)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        
        # Bind to any local address for receiving replies
        s.bind(('', 0))
        
        target_addr = MCAST_GRP
        print(f"[Client] UDP multicast client, sending to {MCAST_GRP}:{PORT}")
    else:
        # Create RDS socket for unicast
        s = socket.socket(socket.AF_RDS, socket.SOCK_SEQPACKET)
        target_addr = HOST
        print(f"[Client] RDS unicast mode")
    
    try:
        if not use_multicast:
            # For RDS, we need to bind to a local address first
            # RDS requires both endpoints to have bound addresses
            s.bind(('127.0.0.1', 0))  # Bind to any available port
            print(f"[Client] Created and bound RDS socket")
        
        print(f"[Client] Simulating {NUM_STREAMS} streams using message identifiers")
        if use_multicast:
            print(f"[Client] UDP multicast provides best-effort delivery")
        else:
            print(f"[Client] RDS provides reliable, ordered delivery like SCTP")
        
        stream = 0
        while True:
            try:
                # Create message with stream identifier
                msg = f"ping-{stream}"
                
                # Send datagram
                if use_multicast:
                    s.sendto(msg.encode(), (MCAST_GRP, PORT))
                    print(f"[Client] Sent multicast '{msg}' (simulated stream {stream})")
                else:
                    s.sendto(msg.encode(), (HOST, PORT))
                    print(f"[Client] Sent '{msg}' (simulated stream {stream})")
                
                # Set timeout for response
                s.settimeout(5.0)
                
                # Receive response
                data, addr = s.recvfrom(1024)
                
                if not data:
                    print("[Client] No data received.")
                    break
                
                response = data.decode()
                if use_multicast:
                    print(f"[Client] Received unicast reply '{response}' from {addr}")
                else:
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
        print(f"[Client] Failed to create or use socket: {e}")
        if not use_multicast:
            print("[Client] Make sure RDS module is loaded: sudo modprobe rds")
            print("[Client] And check if RDS is supported on your system")
    finally:
        s.close()

if __name__ == "__main__":
    main()
