#!/usr/bin/env python3
"""
Generate a simple procedural 3D model for Victor's head
Creates a cyberpunk-styled helmet with basic geometry
Output: glTF 2.0 (.glb) format for Godot
"""

import json
import struct
import base64
import math

def create_victor_head_gltf():
    """Create a simple geometric head model for Victor"""
    
    # Define vertices for a simple helmet shape
    # Using a combination of cylinders and boxes to create angular helmet
    vertices = []
    normals = []
    uvs = []
    indices = []
    
    # Create main helmet body (angular cylinder)
    segments = 8  # 8-sided for angular look
    height = 1.0
    radius_top = 0.35
    radius_bottom = 0.4
    
    # Top cap
    for i in range(segments):
        angle = (i / segments) * 2 * math.pi
        x = math.cos(angle) * radius_top
        z = math.sin(angle) * radius_top
        y = height / 2
        vertices.extend([x, y, z])
        normals.extend([0, 1, 0])
        uvs.extend([i / segments, 1.0])
    
    # Bottom cap
    for i in range(segments):
        angle = (i / segments) * 2 * math.pi
        x = math.cos(angle) * radius_bottom
        z = math.sin(angle) * radius_bottom
        y = -height / 2
        vertices.extend([x, y, z])
        normals.extend([0, -1, 0])
        uvs.extend([i / segments, 0.0])
    
    # Center top
    vertices.extend([0, height / 2, 0])
    normals.extend([0, 1, 0])
    uvs.extend([0.5, 1.0])
    center_top_idx = len(vertices) // 3 - 1
    
    # Center bottom
    vertices.extend([0, -height / 2, 0])
    normals.extend([0, -1, 0])
    uvs.extend([0.5, 0.0])
    center_bottom_idx = len(vertices) // 3 - 1
    
    # Create indices for helmet
    # Top cap triangles
    for i in range(segments):
        next_i = (i + 1) % segments
        indices.extend([center_top_idx, i, next_i])
    
    # Bottom cap triangles
    for i in range(segments):
        next_i = (i + 1) % segments
        indices.extend([center_bottom_idx, segments + next_i, segments + i])
    
    # Side quads
    for i in range(segments):
        next_i = (i + 1) % segments
        # Triangle 1
        indices.extend([i, segments + i, next_i])
        # Triangle 2
        indices.extend([next_i, segments + i, segments + next_i])
    
    # Add eyes (simple spheres)
    eye_offset = 0.15
    eye_forward = 0.3
    eye_up = 0.1
    eye_radius = 0.08
    eye_segments = 8
    
    # Left eye
    eye_base_idx = len(vertices) // 3
    for lat in range(eye_segments):
        lat_angle = (lat / eye_segments) * math.pi
        for lon in range(eye_segments):
            lon_angle = (lon / eye_segments) * 2 * math.pi
            x = eye_radius * math.sin(lat_angle) * math.cos(lon_angle) - eye_offset
            y = eye_radius * math.cos(lat_angle) + eye_up
            z = eye_radius * math.sin(lat_angle) * math.sin(lon_angle) + eye_forward
            vertices.extend([x, y, z])
            # Normal for sphere
            nx = math.sin(lat_angle) * math.cos(lon_angle)
            ny = math.cos(lat_angle)
            nz = math.sin(lat_angle) * math.sin(lon_angle)
            normals.extend([nx, ny, nz])
            uvs.extend([lon / eye_segments, lat / eye_segments])
    
    # Eye indices (simplified)
    for lat in range(eye_segments - 1):
        for lon in range(eye_segments):
            next_lon = (lon + 1) % eye_segments
            i1 = eye_base_idx + lat * eye_segments + lon
            i2 = eye_base_idx + lat * eye_segments + next_lon
            i3 = eye_base_idx + (lat + 1) * eye_segments + lon
            i4 = eye_base_idx + (lat + 1) * eye_segments + next_lon
            indices.extend([i1, i3, i2])
            indices.extend([i2, i3, i4])
    
    # Convert to bytes
    vertex_bytes = struct.pack(f'{len(vertices)}f', *vertices)
    normal_bytes = struct.pack(f'{len(normals)}f', *normals)
    uv_bytes = struct.pack(f'{len(uvs)}f', *uvs)
    index_bytes = struct.pack(f'{len(indices)}H', *indices)
    
    # Combine all buffers
    buffer_data = vertex_bytes + normal_bytes + uv_bytes + index_bytes
    
    # Calculate offsets
    vertex_offset = 0
    normal_offset = len(vertex_bytes)
    uv_offset = normal_offset + len(normal_bytes)
    index_offset = uv_offset + len(uv_bytes)
    
    # Create glTF structure
    gltf = {
        "asset": {
            "version": "2.0",
            "generator": "Victor Visual Engine - Procedural Model Generator"
        },
        "scene": 0,
        "scenes": [
            {
                "nodes": [0]
            }
        ],
        "nodes": [
            {
                "mesh": 0,
                "name": "VictorHead"
            }
        ],
        "meshes": [
            {
                "primitives": [
                    {
                        "attributes": {
                            "POSITION": 0,
                            "NORMAL": 1,
                            "TEXCOORD_0": 2
                        },
                        "indices": 3,
                        "material": 0
                    }
                ],
                "name": "VictorHelmet"
            }
        ],
        "materials": [
            {
                "name": "VictorMaterial",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [0.15, 0.15, 0.2, 1.0],
                    "metallicFactor": 0.9,
                    "roughnessFactor": 0.3
                },
                "emissiveFactor": [0.0, 0.8, 0.8]
            }
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,  # FLOAT
                "count": len(vertices) // 3,
                "type": "VEC3",
                "max": [max(vertices[i::3]) for i in range(3)],
                "min": [min(vertices[i::3]) for i in range(3)]
            },
            {
                "bufferView": 1,
                "componentType": 5126,
                "count": len(normals) // 3,
                "type": "VEC3"
            },
            {
                "bufferView": 2,
                "componentType": 5126,
                "count": len(uvs) // 2,
                "type": "VEC2"
            },
            {
                "bufferView": 3,
                "componentType": 5123,  # UNSIGNED_SHORT
                "count": len(indices),
                "type": "SCALAR"
            }
        ],
        "bufferViews": [
            {
                "buffer": 0,
                "byteOffset": vertex_offset,
                "byteLength": len(vertex_bytes),
                "target": 34962  # ARRAY_BUFFER
            },
            {
                "buffer": 0,
                "byteOffset": normal_offset,
                "byteLength": len(normal_bytes),
                "target": 34962
            },
            {
                "buffer": 0,
                "byteOffset": uv_offset,
                "byteLength": len(uv_bytes),
                "target": 34962
            },
            {
                "buffer": 0,
                "byteOffset": index_offset,
                "byteLength": len(index_bytes),
                "target": 34963  # ELEMENT_ARRAY_BUFFER
            }
        ],
        "buffers": [
            {
                "byteLength": len(buffer_data),
                "uri": f"data:application/octet-stream;base64,{base64.b64encode(buffer_data).decode('ascii')}"
            }
        ]
    }
    
    return gltf

