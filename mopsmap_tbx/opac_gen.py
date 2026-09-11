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
mopsmap_exe = opj(mopsmap_dir, 'mopsmap')
components = pd.read_csv('./data/opac_aerosol_components.csv', skiprows=1, index_col=[1])
components['logS'] = np.log(components.sigma)
opac = pd.read_csv('./data/opac_aerosol_types.csv', index_col=[0])

datapath = opj(mopsmap_dir, 'data')

input_file = './input.txt'

wl_min=0.35
wl_max=2.6

# -- Write scattering angle file
# ang = np.concatenate([[0,0.001,0.005,0.01,0.05,0.1,0.2,0.3,0.4],np.arange(0.5,180.1,0.5)])
# pd.DataFrame(ang).to_csv(opj(datapath,'scat_angle_grid.txt'),index=False)

class input_info:
    def __init__(self,output_file='test.nc', dataroot=''):

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

    def write_info(self,
                   rel_humidity=0,
                   water_refrac_file="refr_water_segelstein",
                   wavelength='range 0.35 2.5 0.05',
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


xr_components = components.to_xarray()
rhs = [0, 50, 70, 80, 90, 95, 98, 99]
for rh in rhs:
    rh_num = rh / 100
    for name, opac_ in opac.iterrows():
        print(name)
        ofile = opj('./scatmat', 'types', name + '_rh{:d}_scatmat.nc'.format(rh))

        #if os.path.exists(ofile):
        #    continue
        print(ofile)
        imode = 0
        input = ""
        info = input_info(output_file=ofile, dataroot=datapath)
        # normalization of particle number
        norm = np.sum(opac_[1:])
        for component, Ni in opac_[1:].items():
            if Ni == 0:
                continue


            Ni_norm = Ni / norm
            imode += 1
            c = xr_components.sel(name=component)
            c = c.to_pandas()
            rmax = c['rmax']
            kappa = c['kappa']
            growth = (1 + kappa * rh_num / (1 - rh_num))**(1./3)
            xparam = 2 * np.pi * rmax / wl_min * growth
            # fix for the incomplete mopsmap x-parameter (upper value around 1010)
            if xparam > 1010:
                rmax = 1010 *wl_min / (2 * np.pi  * growth)
            print(component, Ni, kappa, xparam,rmax)



            if c['shape'] == 'sphere':
                input += info.write_mode(imode, c.rmed_N, c.sigma, shape='sphere', kappa=kappa, r_max=rmax,
                                         refra_file=c.refrac_index_file, Nparticle=Ni_norm)
            elif c['shape'] == 'spheroid':
                input += info.write_mode(imode, c.rmed_N, c.sigma,
                                         shape='spheroid distr_file "' + opj(datapath, 'ar_kandler') + '"', kappa=kappa,
                                         r_max=rmax, refra_file=c.refrac_index_file, Nparticle=Ni_norm)

        input_file = '/media/harmel/vol1/Dropbox/work/git/vrtc/mopsmap_tbx/input.txt'
        input += info.write_info(wavelength='range {:.3f} {:.3f} 0.05'.format(wl_min,wl_max), rel_humidity=rh)

        with open(input_file, 'w') as w:
            w.write(input)

        # call mopsmap

        p = subprocess.Popen(mopsmap_exe + ' ' + input_file, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             close_fds=True, shell=True)
        res = p.communicate()
