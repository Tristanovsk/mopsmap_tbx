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

The notebook `notebook/sensitivity_multilayer_particles.ipynb` needs
[scattnlay](https://github.com/ovidiopr/scattnlay) (GPL-3.0) for the multilayer
Mie computations:

```bash
pip install scattnlay
```

In an Anaconda environment, its import can fail with `GLIBCXX_3.4.32 not found`
when the extension is compiled with a newer compiler than the C++ runtime of the
environment: update the runtime (`conda install -c conda-forge "libstdcxx-ng>=13"`)
or start Jupyter with `LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6`.

## Building the documentation

```bash
pip install -r docs/requirements.txt
cd docs
make html
```

The HTML pages are written to `docs/build/html`.
