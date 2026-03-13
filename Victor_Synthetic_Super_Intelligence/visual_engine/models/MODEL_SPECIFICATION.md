# Victor 3D Model Specification

**Version:** 1.0  
**Target:** Blender 3.6+ → glTF/GLB export for Godot 4

---

## Visual Reference

Based on the provided image: cyberpunk aesthetic with:
- Chrome/metallic helmet with angular panels
- Human eyes (visible through visor/openings)
- Smooth mask covering lower face
- Glossy jacket/torso (optional)
- Neon reflections and emissive accents

---

## Model Requirements

### Geometry

**Head/Helmet:**
- Polygons: 10,000 - 20,000 tris (mid-poly for real-time)
- Angular panels on helmet (forehead, temples, crown)
- Smooth visor/face mask
- Eye sockets with human eyes
- Slight asymmetry for realism
- Clean topology for animation

**Eyes:**
- Separate mesh for each eye
- Spherical geometry
- Proper UV mapping for iris/pupil
- Subsurface scattering material

**Torso (Optional):**
- Upper body/shoulders
- Jacket/armor plating
- Keep poly count under 15,000 tris

**Total Target:** 30,000 - 40,000 tris

---

## Materials (PBR)

### 1. Helmet/Armor (Metallic)

- **Albedo:** Dark gunmetal (RGB: 30, 30, 40)
- **Metallic:** 0.9
- **Roughness:** 0.2 - 0.4 (variation across surface)
- **Normal Map:** Panel edges, panel details
- **Emissive Mask:** Define panel lines/accents
  - White on edges that should glow
  - Black elsewhere
  - Resolution: 2048x2048

### 2. Face Mask (Smooth)

- **Albedo:** Slightly lighter gray (RGB: 50, 50, 60)
- **Metallic:** 0.5
- **Roughness:** 0.3
- **Subsurface:** Subtle (if Godot shader supports)

### 3. Eyes

- **Albedo:** Realistic iris texture
- **Emissive:** Slight glow (optional, for cyberpunk effect)
- **Transparency:** Cornea overlay

### 4. Jacket/Torso (if included)

- **Albedo:** Dark fabric or leather texture
- **Metallic:** 0.1 - 0.3
- **Roughness:** 0.6
- **Normal Map:** Fabric weave or leather grain

---

## Rigging

### Skeleton

**Bones Required:**
1. `Head` - Main head control
2. `Neck` (optional)
3. `Eye_L` - Left eye
4. `Eye_R` - Right eye
5. `Jaw` - Jaw open/close

**Bone Hierarchy:**
```
Root
├── Neck
    └── Head
        ├── Eye_L
        ├── Eye_R
        └── Jaw
```

### Blendshapes (Shape Keys)

For lip sync and facial expressions:

**Required Blendshapes:**
1. `mouth_open` - Jaw open, general open mouth
2. `mouth_closed` - Lips pressed together (M, B, P sounds)
3. `mouth_fv` - Lower lip to upper teeth (F, V sounds)
4. `jaw_open` - Jaw drop without lip movement
5. `blink_L` - Left eye blink (optional)
6. `blink_R` - Right eye blink (optional)

**Optional Blendshapes:**
7. `mouth_smile` - Slight smile
8. `brow_raise` - Eyebrow raise
9. `brow_furrow` - Concentrated look

**Naming Convention:**  
Use lowercase with underscores, exactly as listed (for GDScript compatibility)

---

## UV Mapping

- **Helmet/Face:** Single 2048x2048 UV layout
- **Eyes:** Separate 512x512 per eye
- **Torso:** 1024x1024 (if included)

Ensure no overlapping UVs (except for symmetrical mirroring if desired).

---

## Animation Targets

The model will be animated via:

1. **Blendshapes** - Mouth shapes for phonemes
2. **Bones** - Eye tracking, head tilt, jaw
3. **Procedural** - Idle breathing, micro-movements (in Godot)

---

## Export Settings (Blender → Godot)

**Format:** glTF 2.0 (.glb or .gltf)

**Export Options:**
- ✅ Include: Selected Objects
- ✅ Include: Cameras (if needed)
- ✅ Include: Punctual Lights (if needed)
- ✅ Transform: +Y Up
- ✅ Geometry: Apply Modifiers
- ✅ Geometry: UVs
- ✅ Geometry: Normals
- ✅ Geometry: Vertex Colors
- ✅ Geometry: Materials → Export
- ✅ Animation: Shape Keys
- ✅ Animation: Skinning
- ❌ Animation: Bake Actions (not needed)
- Compression: Draco (optional, for smaller file size)

**File Naming:**
- `victor_head_v1.glb` - Full model
- `victor_head_lod1.glb` - Lower detail version (optional)

---

## Texture Checklist

Create and export these textures:

1. **Helmet_BaseColor.png** (2048x2048)
2. **Helmet_Normal.png** (2048x2048)
3. **Helmet_Metallic.png** (2048x2048) - Grayscale
4. **Helmet_Roughness.png** (2048x2048) - Grayscale
5. **Helmet_Emissive_Mask.png** (2048x2048) - Grayscale or RGB
6. **Eye_Iris_L.png** (512x512)
7. **Eye_Iris_R.png** (512x512) - Can mirror left

**Format:** PNG with transparency where needed

---

## Import into Godot

1. Copy `.glb` file to `visual_engine/godot_project/assets/models/`
2. Copy textures to `visual_engine/godot_project/assets/textures/`
3. In Godot:
   - Drag `.glb` into scene
   - Replace placeholder mesh in `VictorHead` node
   - Assign custom shader material to helmet mesh
   - Configure blendshape paths in `VictorController.gd`

---

## Testing Checklist

After import:

- [ ] Model appears in scene at correct scale
- [ ] Materials display correctly (PBR properties)
- [ ] Emissive mask creates visible glow
- [ ] Blendshapes can be manually adjusted
- [ ] Eye bones can be rotated
- [ ] Jaw bone can be rotated
- [ ] No visual artifacts (z-fighting, inverted normals)
- [ ] Model runs at 60+ FPS

---

## Placeholder Until Production Model

Current placeholder: Simple sphere mesh

To improve placeholder:
```gdscript
# In Godot, create basic geometric helmet
var helmet_mesh = CylinderMesh.new()
helmet_mesh.top_radius = 0.4
helmet_mesh.bottom_radius = 0.5
helmet_mesh.height = 0.8
```

Or use a free CC0 robot/helmet model from:
- Sketchfab (CC0 license)
- Poly Pizza
- Quaternius (free low-poly assets)

---

## Future Enhancements

**Version 2.0+:**
- Full body model
- Holographic projection base
- Multiple helmet variants (battle, advisor, oracle modes)
- Animated panel sections (open/close)
- Integrated HUD elements on visor

---

**Model Artist Notes:**

This spec prioritizes:
1. **Performance** - Real-time rendering at 60 FPS
2. **Flexibility** - Shader-driven effects, not baked
3. **Scalability** - Can add detail later via normal maps
4. **Modularity** - Helmet can be swapped/variants

If creating the model:
- Start with block-out in low-poly
- Test export to Godot early
- Iterate on details once base is working
- Keep emissive mask clean (sharp edges)

---

**Contact:** Model creation can be commissioned or created in-house. Budget ~$500-2000 for professional asset.
