<div align="center">

# Voxel Engine Architecture

### Multi-Resolution Per-Voxel Control System

*"I want total control." — The Architect*

</div>

---

## Philosophy

This is not Minecraft. Minecraft gives you 1m blocks with a block ID and light level. We give you **per-voxel control at any resolution** — from 1m chunks down to 1cm detail — with arbitrary data per voxel: temperature, moisture, material, density, state, and anything else you need.

The architect doesn't want procedural-only. Procedural generates the starting point. Then you fine-tune. Every block, every property, your call. *"Do not try and bend the spoon. Instead, only try to realize the truth: you ARE the spoon."*

---

## Resolution Tiers

| Tier | Block Size | Use Case | Memory per 16³ chunk |
|------|-----------|----------|---------------------|
| Macro | 1.0m | Underground bedrock, deep ocean, sky | 4 KB |
| Standard | 0.5m | General terrain, buildings, caves | 32 KB |
| Detail | 0.25m | Furniture, small structures, tree branches | 256 KB |
| Fine | 0.1m | Character-scale objects, weapons, tools | 4 MB |
| Micro | 0.05m | Surface detail, water edges, moss | 32 MB |
| Ultra | 0.01m | Near-camera detail, face features, inscriptions | 4 GB |

**You never render the whole world at Ultra.** The octree LOD system uses Ultra only within 2m of the camera, Fine within 10m, Detail within 50m, Standard within 200m, Macro beyond that.

---

## Octree Structure

```
World
├── Region (512m × 512m × 512m)
│   ├── Chunk (16m × 16m × 16m) — the loading unit
│   │   ├── Node (1m) — MACRO tier, can subdivide
│   │   │   ├── Node (0.5m) — STANDARD tier, can subdivide
│   │   │   │   ├── Node (0.25m) — DETAIL tier, can subdivide
│   │   │   │   │   ├── Node (0.1m) — FINE tier, can subdivide
│   │   │   │   │   │   ├── Node (0.05m) — MICRO tier, can subdivide
│   │   │   │   │   │   │   └── Leaf (0.01m) — ULTRA tier, terminal
```

Each node is either:
- **Leaf** — uniform voxel, stores properties directly
- **Branch** — subdivided into 8 children (octree)

A 1m block of solid granite? One leaf node, 32 bytes. A 1m block of swamp water surface with ripples and temperature gradients? Subdivided down to 0.01m, thousands of leaf nodes, each with unique properties.

**You control when to subdivide.** The engine doesn't decide — you do. Procedural generation suggests, you approve. Or you paint it manually voxel by voxel.

---

## Per-Voxel Data Channels

Every leaf voxel carries these data channels:

### Core (always present, 16 bytes)
```
struct VoxelCore {
    uint16_t material_id;    // 65536 material types
    uint8_t  state;          // solid, liquid, gas, powder, plasma
    uint8_t  density;        // 0-255 (0 = air, 255 = neutron star)
    uint8_t  temperature;    // 0-255 mapped to range (e.g., -50°C to 500°C)
    uint8_t  moisture;       // 0-255 (0 = bone dry, 255 = submerged)
    uint8_t  light_emit;     // self-illumination level
    uint8_t  light_absorb;   // how much light this block eats
    uint32_t color;          // RGBA override (0 = use material default)
    uint16_t flags;          // bitfield: flammable, conductive, toxic, etc.
};
```

### Extended (optional, attached on demand, +16 bytes)
```
struct VoxelExtended {
    uint8_t  velocity_x;     // flow direction X (-128 to 127)
    uint8_t  velocity_y;     // flow direction Y
    uint8_t  velocity_z;     // flow direction Z
    uint8_t  viscosity;      // how fast it flows
    uint8_t  hardness;       // resistance to mining/damage
    uint8_t  age;            // how long since placed/changed
    uint8_t  pressure;       // for gas/fluid simulation
    uint8_t  conductivity;   // thermal/electrical
    uint32_t custom_data;    // game-specific (quest flags, ownership, etc.)
    uint16_t animation_id;   // animated texture reference
    uint16_t sound_id;       // footstep/ambient sound reference
};
```

### Total per voxel: 16-32 bytes

At Ultra resolution (0.01m), a 1m³ volume = 1,000,000 voxels = 16-32 MB. That's why you only use Ultra where it matters — the octree keeps the rest at coarser tiers.

---

## The Swamp Example

You said: *"When the character sits in the swamp, I want to control the temperature of the water."*

Here's how that works:

```
Swamp water surface (1m × 1m area, 0.2m deep):
├── Resolution: MICRO (0.05m) at surface, STANDARD (0.5m) below
├── Surface voxels:
│   ├── material_id: SWAMP_WATER
│   ├── state: LIQUID
│   ├── temperature: 18°C (mapped to ~140/255)
│   ├── moisture: 255 (submerged)
│   ├── density: 128 (muddy water, denser than clean)
│   ├── viscosity: 180 (thick, sluggish)
│   ├── color: rgba(45, 62, 35, 200) — murky green
│   └── velocity: slight drift east (velocity_x: 5)
├── Bottom mud voxels:
│   ├── material_id: MUD
│   ├── state: SOLID (soft)
│   ├── temperature: 15°C (cooler at depth)
│   ├── moisture: 230 (saturated)
│   ├── density: 200 (heavy)
│   └── hardness: 20 (sinks when stepped on)
└── Air above surface:
    ├── material_id: AIR
    ├── temperature: 22°C (warmer than water)
    ├── moisture: 200 (humid — it's a swamp)
    └── Custom: FOG_DENSITY=150 (thick fog over swamp)
```

