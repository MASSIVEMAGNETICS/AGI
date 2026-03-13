# Victor Personal Runtime

**Cross-Platform Personal AI Assistant for Your Device Ecosystem**

Version: 1.0.0  
Author: MASSIVEMAGNETICS

---

## Overview

Victor Personal Runtime is a **privacy-focused**, **user-controlled** personal AI assistant that runs on your Windows, Android, and iOS devices. It learns from your interactions to become more helpful while keeping all data on your devices.

### Key Features

- 🔒 **Privacy-First**: All data stays on your devices
- 🎛️ **Full User Control**: Enable/disable any feature anytime
- 📱 **Cross-Platform**: Windows, Android, and iOS support
- 🔄 **Device Sync**: Encrypted sync across your personal devices
- 🧠 **Personal Learning**: Adapts to your preferences locally
- 🛡️ **Security**: Encryption, consent management, audit trails

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MASSIVEMAGNETICS/Victor_Synthetic_Super_Intelligence.git
cd Victor_Synthetic_Super_Intelligence

# Install dependencies
pip install -r requirements.txt

# Run Victor Personal Runtime
python -m victor_runtime
```

### Basic Usage

```python
from victor_runtime import VictorPersonalRuntime

# Create runtime instance
runtime = VictorPersonalRuntime()

# Initialize (will request consent for permissions)
await runtime.initialize()

# Run the assistant
await runtime.run()
```

---

## Platform Support

### Windows

Full feature support including:
- System tray integration
- Global hotkeys
- Toast notifications
- Window overlay (transparency)
- Accessibility via UI Automation

Requirements:
- Python 3.8+
- pywin32 (optional, for full features)
- windows-toasts (optional, for notifications)

### Android

Features:
- Foreground service for background operation
- System overlay (requires permission)
- Notifications
- App usage tracking (with permission)

Requirements:
- Kivy + python-for-android
- Or BeeWare Toga

Build with:
```bash
# Using buildozer
buildozer android debug
```

### iOS

Features:
- Local notifications
- Background app refresh
- Spotlight integration
- Siri shortcuts

Note: iOS does not allow system overlays.

Requirements:
- Kivy + kivy-ios
- Or BeeWare Toga

---

## Architecture

```
victor_runtime/
├── core/
│   ├── runtime.py          # Main runtime engine
│   ├── consent.py          # Consent management (GDPR compliant)
│   ├── user_control.py     # User control panel
│   ├── device_registry.py  # Device registration
│   ├── sync_manager.py     # Cross-device sync
│   └── learning.py         # Personal learning engine
├── platforms/
│   ├── base.py             # Base platform adapter
│   ├── windows.py          # Windows adapter
│   ├── android.py          # Android adapter
│   └── ios.py              # iOS adapter
├── mesh/
│   └── client.py           # Cross-device mesh networking
└── config/
    ├── config_schema.json  # Configuration schema
    └── default_config.yaml # Default configuration
```

---

## Features

### 1. Consent Management

All features require explicit user consent. Consent can be revoked anytime.

```python
from victor_runtime.core.consent import ConsentManager, ConsentType

manager = ConsentManager(data_dir, user_id)

# Request consent
granted = await manager.request_consent(ConsentType.LEARNING)

# Check consent
if manager.has_consent(ConsentType.LEARNING):
    # Feature enabled
    pass

# Revoke consent
manager.revoke_consent(ConsentType.LEARNING)
```

### 2. User Control Panel

Full control over all runtime features.

```python
from victor_runtime.core.user_control import UserControlPanel

panel = UserControlPanel(runtime)

# Get status
status = panel.get_status()

# Toggle features
await panel.enable_feature('learning')
await panel.disable_feature('overlay')

# Stop runtime
await panel.stop_runtime()

# Clear all data
await panel.clear_all_data()
```

### 3. Cross-Device Sync

Encrypted sync using your own GitHub Gist.

```python
# Configure sync
runtime.config['sync']['github_gist_id'] = 'your_gist_id'

# Sync happens automatically
# Or trigger manually:
await runtime._sync_manager.sync()
```

### 4. Personal Learning

Local machine learning that adapts to you.

```python
from victor_runtime.core.learning import PersonalLearningEngine

