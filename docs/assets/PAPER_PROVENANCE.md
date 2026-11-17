# UR-MAT source assets

Original source: Russo, Mazzocca and Vittorini, *UR-MAT: A Multimodal, Material-Aware Synthetic Dataset of Urban Scenarios*, ACM Multimedia 2025. DOI: https://doi.org/10.1145/3746027.3758314. Paper licensed CC BY 4.0.

The following image streams were extracted losslessly from the author's local `Downloads/ACMMM2025_URMAT.pdf` using PyMuPDF `extract_image`:

| Asset | Paper location | Embedded resolution |
| --- | --- | --- |
| paper-pipeline.jpeg | Figure 1, page 3 | 3117 × 1282 |
| paper-segmentation-a.png | Figure 2, top row, page 5 | 3580 × 968 |
| paper-segmentation-b.png | Figure 2, middle row, page 5 | 3580 × 968 |
| paper-segmentation-c.png | Figure 2, bottom row, page 5 | 3580 × 968 |
| paper-ray-tracing.png | Figure 3, page 6 | 786 × 591 |

Each segmentation row contains RGB input, ground truth, and prediction, in that order. These are the original ACM 2025 qualitative results.

`louvre_ds_rgb.png`, `louvre_ds_depth.png`, `louvre_ds_material.png`, and `louvre_ds_mesh.png` were copied unchanged from the author's local thesis source `6aa74b26d7623bd9e52cc0be/figs/ch3/`. They are example dataset modality illustrations, not new experimental results. Validate correspondence with desktop source samples before using an interactive aligned overlay.

`paper-metrics.json` transcribes dataset scale from page 3, experimental setup and reported metrics from page 4, Table 3 class IoUs from page 4, and scene list from Table 2 on page 4. It describes the original seven-scene paper release. Keep separate from the later eight-scene Zenodo v3 release (record 18911512).

The thesis also includes different later journal experiments. Those values and figures were intentionally excluded from this bundle to avoid mixing experimental protocols.
