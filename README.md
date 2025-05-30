# UR-MAT: URban MATerials Dataset

**UR-mat** (*Urban Materials Dataset*) is a multimodal, material-aware synthetic dataset designed for 3D scene understanding, semantic segmentation, and electromagnetic simulation in urban environments. It includes RGB images, depth maps, material segmentation masks, point clouds, camera poses, 3D meshes, and physical material metadata, all generated from diverse urban scenarios.

## 🏙️ Overview

UR-mat features **6 urban scenes** with diverse architecture and materials:
- Louvre (Paris)
- Trastevere (Rome)
- CityLife (Milan)
- Canary Wharf (London)
- Siemensstadt (Berlin)
- Eixample (Barcelona)

Each scene includes:
- Realistic material annotations
- Physically grounded metadata (permittivity, reflectance, attenuation)
- Multiview synthetic camera data

## 📦 Dataset Contents

Each scene is organized into:
- `UR-MAT/`
  - `train/`
  - `val/`
  - `test/`
  - `metadata/`
  - `scene_physical_metadata.json`
  - `segmentation_classes.json`

Modalities:
- `rgb/` — Rendered RGB images
- `seg/` — Per-pixel material segmentation masks
- `depth/` — Depth maps (.npy)
- `pcd/` — 3D point clouds (.ply)
- `poses/` — Camera parameters (intrinsics, extrinsics)
- `mesh.glb` — Annotated 3D scene mesh
- `scene_physical_metadata.json` — Material metadata with physical properties

## 🛠️ Tools & Scripts

This repository includes two utility scripts:

### 🔹 `extract_material_sections.py`
Extracts per-object and per-section material assignments from Unreal Engine and stores them as JSON.

### 🔹 `annotate_material_metadata.py`
Classifies Unreal materials into high-level material types (e.g., Glass, Limestone) and assigns physical properties like permittivity and reflectance.

## 📜 License

The dataset and accompanying tools are released under the **Creative Commons Attribution 4.0 International (CC-BY 4.0)** license.

## 📎 Citation

If you use UR-mat in your research, please cite:


## 🤝 Acknowledgments
UR-mat is built using open and source-available tools:

- [OpenStreetMap](https://www.openstreetmap.org/#map=17/41.868994/12.445643)
- [OSM2World](https://osm2world.org/)
- [Unreal Engine](https://www.unrealengine.com/en-US)
- [UnrealCV](https://unrealcv.org/)
