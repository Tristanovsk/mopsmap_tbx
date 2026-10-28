"""Scattering matrices of the OPAC aerosol types for several relative humidities.

Each type is an external mixture of the OPAC components weighted by their
number fraction. Run from the command line: ``python -m mopsmap_tbx.opac_gen``
"""

import os

import dask
import numpy as np

from mopsmap_tbx.opac_mopsmap import (MOPSMAP_DATA, RHS, SCATMAT_DIR, compute_tasks,
                                      input_info, load_components, load_types, run_mopsmap)

opj = os.path.join

wl_min = 0.35
wl_max = 2.6


def type_input(opac_, components, rh, ofile):
    """MOPSMAP input of OPAC type `opac_` (row of :func:`load_types`)."""
    rh_num = rh / 100
    imode = 0
    input = ""
    info = input_info(output_file=ofile, dataroot=MOPSMAP_DATA)
    # normalization of particle number
    norm = np.sum(opac_.iloc[1:])
    for component, Ni in opac_.iloc[1:].items():
        if Ni == 0:
            continue

        Ni_norm = Ni / norm
        imode += 1
        c = components.loc[component]
        rmax = c['rmax']
        growth = (1 + c['kappa'] * rh_num / (1 - rh_num)) ** (1. / 3)
        xparam = 2 * np.pi * rmax / wl_min * growth
        # fix for the incomplete mopsmap x-parameter (upper value around 1010)
        if xparam > 1010:
            rmax = 1010 * wl_min / (2 * np.pi * growth)

        input += info.write_component(imode, c, r_max=rmax, Nparticle=Ni_norm)

    input += info.write_info(wavelength='range {:.3f} {:.3f} 0.05'.format(wl_min, wl_max), rel_humidity=rh)
    return input


@dask.delayed
def type_task(name, input, ofile):
    """Run MOPSMAP for one OPAC type; returns the output file, or None on error."""
    log = run_mopsmap(input)
    if 'Error' in log:
        print('MOPSMAP failed for', name, ':', log)
        return None
    return ofile


def main(rhs=RHS, odir=opj(SCATMAT_DIR, 'types'), overwrite=True, num_workers=None):
    components = load_components()
    opac = load_types()
    os.makedirs(odir, exist_ok=True)
    tasks = []
    for rh in rhs:
        for name, opac_ in opac.iterrows():
            ofile = opj(odir, name + '_rh{:d}_scatmat.nc'.format(rh))
            if not overwrite and os.path.exists(ofile):
                continue
            input = type_input(opac_, components, rh, ofile)
            tasks.append(type_task(name + '_rh{:d}'.format(rh), input, ofile))
    return compute_tasks(tasks, num_workers=num_workers)


if __name__ == '__main__':
    main()
