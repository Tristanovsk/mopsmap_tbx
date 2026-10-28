import numpy as np
import subprocess
import collections

# needs to be adjusted to your installation
path_optical_dataset = '../optical_dataset/'
path_mopsmap_executable = '../mopsmap'


def call_mopsmap(wvl, size_equ, n, r_mod, sigma, r_min, r_max, m, nonabs_fraction, shape, num_theta):
    """Run MOPSMAP for (multi-modal) log-normal size distributions.

    Writes the input files ``tmp_mopsmap.inp`` and ``tmp_mopsmap.wvl`` in the
    current directory and runs the executable ``path_mopsmap_executable``
    with the optical dataset ``path_optical_dataset`` (module variables to
    adjust to your installation). Results are written by MOPSMAP to the
    ASCII files ``tmp_mopsmap.*``.

    Parameters
    ----------
    wvl : float or list of float
        Wavelength(s).
    size_equ : str
        Size equivalence.
    n, r_mod, sigma : float or list of float
        Parameters of the log-normal size modes (lists of same length, one
        value per mode).
    r_min, r_max : float or list of float
        Minimum and maximum radii, applied to all modes if a single value.
    m : str or list of str
        Refractive index, added in the input file after ``refrac``; applied
        to all modes if a single string.
    nonabs_fraction : float or list of float
        Ratio of non-absorbing particles; applied to all modes if a single
        value.
    shape : str or list of str
        Particle shape, added in the input file after ``shape``; applied to
        all modes if a single string.
    num_theta : int
        Number of scattering angles in output.
    """
    # create a input file for the Fortran code and a wavelength file
    mopsmap_input_file = open('tmp_mopsmap.inp', 'w')
    mopsmap_wvl_file = open('tmp_mopsmap.wvl', 'w')

    # write wavelength file
    wvl = np.array(wvl, ndmin=1)
    mopsmap_input_file.write("wavelength file tmp_mopsmap.wvl \n")
    for i_wvl in range(wvl.shape[0]):
        mopsmap_wvl_file.write('%10.8f \n' % wvl[i_wvl])
    mopsmap_wvl_file.close()

    # write size_equ
    mopsmap_input_file.write('size_equ %s\n' % size_equ)

    # write modes
    n = np.array(n, ndmin=1)
    r_mod = np.array(r_mod, ndmin=1)
    sigma = np.array(sigma, ndmin=1)
    r_min = np.array(r_min, ndmin=1)
    r_max = np.array(r_max, ndmin=1)
    if n.shape != r_mod.shape or n.shape != sigma.shape:
        raise ValueError("shapes of n, r_mod, and sigma do not agree")
    if n.shape[0] > 1 and r_min.shape[0] == 1:
        r_min = np.resize(r_min, n.shape[0])
        r_min[:] = r_min[0]
    if n.shape[0] > 1 and r_max.shape[0] == 1:
        r_max = np.resize(r_max, n.shape[0])
        r_max[:] = r_max[0]

    if isinstance(m, str):
        m = [m, ]
    if n.shape[0] > 1 and len(m) == 1:
        for i in range(1, n.shape[0]):
            m.append(m[0])

    if isinstance(nonabs_fraction, (int, float, complex)):
        nonabs_fraction = [nonabs_fraction, ]
    if n.shape[0] > 1 and len(nonabs_fraction) == 1:
        for i in range(1, n.shape[0]):
            nonabs_fraction.append(nonabs_fraction[0])

    if isinstance(shape, str):
        shape = [shape, ]
    if n.shape[0] > 1 and len(shape) == 1:
        for i in range(1, n.shape[0]):
            shape.append(shape[0])

    for i_mode in range(n.shape[0]):
        mopsmap_input_file.write('mode %d size log_normal %f %f %f %f %f\n' % (
        i_mode + 1, r_mod[i_mode], sigma[i_mode], n[i_mode], r_min[i_mode], r_max[i_mode]))
        mopsmap_input_file.write('mode %d refrac %s\n' % (i_mode + 1, m[i_mode]))
        mopsmap_input_file.write('mode %d refrac nonabs_fraction %f\n' % (i_mode + 1, nonabs_fraction[i_mode]))
        mopsmap_input_file.write('mode %d shape %s\n' % (i_mode + 1, shape[i_mode]))

    mopsmap_input_file.write('scatlib \'%s\'\n' % path_optical_dataset)
    mopsmap_input_file.write('output integrated\n')
    mopsmap_input_file.write('output scattering_matrix\n')
    mopsmap_input_file.write('output volume_scattering_function\n')
    mopsmap_input_file.write('output num_theta %i\n' % num_theta)
    mopsmap_input_file.write('output lidar\n')
    mopsmap_input_file.write('output digits 15\n')
    mopsmap_input_file.write('output ascii_file tmp_mopsmap\n')

    mopsmap_input_file.close()

    # after writing the input file now start mopsmap
    p = subprocess.Popen([path_mopsmap_executable, 'tmp_mopsmap.inp'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         close_fds=True)
    stdout1, stderr1 = p.communicate()