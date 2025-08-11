# simulation/simulator.py
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
