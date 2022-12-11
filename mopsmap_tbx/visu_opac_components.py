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

dir = "/sat_data/vrtc/aerosol/mopsmap/misc"


dir = "./"

# ------------------------------------
# load data
# ------------------------------------
scatmat = []
for file in glob.glob('./scatmat/components/*.nc'):
    print(file)
    name, rh = os.path.basename(file).replace('_scatmat.nc', '').split('_')
    ds = xr.open_dataset(file).squeeze()
    # reset dim and coords for practical use
    ds = ds.rename({'wavelen': 'wl'}).rename({'nlam': 'wl', 'nphamat': 'scamat', 'nthetamax': 'angle'}).set_coords(
        ['wl'])
    scaang = ds.theta.isel(wl=0, scamat=0).squeeze().values
    ds['rh'] = rh
    ds['name'] = name
    ds = ds.assign_coords({'angle': scaang}).drop('theta') #.set_coords(['name','rh']).expand_dims(['name','rh'])


    scatmat.append(ds)
scamat = xr.concat(scatmat, dim='name')

# -----------------
# plot
# -----------------

cmap = mpl.colors.LinearSegmentedColormap.from_list("",
                                                    ['navy', "blue", 'lightskyblue',
                                                     'gray', 'yellowgreen', 'forestgreen', 'gold', 'darkgoldenrod',
                                                     'darkred', 'black'])

norm = mpl.colors.Normalize(vmin=0.4, vmax=2.2)
sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])

# --------------------------
# plot scattering matrix
# --------------------------
for name, ds_ in scamat.groupby('name'):
    for rh, ds in ds_.groupby('rh'):
        print(name, rh)
        ds = ds.squeeze()
        fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(20, 12), sharex=True)
        fig.subplots_adjust(bottom=-0.05, top=0.925, left=0.07, right=0.975,
                            hspace=0.1, wspace=0.25)
        axs = axs.ravel()
        for wl in ds.wl.values:
            ds_ = ds.sel(wl=wl).squeeze()
            f11 = ds_.phase.isel(scamat=0)
            axs[0].plot(ds_.angle, ds_.phase.isel(scamat=0), color=cmap(norm(wl)))
            # -F12/F11
            axs[1].plot(ds_.angle, -ds_.phase.isel(scamat=1) / f11, color=cmap(norm(wl)))
            # F22/F11
            axs[2].plot(ds_.angle, ds_.phase.isel(scamat=4) / f11, color=cmap(norm(wl)))
            # F33/F11
            axs[3].plot(ds_.angle, ds_.phase.isel(scamat=2) / f11, color=cmap(norm(wl)))

        for i in range(4):
            axs[i].set_xlabel('$Scattering\ angle\ (deg)$')
        axs[0].semilogy()
        axs[0].set_ylabel('$F_{11}$')
        axs[1].set_ylabel('$-F_{12}/F_{11}$')
        axs[2].set_ylabel('$F_{22}/F_{11}$')
        axs[3].set_ylabel('$F_{33}/F_{11}$')
        plt.suptitle(name + ' ' + rh)
        cb = fig.colorbar(sm, ax=axs, shrink=0.6, aspect=30, pad=0.1, location='bottom')
        cb.set_label('$Wavelength\ (\mu m)$', fontsize=22)
        plt.savefig(opj('./fig/OPAC_components', name + '_' + rh + '_scatmat.png'), dpi=300)
        plt.close()
        plt.show()

# --------------------------
# plot Cext, SSA spectra
# --------------------------

# Rel. humidity = 0
suff='_norm'
suff=''
fig, axs = plt.subplots(ncols=3, nrows=1, figsize=(24, 6), sharex=True)
fig.subplots_adjust(bottom=0.15, top=0.925, left=0.1, right=0.975,
                    hspace=0.1, wspace=0.25)
axs = axs.ravel()

for name, ds_ in scamat.groupby('name'):
    for rh, ds in ds_.groupby('rh'):
        if 'rh0' == ds['rh'].values:
            print(name)
            ds = ds.squeeze()
            if suff == '_norm':
                Cext_550 = ds.ext.interp(wl=0.550)
            else:
                Cext_550 = 1.
            axs[0].plot(ds.wl, ds.ext / Cext_550, 'o-', label=name)
            axs[1].plot(ds.wl, ds.ext / Cext_550, 'o-', label=name)
            axs[2].plot(ds.wl, ds.ssa, 'o-', label=name)
for i in range(3):
    axs[i].set_xlabel('$Wavelength\ (\mu m)$')
    axs[i].legend(fontsize=11)