def save_glb(gltf_dict, output_path):
    """Save glTF as binary .glb file"""
    # Convert JSON to bytes
    json_data = json.dumps(gltf_dict, separators=(',', ':')).encode('utf-8')
    
    # Pad JSON to 4-byte boundary
    json_padding = (4 - len(json_data) % 4) % 4
    json_data += b' ' * json_padding
    
    # Extract binary buffer from data URI
    buffer_uri = gltf_dict['buffers'][0]['uri']
    buffer_data = base64.b64decode(buffer_uri.split(',')[1])
    
    # Pad binary to 4-byte boundary
    bin_padding = (4 - len(buffer_data) % 4) % 4
    buffer_data += b'\x00' * bin_padding
    
    # Create glTF with embedded buffer (no data URI)
    gltf_embedded = gltf_dict.copy()
    gltf_embedded['buffers'][0] = {"byteLength": len(buffer_data)}
    json_data_embedded = json.dumps(gltf_embedded, separators=(',', ':')).encode('utf-8')
    json_padding = (4 - len(json_data_embedded) % 4) % 4
    json_data_embedded += b' ' * json_padding
    
    # GLB header
    magic = 0x46546C67  # "glTF"
    version = 2
    total_length = 12 + 8 + len(json_data_embedded) + 8 + len(buffer_data)
    
    # JSON chunk
    json_chunk_length = len(json_data_embedded)
    json_chunk_type = 0x4E4F534A  # "JSON"
    
    # Binary chunk
    bin_chunk_length = len(buffer_data)
    bin_chunk_type = 0x004E4942  # "BIN\0"
    
    # Write GLB
    with open(output_path, 'wb') as f:
        f.write(struct.pack('<I', magic))
        f.write(struct.pack('<I', version))
        f.write(struct.pack('<I', total_length))
        
        f.write(struct.pack('<I', json_chunk_length))
        f.write(struct.pack('<I', json_chunk_type))
        f.write(json_data_embedded)
        
        f.write(struct.pack('<I', bin_chunk_length))
        f.write(struct.pack('<I', bin_chunk_type))
        f.write(buffer_data)

def main():
    print("Generating Victor 3D model...")
    gltf = create_victor_head_gltf()
    
    # Save as .glb
    output_path = "visual_engine/godot_project/models/victor_head.glb"
    save_glb(gltf, output_path)
    print(f"✓ Model saved to {output_path}")
    
    # Also save as .gltf (text format) for inspection
    gltf_text_path = "visual_engine/godot_project/models/victor_head.gltf"
    with open(gltf_text_path, 'w') as f:
        json.dump(gltf, f, indent=2)
    print(f"✓ Text format saved to {gltf_text_path}")
    
    print("\nModel details:")
    print(f"  Vertices: {len(gltf['accessors'][0]['max'])}")
    print(f"  Triangles: {gltf['accessors'][3]['count'] // 3}")
    print(f"  Material: Metallic PBR with teal emissive")

if __name__ == "__main__":
    import sys
    import os
    os.chdir('/home/runner/work/Victor_Synthetic_Super_Intelligence/Victor_Synthetic_Super_Intelligence')
    main()
