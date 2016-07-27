import matplotlib.pyplot as plt
import astropy.units as u
import warnings
import numpy as np
import os

from astropy.io import fits
import aplpy

region_list=['L1688', 'B18', 'NGC1333', 'OrionA']
region_list=['B18']
line_list=['NH3_11','NH3_22','NH3_33','C2S','HC5N','HC7N_21_20','HC7N_22_21']
label_list=['NH$_3$(1,1)','NH$_3$(2,2)','NH$_3$(3,3)','C$_2$S','HC$_5$N',
            'HC$_7$N (21-20)','HC$_7$N (22-21)']
extension='DR1_rebase3'
color_table='magma'
text_color='black'
beam_color='#d95f02'  # previously used '#E31A1C'

def setup_plot_parameters(region='L1688'):
    """
    This function returns a dictionary with the plotting parameters for the 
    requested region.

    There might be a better or more elegant solution, to be discussed

    the mom0_max array is the array with the maximum mom0 to be plotted, where
    the array loops over the lines in hte order of line_list
    """
    if region=='L1688':
        param={'size_x' : 9, 'size_y' : 7, 
               'scalebar_size' : 0.1*u.pc, 'scalebar_pos' : 'bottom right',
               'distance' : 145.*u.pc, 'beam_pos' : 'bottom left',
               'label_xpos' : 0.025, 'label_ypos' : 0.1,
               'label_align' : 'left',
               'mom0_min' : np.array([0.05, 0.05, 0.05, 0.1, 0.05, 0.05, 0.05]),
               'mom0_max' : np.array([0.75, 0.75, 0.75, 1.0, 0.75, 0.75, 0.75]),
               'w11_step' : 0.3}
    elif region=='B18':
        param={'size_x' : 19, 'size_y' : 7, 
               'scalebar_size' : 0.1*u.pc, 'scalebar_pos' : 'bottom right',
               'distance' : 145.*u.pc, 'beam_pos' : 'top left',
               'label_xpos' : 0.025, 'label_ypos' : 0.9,
               'label_align' : 'left',
               'mom0_min' : np.array([-0.17,-0.1,-0.1,-0.3,-0.25,-0.25,-0.36]),
               'mom0_max' : np.array([3.0, 0.5, 0.5, 1.8, 1.4, 1.0, 1.5]),
               'w11_step' : 0.3}
    elif region=='NGC1333':
        param={'size_x' : 8, 'size_y' : 12, 
               'scalebar_size' : 0.1*u.pc, 'scalebar_pos' : 'top right',
               'distance' : 250.*u.pc, 'beam_pos' : 'bottom left',
               'label_xpos' : 0.025, 'label_ypos' : 0.075,
               'label_align' : 'left',
               'mom0_min' : np.array([0.05, 0.05, 0.05, 0.1, 0.05, 0.05, 0.05]),
               'mom0_max' : np.array([0.75, 0.75, 0.75, 1.0, 0.75, 0.75, 0.75]),
               'w11_step' : 0.3}
    elif region=='OrionA':
        param={'size_x' : 4.5, 'size_y' : 11, 
               'scalebar_size' : 0.1*u.pc, 'scalebar_pos' : 'bottom right',
               'distance' : 450.*u.pc, 'beam_pos' : 'top left',
               'label_xpos' : 0.025, 'label_ypos' : 0.925,
               'label_align' : 'left',
               'mom0_min' : np.array([0.05, 0.05, 0.05, 0.1, 0.05, 0.05, 0.05]),
               'mom0_max' : np.array([0.75, 0.75, 0.75, 1.0, 0.75, 0.75, 0.75]),
               'w11_step' : 0.3}
    else:
        warnings.warn("Region not in DR1 or not defined yet")
    return param


for region_i in region_list:
    plot_param=setup_plot_parameters(region=region_i)
    file_w11='{0}/{0}_NH3_11_{1}_mom0.fits'.format(region_i,extension)
    for i in range(len(line_list)):
        line_i=line_list[i]
        label_i=label_list[i]
        file_mom0='{0}/{0}_{1}_{2}_mom0.fits'.format(region_i,line_i,extension)
        v_min=plot_param['mom0_min'][i]
        v_max=plot_param['mom0_max'][i]
        cont_levs=2**np.arange( 0,20)*plot_param['w11_step']
        if os.path.isfile(file_mom0):
            fig=aplpy.FITSFigure(file_mom0, hdu=0, figsize=(plot_param['size_x'], plot_param['size_y']) )
            fig.show_colorscale( cmap=color_table,vmin=v_min, vmax=v_max)
            fig.set_nan_color('0.9')
            #
            fig.show_contour(file_w11, colors='gray', levels=cont_levs)
            #
            # Ticks
            fig.ticks.set_color(text_color)
            fig.tick_labels.set_xformat('hh:mm:ss')
            # Add beam
            fig.add_beam()
            fig.beam.set_color(beam_color)
            fig.beam.set_corner(plot_param['beam_pos'])
            # Scale bar
            # magic line of code to obtain scale in arcsec obtained from 
            # http://www.astropy.org/astropy-tutorials/Quantities.html
            ang_sep =  (plot_param['scalebar_size'].to(u.au)/plot_param['distance']).to(u.arcsec, equivalencies=u.dimensionless_angles())
            fig.add_scalebar(ang_sep.to(u.degree))
            fig.scalebar.set_corner(plot_param['scalebar_pos'])
            fig.scalebar.set(color=text_color)
            fig.scalebar.set_label('{0:4.2f}'.format(plot_param['scalebar_size']))
            # Labels
            fig.add_label(plot_param['label_xpos'], plot_param['label_ypos'], 
                          '{0}\n{1}'.format(region_i,label_i), 
                          relative=True, color=text_color, 
                          horizontalalignment=plot_param['label_align'])
            # add colorbar
            fig.add_colorbar()
            fig.colorbar.set_width(0.15)
            fig.colorbar.show( box_orientation='horizontal', width=0.1, pad=0.0, 
                                location='top', axis_label_text='Integrated Intensity (K km s$^{-1}$)')
            # fig.set_system_latex(True)
            fig.save( 'figures/{0}_{1}_{2}_mom0_map.pdf'.format(region_i,line_i,extension),adjust_bbox=True)#, bbox_inches='tight')
            fig.close()
        else:
            print('File {0} not found'.format(file_mom0))
