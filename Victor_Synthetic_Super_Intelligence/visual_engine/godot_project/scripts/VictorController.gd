"""
VictorController - Main control script for Victor Visual Engine
Connects to Victor backend via WebSocket and drives all visual elements

This script manages:
- WebSocket connection to Victor backend
- Phoneme-based lip sync animation
- Emotion-driven visual effects
- Eye tracking and idle animations
- Subtitle display
"""

extends Node

# WebSocket connection
var ws := WebSocketPeer.new()
var ws_url := "ws://127.0.0.1:8765"
var connection_retry_timer := 0.0
var retry_interval := 5.0

# Victor state
var current_emotion := "calm_focus"
var current_energy := 0.5
var current_aura := "teal"
var current_mode := "advisor"

# Phoneme animation
var phoneme_queue := []
var speaking := false
var phoneme_time := 0.0

# References to scene nodes (set via @onready or in _ready)
@onready var skeleton: Skeleton3D = $VictorHead/Skeleton3D if has_node("VictorHead/Skeleton3D") else null
@onready var subtitle_label: Label = $UI/Subtitles/Label if has_node("UI/Subtitles/Label") else null
@onready var audio_player: AudioStreamPlayer = $AudioStreamPlayer if has_node("AudioStreamPlayer") else null
@onready var victor_head: Node3D = $VictorHead if has_node("VictorHead") else null
@onready var camera: Camera3D = $VictorCamera if has_node("VictorCamera") else null
@onready var lights: Node3D = $VictorLights if has_node("VictorLights") else null
@onready var background: Node3D = $Background if has_node("Background") else null

# Emotion colors (for aura/lighting)
var emotion_colors := {
	"teal": Color(0.0, 0.8, 0.8),
	"blue": Color(0.2, 0.4, 1.0),
	"gold": Color(1.0, 0.8, 0.2),
	"orange": Color(1.0, 0.5, 0.0),
	"red": Color(1.0, 0.2, 0.2),
	"purple": Color(0.7, 0.2, 1.0),
	"cyan": Color(0.0, 1.0, 1.0),
	"magenta": Color(1.0, 0.2, 0.8),
	"white": Color(1.0, 1.0, 1.0),
	"violet": Color(0.5, 0.0, 1.0)
}


func _ready() -> void:
	print("Victor Visual Engine starting...")
	print("Connecting to Victor backend at: ", ws_url)
	_connect_to_backend()
	
	# Initialize subtitle if available
	if subtitle_label:
		subtitle_label.text = "Connecting to Victor..."


func _process(delta: float) -> void:
	# Handle WebSocket connection
	_process_websocket(delta)
	
	# Update animations if speaking
	if speaking and audio_player:
		_update_phoneme_animation(delta)
	
	# Idle animations
	_update_idle_animations(delta)


func _connect_to_backend() -> void:
	"""Attempt to connect to Victor backend WebSocket"""
	var err = ws.connect_to_url(ws_url)
	if err != OK:
		push_error("Victor WebSocket connect failed: %s" % err)
		if subtitle_label:
			subtitle_label.text = "Connection failed. Retrying..."
	else:
		print("WebSocket connection initiated...")


func _process_websocket(delta: float) -> void:
	"""Process WebSocket messages and connection state"""
	var state = ws.get_ready_state()
	
	match state:
		WebSocketPeer.STATE_CONNECTING:
			# Still connecting
			pass
			
		WebSocketPeer.STATE_OPEN:
			# Connected - poll for messages
			ws.poll()
			
			while ws.get_available_packet_count() > 0:
				var packet = ws.get_packet()
				var message = packet.get_string_from_utf8()
				_handle_victor_message(message)
			
			# Reset retry timer
			connection_retry_timer = 0.0
			
		WebSocketPeer.STATE_CLOSING, WebSocketPeer.STATE_CLOSED:
			# Connection lost - attempt reconnect
			connection_retry_timer += delta
			if connection_retry_timer >= retry_interval:
				print("Reconnecting to Victor backend...")
				_connect_to_backend()
				connection_retry_timer = 0.0


func _handle_victor_message(message: String) -> void:
	"""Handle incoming message from Victor backend"""
	var json = JSON.new()
	var parse_result = json.parse(message)
	
	if parse_result != OK:
		push_error("Failed to parse Victor message: %s" % json.get_error_message())
		return
	
	var data = json.data
	if typeof(data) != TYPE_DICTIONARY:
		push_error("Victor message is not a dictionary")
		return
	
	print("Received Victor state: ", data)
	
	# Update subtitle text
	if data.has("text") and subtitle_label:
		subtitle_label.text = data["text"]
	
	# Update emotion and visual effects
	if data.has("emotion"):
		current_emotion = data["emotion"]
		current_energy = data.get("energy", 0.5)
		current_aura = data.get("aura", "teal")
		current_mode = data.get("mode", "advisor")
		_apply_emotion_fx(current_emotion, current_energy)
	
	# Update phoneme queue for lip sync
	if data.has("phonemes") and data["phonemes"] is Array:
		phoneme_queue = data["phonemes"].duplicate()
		if phoneme_queue.size() > 0:
			speaking = true
			phoneme_time = 0.0
			_play_audio(data.get("audio_path", ""))