engine = PersonalLearningEngine(data_dir, config)

# Record observations
engine.observe('app_usage', {'app_name': 'Chrome'})
engine.observe('command', {'command': 'search weather'})

# Get predictions
predictions = engine.predict({'context': 'morning'})

# View learned patterns
patterns = engine.get_patterns()

# Clear learning data
engine.clear_patterns()
```

### 5. Cross-Device Mesh

Communicate between your devices.

```python
from victor_runtime.mesh.client import MeshClient

client = MeshClient(device_info, config)
await client.run()

# Broadcast to all devices
await client.broadcast({'type': 'sync', 'data': {...}})

# Send to specific device
await client.send_to('device_id', {'type': 'command', ...})

# Get connected peers
peers = client.get_online_peers()
```

### 6. Overlay Assistant (Windows/Android)

Floating assistant overlay.

```python
# Enable in config
runtime.config['overlay']['enabled'] = True
runtime.config['overlay']['position'] = 'bottom_right'

# Or via platform adapter
await runtime.platform_adapter.create_overlay({
    'opacity': 0.9,
    'x': 100,
    'y': 100
})
```

---

## Privacy & Security

### Data Storage

- All data stored locally on your devices
- Encrypted with keys you control
- Sync uses your own GitHub Gist (encrypted)
- No data sent to external servers

### Permissions

| Permission | Purpose | Required |
|------------|---------|----------|
| Storage | Save settings and learning data | Yes |
| Background | Run continuously to assist | Yes |
| Network | Sync across devices | Optional |
| Accessibility | Overlay features | Optional |
| Automation | Task automation | Optional |

### Consent

- All features require explicit consent
- Consent can be revoked anytime
- Full audit trail of consent changes
- GDPR-compliant data handling

### User Rights

- **Access**: View all stored data
- **Export**: Export all your data
- **Delete**: Clear all data at any time
- **Control**: Enable/disable any feature

---

## Configuration

### Default Config Location

- Windows: `%APPDATA%\VictorRuntime\config.json`
- macOS: `~/Library/Application Support/VictorRuntime/config.json`
- Linux: `~/.victor_runtime/config.json`
- Android: `/data/data/org.victor.runtime/files/config.json`
- iOS: `Documents/VictorRuntime/config.json`

### Configuration Options

See `config/config_schema.json` for full schema.

Key options:

```yaml
sync:
  enabled: true
  interval_seconds: 300
  github_gist_id: null

learning:
  enabled: true
  local_only: true

overlay:
  enabled: false
  position: bottom_right

automation:
  enabled: false
  require_confirmation: true

privacy:
  telemetry: false
  crash_reports: false
```

---

## Building for Mobile

### Android

```bash
# Install buildozer
pip install buildozer

# Initialize (creates buildozer.spec)
buildozer init

# Build APK
buildozer android debug

# Build release APK
buildozer android release
```

### iOS

```bash
# Install kivy-ios
pip install kivy-ios

# Create Xcode project
toolchain build python3 kivy

# Then open in Xcode and build
```

---

## Integration with Victor SSI

Victor Personal Runtime integrates with the broader Victor Synthetic Super Intelligence system:

```python
# Use with Victor Hub
from victor_hub.victor_boot import VictorHub
from victor_runtime import VictorPersonalRuntime

hub = VictorHub()
runtime = VictorPersonalRuntime()

# Connect runtime to hub
runtime.on_learning_update = hub.process_learning_update
```

---

## Troubleshooting

### Overlay Not Showing (Android)

1. Check SYSTEM_ALERT_WINDOW permission
2. Go to Settings → Apps → Victor → Display over other apps

### Sync Not Working

1. Verify GitHub Gist ID is correct
2. Check network connectivity
3. Ensure sync is enabled in config

### Learning Not Working

1. Check consent is granted for learning
2. Verify learning is enabled in config
3. Check storage permissions

---

## License

See individual repository licenses. This runtime is part of the Victor Synthetic Super Intelligence project by MASSIVEMAGNETICS.

---

**Built with 🔒 Privacy and 🎛️ User Control by MASSIVEMAGNETICS**
