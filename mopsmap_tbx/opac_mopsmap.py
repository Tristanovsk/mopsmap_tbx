"""Shared tools to build MOPSMAP inputs for the OPAC aerosols and run MOPSMAP.

MOPSMAP runs are independent of each other, so they are wrapped in
:func:`dask.delayed` tasks and computed together with :func:`compute_tasks`.
Each run writes its input file in its own temporary directory, which keeps
concurrent runs from overwriting each other.
"""

import os
import subprocess
import tempfile
from pathlib import Path

import dask
import numpy as np
import pandas as pd
from dask.diagnostics import ProgressBar

opj = os.path.join

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
SCATMAT_DIR = ROOT / 'scatmat'

# MOPSMAP installation, can be set with the MOPSMAP_DIR environment variable
MOPSMAP_DIR = os.environ.get('MOPSMAP_DIR', '/sat_data/vrtc/aerosol/mopsmap')
MOPSMAP_EXE = opj(MOPSMAP_DIR, 'mopsmap')
MOPSMAP_DATA = opj(MOPSMAP_DIR, 'data')

RHS = [0, 50, 70, 80, 90, 95, 98, 99]

# -- Write scattering angle file
# ang = np.concatenate([[0,0.001,0.005,0.01,0.05,0.1,0.2,0.3,0.4],np.arange(0.5,180.1,0.5)])
# pd.DataFrame(ang).to_csv(opj(MOPSMAP_DATA,'scat_angle_grid.txt'),index=False)


def load_components(file=DATA_DIR / 'opac_aerosol_components.csv'):
    """OPAC aerosol components indexed by their short name (e.g. WASO)."""
    components = pd.read_csv(file, skiprows=1, index_col=[1])
    components['logS'] = np.log(components.sigma)
    return components


def load_types(file=DATA_DIR / 'opac_aerosol_types.csv'):
    """Number concentration of the components for each OPAC aerosol type."""
    return pd.read_csv(file, index_col=[0])


class input_info:
    def __init__(self, output_file='test.nc', dataroot=''):
        self.dataroot = dataroot
        self.output_file = output_file

    def write_mode(self, imode, rmed_N, sigma,
                   Nparticle=1, r_min=1e-3, r_max=60,
                   refra_file='refr_water_soluble',
                   shape='sphere',
                   kappa=0):
        mode = 'mode %d size log_normal %f %f %f %f %f\n' % (
            imode, rmed_N, sigma, Nparticle, r_min, r_max)
        mode += 'mode %d refrac file "%s"\n' % (imode, opj(self.dataroot, refra_file))
        mode += 'mode %d shape %s\n' % (imode, shape)
        mode += 'mode %d kappa %s\n' % (imode, kappa)
        return mode

    def write_component(self, imode, c, r_max, Nparticle=1):
        """Mode of OPAC component `c` (row of :func:`load_components`)."""
        if c['shape'] == 'sphere':
            shape = 'sphere'
        elif c['shape'] == 'spheroid':
            shape = 'spheroid distr_file "' + opj(self.dataroot, 'ar_kandler') + '"'
        else:
            raise ValueError('unknown shape: %s' % c['shape'])
        return self.write_mode(imode, c.rmed_N, c.sigma, Nparticle=Nparticle, r_max=r_max,
                               refra_file=c.refrac_index_file, shape=shape, kappa=c['kappa'])

    def write_info(self,
                   rel_humidity=0,
                   water_refrac_file="refr_water_segelstein",
                   wavelength='range 0.4 2.4 0.1',
                   theta_file='scat_angle_grid.txt',
                   scatlib='optical_dataset'):
        info = 'size_equ cs\n'
        info += 'rH %d\n' % rel_humidity
        info += 'water_refrac_file "%s"\n' % opj(self.dataroot, water_refrac_file)
        info += 'wavelength %s\n' % wavelength
        info += 'output theta_file "%s"\n' % opj(self.dataroot, theta_file)
        info += 'scatlib "%s"\n' % opj(self.dataroot, scatlib)
        info += 'output netcdf "%s" reff\n' % self.output_file
        return info


def run_mopsmap(input_text, mopsmap_exe=MOPSMAP_EXE):
    """Run MOPSMAP on `input_text` in a temporary directory.

    Returns the MOPSMAP log (stdout and stderr). Output paths in
    `input_text` must be absolute.
    """
    with tempfile.TemporaryDirectory(prefix='mopsmap_') as tmpdir:
        input_file = opj(tmpdir, 'input.txt')
        with open(input_file, 'w') as w:
            w.write(input_text)
        res = subprocess.run([mopsmap_exe, input_file], cwd=tmpdir,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return res.stdout


def compute_tasks(tasks, num_workers=None):
    """Compute a list of :func:`dask.delayed` tasks with a progress bar.

    MOPSMAP runs in a subprocess and the GIL is released while waiting for
    it, so the threaded scheduler is enough to run `num_workers` MOPSMAP
    instances at a time (default: number of CPUs).
    """
    with ProgressBar():
        return dask.compute(*tasks, scheduler='threads', num_workers=num_workers)