func _play_audio(path: String) -> void:
	"""Play audio file if path provided"""
	if path == "" or not audio_player:
		return
	
	# In production, load and play the audio file
	# For now, we'll just simulate with placeholder
	print("Would play audio: ", path)
	# var stream = load(path)
	# if stream:
	#     audio_player.stream = stream
	#     audio_player.play()


func _update_phoneme_animation(delta: float) -> void:
	"""Update mouth animation based on phoneme timing"""
	if not skeleton or phoneme_queue.is_empty():
		speaking = false
		_set_mouth_rest()
		return
	
	# Update phoneme time
	if audio_player and audio_player.playing:
		phoneme_time = audio_player.get_playback_position()
	else:
		phoneme_time += delta
	
	# Find current phoneme based on time
	var current_phoneme = null
	for i in range(phoneme_queue.size()):
		var ph = phoneme_queue[i]
		if ph.has("t") and ph["t"] <= phoneme_time:
			current_phoneme = ph
		else:
			break
	
	# Apply phoneme shape
	if current_phoneme and current_phoneme.has("p"):
		_apply_phoneme(current_phoneme["p"])
	else:
		_set_mouth_rest()
	
	# End speaking if we've processed all phonemes
	if phoneme_time > 10.0 or (phoneme_queue.size() > 0 and phoneme_time > phoneme_queue[-1].get("t", 0.0) + 1.0):
		speaking = false
		phoneme_queue.clear()


func _apply_phoneme(p: String) -> void:
	"""Map phoneme to jaw/mouth blendshapes"""
	if not skeleton:
		return
	
	# Reset all mouth shapes
	_set_mouth_rest()
	
	# Apply appropriate blend shape based on phoneme
	match p:
		"M", "B", "P":
			_set_blend("mouth_closed", 1.0)
		"AA", "AE", "AH", "AO":
			_set_blend("mouth_open", 0.8)
			_set_blend("jaw_open", 0.6)
		"F", "V":
			_set_blend("mouth_fv", 1.0)
		"K", "G":
			_set_blend("mouth_open", 0.3)
		_:
			# Default slightly open for other sounds
			_set_blend("mouth_open", 0.2)


func _set_blend(shape_name: String, value: float) -> void:
	"""Set blend shape weight (placeholder - depends on actual model)"""
	if not skeleton:
		return
	
	# In production, this would set actual blend shapes on the mesh
	# For now, this is a placeholder for when the 3D model is added
	# Example: skeleton.set_blend_shape_value(shape_name, value)
	pass


func _set_mouth_rest() -> void:
	"""Reset mouth to rest position"""
	if not skeleton:
		return
	
	# Reset all mouth-related blend shapes to 0
	var mouth_shapes = ["mouth_closed", "mouth_open", "mouth_fv", "jaw_open"]
	for shape in mouth_shapes:
		_set_blend(shape, 0.0)


func _apply_emotion_fx(emotion: String, energy: float) -> void:
	"""Apply visual effects based on emotion and energy level"""
	print("Applying emotion FX: ", emotion, " energy: ", energy)
	
	# Get emotion color
	var color = emotion_colors.get(emotion, Color.WHITE)
	
	# Update lighting (if lights exist)
	if lights:
		_update_lights(color, energy)
	
	# Update shader parameters (if materials exist)
	if victor_head:
		_update_head_material(color, energy)
	
	# Update background effects
	if background:
		_update_background(color, energy)


func _update_lights(color: Color, energy: float) -> void:
	"""Update lighting based on emotion"""
	# Placeholder - would update actual light nodes
	# Example: lights.get_node("KeyLight").light_color = color
	# Example: lights.get_node("RimLight").light_energy = energy * 2.0
	pass


func _update_head_material(color: Color, energy: float) -> void:
	"""Update head/helmet material shader parameters"""
	# Placeholder - would update shader parameters for emissive glow
	# Example:
	# var material = victor_head.get_surface_material(0)
	# if material:
	#     material.set_shader_parameter("emissive_color", color)
	#     material.set_shader_parameter("emissive_strength", energy)
	pass


func _update_background(color: Color, energy: float) -> void:
	"""Update background effects"""
	# Placeholder - would update background particles, fog color, etc.
	pass


func _update_idle_animations(delta: float) -> void:
	"""Subtle idle movements when not speaking"""
	if speaking or not victor_head:
		return
	
	# Subtle breathing and head tilt
	var time = Time.get_ticks_msec() / 1000.0
	
	# Breathing (slow sine wave)
	var breath = sin(time * 0.5) * 0.02
	
	# Micro head movements
	var tilt = sin(time * 0.3) * 0.01
	
	# Apply to head node (if it exists)
	# victor_head.rotation.z = tilt
	# victor_head.scale = Vector3.ONE * (1.0 + breath)
	pass


# Utility function to send messages back to backend
func send_to_backend(data: Dictionary) -> void:
	"""Send message to Victor backend"""
	if ws.get_ready_state() == WebSocketPeer.STATE_OPEN:
		var json_str = JSON.stringify(data)
		ws.send_text(json_str)
	else:
		push_error("Cannot send to backend - not connected")


# Handle cleanup
func _exit_tree() -> void:
	if ws.get_ready_state() == WebSocketPeer.STATE_OPEN:
		ws.close()
	print("Victor Visual Engine shutting down...")
