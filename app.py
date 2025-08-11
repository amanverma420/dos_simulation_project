#!/usr/bin/env python3
# app.py - Fixed DOS Simulation Web Interface
import sys, os, time, threading, random
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime

# Add simulation directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.join(BASE_DIR, "simulation")
if SIM_DIR not in sys.path:
    sys.path.insert(0, SIM_DIR)

# Import modules
try:
    import simulator
    import config
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Creating minimal config module...")
    # Create minimal config if missing
    with open(os.path.join(BASE_DIR, 'config.py'), 'w') as f:
        f.write('''# config.py
dst_ip = "127.0.0.1"
n_ips = 5
n_msg = 10
interface = "lo"
attack_type = "flood"
orig_type = "random"
threads = 2
packet_size = 512
pps = 50
''')
    import config

app = Flask(__name__)

# Enhanced stats tracking
class StatsTracker:
    def __init__(self):
        self.reset()
        self.attack_history = []
        self.max_history = 100
        
    def reset(self):
        self.start_time = None
        self.total_attacks = 0
        self.peak_pps = 0
        self.total_bandwidth = 0
        self.stress_events = []
        
    def log_attack_start(self, config):
        self.start_time = time.time()
        self.attack_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'start',
            'config': config,
            'duration': 0
        })
        if len(self.attack_history) > self.max_history:
            self.attack_history.pop(0)
            
    def log_attack_stop(self):
        if self.start_time:
            duration = time.time() - self.start_time
            if self.attack_history:
                self.attack_history[-1]['duration'] = duration
                self.attack_history[-1]['type'] = 'completed'
        self.start_time = None
        
    def update_stats(self, current_pps, packet_size):
        if current_pps > self.peak_pps:
            self.peak_pps = current_pps
        
        # Calculate bandwidth (approximate)
        bandwidth_mbps = (current_pps * packet_size * 8) / (1024 * 1024)  # Convert to Mbps
        self.total_bandwidth += bandwidth_mbps

stats_tracker = StatsTracker()

# Enhanced stats data with additional metrics
stats_data = {
    "last_update": 0,
    "network_latency": 0,
    "connection_success_rate": 100,
    "target_availability": 100,
    "attack_effectiveness": 0
}

def calculate_network_metrics(status):
    """Calculate additional network metrics for enhanced monitoring"""
    pps = status.get('last_tick_packets', 0)
    total_packets = status.get('total_packets', 0)
    
    # Simulate network latency (increases with load)
    base_latency = 1.0  # 1ms base
    load_factor = min(pps / 100, 5.0)  # Scale with PPS
    latency = base_latency + (load_factor * random.uniform(0.8, 1.2))
    
    # Simulate connection success rate (decreases under heavy load)
    if pps > 500:
        success_rate = max(60, 100 - (pps - 500) / 10)
    elif pps > 200:
        success_rate = max(80, 100 - (pps - 200) / 20)
    else:
        success_rate = 100
    
    # Add some random variation
    success_rate += random.uniform(-5, 5)
    success_rate = max(0, min(100, success_rate))
    
    # Simulate target availability
    if pps > 800:
        availability = max(30, 100 - (pps - 800) / 5)
    elif pps > 400:
        availability = max(70, 100 - (pps - 400) / 10)
    else:
        availability = 100
    
    availability += random.uniform(-3, 3)
    availability = max(0, min(100, availability))
    
    # Calculate attack effectiveness
    target_pps = status.get('pps', 50)
    if target_pps > 0:
        effectiveness = min(100, (pps / target_pps) * 100)
    else:
        effectiveness = 0
    
    return {
        'network_latency': round(latency, 2),
        'connection_success_rate': round(success_rate, 1),
        'target_availability': round(availability, 1),
        'attack_effectiveness': round(effectiveness, 1)
    }

