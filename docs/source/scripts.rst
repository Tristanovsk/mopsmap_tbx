Scripts
=======

The generators read the tables in ``data/`` and write their NetCDF outputs to
``scatmat/``. Set the ``MOPSMAP_DIR`` environment variable to your MOPSMAP
installation (see :mod:`mopsmap_tbx.opac_mopsmap`) and run them as modules:

.. code-block:: bash

   export MOPSMAP_DIR=/path/to/mopsmap
   python -m mopsmap_tbx.opac_component_gen
   python -m mopsmap_tbx.opac_gen

The independent MOPSMAP runs are computed in parallel with
:func:`dask.delayed` and the threaded scheduler, one run per CPU by default
(``main(num_workers=...)`` to change it). The other scripts run when executed
from the repository root and write to ``scatmat/`` and ``fig/``.

Data
----

``data/opac_aerosol_components.csv``
   Log-normal size distribution (:math:`\sigma`, :math:`r_{mod,N}`,
   :math:`r_{min}`, :math:`r_{max}`), density, shape, hygroscopicity parameter
   :math:`\kappa` and refractive index file of the OPAC aerosol components.

``data/opac_aerosol_types.csv``
   Number concentration (particles cm\ :sup:`-3`) of each component for the
   OPAC aerosol types.

``data/refrac_index/``
   Spectral refractive indices of the OPAC materials.

Processing
----------

``opac_component_gen.py`` (:mod:`~mopsmap_tbx.opac_component_gen`)
   Scattering matrices of each OPAC component for relative humidities from 0
   to 99 %, written to ``scatmat/components``. Hygrophobic components
   (:math:`\kappa = 0`) are computed at 0 % only.

``opac_gen.py`` (:mod:`~mopsmap_tbx.opac_gen`)
   Scattering matrices of the OPAC aerosol types (external mixture of the
   components weighted by their number fraction), written to
   ``scatmat/types``. The maximum radius is reduced so that the size
   parameter stays within the MOPSMAP dataset (:math:`x \leq 1010`) after
   hygroscopic growth :math:`(1 + \kappa\, RH / (1 - RH))^{1/3}`.

``opac_osoaa_ascii.py``
   Conversion of the NetCDF outputs into ASCII files per wavelength
   (:math:`F_{11}`, :math:`-F_{12}/F_{11}`, :math:`F_{22}/F_{11}`,
   :math:`F_{33}/F_{11}`, extinction and scattering cross sections) for
   OSOAA.

Visualization
-------------

``visu.py``
   Scattering matrices, extinction and single scattering albedo of the OPAC
   types.

``visu_opac_components.py``
   Same for the OPAC components.

``visu_opac_refrac_index.py``
   Real and imaginary parts of the OPAC refractive indices.
