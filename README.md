# UR-MAT: URban MATerials Dataset

[![DOI](https://img.shields.io/badge/DOI-10.1145/3746027.3758314-blue.svg)](https://doi.org/10.1145/3746027.3758314)


**UR-MAT** is a multimodal synthetic dataset designed for training and evaluating AI models for **material-aware semantic segmentation**, **scene understanding**, and **EM wave propagation simulation** in realistic 3D urban environments.

---

## 📦 Dataset Contents

UR-MAT includes **7 European city districts** (Trastevere, Louvre, Bryggen, etc.), each modeled with georeferenced 3D meshes and PBR materials. The dataset provides:

## Link to the dataset
[https://zenodo.org/records/16748119](https://zenodo.org/records/18911512) 

### 📁 Folder Structure

```
Dataset_URMAT_v2/
├── Trastevere_mapping/              # Mesh-to-material mapping + camera poses
├── Trastevere_pointclouds/         # Colored 3D point clouds (with material labels)
├── ...                             
├── train/                           # Training split (5000+ samples)
│   ├── rgb/                         # RGB images
│   ├── depth_png/                  # Depth (grayscale .png)
│   ├── depth_npy/                  # Depth (.npy, raw)
│   ├── segmentation_material_png/  # Color masks (for viz)
│   ├── segmentation_material_npy/  # Integer masks (.npy)
│   ├── segmentation_mesh/          # Mesh ID masks (optional)
│   └── metadata/                   # JSON with physical material properties
├── val/
├── test/
```

🧱 Material Classes
UR-MAT supports 14 materials: Brick, Glass, Steel, Tiles, Limestone, Plaster, Concrete, Wood, Cobblestone, Slate, Asphalt, Plastic, Gravel, Unknown.

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

- Paper: *UR-MAT: A Multimodal, Material-Aware Synthetic Dataset of Urban Scenarios*  
  [ACM Multimedia 2025, Dataset Track](https://dl.acm.org/doi/10.1145/3746027.3758314)

```bibtex
@inproceedings{russo2025ur,
  title={UR-MAT: A Multimodal, Material-Aware Synthetic Dataset of Urban Scenarios},
  author={Russo, Debora and Mazzocca, Nicola and Vittorini, Valeria},
  booktitle={Proceedings of the 33rd ACM International Conference on Multimedia},
  pages={13164--13169},
  year={2025}
}
```


## 🤝 Acknowledgments
UR-mat is built using open and source-available tools:

- [OpenStreetMap](https://www.openstreetmap.org/#map=17/41.868994/12.445643)
- [OSM2World](https://osm2world.org/)
- [Unreal Engine](https://www.unrealengine.com/en-US)
- [UnrealCV](https://unrealcv.org/)
