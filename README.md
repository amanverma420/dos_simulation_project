# 🚀 DOS Attack Simulator

**Advanced Network Stress Testing & Security Analysis Platform**

A professional-grade DoS (Denial of Service) attack simulation tool designed for cybersecurity education, network stress testing, and security research purposes. This simulator provides a safe, controlled environment for understanding network vulnerabilities and testing system resilience.

## ⚠️ IMPORTANT DISCLAIMER

**This tool is designed exclusively for educational and authorized testing purposes. Only use this software on networks and systems you own or have explicit permission to test. Unauthorized use of this software against networks or systems is illegal and may result in severe legal consequences.**
## 🌟 Features

### 🎯 Attack Types
- **UDP Flood**: High-volume packet flooding for bandwidth saturation testing
- **Teardrop**: Fragmented packet attacks to test packet reassembly vulnerabilities  
- **Black Nurse**: ICMP-based DoS simulation with variable intensity patterns

### 📊 Advanced Dashboard
- **Real-time Statistics**: Live packet counts, PPS rates, system resource monitoring
- **Interactive Charts**: Packet flow analysis and resource usage visualization
- **Network Health Monitoring**: Stress levels, responsiveness metrics, packet loss tracking
- **Activity Logging**: Comprehensive attack logging with timestamp tracking

### ⚙️ Configurable Parameters
- Packets Per Second (1-1000 PPS)
- Custom packet sizes (64-1472 bytes)
- Target port configuration
- Multi-threading support
- Real-time parameter adjustment during attacks

## 📸 Screenshots & Videos

See the `media/` folder for:
- Screenshots of the dashboard interface
- Demo videos showing different attack types
- System performance monitoring examples


### 🔒 Safety Features
- **Localhost Only**: All attacks are restricted to 127.0.0.1 for safe testing
- **Emergency Stop**: Immediate attack termination with system reset
- **Resource Monitoring**: Built-in CPU and RAM usage tracking
- **Controlled Environment**: No external network access

## 🛠️ Installation

### Prerequisites
- Python 3.7+
- Linux/Unix environment (tested on Kali Linux)
- Virtual environment support

### Quick Setup

1. **Clone/Download the project**
   ```bash
   mkdir ~/Desktop/ddos_simulation
   cd ~/Desktop/ddos_simulation
   ```

2. **Copy all project files to the directory**
   ```
   ddos_simulation/
   ├── app.py
   ├── config.py  
   ├── requirements.txt
   ├── setup.sh
   ├── test_server.py
   ├── simulation/
   │   ├── __init__.py
   │   └── simulator.py
   └── media/
       ├── screenshots/
       └── videos/
   ```

3. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

### Manual Installation
If the setup script fails:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install Flask==2.3.3 psutil==5.9.5
```

## 🚀 Usage

### Starting the Application

1. **Start the main application**
   ```bash
   cd ~/Desktop/ddos_simulation
   source venv/bin/activate
   python app.py
   ```

2. **Start the test server** (in another terminal)
   ```bash
   cd ~/Desktop/ddos_simulation
   source venv/bin/activate
   python test_server.py
   ```

3. **Access the web interface**
   Open your browser to: `http://localhost:5000`

### Basic Workflow

1. **Configure Attack Parameters**
   - Set desired PPS (Packets Per Second)
   - Choose packet size
   - Select attack type (UDP Flood, Teardrop, Black Nurse)
   - Configure target port (default: 9999)

2. **Monitor Target Server**
   - Run `test_server.py` to see incoming packets
   - Monitor real-time packet reception rates
   - Observe system impact

3. **Launch Attack**
   - Click "Launch Attack" in the web interface
   - Monitor live statistics and charts
   - Adjust parameters in real-time if needed

4. **Analyze Results**
   - Review packet flow charts
   - Check system resource usage
   - Examine activity logs

## 📋 Project Structure

```
ddos_simulation/
├── app.py                 # Main Flask web application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── setup.sh             # Automated setup script
├── test_server.py       # UDP test server for receiving packets
├── README.md           # This documentation
├── simulation/
│   ├── __init__.py     # Python package init
│   └── simulator.py   # Core attack simulation engine
└── media/
    ├── screenshots/    # Dashboard screenshots
    └── videos/        # Demo videos
```

## 🔧 Configuration Options

### config.py Settings
```python
dst_ip = "127.0.0.1"      # Target IP (locked to localhost)
n_ips = 5                 # Number of source IPs (simulation)
n_msg = 10               # Messages per burst
interface = "lo"         # Network interface
attack_type = "flood"    # Default attack type
packet_size = 512        # Default packet size (bytes)
pps = 50                # Default packets per second
threads = 2             # Number of threads
```

### Runtime Parameters
- **PPS Range**: 1-1000 packets per second
- **Packet Size**: 64-1472 bytes
- **Port Range**: 1-65535
- **Thread Count**: 1-10 threads

## 📊 Monitoring & Analytics

### Real-time Metrics
- **Current PPS**: Live packet transmission rate
- **Total Packets**: Cumulative packet count
- **CPU Usage**: System processor utilization
- **RAM Usage**: Memory consumption
- **Bandwidth Estimation**: Network throughput calculation
- **Attack Duration**: Elapsed time tracking

### Network Health Indicators
- **Stress Level**: Network load assessment
- **Target Responsiveness**: Server response simulation
- **Packet Loss Rate**: Simulated packet drop percentage

## 🔒 Security & Safety

### Built-in Protections
- **Localhost Restriction**: Cannot target external IPs
- **Rate Limiting**: Maximum PPS constraints
- **Resource Monitoring**: Prevents system overload
- **Emergency Stops**: Multiple termination methods

### Ethical Use Guidelines
1. **Only test your own systems**
2. **Obtain explicit permission** for any network testing
3. **Use in isolated environments** when possible
4. **Document all testing activities**
5. **Follow local laws and regulations**

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Kill processes using port 5000
sudo lsof -ti:5000 | xargs sudo kill -9
```

**Permission Denied**
```bash
# Make scripts executable
chmod +x setup.sh test_server.py
```

**Module Import Errors**
```bash
# Reinstall dependencies
pip uninstall Flask psutil
pip install Flask==2.3.3 psutil==5.9.5
```

**Virtual Environment Issues**
```bash
# Remove and recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Performance Optimization
- Use **lower PPS rates** for longer tests
- Monitor **system resources** during high-intensity attacks
- **Limit concurrent threads** to prevent system overload
- **Close unnecessary applications** for better performance

## 🤝 Contributing

This project is designed for educational purposes. If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Test thoroughly in safe environments
4. Submit pull requests with detailed descriptions
5. Follow ethical hacking guidelines

## 📝 License & Legal

**Educational Use Only**: This software is provided for educational and research purposes only. Users are responsible for complying with all applicable laws and regulations.

**No Warranty**: This software is provided "as-is" without any warranty. Use at your own risk.

**Liability**: The authors are not responsible for any misuse of this software or any damages caused by its use.

## 📞 Support

For technical support or questions:
- Review this README thoroughly
- Check the troubleshooting section
- Test in isolated environments first
- Ensure all dependencies are correctly installed

## 🔮 Future Enhancements

- [ ] Additional attack vectors (SYN flood, Slowloris)
- [ ] Advanced payload customization
- [ ] Network topology simulation
- [ ] Enhanced reporting and analytics
- [ ] Docker containerization
- [ ] API documentation
- [ ] Integration with network monitoring tools

---

**Remember: Use this tool responsibly and only on systems you own or have explicit permission to test. Cybersecurity education should always be conducted ethically and legally.**

🔐 **Stay Secure, Test Responsibly** 🔐
