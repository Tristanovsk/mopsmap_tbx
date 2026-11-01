# Changelog

All notable changes to `mopsmap_tbx` are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- pip-installable package (`pyproject.toml`, `mopsmap_tbx.__version__`).
- Sphinx documentation (`docs/`) and Read the Docs configuration: README landing
  page, installation and scripts pages, tutorial notebooks rendered with MyST-NB
  (moved from `notebook/` to `docs/source/tutorials/`), and API reference
  generated with autosummary.
- `mopsmap_tbx.opac_mopsmap`: shared tools for the OPAC generators
  (`load_components`, `load_types`, `input_info`, `run_mopsmap`,
  `compute_tasks`). The MOPSMAP installation is set with the `MOPSMAP_DIR`
  environment variable.
- NumPy-style docstring for `call_mopsmap`.
- Notebook `notebook/sensitivity_marine_particles.ipynb` (also in the docs):
  sensitivity of the efficiency factors, single scattering albedo, asymmetry
  parameter, backscattering ratio and scattering matrix of marine particles
  (spheres, refractive index relative to seawater) to the real part of the
  refractive index (1.02 to 1.20), four spectral shapes of the imaginary part and
  eight power-law and log-normal size distributions (r <= 40 µm), at the
  Sentinel-3/OLCI bands. MOPSMAP is used at its dataset nodes (1.04 to 1.20) and
  exact Mie (`miepython`, Dask processes scheduler) at 1.02, with a Mie vs MOPSMAP
  cross-check at 1.04.
- Notebook `notebook/sensitivity_nonspherical_particles.ipynb` (also in the
  docs): effect of non-sphericity on the efficiency factors, backscattering
  ratio, asymmetry parameter, depolarization ratio and scattering matrix of
  marine particles, with MOPSMAP randomly oriented spheroids (oblate and prolate,
  aspect ratios 1.2, 2, 3, and a log-normal aspect-ratio mixture) compared with
  spheres, for m_r = 1.04 to 1.20 and cross-section-equivalent radii <= 40 µm.
  Spheroids with an aspect ratio of 1.2 serve as near-spherical reference to
  separate the shape effect from the T-matrix/geometric-optics vs Mie methods.
- Notebook `notebook/sensitivity_multilayer_particles.ipynb` (also in the
  docs): optical properties of multilayered marine particles with exact
  multilayer Mie theory (`scattnlay`): two-layer particles (core m = 1.02 and
  chloroplast-like shell of m = 1.06 to 1.20 and 10 to 50 % of the volume) and
  three-layer particles with a silica- or calcite-like outer wall, compared
  with homogeneous spheres of volume-averaged refractive index, for
  non-absorbing particles and pigments confined to the chloroplast layer.
- Notebook `notebook/sensitivity_core_particles.ipynb` (also in the docs):
  marine particles with a dense core mimicking the nucleus or other organelles
  (m = 1.04 to 1.20, 5 to 25 % of the volume) in a cytoplasm of m = 1.02, and
  three-layer cells with an organelle core, cytoplasm and chloroplast layer,
  compared with homogeneous spheres of volume-averaged refractive index.
- Multilayer notebooks limit BLAS to one thread per worker process, which
  avoids stalled computations on many-core machines.
- `compute_tasks(progress=False)` to disable the progress bar.

### Changed

- `opac_component_gen` and `opac_gen` run the independent MOPSMAP computations in
  parallel as `dask.delayed` tasks with the threaded scheduler (one run per CPU by
  default, `main(num_workers=...)`), each in its own temporary directory instead
  of a shared hard-coded `input.txt`. The generated MOPSMAP inputs are unchanged.
- `opac_component_gen` and `opac_gen` no longer run on import: use
  `python -m mopsmap_tbx.opac_component_gen` / `python -m mopsmap_tbx.opac_gen`
  or `main()`. Paths to `data/` and `scatmat/` are resolved from the repository
  root instead of the working directory.
- `xarray` `.drop` replaced by `.drop_vars`.

### Fixed

- `opac_component_gen` skipped the components with `rmax` <= 10 (MITR): they are
  now computed with a single try at `rmax`.
- `call_mopsmap` raises `ValueError` when the shapes of `n`, `r_mod` and `sigma`
  do not agree, instead of exiting without message.
- Unused `np.trapz` call removed from `opac_osoaa_ascii` (deprecated in NumPy 2).
- `SyntaxWarning: invalid escape sequence` in the plot labels of the
  visualization scripts (Python >= 3.12).
