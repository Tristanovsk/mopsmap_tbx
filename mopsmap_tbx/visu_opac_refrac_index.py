import os, sys
import glob
import numpy as np
import pandas as pd
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



components = pd.read_csv('./data/opac_aerosol_components.csv', skiprows=1, index_col=[1])
components['logS'] = np.log(components.sigma)
refrac_dir = './data/refrac_index'

materials = []

colors = {'insoluble':'olivedrab','mineral':'darkgoldenrod','soot':'dimgrey',
          'sulfate':'darkorchid','water_segelstein':'mediumblue','water_soluble':'cornflowerblue'}


# ------------------------------------
# load and arrange data
# ------------------------------------
fig, axs = plt.subplots(ncols=2, nrows=1, figsize=(15, 6), sharex=True)
fig.subplots_adjust(bottom=0.15, top=0.925, left=0.1, right=0.975,
                    hspace=0.1, wspace=0.25)
wl_common = np.linspace(0.35,2.5,150)

for material in materials:
    file = opj(refrac_dir,'refr_'+material)
    print(file)
    refrac = pd.read_csv(file,sep='\s+',names=['wl','mr','mi'],index_col=0).to_xarray()
    color=colors[material]
    marker='o'
    if material == 'water_segelstein':
        material='pure water'
        marker=''

    material =material.replace('_',' ')
    axs[0].plot(refrac.wl,refrac.mr,'-',marker=marker,ms=6,lw=2,alpha=0.65,color=color,label=material)
    axs[1].plot(refrac.wl,refrac.mi,'-',marker=marker,ms=6,lw=2,alpha=0.65,color=color,label=material)

    #refrac = refrac.interp(wl=wl_common)
axs[0].set_xlim(0.3,2.5)
axs[0].set_ylim(1.15,1.85)

axs[1].semilogy()
axs[1].legend(fontsize=14,ncol=2)#,loc='upper center', bbox_to_anchor=(0.5, 0.99))
axs[0].set_ylabel('$m_r$')
axs[1].set_ylabel('$m_i$')


for i in range (2):
    axs[i].set_xlabel('$Wavelength\ (\mu m)$')
    axs[i].minorticks_on()
plt.show()

# -
plt.tight_layout()
plt.savefig(opj('./fig', 'opac_refractive_index.png'), dpi=300)
plt.close()