def enhanced_update_stats():
    """Enhanced background thread to update stats with additional metrics"""
    while True:
        try:
            # Get base simulator status
            status = simulator.get_status()
            
            # Calculate additional network metrics
            network_metrics = calculate_network_metrics(status)
            
            # Update stats data
            stats_data.update(status)
            stats_data.update(network_metrics)
            stats_data["last_update"] = time.time()
            
            # Update peak PPS tracking
            current_pps = status.get('last_tick_packets', 0)
            packet_size = status.get('packet_size', 512)
            stats_tracker.update_stats(current_pps, packet_size)
            
        except Exception as e:
            print(f"❌ Error updating stats: {e}")
        time.sleep(1)

# HTML template embedded in Python (since templates folder might be missing)
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DOS Attack Simulation Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #0d1117;
            --secondary-color: #161b22;
            --accent-color: #238636;
            --danger-color: #da3633;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --border-color: #30363d;
            --neon-green: #39ff14;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'JetBrains Mono', monospace;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: var(--text-primary);
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header {
            text-align: center;
            padding: 30px;
            background: rgba(22, 27, 34, 0.8);
            border-radius: 15px;
            border: 1px solid var(--border-color);
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            color: var(--neon-green);
            text-shadow: 0 0 20px var(--neon-green);
        }
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(22, 27, 34, 0.8);
            border: 1px solid var(--border-color);
            border-radius: 15px;
            padding: 20px;
        }
        .card h3 {
            color: var(--accent-color);
            margin-bottom: 20px;
            font-size: 1.4em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: var(--text-primary);
            font-weight: 600;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            background: var(--secondary-color);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            color: var(--text-primary);
            font-family: inherit;
        }
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            text-transform: uppercase;
            font-family: inherit;
            margin: 5px;
        }
        .btn-start {
            background: linear-gradient(45deg, var(--accent-color), #2ea043);
            color: white;
        }
        .btn-stop {
            background: linear-gradient(45deg, var(--danger-color), #f85149);
            color: white;
        }
        .btn:hover { transform: translateY(-2px); transition: 0.3s; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        .stat-card {
            background: rgba(35, 134, 54, 0.1);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: var(--neon-green);
        }
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9em;
        }
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            padding: 10px;
            border-radius: 8px;
        }
        .status-running {
            background: rgba(35, 134, 54, 0.2);
            color: var(--accent-color);
        }
        .status-stopped {
            background: rgba(218, 54, 51, 0.2);
            color: var(--danger-color);
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .status-running .status-dot { background: var(--neon-green); }
        .status-stopped .status-dot { background: var(--danger-color); }
        @keyframes pulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        .attack-profiles {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }
        .profile-card {
            padding: 10px;
            background: var(--secondary-color);
            border: 2px solid var(--border-color);
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
            transition: 0.3s;
        }
        .profile-card:hover, .profile-card.active {
            border-color: var(--accent-color);
            background: rgba(35, 134, 54, 0.1);
        }
        .log-container {
            background: var(--primary-color);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            height: 200px;
            overflow-y: auto;
            padding: 15px;
            font-size: 12px;
            font-family: monospace;
        }
        .log-entry {
            margin-bottom: 5px;
            color: var(--text-secondary);
        }
        .log-success { color: var(--accent-color); }
        .log-error { color: var(--danger-color); }
        .log-info { color: var(--text-primary); }
        @media (max-width: 768px) {
            .dashboard { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-crosshairs"></i> DOS ATTACK SIMULATOR</h1>
            <p>Network Stress Testing Platform</p>
        </div>

        <div class="dashboard">
            <!-- Control Panel -->
            <div class="card">
                <h3><i class="fas fa-sliders-h"></i> Attack Configuration</h3>
                
                <div class="form-group">
                    <label>Packets Per Second (PPS)</label>
                    <input type="range" id="pps-slider" min="1" max="1000" value="50">
                    <span id="pps-value">50</span>
                </div>

                <div class="form-group">
                    <label>Target Port</label>
                    <input type="number" id="port" value="9999" min="1" max="65535">
                </div>

                <div class="form-group">
                    <label>Packet Size (bytes)</label>
                    <input type="range" id="packet-size-slider" min="64" max="1472" value="512">
                    <span id="packet-size-value">512</span>
                </div>

                <div class="form-group">
                    <label>Attack Type</label>
                    <div class="attack-profiles">
                        <div class="profile-card active" data-profile="flood">
                            <div>UDP Flood</div>
                        </div>
                        <div class="profile-card" data-profile="teardrop">
                            <div>Teardrop</div>
                        </div>
                        <div class="profile-card" data-profile="blacknurse">
                            <div>Black Nurse</div>
                        </div>
                    </div>
                </div>

                <div class="status-indicator status-stopped" id="status-indicator">
                    <div class="status-dot"></div>
                    <span id="status-text">Attack Stopped</span>
                </div>

                <div>
                    <button class="btn btn-start" onclick="startAttack()">
                        <i class="fas fa-rocket"></i> Launch Attack
                    </button>
                    <button class="btn btn-stop" onclick="stopAttack()">
                        <i class="fas fa-stop"></i> Stop Attack
                    </button>
                </div>
            </div>

            <!-- Live Statistics -->
            <div class="card">
                <h3><i class="fas fa-chart-line"></i> Live Statistics</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="current-pps">0</div>
                        <div class="stat-label">Current PPS</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="total-packets">0</div>
                        <div class="stat-label">Total Packets</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="cpu-usage">0%</div>
                        <div class="stat-label">CPU Usage</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="ram-usage">0%</div>
                        <div class="stat-label">RAM Usage</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="uptime">00:00</div>
                        <div class="stat-label">Duration</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="dashboard">
            <div class="card">
                <h3><i class="fas fa-chart-area"></i> Packet Flow</h3>
                <canvas id="packetChart" width="400" height="200"></canvas>
            </div>
            <div class="card">
                <h3><i class="fas fa-chart-pie"></i> System Resources</h3>
                <canvas id="resourceChart" width="400" height="200"></canvas>
            </div>
        </div>

        <!-- Activity Log -->
        <div class="card">
            <h3><i class="fas fa-terminal"></i> Activity Log</h3>
            <div class="log-container" id="log-content">
                <div class="log-entry log-info">[INFO] DOS Attack Simulator initialized</div>
                <div class="log-entry log-success">[SUCCESS] Backend connection established</div>
                <div class="log-entry log-info">[INFO] Target: 127.0.0.1:9999 (localhost)</div>
            </div>
        </div>
    </div>

    <script>
        let packetChart, resourceChart;
        let attackStartTime = null;
        let selectedAttackType = 'flood';

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            initializeSliders();
            initializeCharts();
            initializeAttackProfiles();
            startStatusUpdates();
        });

        // Initialize sliders
        function initializeSliders() {
            const ppsSlider = document.getElementById('pps-slider');
            const packetSizeSlider = document.getElementById('packet-size-slider');
            const ppsValue = document.getElementById('pps-value');
            const packetSizeValue = document.getElementById('packet-size-value');

            ppsSlider.addEventListener('input', function() {
                ppsValue.textContent = this.value;
            });

            packetSizeSlider.addEventListener('input', function() {
                packetSizeValue.textContent = this.value;
            });
        }

        // Initialize charts
        function initializeCharts() {
            // Packet flow chart
            const ctx1 = document.getElementById('packetChart').getContext('2d');
            packetChart = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: Array.from({length: 20}, (_, i) => i + 1),
                    datasets: [{
                        label: 'Packets/sec',
                        data: Array(20).fill(0),
                        borderColor: '#39ff14',
                        backgroundColor: 'rgba(57, 255, 20, 0.1)',
                        borderWidth: 2,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#f0f6fc' } } },
                    scales: {
                        x: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } },
                        y: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } }
                    }
                }
            });

            // Resource usage chart
            const ctx2 = document.getElementById('resourceChart').getContext('2d');
            resourceChart = new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: ['CPU', 'RAM', 'Network', 'Free'],
                    datasets: [{
                        data: [0, 0, 0, 100],
                        backgroundColor: ['#da3633', '#f85149', '#58a6ff', '#30363d']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#f0f6fc' } } }
                }
            });
        }

        // Initialize attack profiles
        function initializeAttackProfiles() {
            document.querySelectorAll('.profile-card').forEach(card => {
                card.addEventListener('click', function() {
                    document.querySelectorAll('.profile-card').forEach(c => c.classList.remove('active'));
                    this.classList.add('active');
                    selectedAttackType = this.dataset.profile;
                    addLog(`Selected attack type: ${selectedAttackType.toUpperCase()}`, 'info');
                });
            });
        }

        // Start attack
        async function startAttack() {
            const pps = document.getElementById('pps-slider').value;
            const port = document.getElementById('port').value;
            const packetSize = document.getElementById('packet-size-slider').value;

            const config = {
                pps: parseInt(pps),
                attack_type: selectedAttackType,
                port: parseInt(port),
                packet_size: parseInt(packetSize),
                threads: 1
            };

            try {
                addLog(`Initiating ${selectedAttackType.toUpperCase()} attack...`, 'info');
                
                const response = await fetch('/api/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });

                const result = await response.json();
                
                if (result.started) {
                    attackStartTime = Date.now();
                    updateAttackStatus(true);
                    addLog(result.message, 'success');
                } else {
                    addLog(result.message, 'error');
                }
            } catch (error) {
                addLog(`Connection error: ${error.message}`, 'error');
            }
        }

        // Stop attack
        async function stopAttack() {
            try {
                const response = await fetch('/api/stop', { method: 'POST' });
                const result = await response.json();
                
                attackStartTime = null;
                updateAttackStatus(false);
                addLog(result.message, 'success');
            } catch (error) {
                addLog(`Stop error: ${error.message}`, 'error');
            }
        }

        // Update attack status
        function updateAttackStatus(running) {
            const indicator = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');

            if (running) {
                indicator.className = 'status-indicator status-running';
                statusText.textContent = 'Attack Running';
            } else {
                indicator.className = 'status-indicator status-stopped';
                statusText.textContent = 'Attack Stopped';
            }
        }

        // Start status updates
        function startStatusUpdates() {
            setInterval(updateDashboard, 1000);
        }

        // Update dashboard
        async function updateDashboard() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();

                // Update stats
                document.getElementById('current-pps').textContent = data.last_tick_packets || 0;
                document.getElementById('total-packets').textContent = formatNumber(data.total_packets || 0);
                document.getElementById('cpu-usage').textContent = Math.round(data.cpu_percent || 0) + '%';
                document.getElementById('ram-usage').textContent = Math.round(data.ram_percent || 0) + '%';

                // Update uptime
                updateUptime();

                // Update charts
                if (packetChart) {
                    packetChart.data.datasets[0].data.shift();
                    packetChart.data.datasets[0].data.push(data.last_tick_packets || 0);
                    packetChart.update('none');
                }

                if (resourceChart) {
                    const cpu = data.cpu_percent || 0;
                    const ram = data.ram_percent || 0;
                    const network = Math.min(((data.last_tick_packets || 0) / 100) * 10, 30);
                    const free = Math.max(0, 100 - cpu - ram - network);
                    resourceChart.data.datasets[0].data = [cpu, ram, network, free];
                    resourceChart.update('none');
                }

            } catch (error) {
                console.error('Status update error:', error);
            }
        }

        // Update uptime
        function updateUptime() {
            if (attackStartTime) {
                const elapsed = Math.floor((Date.now() - attackStartTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                document.getElementById('uptime').textContent = 
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            } else {
                document.getElementById('uptime').textContent = '00:00';
            }
        }

        // Add log entry
        function addLog(message, level = 'info') {
            const logContent = document.getElementById('log-content');
            const timestamp = new Date().toLocaleTimeString();
            
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry log-${level}`;
            logEntry.textContent = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
            
            logContent.appendChild(logEntry);
            logContent.scrollTop = logContent.scrollHeight;

            // Keep only last 50 entries
            while (logContent.children.length > 50) {
                logContent.removeChild(logContent.firstChild);
            }
        }

        // Format large numbers
        function formatNumber(num) {
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toString();
        }
    </script>
</body>
</html>'''

# Start enhanced background stats updater
stats_thread = threading.Thread(target=enhanced_update_stats, daemon=True)
stats_thread.start()

@app.route("/")
def index():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/status")
def api_status():
    """Enhanced status endpoint with additional metrics"""
    enhanced_stats = dict(stats_data)
    
    # Add historical data
    enhanced_stats.update({
        'peak_pps': stats_tracker.peak_pps,
        'total_attacks': len(stats_tracker.attack_history),
        'uptime_seconds': int(time.time() - stats_tracker.start_time) if stats_tracker.start_time else 0
    })
    
    return jsonify(enhanced_stats)

@app.route("/api/start", methods=["POST"])
def api_start():
    try:
        data = request.json or {}
        pps = int(data.get("pps", getattr(config, 'pps', 50)))
        attack_type = data.get("attack_type", getattr(config, 'attack_type', 'flood'))
        target = data.get("target", getattr(config, 'dst_ip', '127.0.0.1'))
        port = int(data.get("port", 9999))
        packet_size = int(data.get("packet_size", getattr(config, 'packet_size', 512)))
        threads = int(data.get("threads", getattr(config, 'threads', 1)))
        
        ok = simulator.start_safe_simulation(
            pps=pps, 
            attack_type=attack_type, 
            target=target, 
            port=port, 
            packet_size=packet_size, 
            threads=threads
        )
        
        if ok:
            # Log attack start
            attack_config = {
                'pps': pps,
                'attack_type': attack_type,
                'target': target,
                'port': port,
                'packet_size': packet_size,
                'threads': threads
            }
            stats_tracker.log_attack_start(attack_config)
            
            message = f"✅ {attack_type.upper()} attack initiated successfully"
        else:
            message = "❌ Attack already running or failed to start"
            
        return jsonify({
            "started": ok, 
            "message": message,
            "attack_type": attack_type,
            "target_pps": pps
        })
        
    except Exception as e:
        return jsonify({
            "started": False, 
            "message": f"❌ Configuration error: {str(e)}"
        })

@app.route("/api/stop", methods=["POST"])
def api_stop():
    try:
        ok = simulator.stop_safe_simulation()
        
        if ok:
            stats_tracker.log_attack_stop()
            message = "🛑 Attack terminated successfully"
        else:
            message = "ℹ️ No active attack to stop"
            
        return jsonify({
            "stopped": ok, 
            "message": message
        })
        
    except Exception as e:
        return jsonify({
            "stopped": False, 
            "message": f"❌ Stop error: {str(e)}"
        })

@app.route("/api/set_pps", methods=["POST"])
def api_set_pps():
    try:
        data = request.json or {}
        pps = int(data.get("pps", 50))
        
        # Validate PPS range
        pps = max(1, min(1000, pps))
        
        simulator.update_pps(pps)
        return jsonify({
            "pps": pps, 
            "message": f"⚡ Attack intensity updated to {pps} PPS"
        })
        
    except Exception as e:
        return jsonify({
            "pps": 50, 
            "message": f"❌ Update error: {str(e)}"
        })

@app.route("/api/emergency_stop", methods=["POST"])
def api_emergency_stop():
    """Emergency stop with system reset"""
    try:
        # Force stop the attack
        ok = simulator.stop_safe_simulation()
        
        # Reset tracking
        stats_tracker.reset()
        
        return jsonify({
            "stopped": True,
            "message": "🚨 EMERGENCY STOP - All systems reset"
        })
        
    except Exception as e:
        return jsonify({
            "stopped": False,
            "message": f"❌ Emergency stop failed: {str(e)}"
        })

# Enhanced error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    print("🚀 Starting DOS Simulation Dashboard...")
    print("📊 Features: Real-time charts, network monitoring, attack profiles")
    print("🎯 Target: localhost (127.0.0.1) - Safe testing environment")
    print("🌐 Access at: http://localhost:5000")
    print("=" * 60)
    
    # Initialize stats tracker
    stats_tracker.reset()
    
    app.run(host="0.0.0.0", port=5000, debug=False)
