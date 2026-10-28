"""Scattering matrices of the OPAC components for several relative humidities.

Run from the command line: ``python -m mopsmap_tbx.opac_component_gen``
"""

import os

import dask

from mopsmap_tbx.opac_mopsmap import (MOPSMAP_DATA, RHS, SCATMAT_DIR, compute_tasks,
                                      input_info, load_components, run_mopsmap)

opj = os.path.join


@dask.delayed
def component_task(name, c, rh, ofile):
    """Run MOPSMAP for component `name` at relative humidity `rh`.

    MOPSMAP fails when the size parameter exceeds its optical dataset, so
    `rmax` is decreased down to 11 until it succeeds (single try if
    `rmax` <= 10). Returns the output file, or None if every run failed.
    """
    info = input_info(output_file=ofile, dataroot=MOPSMAP_DATA)
    for rmax in range(c['rmax'], min(10, c['rmax'] - 1), -1):
        input = info.write_component(1, c, r_max=rmax)
        input += info.write_info(rel_humidity=rh)
        log = run_mopsmap(input)
        if 'Error' not in log:
            return ofile
    print('MOPSMAP failed for', name, rh, ':', log)
    return None


def main(rhs=RHS, odir=opj(SCATMAT_DIR, 'components'), num_workers=None):
    components = load_components()
    os.makedirs(odir, exist_ok=True)
    tasks = []
    for name, c in components.iterrows():
        for rh in rhs:
            # if hygrophobic compute for rh=0 only
            if c['kappa'] == 0 and rh > 0:
                continue
            ofile = opj(odir, name + '_rh{:d}_scatmat.nc'.format(rh))
            if os.path.exists(ofile):
                continue
            tasks.append(component_task(name, c, rh, ofile))
    return compute_tasks(tasks, num_workers=num_workers)


if __name__ == '__main__':
    main()
