#!/bin/bash

echo "🔧 Fixing DOS Simulation Project Structure..."
echo "================================================"

# Create project directory structure
mkdir -p ddos_simulation/simulation
mkdir -p ddos_simulation/templates
mkdir -p ddos_simulation/static

cd ddos_simulation

# Copy the working simulator.py file
echo "📁 Setting up simulator.py..."
cat > simulation/simulator.py << 'EOF'
import threading, time, socket
import psutil

_state = {
    "running": False,
    "pps": 50,
    "attack_type": "flood",
    "target": "127.0.0.1",
    "port": 9999,
    "packet_size": 512,
    "threads": 1,
    "total_packets": 0,
    "last_tick_packets": 0,
    "udp_thread": None,
    "stop_event": None
}

def _send_udp_once(target, port, payload):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(payload, (target, port))
        sock.close()
        return True
    except Exception:
        return False

def _flood_loop(stop_event):
    while not stop_event.is_set():
        start = time.time()
        sent = 0
        payload = b"A" * int(_state["packet_size"])
        current_pps = int(_state["pps"])
        for _ in range(current_pps):
            if stop_event.is_set(): break
            _send_udp_once(_state["target"], _state["port"], payload)
            sent += 1
        _state["last_tick_packets"] = sent
        _state["total_packets"] += sent
        elapsed = time.time() - start
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

