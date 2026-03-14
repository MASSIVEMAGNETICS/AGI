// Victor Head Shader - Emissive cyberpunk helmet with reactive glow
// Supports emotion-driven color changes and energy pulsing

shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

// PBR Material parameters
uniform vec4 albedo : source_color = vec4(0.1, 0.1, 0.15, 1.0);
uniform float metallic : hint_range(0.0, 1.0) = 0.8;
uniform float roughness : hint_range(0.0, 1.0) = 0.3;

// Emissive parameters (driven by Victor's emotion/energy)
uniform vec4 emissive_color : source_color = vec4(0.0, 0.8, 0.8, 1.0);
uniform float emissive_strength : hint_range(0.0, 10.0) = 2.0;
uniform float pulse_speed : hint_range(0.0, 10.0) = 1.0;

// Panel/accent lines
uniform sampler2D emission_mask : hint_default_white;
uniform float panel_intensity : hint_range(0.0, 1.0) = 0.5;

// Glitch effect (activated during deep thinking)
uniform float glitch_amount : hint_range(0.0, 1.0) = 0.0;
uniform float glitch_speed : hint_range(0.0, 10.0) = 5.0;

// Time-based animations
varying vec3 world_position;

void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

// Simple noise function
float random(vec2 st) {
	return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

void fragment() {
	// Base PBR properties
	ALBEDO = albedo.rgb;
	METALLIC = metallic;
	ROUGHNESS = roughness;
	
	// Get emission mask (defines which parts glow - panel lines, accents)
	vec4 mask = texture(emission_mask, UV);
	
	// Pulse effect based on time
	float pulse = sin(TIME * pulse_speed) * 0.5 + 0.5;
	float energy_pulse = mix(0.8, 1.0, pulse);
	
	// Base emissive from mask and color
	vec3 emission = emissive_color.rgb * mask.r * panel_intensity * energy_pulse;
	
	// Add overall glow modulated by strength
	emission += emissive_color.rgb * emissive_strength * 0.1;
	
	// Glitch effect - scanline distortion
	if (glitch_amount > 0.0) {
		float scanline = fract(world_position.y * 20.0 + TIME * glitch_speed);
		float glitch_noise = random(vec2(scanline, TIME * 0.1));
		
		if (glitch_noise < glitch_amount) {
			// Offset emission color
			emission += vec3(glitch_noise, 0.0, 1.0 - glitch_noise) * 0.5;
		}
	}
	
	EMISSION = emission;
}
