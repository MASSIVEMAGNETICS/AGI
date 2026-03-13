# Victor 3D Model

## victor_head.glb / victor_head.gltf

**Version:** 1.0 (Procedural)  
**Format:** glTF 2.0  
**Generator:** Victor Visual Engine Procedural Model Generator

### Description

This is a procedurally-generated 3D model of Victor's head/helmet. It features:

- **Geometry:** Angular 8-sided helmet (cyberpunk aesthetic)
- **Eyes:** Basic spherical geometry for human-like eyes
- **Material:** PBR metallic material with teal emissive glow
- **Triangles:** ~144 triangles (optimized for real-time)

### Specifications

```
Vertices:     Variable (procedural)
Triangles:    ~144
Material:     
  - Base Color: Dark gray (RGB: 0.15, 0.15, 0.2)
  - Metallic: 0.9
  - Roughness: 0.3
  - Emissive: Teal (RGB: 0.0, 0.8, 0.8)
Format:       glTF 2.0 Binary (.glb) and Text (.gltf)
```

### Usage in Godot

The model is automatically loaded in `VictorScene.tscn`:

```gdscript
[ext_resource type="PackedScene" path="res://models/victor_head.glb" id="2"]
[node name="VictorHead" parent="." instance=ExtResource("2")]
```

### Regenerating the Model

To regenerate or modify the model:

```bash
python generate_victor_model.py
```

The generator script creates:
- `victor_head.glb` - Binary glTF (used by Godot)
- `victor_head.gltf` - Text glTF (for inspection/debugging)

### Material Properties

The model uses a PBR (Physically Based Rendering) material with:

- **Metallic workflow:** High metallic value for chrome-like appearance
- **Low roughness:** Creates reflective surface
- **Emissive teal:** Matches Victor's default "calm_focus" emotion state

The emissive color changes dynamically in Godot based on Victor's emotion state through the shader system.

### Future Improvements

For production use, consider:

1. **Professional Model:** Commission or create a high-detail model in Blender
   - More facial features
   - Blend shapes for phoneme animation
   - Higher polygon count (~30K-40K tris)
   - Detailed panel lines and accents

2. **Textures:** Add PBR texture maps
   - Base color map with panel details
   - Metallic map with variation
   - Roughness map for surface detail
   - Normal map for fine details
   - Emissive mask for glow patterns

3. **Rigging:** Add skeleton/bones for:
   - Eye movement
   - Jaw animation
   - Head tilt/rotation

See `MODEL_SPECIFICATION.md` for detailed requirements for a production model.

---

**Current Status:** Functional procedural model ✓  
**Production Ready:** Awaiting professional 3D asset
