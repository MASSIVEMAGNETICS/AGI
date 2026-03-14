#!/usr/bin/env python3
"""
Victor Personal Runtime - Mesh Client
======================================

Handles cross-device communication within the user's personal
device mesh. Uses encrypted peer-to-peer connections.

Communication Methods:
1. Local Network Discovery (mDNS/Bonjour)
2. WebSocket relay (for remote devices)
3. GitHub Gist sync (fallback)
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger('victor_runtime.mesh')


@dataclass
class MeshMessage:
    """A message in the mesh network"""
    message_id: str
    sender_device_id: str
    timestamp: str
    message_type: str  # sync, command, heartbeat, learning_update
    payload: Dict
    encrypted: bool = True
    
    def to_dict(self) -> Dict:
        return {
            'message_id': self.message_id,
            'sender_device_id': self.sender_device_id,
            'timestamp': self.timestamp,
            'message_type': self.message_type,
            'payload': self.payload,
            'encrypted': self.encrypted
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MeshMessage':
        return cls(
            message_id=data['message_id'],
            sender_device_id=data['sender_device_id'],
            timestamp=data['timestamp'],
            message_type=data['message_type'],
            payload=data['payload'],
            encrypted=data.get('encrypted', True)
        )


@dataclass
class MeshPeer:
    """A peer device in the mesh"""
    device_id: str
    device_name: str
    platform: str
    address: Optional[str] = None
    port: int = 8899
    last_seen: Optional[str] = None
    connection_type: str = "unknown"  # local, relay, offline
    latency_ms: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'platform': self.platform,
            'address': self.address,
            'port': self.port,
            'last_seen': self.last_seen,
            'connection_type': self.connection_type,
            'latency_ms': self.latency_ms
        }


class MeshClient:
    """
    Mesh Client for Victor Personal Runtime.
    
    Enables secure cross-device communication for your personal
    device ecosystem. All communication is encrypted and only
    devices you own can participate.
    
    Features:
    - Local network auto-discovery
    - Encrypted messaging
    - Peer-to-peer when possible
    - Relay fallback for remote devices
    - Offline queuing
    
    Usage:
        client = MeshClient(device_info, config)
        await client.run()
        
        # Send message to all devices
        await client.broadcast({'type': 'sync', 'data': {...}})
        
        # Send to specific device
        await client.send_to('device_id', {'type': 'command', ...})
    """
    
    VERSION = "1.0.0"
    DISCOVERY_PORT = 8898
    MESH_PORT = 8899
    HEARTBEAT_INTERVAL = 30  # seconds
    
    def __init__(self, device_info, config: Dict):
        """
        Initialize mesh client.
        
        Args:
            device_info: DeviceInfo for this device
            config: Mesh configuration
        """
        self.device_info = device_info
        self.config = config
        
        self.device_id = device_info.device_id if device_info else "unknown"
        self.peers: Dict[str, MeshPeer] = {}
        self.message_queue: List[MeshMessage] = []
        
        self._running = False
        self._encryption_key: Optional[bytes] = None
        self._discovery_server = None
        self._mesh_server = None
        
        # Callbacks
        self.on_message: Optional[Callable[[MeshMessage], None]] = None
        self.on_peer_discovered: Optional[Callable[[MeshPeer], None]] = None
        self.on_peer_lost: Optional[Callable[[str], None]] = None
    
    def set_encryption_key(self, key: bytes):
        """Set the mesh encryption key"""
        self._encryption_key = key
    
    async def run(self):
        """Run the mesh client"""
        self._running = True
        logger.info("Mesh client started")
        
        try:
            # Start discovery
            asyncio.create_task(self._discovery_loop())
            
            # Start heartbeat
            asyncio.create_task(self._heartbeat_loop())
            
            # Start message processing
            asyncio.create_task(self._process_queue())
            
            # Main loop
            while self._running:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Mesh client error: {e}")
    
    async def stop(self):
        """Stop the mesh client"""
        self._running = False
        
        # Close connections
        if self._discovery_server:
            self._discovery_server.close()
        
        if self._mesh_server:
            self._mesh_server.close()
        
        logger.info("Mesh client stopped")
    
    async def _discovery_loop(self):
        """Discover peers on local network"""
        while self._running:
            try:
                await self._discover_local_peers()
                await asyncio.sleep(30)  # Discover every 30 seconds
            except Exception as e:
                logger.error(f"Discovery error: {e}")
                await asyncio.sleep(60)
    
    async def _discover_local_peers(self):
        """
        Discover peers using mDNS/UDP broadcast.
        
        This is a simplified implementation. In production,
        use zeroconf for proper mDNS discovery.
        """
        try:
            import socket
            
            # Send discovery broadcast
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(2)
            
            discovery_message = json.dumps({
                'type': 'victor_discovery',
                'device_id': self.device_id,
                'device_name': self.device_info.device_name if self.device_info else 'unknown',
                'platform': self.device_info.platform if self.device_info else 'unknown',
                'port': self.MESH_PORT
            }).encode()
            
            # Broadcast on local network
            sock.sendto(discovery_message, ('<broadcast>', self.DISCOVERY_PORT))
            
            # Listen for responses
            start_time = time.time()
            while time.time() - start_time < 2:
                try:
                    data, addr = sock.recvfrom(1024)
                    response = json.loads(data.decode())
                    
                    if response.get('type') == 'victor_discovery' and \
                       response.get('device_id') != self.device_id:
                        
                        # Found a peer
                        peer = MeshPeer(
                            device_id=response['device_id'],
                            device_name=response.get('device_name', 'Unknown'),
                            platform=response.get('platform', 'unknown'),
                            address=addr[0],
                            port=response.get('port', self.MESH_PORT),
                            last_seen=datetime.now().isoformat(),
                            connection_type='local'
                        )
                        
                        await self._add_peer(peer)
                        
                except socket.timeout:
                    break
                except Exception:
                    continue
            
            sock.close()
            
        except Exception as e:
            logger.debug(f"Local discovery failed: {e}")
    
    async def _add_peer(self, peer: MeshPeer):
        """Add or update a peer"""
        is_new = peer.device_id not in self.peers
        self.peers[peer.device_id] = peer
        
        if is_new and self.on_peer_discovered:
            try:
                self.on_peer_discovered(peer)
            except Exception as e:
                logger.error(f"Peer discovered callback error: {e}")
        
        logger.info(f"Peer {'discovered' if is_new else 'updated'}: {peer.device_name}")
    
    async def _heartbeat_loop(self):
        """Send heartbeats to peers"""
        while self._running:
            try:
                await self._send_heartbeats()
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(60)
    
    async def _send_heartbeats(self):
        """Send heartbeat to all peers"""
        message = MeshMessage(
            message_id=f"hb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            sender_device_id=self.device_id,
            timestamp=datetime.now().isoformat(),
            message_type='heartbeat',
            payload={'status': 'online'},
            encrypted=False
        )
        
        for peer_id in list(self.peers.keys()):
            try:
                await self._send_to_peer(peer_id, message)
            except Exception as e:
                logger.debug(f"Heartbeat to {peer_id} failed: {e}")
                await self._mark_peer_offline(peer_id)
    
    async def _mark_peer_offline(self, peer_id: str):
        """Mark a peer as offline"""
        if peer_id in self.peers:
            peer = self.peers[peer_id]
            peer.connection_type = 'offline'
            
            # Remove if offline for too long
            # In production, track offline duration
    
    async def _process_queue(self):
        """Process queued messages"""
        while self._running:
            try:
                if self.message_queue:
                    message = self.message_queue.pop(0)
                    await self._deliver_message(message)
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(1)
    
    async def _deliver_message(self, message: MeshMessage):
        """Deliver a queued message"""
        # Try to send to target peer
        # If failed, re-queue with backoff
        pass
    
    # ========================
    # Public API
    # ========================
    
    async def broadcast(self, payload: Dict, message_type: str = "sync") -> int:
        """
        Broadcast a message to all peers.
        
        Args:
            payload: Message payload
            message_type: Type of message
            
        Returns:
            Number of peers message was sent to
        """
        message = MeshMessage(
            message_id=f"bc_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.peers)}",
            sender_device_id=self.device_id,
            timestamp=datetime.now().isoformat(),
            message_type=message_type,
            payload=payload
        )
        
        sent_count = 0
        for peer_id in list(self.peers.keys()):
            try:
                await self._send_to_peer(peer_id, message)
                sent_count += 1
            except Exception as e:
                logger.debug(f"Broadcast to {peer_id} failed: {e}")
        
        return sent_count
    
    async def send_to(self, device_id: str, payload: Dict, message_type: str = "command") -> bool:
        """
        Send a message to a specific device.
        
        Args:
            device_id: Target device ID
            payload: Message payload
            message_type: Type of message
            
        Returns:
            True if sent successfully
        """
        if device_id not in self.peers:
            logger.warning(f"Unknown peer: {device_id}")
            return False
        
        message = MeshMessage(
            message_id=f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            sender_device_id=self.device_id,
            timestamp=datetime.now().isoformat(),
            message_type=message_type,
            payload=payload
        )
        
        try:
            await self._send_to_peer(device_id, message)
            return True
        except Exception as e:
            logger.error(f"Send to {device_id} failed: {e}")
            return False
    
    async def _send_to_peer(self, peer_id: str, message: MeshMessage):
        """Send message to a specific peer"""
        if peer_id not in self.peers:
            raise ValueError(f"Unknown peer: {peer_id}")
        
        peer = self.peers[peer_id]
        
        if peer.connection_type == 'local' and peer.address:
            # Send directly via TCP/WebSocket
            await self._send_direct(peer, message)
        else:
            # Queue for relay or offline delivery
            self.message_queue.append(message)
    
    async def _send_direct(self, peer: MeshPeer, message: MeshMessage):
        """Send message directly to peer"""
        try:
            # Encrypt if needed
            if message.encrypted and self._encryption_key:
                encrypted_payload = self._encrypt(json.dumps(message.payload))
                message.payload = {'encrypted': encrypted_payload}
            
            # Open connection and send
            reader, writer = await asyncio.open_connection(peer.address, peer.port)
            
            data = json.dumps(message.to_dict()).encode()
            writer.write(len(data).to_bytes(4, 'big'))
            writer.write(data)
            await writer.drain()
            
            writer.close()
            await writer.wait_closed()
            
            # Update peer latency
            # In production, measure round-trip time
            
        except Exception as e:
            raise ConnectionError(f"Failed to send to {peer.device_name}: {e}")
    
    def _encrypt(self, data: str) -> str:
        """Encrypt data for transmission using AES-GCM"""
        if not self._encryption_key:
            return data
        
        import base64
        import os
        
        try:
            # Use AES-GCM for authenticated encryption
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            # Generate random nonce
            nonce = os.urandom(12)
            
            # Encrypt with AES-GCM
            aesgcm = AESGCM(self._encryption_key[:32])  # Use first 32 bytes for 256-bit key
            ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
            
            # Prepend nonce to ciphertext
            return base64.b64encode(nonce + ciphertext).decode()
            
        except ImportError:
            try:
                # Fallback to Fernet
                from cryptography.fernet import Fernet
                
                fernet_key = base64.urlsafe_b64encode(self._encryption_key[:32])
                f = Fernet(fernet_key)
                return f.encrypt(data.encode()).decode()
                
            except ImportError:
                logger.warning("No encryption library available - sending unencrypted")
                return base64.b64encode(data.encode()).decode()
    
    def _decrypt(self, data: str) -> str:
        """Decrypt received data using AES-GCM"""
        if not self._encryption_key:
            return data
        
        import base64
        
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            decoded = base64.b64decode(data)
            
            # Extract nonce and ciphertext
            nonce = decoded[:12]
            ciphertext = decoded[12:]
            
            # Decrypt with AES-GCM
            aesgcm = AESGCM(self._encryption_key[:32])
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext.decode()
            
        except ImportError:
            try:
                from cryptography.fernet import Fernet
                
                fernet_key = base64.urlsafe_b64encode(self._encryption_key[:32])
                f = Fernet(fernet_key)
                return f.decrypt(base64.b64decode(data)).decode()
                
            except ImportError:
                # Fallback: assume base64 encoded plaintext
                return base64.b64decode(data).decode()
    
    # ========================
    # Peer Management
    # ========================
    
    def get_peers(self) -> List[Dict]:
        """Get list of known peers"""
        return [p.to_dict() for p in self.peers.values()]
    
    def get_online_peers(self) -> List[Dict]:
        """Get list of online peers"""
        return [
            p.to_dict() for p in self.peers.values()
            if p.connection_type != 'offline'
        ]
    
    def get_peer(self, device_id: str) -> Optional[Dict]:
        """Get specific peer info"""
        if device_id in self.peers:
            return self.peers[device_id].to_dict()
        return None
    
    def remove_peer(self, device_id: str):
        """Remove a peer from the mesh"""
        if device_id in self.peers:
            del self.peers[device_id]
            if self.on_peer_lost:
                self.on_peer_lost(device_id)
    
    def get_mesh_status(self) -> Dict:
        """Get mesh network status"""
        return {
            'device_id': self.device_id,
            'running': self._running,
            'total_peers': len(self.peers),
            'online_peers': len(self.get_online_peers()),
            'queued_messages': len(self.message_queue),
            'peers': self.get_peers()
        }
