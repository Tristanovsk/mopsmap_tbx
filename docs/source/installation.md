# Installation

## MOPSMAP

The toolbox drives the MOPSMAP Fortran code, which must be installed separately
together with its optical dataset (see the
[MOPSMAP website](https://mopsmap.net) and
Gasteiger and Wiegner, 2018, [doi:10.5194/gmd-11-2739-2018](https://doi.org/10.5194/gmd-11-2739-2018)).

The location of the MOPSMAP executable and data directory is set at the top of
each script and notebook (`mopsmap_dir`, `path_mopsmap_executable`,
`path_optical_dataset`): adjust these to your installation.

## mopsmap_tbx

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/Tristanovsk/mopsmap_tbx.git
cd mopsmap_tbx
pip install -e .
```

The notebook `notebook/sensitivity_marine_particles.ipynb` also needs
[miepython](https://github.com/scottprahl/miepython) for the exact Mie computations:

```bash
pip install miepython
```

## Building the documentation

```bash
pip install -r docs/requirements.txt
cd docs
make html
```

The HTML pages are written to `docs/build/html`.
