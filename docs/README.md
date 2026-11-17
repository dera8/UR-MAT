# UR-MAT project page

Static GitHub Pages site. Serve `docs/` at `/UR-MAT/`; no build step required.

The page separates the Zenodo v3 release (8 scenes) from the published ACM MM 2025 benchmark (7 scenes). See `assets/paper-metrics.json` for the extracted source results and `assets/PAPER_PROVENANCE.md` for figure provenance.

## Reproduce assets

- `python tools/prepare_site_assets.py` from the repository root prepares aligned frame previews, a GIF wipe and local file counts. It uses the author's Desktop dataset folders and thesis image assets, with Pillow and NumPy.
- `tools/build_geometry_preview.py` documents the geometry-preserving conversion of the author's Bryggen OSM2World GLB. Its local paths can be adjusted to the downloaded source.
- `python tools/fetch_viewer_vendor.py` fetches the pinned Three.js 0.170.0 browser modules and MIT license.

The 3D preview loads only when requested. Its averaged appearance colours are not material-class labels. Geometry counts describe this source file only. GIF playback starts only on request. All interactions support keyboard input; 3D supports arrows and +/- as well as pointer gestures.

Dataset download and licensing information remain with the linked Zenodo record. The repository's existing LICENSE is unchanged; Three.js retains its upstream MIT license.