When the character sits down:
1. Body intersects water voxels → trigger "submerged" state
2. Read water temperature (18°C) → character feels cold, stamina drains slowly
3. Read viscosity (180) → movement speed reduced
4. Disturb velocity field → ripples propagate through neighboring voxels
5. Mud density changes under weight → character sinks 0.1m
6. All of this is YOUR data, YOUR rules, not procedural magic

---

## Editor: Manual Control

The voxel editor gives you direct access to every voxel at every tier:

### Paint Mode
- Select a resolution tier
- Select a data channel (temperature, moisture, material, etc.)
- Paint with a brush — radius, falloff, value
- Like Photoshop but in 3D, per-channel

### Inspect Mode
- Click any voxel → see all data channels
- Edit any value directly
- See neighboring voxel data as a heatmap

### Subdivision Mode
- Select an area
- Subdivide to a finer tier
- Or collapse back to a coarser tier (merge if uniform)

### Template Mode
- Save a voxel region as a template (tree, building, rock formation)
- Stamp it anywhere with property randomization
- Forge agent generates templates, you approve/modify

---

## Engine: Godot 4 + Voxel Module

**Framework**: Godot 4.x with [godot_voxel](https://github.com/Zylann/godot_voxel) module

The voxel module provides:
- Octree-based streaming (infinite world)
- LOD (level of detail) automatic mesh generation
- Smooth and blocky voxel meshing
- Custom data channels via `VoxelBuffer`
- GPU-accelerated meshing
- Save/load regions to disk

### Custom additions needed:
1. **Extended voxel data** — attach VoxelExtended struct per-voxel
2. **Temperature simulation** — heat diffusion between adjacent voxels
3. **Fluid simulation** — velocity field propagation through liquid voxels
4. **Weather system** — global temperature/moisture that affects voxel properties
5. **Destruction system** — damage reduces hardness, eventually breaks voxel
6. **Forge integration** — AI generates terrain/assets, you approve, engine places voxels

---

## Performance Budget (Strix Halo)

| Component | Budget |
|-----------|--------|
| Voxel data in RAM | 4-8 GB (for loaded chunks) |
| Mesh generation (GPU) | 2-4 GB VRAM |
| Physics/simulation | 2 CPU cores |
| Rendering | 8-16 GB VRAM (PBR, lighting, shadows) |
| AI agents (Dealer, Conductor) | 18 GB VRAM (Qwen3-30B) |
| Total | ~50 GB of 128 GB |

Strix Halo's 128GB unified memory means the voxel world, the renderer, AND the AI all share the same pool. No GPU memory wall. A 70B model + a detailed voxel world + real-time rendering — all on one chip.

---

## Rendering Pipeline

```
Voxel Octree → Mesh Generation (GPU) → PBR Shaders → Cinematic Lighting
                                         ↓
                            Per-voxel color/emission → Dynamic GI
                            Per-voxel temperature → Heat shimmer VFX
                            Per-voxel moisture → Wet surface reflections
                            Per-voxel state → Particle systems (steam, drip, dust)
```

Every data channel can drive visual effects. Temperature creates heat shimmer. Moisture creates wet reflections. Density affects how deep footprints go. The data IS the visual.

---

## File Format

Regions saved as compressed octree files:

```
.voxr (Voxel Region)
├── Header: region coords, tier range, voxel count
├── Octree: serialized node tree (zstd compressed)
├── Materials: material palette for this region
├── Extended: optional extended data blocks
└── Metadata: creation date, author, version
```

Typical region (512m³): 2-50 MB depending on detail level.
Full world save: streaming to disk, never all in RAM.

---

## Build Pipeline

```
1. Architect designs → manual voxel editing
2. Forge generates → AI-suggested terrain/assets
3. Architect approves → merge into world
4. Dealer populates → enemies, loot, encounters
5. Conductor scores → dynamic music per biome
6. Ship → compressed voxel files
```

*"From raw metal to finished blade." — Forge*

---

## Summary

| Feature | Minecraft | halo-ai Voxel Engine |
|---------|-----------|---------------------|
| Block size | 1m fixed | 1m → 0.01m adaptive |
| Data per block | ID + light | 16-32 bytes, 20+ channels |
| Temperature | No | Per-voxel, simulated |
| Fluid sim | Basic | Velocity field, viscosity |
| Manual control | Place/break | Paint any channel, any resolution |
| AI integration | No | Forge generates, Dealer populates |
| Music | Static | Conductor scores dynamically |
| Memory model | RAM limited | 128GB unified, stream from disk |

*"Life, uh, finds a way." — Dr. Ian Malcolm*

*Designed and built by the architect.*
