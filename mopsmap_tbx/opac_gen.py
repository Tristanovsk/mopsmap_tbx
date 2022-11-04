import os, sys
import glob
import numpy as np
import pandas as pd
import xarray as xr
import subprocess

# ----------------------------
# set plotting styles
import matplotlib.pyplot as plt
import matplotlib as mpl

plt.ioff()
rc = {"font.family": "serif",
      "mathtext.fontset": "stix"}
plt.rcParams.update(rc)
plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]
plt.rcParams.update({'font.size': 16, 'axes.labelsize': 18})
opj = os.path.join

mopsmap_dir = '/sat_data/vrtc/aerosol/mopsmap'
mopsmap_exe =opj(mopsmap_dir,'mopsmap')
components = pd.read_csv('./data/opac_aerosol_components.csv', skiprows=1, index_col=[1])
components['logS'] = np.log(components.sigma)

datapath = opj(mopsmap_dir, 'data')

input_file = './input.txt'

# -- Write scattering angle file
# ang = np.concatenate([[0,0.001,0.005,0.01,0.05,0.1,0.2,0.3,0.4],np.arange(0.5,180.1,0.5)])
# pd.DataFrame(ang).to_csv(opj(datapath,'scat_angle_grid.txt'),index=False)

class input_info:
    def __init__(self,output_file='test.nc',dataroot=''):
        self.dataroot = dataroot
        self.output_file = output_file

    def write_mode(self,imode, rmed_N, sigma,
                   Nparticle=1, r_min=1e-3, r_max=60,
                   refra_file='refr_water_soluble',
                   shape='sphere',
                   kappa=0):
        mode = 'mode %d size log_normal %f %f %f %f %f\n' % (
            imode, rmed_N, sigma, Nparticle, r_min, r_max)
        mode += 'mode %d refrac file "%s"\n' % (imode,opj(self.dataroot,refra_file))
        mode += 'mode %d shape %s\n' % (imode,shape)
        mode += 'mode %d kappa %s\n' % (imode,kappa)
        return mode

    def write_info(self,
                   rel_humidity=0,
                   water_refrac_file="refr_water_segelstein",
                   wavelength='range 0.4 2.4 0.1',
                   theta_file='scat_angle_grid.txt',
                   scatlib='optical_dataset'):
        info ='size_equ cs\n'
        info += 'rH %d\n' % rel_humidity
        info+= 'water_refrac_file "%s"\n' % water_refrac_file
        info+= 'wavelength %s\n' % wavelength
        info += 'output theta_file "%s"\n' % opj(self.dataroot,theta_file)
        info += 'scatlib "%s"\n' % opj(self.dataroot,scatlib)
        info += 'output netcdf "%s" reff\n' % self.output_file
        return info


for name,c in components.iterrows():
    print(name)
    info = input_info(output_file= opj('./scatmat',name+'rh0_scatmat.nc'),dataroot=datapath)

    if c['shape'] == 'sphere':
        input = info.write_mode(1, c.rmed_N, c.sigma, shape='sphere')
    elif c['shape'] == 'spheroid':
        input += info.write_mode(2,c.rmed_N, c.sigma,shape='spheroid distr_file "'+opj(datapath,'ar_kandler')+'"')
    input += info.write_info()


    with open(input_file, 'w') as w:
        w.write(input)

    # call mopsmap
    input_file='/media/harmel/vol1/Dropbox/work/git/vrtc/mopsmap_tbx/input.txt'

    p = subprocess.Popen(mopsmap_exe+' '+ input_file, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         close_fds=True,shell=True)
    p.communicate()