if suff == '_norm':
    ylabel='$C_{ext}/C_{ext}(550nm)$'
else:
    ylabel='$C_{ext}\ (\mu m^2)$'
axs[0].set_ylabel(ylabel)
axs[1].set_ylabel(ylabel)

axs[1].semilogy()
axs[2].set_ylabel('$ssa$')
plt.tight_layout()
plt.savefig(opj('./fig/OPAC_components', 'spectral_prop'+suff+'.png'), dpi=300)
plt.close()
plt.show()

# by aerosol component with relative humidity

cmap = cmap.reversed()

cmap = mpl.colors.LinearSegmentedColormap.from_list("",
                                                    ['navy', "blue", 'lightskyblue',
                                                     'gray', 'yellowgreen', 'forestgreen', 'gold', 'darkgoldenrod',
                                                     'darkred', 'black']).reversed()
norm = mpl.colors.Normalize(vmin=0, vmax=8)
sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
for name, ds_ in scamat.groupby('name'):
    # if name != 'MICM':
    #     continue
    print(name)
    fig, axs = plt.subplots(ncols=3, nrows=1, figsize=(24, 6), sharex=True)
    fig.subplots_adjust(bottom=0.15, top=0.925, left=0.1, right=0.975,
                        hspace=0.1, wspace=0.25)
    axs = axs.ravel()
    for irh, (rh, ds) in enumerate(ds_.groupby('rh')):
        rel_hum = (rh.replace('rh', '')) + '%'
        ds = ds.squeeze()

        axs[0].plot(ds.wl, ds.ext, 'o-', color=cmap(norm(irh)), label=rel_hum)
        axs[1].plot(ds.wl, ds.ext, 'o-', color=cmap(norm(irh)), label=rel_hum)
        axs[2].plot(ds.wl, ds.ssa, 'o-', color=cmap(norm(irh)), label=rel_hum)
    for i in range(3):
        axs[i].set_xlabel('$Wavelength\ (\mu m)$')
        axs[i].legend(title='Rel. humidity', fontsize=11)
    axs[0].set_ylabel('$C_{ext}$')
    axs[1].set_ylabel('$C_{ext}$')
    axs[1].semilogy()
    axs[2].set_ylabel('$ssa$')
    plt.suptitle(name)
    plt.tight_layout()
    plt.savefig(opj('./fig/OPAC_components', 'spectral_prop' + name + '.png'), dpi=300)
    plt.close()
    plt.show()

# --------------------------
# plot scattering matrix
wl = 1.600
scamat_ = scamat.sel(wl=wl)
for name, ds in scamat_.groupby('name'):

    print(name)
    fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(20, 12), sharex=True)
    fig.subplots_adjust(bottom=0.15, top=0.925, left=0.1, right=0.975,
                        hspace=0.1, wspace=0.25)
    axs = axs.ravel()
    for irh, (rh, ds_) in enumerate(ds.groupby('rh')):
        print(rh)
        rel_hum = (rh.replace('rh', '')) + '%'
        ds_ = ds_.squeeze()

        f11 = ds_.phase.isel(scamat=0)
        axs[0].plot(ds_.angle, ds_.phase.isel(scamat=0), color=cmap(norm(irh)), label=rel_hum)
        # -F12/F11
        axs[1].plot(ds_.angle, -ds_.phase.isel(scamat=1) / f11, color=cmap(norm(irh)), label=rel_hum)
        # F22/F11
        axs[2].plot(ds_.angle, ds_.phase.isel(scamat=4) / f11, color=cmap(norm(irh)), label=rel_hum)
        # F33/F11
        axs[3].plot(ds_.angle, ds_.phase.isel(scamat=2) / f11, color=cmap(norm(irh)), label=rel_hum)

    for i in range(4):
        axs[i].set_xlabel('$Scattering\ angle\ (deg)$')
    axs[0].semilogy()
    axs[0].legend(title='Rel. humidity', fontsize=11)
    axs[0].set_ylabel('$F_{11}$')
    axs[1].set_ylabel('$-F_{12}/F_{11}$')
    axs[2].set_ylabel('$F_{22}/F_{11}$')
    axs[3].set_ylabel('$F_{33}/F_{11}$')
    plt.suptitle(name + ' at ' + str(wl * 1000) + ' nm')

    plt.tight_layout()
    plt.savefig(opj('./fig/OPAC_components', 'scatmat_' + name + '_' + str(int(wl * 1000)) + 'nm.png'), dpi=300)
    plt.close()
    # plt.show()
