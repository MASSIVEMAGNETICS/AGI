# Victor Visual Engine - Deployment Guide

**Version:** 1.0.0  
**Status:** Ready for Deployment  
**Date:** November 2025

---

## Quick Deployment Checklist

### ✅ Prerequisites
- [ ] Python 3.8+ installed
- [ ] Godot 4.2+ installed
- [ ] WebSocket port 8765 available
- [ ] Dependencies installed (`pip install -r requirements.txt`)

### ✅ Development Deployment (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/MASSIVEMAGNETICS/Victor_Synthetic_Super_Intelligence.git
cd Victor_Synthetic_Super_Intelligence

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test backend
python visual_engine/test_visual_engine.py

# 4. Open Godot project
# Open Godot → Import → visual_engine/godot_project/project.godot

# 5. Run (in Godot: Press F5)
```

**Expected Result:** Sphere with subtitles, cycling through emotions every 5 seconds.

---

## Production Deployment Options

### Option 1: Standalone Desktop Application

**Best for:** End-user deployment, demos, permanent installations

**Steps:**

1. **Export Godot Project**
   ```
   In Godot:
   - Project → Export
   - Add preset (Windows/Mac/Linux)
   - Select export path: visual_engine/godot_project/builds/
   - Click "Export Project"
   ```

2. **Create Bundle**
   ```bash
   mkdir victor_visual_bundle
   cp -r visual_engine/backend victor_visual_bundle/
   cp launch_visual_engine.py victor_visual_bundle/
   cp requirements.txt victor_visual_bundle/
   cp -r visual_engine/godot_project/builds/* victor_visual_bundle/
   ```

3. **Create Launcher Script**
   
   **Windows (launch.bat):**
   ```batch
   @echo off
   start python launch_visual_engine.py
   timeout /t 2
   start VictorVisualEngine.exe
   ```
   
   **Mac/Linux (launch.sh):**
   ```bash
   #!/bin/bash
   python3 launch_visual_engine.py &
   sleep 2
   ./VictorVisualEngine.x86_64 &
   ```

4. **Distribute**
   - Zip `victor_visual_bundle/`
   - Include README with instructions
   - Users run `launch.bat` or `launch.sh`

---

### Option 2: Development Mode

**Best for:** Active development, testing, iteration

**Setup:**
```bash
# Terminal 1: Run backend
python launch_visual_engine.py --demo

# Terminal 2: Run Godot (or press F5 in editor)
```

**Benefits:**
- Live editing in Godot
- Immediate feedback
- Debug console access

---

### Option 3: Server Mode

**Best for:** Remote displays, multiple clients, centralized control

**Setup:**

1. **Server Configuration**
   ```yaml
   # victor_hub/config.yaml
   visual_engine:
     enabled: true
     server:
       host: "0.0.0.0"  # Listen on all interfaces
       port: 8765
       auto_start: true
   ```

2. **Start Server**
   ```bash
   python launch_visual_engine.py --host 0.0.0.0 --port 8765
   ```

3. **Configure Clients**
   ```gdscript
   # In VictorController.gd
   var ws_url := "ws://YOUR_SERVER_IP:8765"
   ```

4. **Deploy Clients**
   - Export Godot project as executable
   - Distribute to display machines
   - Point all clients to server IP

**Use Cases:**
- Multiple displays showing same Victor
- Remote monitoring stations
- Exhibition/museum installations

---

### Option 4: Web Deployment (Experimental)

**Best for:** Web browsers, maximum accessibility

**Limitations:**
- WebGL performance constraints
- No native audio (yet)
- Larger download size

**Steps:**

1. **Export for Web**
   ```
   Godot → Project → Export → HTML5
   Export to: visual_engine/web_build/
   ```

2. **Serve Files**
   ```bash
   cd visual_engine/web_build
   python -m http.server 8080
   ```

3. **Access**
   ```
   http://localhost:8080
   ```

**Note:** WebSocket server must still run separately.

---

## Integration Deployment

### With Victor Hub

**Full Integration:**

```python
# In your Victor Hub startup
from visual_engine.backend import VictorVisualServer, VictorVisualBridge
import asyncio

async def start_with_visual():
    # Start visual server
    server = VictorVisualServer()
    server_task = asyncio.create_task(server.start())
    
    # Create Victor Hub
    hub = VictorHub()
    
    # Create bridge
    bridge = VictorVisualBridge(server)
    
    # Hook into task execution
    hub.visual_bridge = bridge
    
    # Run
    await asyncio.gather(
        server_task,
        run_hub(hub, bridge)
    )

asyncio.run(start_with_visual())
```

---

## Environment-Specific Deployments

### Development Environment

```bash
# Config: Development mode
visual_engine:
  enabled: true
  demo_mode: true
  
# Run with hot reload
python launch_visual_engine.py --demo
```

### Staging Environment

```bash
# Config: Staging mode
visual_engine:
  enabled: true
  demo_mode: false
  server:
    host: "staging.internal"
    
# Run with logging
python launch_visual_engine.py 2>&1 | tee visual_engine.log
```

### Production Environment

```bash
# Config: Production mode
visual_engine:
  enabled: true
  demo_mode: false
  server:
    host: "0.0.0.0"
    
# Run as service (systemd)
sudo systemctl start victor-visual-engine
```

**Systemd Service File:**
```ini
[Unit]
Description=Victor Visual Engine WebSocket Server
After=network.target

[Service]
Type=simple
User=victor
WorkingDirectory=/opt/victor
ExecStart=/usr/bin/python3 launch_visual_engine.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Performance Optimization

### Low-End Hardware

```gdscript
# In Godot project settings
rendering/quality/msaa = 0
rendering/quality/shadows = false
rendering/limits/rendering/max_lights = 4
```

### High-End Hardware

```gdscript
# Enable all features
rendering/quality/msaa = 4
rendering/quality/ssao = true
rendering/quality/hdr = true
rendering/limits/rendering/max_lights = 16
```

---

## Security Hardening

### Production Checklist

- [ ] Use WSS (WebSocket Secure) not WS
- [ ] Add authentication tokens
- [ ] Implement rate limiting
- [ ] Enable CORS restrictions
- [ ] Run server as non-root user
- [ ] Configure firewall rules
- [ ] Enable logging and monitoring
- [ ] Regular security updates

**WSS Configuration:**
```python
# Use wss:// instead of ws://
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

# In server start
async with websockets.serve(
    self.handle_client, 
    self.host, 
    self.port,
    ssl=ssl_context
):
    ...
```

---

## Monitoring & Logging

### Log Configuration

```python
# Enhanced logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/visual_engine.log'),
        logging.handlers.RotatingFileHandler(
            'logs/visual_engine.log',
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
    ]
)
```

### Metrics to Monitor

- WebSocket connection count
- Message send/receive rate
- Error frequency
- Server uptime
- Memory usage
- CPU usage

---

## Troubleshooting Production Issues

### Server Won't Start

**Check:**
1. Port 8765 not in use: `netstat -an | grep 8765`
2. Python dependencies installed: `pip list | grep websockets`
3. Permissions: Server has bind permission

**Fix:**
```bash
# Kill existing process
pkill -f launch_visual_engine

# Try different port
python launch_visual_engine.py --port 8766
```

### Client Can't Connect

**Check:**
1. Server is running: `ps aux | grep launch_visual_engine`
2. Firewall allows port: `sudo ufw status`
3. Network reachable: `ping SERVER_IP`

**Fix:**
```bash
# Allow port through firewall
sudo ufw allow 8765/tcp

# Test connection
telnet SERVER_IP 8765
```

### High Latency

**Check:**
1. Network bandwidth
2. Server CPU usage
3. Client rendering performance

**Fix:**
- Reduce phoneme array size
- Lower Godot quality settings
- Use localhost if possible
- Add WebSocket compression

---

## Backup & Recovery

### Backup Critical Files

```bash
# Backup script
tar -czf victor_visual_backup_$(date +%Y%m%d).tar.gz \
  visual_engine/ \
  victor_hub/config.yaml \
  requirements.txt
```

### Restore Process

```bash
# Extract backup
tar -xzf victor_visual_backup_20251109.tar.gz

# Reinstall dependencies
pip install -r requirements.txt

# Restart service
systemctl restart victor-visual-engine
```

---

## Scaling

### Horizontal Scaling (Multiple Servers)

```
Load Balancer
    ├── Visual Server 1 (ws://server1:8765)
    ├── Visual Server 2 (ws://server2:8765)
    └── Visual Server 3 (ws://server3:8765)
         ↓
    Multiple Godot Clients
```

### Vertical Scaling (More Resources)

- Increase Python process memory
- Use faster CPU
- Upgrade network bandwidth
- SSD for faster I/O

---

## Testing Deployment

### Pre-Deployment Checklist

```bash
# 1. Test server starts
python launch_visual_engine.py &
SERVER_PID=$!
sleep 2
kill $SERVER_PID

# 2. Test demo mode
timeout 10 python visual_engine/test_visual_engine.py

# 3. Test integration
timeout 15 python run_victor_with_visual.py --mode demo

# 4. Validate Godot project
# Open in Godot, check for errors
```

### Post-Deployment Verification

1. **Check Logs**
   ```bash
   tail -f logs/visual_engine.log
   ```

2. **Monitor Connections**
   ```bash
   netstat -an | grep 8765 | wc -l
   ```

3. **Test Client**
   - Connect Godot client
   - Verify visual updates
   - Check subtitle display
   - Confirm color changes

---

## Version Management

### Current: v1.0.0

**Features:**
- WebSocket server
- Basic emotion system
- Phoneme framework
- Placeholder visuals

### Planned: v1.1.0

**Features:**
- Production 3D model
- Real TTS integration
- Advanced shaders
- Performance improvements

### Upgrade Path

```bash
# Backup current
cp -r visual_engine visual_engine_v1.0_backup

# Pull new version
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Test
python visual_engine/test_visual_engine.py
```

---

## Support & Maintenance

### Regular Maintenance Tasks

**Weekly:**
- Check logs for errors
- Monitor connection stability
- Verify disk space

**Monthly:**
- Update dependencies
- Review security patches
- Performance audit

**Quarterly:**
- Full backup
- Test disaster recovery
- Update documentation

---

## Contact & Resources

**Documentation:**
- README: `visual_engine/README.md`
- Quick Start: `visual_engine/QUICKSTART.md`
- Technical: `visual_engine/docs/TECHNICAL_OVERVIEW.md`

**Repository:**
- GitHub: MASSIVEMAGNETICS/Victor_Synthetic_Super_Intelligence

**Issues:**
- Report bugs via GitHub Issues
- Include logs and system info

---

**Deployment Status:** PRODUCTION-READY ✓

**Last Updated:** November 2025  
**Maintained by:** MASSIVEMAGNETICS
