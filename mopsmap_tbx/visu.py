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
opj =os.path.join

dir = "/sat_data/vrtc/aerosol/mopsmap/misc"
file= "opac_dust_rh70.nc"

dir = "./"
file= "test.nc"
#------------------------------------
# load data
#------------------------------------
scatmat = []
for file in glob.glob('./scatmat/*.nc'):
    print(file)
    name = os.path.basename(file).replace('_scatmat.nc','')
    ds = xr.open_dataset(file)
    # reset dim and coords for practical use
    ds = ds.rename({'wavelen':'wl'}).rename({'nlam':'wl','nphamat':'scamat','nthetamax':'angle'}).set_coords(['wl'])
    scaang = ds.theta.isel(wl=0,scamat=0).squeeze().values
    ds = ds.assign_coords({'angle':scaang}).drop('theta')
    ds['name']=name
    scatmat.append(ds)
scamat = xr.concat(scatmat,dim='name')

#-----------------
# plot
# -----------------

cmap = mpl.colors.LinearSegmentedColormap.from_list("",
                                                    ['navy', "blue", 'lightskyblue',
                                                     'gray', 'yellowgreen', 'forestgreen','gold','darkgoldenrod','darkred','black'])

norm = mpl.colors.Normalize(vmin=0.4, vmax=2.2)
sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])


#--------------------------
# plot norm. radiance spectra
#--------------------------
for name,ds in scamat.groupby('name'):
    print(name)
    ds = ds.squeeze()
    fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(20, 12), sharex=True)
    fig.subplots_adjust(bottom=0.15, top=0.925, left=0.1, right=0.975,
                        hspace=0.1, wspace=0.25)
    axs = axs.ravel()
    for wl in ds.wl.values:
          ds_ = ds.sel(wl=wl).squeeze()
          f11 = ds_.phase.isel(scamat=0)
          axs[0].plot(ds_.angle,ds_.phase.isel(scamat=0),color=cmap(norm(wl)))
          # -F12/F11
          axs[1].plot(ds_.angle,-ds_.phase.isel(scamat=1)/f11,color=cmap(norm(wl)))
          # F22/F11
          axs[2].plot(ds_.angle,ds_.phase.isel(scamat=4)/f11,color=cmap(norm(wl)))
          # F33/F11
          axs[3].plot(ds_.angle,ds_.phase.isel(scamat=2)/f11,color=cmap(norm(wl)))

    for i in range(4):
        axs[i].set_xlabel('$Scattering\ angle\ (deg)$')
    axs[0].semilogy()
    axs[0].set_ylabel('$F_{11}$')
    axs[1].set_ylabel('$-F_{12}/F_{11}$')
    axs[2].set_ylabel('$F_{22}/F_{11}$')
    axs[3].set_ylabel('$F_{33}/F_{11}$')
    plt.suptitle(name)
    plt.savefig(opj('./fig/OPAC_components',name+'_scatmat.png'),dpi=300)
    plt.close()
    plt.show()


#--------------------------
# plot norm. radiance spectra
#--------------------------
fig, axs = plt.subplots(ncols=3, nrows=1, figsize=(22, 6), sharex=True)
fig.subplots_adjust(bottom=0.15, top=0.925, left=0.1, right=0.975,
                    hspace=0.1, wspace=0.25)
axs = axs.ravel()

for name,ds in scamat.groupby('name'):
    print(name)
    ds = ds.squeeze()
    axs[0].plot(ds.wl,ds.ext,'o-',label=name)
    axs[1].plot(ds.wl,ds.ext,'o-',label=name)
    axs[2].plot(ds.wl,ds.ssa,'o-',label=name)
for i in range(3):
    axs[i].set_xlabel('$Wavelength\ (\mu m)$')
    axs[i].legend(fontsize=11)
axs[0].set_ylabel('$C_{ext}$')
axs[1].set_ylabel('$C_{ext}$')
axs[1].semilogy()
axs[1].set_ylabel('$ssa$')
plt.tight_layout()
plt.savefig(opj('./fig/OPAC_components','spectral_prop.png'),dpi=300)
#plt.close()
plt.show()