def _teardrop_loop(stop_event):
    while not stop_event.is_set():
        start = time.time()
        sent = 0
        payload_small = b"T" * max(64, int(_state["packet_size"]//4))
        bursts = max(1, int(_state["pps"]//10))
        per_burst = max(1, int(_state["pps"] / max(1, bursts)))
        for _ in range(bursts):
            if stop_event.is_set(): break
            for _ in range(per_burst):
                if stop_event.is_set(): break
                _send_udp_once(_state["target"], _state["port"], payload_small)
                sent += 1
            time.sleep(0.05)
        _state["last_tick_packets"] = sent
        _state["total_packets"] += sent
        elapsed = time.time() - start
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

def _blacknurse_loop(stop_event):
    counter = 0
    while not stop_event.is_set():
        start = time.time()
        sent = 0
        payload = b"B" * max(64, int(_state["packet_size"]//2))
        base = max(1, int(_state["pps"] * 0.6))
        for _ in range(base):
            if stop_event.is_set(): break
            _send_udp_once(_state["target"], _state["port"], payload)
            sent += 1
        counter += 1
        if counter % 5 == 0:
            spike = min(int(_state["pps"]*0.8), 200)
            for _ in range(spike):
                if stop_event.is_set(): break
                _send_udp_once(_state["target"], _state["port"], payload)
                sent += 1
        _state["last_tick_packets"] = sent
        _state["total_packets"] += sent
        elapsed = time.time() - start
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

# Public API
def start_safe_simulation(pps=50, attack_type="flood", target="127.0.0.1", port=9999, packet_size=512, threads=1):
    if _state["running"]:
        return False
    if target != "127.0.0.1":
        target = "127.0.0.1"
    _state.update({
        "running": True,
        "pps": int(pps),
        "attack_type": attack_type,
        "target": target,
        "port": int(port),
        "packet_size": int(packet_size),
        "threads": int(threads),
        "total_packets": 0,
        "last_tick_packets": 0
    })
    stop_event = threading.Event()
    _state["stop_event"] = stop_event
    if attack_type == "flood":
        t = threading.Thread(target=_flood_loop, args=(stop_event,), daemon=True)
    elif attack_type == "teardrop":
        t = threading.Thread(target=_teardrop_loop, args=(stop_event,), daemon=True)
    elif attack_type == "blacknurse":
        t = threading.Thread(target=_blacknurse_loop, args=(stop_event,), daemon=True)
    else:
        t = threading.Thread(target=_flood_loop, args=(stop_event,), daemon=True)
    _state["udp_thread"] = t
    t.start()
    return True

def stop_safe_simulation():
    if not _state["running"]:
        return False
    _state["running"] = False
    if _state["stop_event"]:
        _state["stop_event"].set()
    _state["udp_thread"] = None
    _state["stop_event"] = None
    _state["last_tick_packets"] = 0
    return True

def update_pps(new_pps):
    _state["pps"] = int(new_pps)
    return True

def get_status():
    mem = psutil.virtual_memory()
    return {
        "running": _state["running"],
        "pps": _state["pps"],
        "attack_type": _state["attack_type"],
        "target": _state["target"],
        "port": _state["port"],
        "packet_size": _state["packet_size"],
        "threads": _state["threads"],
        "last_tick_packets": _state["last_tick_packets"],
        "total_packets": _state["total_packets"],
        "cpu_percent": psutil.cpu_percent(interval=None),
        "ram_percent": mem.percent,
        "ram_used_mb": mem.used // (1024*1024),
        "ram_total_mb": mem.total // (1024*1024),
        "timestamp": int(time.time() * 1000),
    }
EOF

# Create config.py
echo "📁 Setting up config.py..."
cat > config.py << 'EOF'
# config.py
dst_ip = "127.0.0.1"
n_ips = 5
n_msg = 10
interface = "lo"
attack_type = "flood"
orig_type = "random"
threads = 2
packet_size = 512
pps = 50
EOF

# Create requirements.txt
echo "📁 Setting up requirements.txt..."
cat > requirements.txt << 'EOF'
Flask==2.3.3
psutil==5.9.5
EOF

# Create __init__.py files
touch simulation/__init__.py

# Create enhanced setup script
echo "📁 Setting up enhanced setup.sh..."
cat > setup.sh << 'EOF'
#!/bin/bash

echo "🚀 Setting up DOS Simulation Environment..."
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Remove old virtual environment
if [ -d "venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python packages..."
pip install Flask==2.3.3
pip install psutil==5.9.5

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "To run the DOS Attack Simulator:"
echo "1. source venv/bin/activate"
echo "2. python app.py"
echo ""
echo "Then open: http://localhost:5000"
echo ""
echo "🎯 Target will be localhost (127.0.0.1) for safe testing"
echo "⚠️  Remember to run 'python test_server.py' in another terminal to see received packets"
EOF

chmod +x setup.sh

# Create test server
echo "📁 Setting up test_server.py..."
cat > test_server.py << 'EOF'
#!/usr/bin/env python3
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
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.settimeout(1.0)
        
        print(f"🎯 UDP Test Server listening on {host}:{port}")
        print("📡 Waiting for DOS simulation packets...")
        print("⏹️  Press Ctrl+C to stop\n")
        
        while counter.running:
            try:
                data, addr = sock.recvfrom(4096)
                counter.increment()
            except socket.timeout:
                continue
            except Exception as e:
                if counter.running:
                    print(f"Error: {e}")
                break
    
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        try:
            sock.close()
        except:
            pass

def stats_reporter():
    while counter.running:
        time.sleep(1)
        if counter.running:
            print(f"[{time.strftime('%H:%M:%S')}] Total: {counter.total_packets:6d} packets | Rate: {counter.packets_per_second:4d} pps")

def signal_handler(sig, frame):
    print(f"\n\n🛑 Shutting down...")
    print(f"📊 Final Statistics:")
    print(f"📦 Total packets received: {counter.total_packets}")
    counter.stop()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    stats_thread = threading.Thread(target=stats_reporter, daemon=True)
    stats_thread.start()
    udp_server()
EOF

chmod +x test_server.py

echo ""
echo "✅ Project structure fixed successfully!"
echo ""
echo "📁 Directory structure:"
echo "├── ddos_simulation/"
echo "│   ├── app.py (updated with embedded HTML)"
echo "│   ├── config.py"
echo "│   ├── requirements.txt"
echo "│   ├── setup.sh"
echo "│   ├── test_server.py"
echo "│   └── simulation/"
echo "│       ├── __init__.py"
echo "│       └── simulator.py"
echo ""
echo "🚀 To run the application:"
echo "1. cd ddos_simulation"
echo "2. chmod +x setup.sh"
echo "3. ./setup.sh"
echo "4. source venv/bin/activate"
echo "5. python app.py"
echo ""
echo "In another terminal:"
echo "6. python test_server.py"
echo ""
echo "Then open: http://localhost:5000"
