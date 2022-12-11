import os, sys
import glob
import numpy as np
import netCDF4 as nc
import xarray as xr

# ----------------------------
# set plotting styles
import matplotlib.pyplot as plt
import matplotlib as mpl

plt.ioff()
rc = {"font.family": "serif",
      "mathtext.fontset": "stix"}
plt.rcParams.update(rc)
plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]
plt.rcParams.update({'font.size': 18, 'axes.labelsize': 20})
opj = os.path.join

odir = './scatmat/ascii'

dir = "./"
file = "test.nc"
# ------------------------------------
# load data
# ------------------------------------
scatmat = []
for file in glob.glob('./scatmat/types/*.nc'):
    print(file)
    name, rh = os.path.basename(file).replace('_scatmat.nc', '').split('_')
    ds = xr.open_dataset(file)
    # reset dim and coords for practical use
    ds = ds.rename({'wavelen': 'wl'}).rename({'nlam': 'wl', 'nphamat': 'scamat', 'nthetamax': 'angle'}).set_coords(
        ['wl'])
    scaang = ds.theta.isel(wl=0, scamat=0).squeeze().values
    ds = ds.assign_coords({'angle': scaang}).drop('theta')
    ds = ds.squeeze()
    # put angle in increasing order
    ds = ds.isel(angle=slice(None, None, -1))
    ds['name'] = name
    ds['rh'] = rh
    theta_deg = ds.angle.round(4).values
    theta = np.radians(ds.angle)
    Nang = len(theta)
    for wl_, ds_ in ds.groupby('wl'):
        ofile = opj(odir, 'scat_mat_opac_' + name + '_' + rh + '_wl{:.1f}'.format(wl_ * 1000) + '.csv')
        if os.path.exists(ofile):
            continue
        print(wl_, ofile)
        S11 = ds_.phase.isel(scamat=0)
        np.trapz(S11 * np.sin(theta), theta) / 2
        minusS12 = -ds_.phase.isel(scamat=1) / S11
        S22 = ds_.phase.isel(scamat=4) / S11
        S33 = ds_.phase.isel(scamat=2) / S11
        mat = xr.Dataset({'s11': S11, 'minus_s12': minusS12, 's22': S22, 's33': S33})
        mat = mat.assign_coords(angle=theta_deg)
        df_mat = mat.reset_coords(drop=True).to_pandas()
        Cext = ds_.ext
        ssa = ds_.ssa
        Csca = ssa * Cext
        Cext_ = "{:12.6e}".format(Cext.values)
        Csca_ = "{:12.6e}".format(Csca.values)
        header = 'Cext : ' + Cext_ + '\nCsca : ' + Csca_ + \
                 '\nNb angles : ' + str(Nang) + '\n'

        with open(ofile, 'w') as fp:
            fp.write(header)
        df_mat.to_csv(ofile, sep=' ', header=True, mode='a', float_format='%.8e')

