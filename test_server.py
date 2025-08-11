#!/usr/bin/env python3
# test_server.py - Simple UDP server to receive DOS simulation packets

import socket
import threading
import time
import signal
import sys

class PacketCounter:
    def __init__(self):
        self.total_packets = 0
        self.packets_per_second = 0
        self.last_second_packets = 0
        self.last_time = time.time()
        self.running = True
    
    def increment(self):
        self.total_packets += 1
        current_time = time.time()
        
        if current_time - self.last_time >= 1.0:
            self.packets_per_second = self.total_packets - self.last_second_packets
            self.last_second_packets = self.total_packets
            self.last_time = current_time
    
    def stop(self):
        self.running = False

counter = PacketCounter()

def udp_server(host='127.0.0.1', port=9999):
    """Simple UDP server that receives and counts packets"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.settimeout(1.0)  # 1 second timeout for clean shutdown
        
        print(f"UDP Test Server listening on {host}:{port}")
        print("Waiting for DOS simulation packets...")
        print("Press Ctrl+C to stop\n")
        
        while counter.running:
            try:
                data, addr = sock.recvfrom(4096)
                counter.increment()
            except socket.timeout:
                continue
            except Exception as e:
                if counter.running:
                    print(f"Error receiving packet: {e}")
                break
    
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        try:
            sock.close()
        except:
            pass

def stats_reporter():
    """Reports packet statistics every second"""
    while counter.running:
        time.sleep(1)
        if counter.running:
            print(f"[{time.strftime('%H:%M:%S')}] Total: {counter.total_packets:6d} packets | Rate: {counter.packets_per_second:4d} pps")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print(f"\n\nShutting down...")
    print(f"Final Statistics:")
    print(f"Total packets received: {counter.total_packets}")
    counter.stop()
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the stats reporter in a separate thread
    stats_thread = threading.Thread(target=stats_reporter, daemon=True)
    stats_thread.start()
    
    # Start the UDP server (blocking)
    udp_server()
