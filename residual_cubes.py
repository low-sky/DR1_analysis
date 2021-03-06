import numpy as np
import astropy.io.fits as fits
from spectral_cube import SpectralCube
import astropy.units as u
import pyspeckit
from pyspeckit.spectrum.models import ammonia
import astropy.utils.console as console
import scipy.ndimage as nd

def residual_cube(cubename, fitfile=None, 
                  expand=20, writemodel=False, fileprefix=None,
                  filesuffix=None,
                  writeresidual=False, writechisq=True):
    """This function generates products for evaluating the goodness of
    fit for a cold_ammonia model.  Either a parameter cube name must
    be passed or the prefix/suffixes of the files.

    Parameters
    ----------

    cubename : str
        Name of the original data file
    
    Keywords
    --------
    fitfile : str
        Name of the parameter file produced by the cube fitter
    fileprefix : str
        Prefix of file name before the parameter name (e.g., for
        L1688_N_NH3_DR1_rebase3_flag.fits, this would be 'L1688_').
    filesufffix : str
        Prefix of file name before the parameter name (e.g., for
        L1688_N_NH3_DR1_rebase3_flag.fits, this would be
        '_DR1_rebase3_flag').
    expand : int
        Expands the region where the residual is evaluated by this
        many channels in the spectral dimension
    writemodel : bool
        Setting to True writes out a model cube of the ammonia fit
    writeresidual : bool
        Setting to True writes out a residual cube
    writechisq : bool
        Setting to True writes out a map of the reduced chi-squared
        goodness of fit.

    Returns
    -------
        None
    """
    try:
        if fitfile is None:
            tkin = fits.getdata(fileprefix + 'Tkin' + filesuffix + '.fits')
            tex = fits.getdata(fileprefix + 'Tex' + filesuffix + '.fits')
            sigma = fits.getdata(fileprefix + 'Sigma' + filesuffix + '.fits')
            column = fits.getdata(fileprefix + 'N_NH3' + filesuffix + '.fits')
            v0 = fits.getdata(fileprefix + 'Vlsr' + filesuffix + '.fits')
            fortho = np.zeros_like(v0)
        else:
            hdu = fits.open(fitfile)
            fitparams = hdu[0].data
            tkin = fitparams[0, :, :]
            tex = fitparams[1, :, :]
            column = fitparams[2, :, :]
            sigma = fitparams[3, :, :]
            v0 = fitparams[4, :, :]
            fortho = fitparams[5, :,:]
    except NameError:
        warnings.warn("Either fitfile or fileprefix/filesuffix"+
                      " must be specified")

    cube = SpectralCube.read(cubename)
    cube  = cube.with_spectral_unit(u.km/u.s,velocity_convention='radio')
    model = np.zeros(cube.shape)

    yy, xx = np.where(column>0)
    cube = cube.with_spectral_unit(u.Hz)
    spaxis = pyspeckit.spectrum.units.SpectroscopicAxis(cube.spectral_axis)
    for y, x in console.ProgressBar(zip(yy,xx)):
        fit = ammonia.cold_ammonia(spaxis, tkin[y, x], tex=tex[y, x], 
                                   ntot=column[y, x], width=sigma[y, x],
                                   xoff_v=v0[y, x], fortho=fortho[y, x])
        model[:, y, x] = fit

    mask = model > 0
    residual = cube.filled_data[:].value-model

    # This calculates chisq over the region where the fit is non-zero
    # plus a buffer of size set by the expand keyword.

    selem = np.ones(expand,dtype=np.bool)
    selem.shape += (1,1,)
    mask = nd.binary_dilation(mask, selem)
    mask = mask.astype(np.float)
    chisq = np.sum((residual * mask)**2, axis=0) / np.sum(mask, axis=0)

    # This produces a robust estimate of the RMS along every line of sight:
    diff = residual - np.roll(residual, 2, axis=0)
    rms = 1.4826 * np.nanmedian(np.abs(diff), axis=0) / 2**0.5

    chisq /= rms**2

    root = (cubename.split('.'))[0]
    if writechisq:
        hdu = fits.PrimaryHDU(chisq, cube.wcs.celestial.to_header())
        hdu.writeto(root+'_chisq.fits', clobber=True)
    if writeresidual:
        newcube = SpectralCube(residual,cube.wcs,header=cube.header)
        newcube.write(root+'_residual.fits', overwrite=True)
    if writemodel:
        model = SpectralCube(model, cube.wcs, header=cube.header)
        model.write(root + '_model.fits', overwrite=True)


