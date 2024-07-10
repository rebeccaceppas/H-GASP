## this is an example of how to run every step of the pipeline

## first need to make sure the modules are loaded
'''
module use /project/rrg-kmsmith/shared/chord_env/modules/modulefiles/
module load chord/chord_pipeline/2023.06
'''

import sys

sys.path.append('/home/rebeccac/scratch/H-GASP')

import input_maps as im
import observations as obs
import frequencies as fr

############# setting up the basic parameters for the run ##########
fmax = 1420
fmin = 1415
nfreq  = 40
nside = 128
output_directory = '/home/rebeccac/scratch/H-GASP/notebooks/full_run/'

U = 2

compute_R = False

CHORDdec_pointing = 10  # declination in degrees
n_dishes_ew = 2
n_dishes_ns = 1
# these are the CHORD pathfinder defaults but I'm explicitely using them to show it can be changed
spacing_ew = 6.3
spacing_ns = 8.5
dish_diameter = 6.0

ndays = 100


############## creating input maps: one with all galaxies in the galaxy catalog and one with cora-makesky foregrounds ##############

print('creating maps')

catalog_filepath = './HI_Catalog.txt'
HIgals_filename = 'HI_gals.h5'
#hi_gals = im.HIGalaxies(catalog_filepath, fmax, fmin, nfreq)
#hi_gals.get_map(nside, output_directory+HIgals_filename)


components = ['foreground', '21cm']
#fg = im.Foregrounds(fmax, fmin, nfreq, nside, output_directory)
#fg.get_maps(components)

############## up-channelizing the maps ################

print('upchannelizing')

map_paths = [output_directory+HIgals_filename,
             output_directory+'foregrounds_all.h5']

upchan_filename = 'upchan_map.h5'
R_filename = 'R_{}_{}_{}.npy'.format(fmax, fmin, U)
norm_filename = 'norm_{}_{}_{}.npy'.format(fmax, fmin, U)
freq_matrix_filename = 'freqs_matrix_{}_{}_{}.npy'.format(fmax, fmin, U)

upchan = obs.Upchannelization(U,
                              fmax,
                              fmin,
                              output_directory,
                              upchan_filename,
                              R_filename,
                              norm_filename,
                              freq_matrix_filename)

#if compute_R:
#    upchan.get_R_norm()

f_start, f_end, nfreqU = upchan.upchannelize(map_paths=map_paths)

fstate = fr.FreqState()
fstate.freq = (f_start, f_end, nfreqU)

############# computing beam transfer matrices #####################

print('getting btm')

btm_directory = output_directory

#btm = obs.BeamTransferMatrices(f_start, f_end, nfreqU, output_directory, CHORDdec_pointing,
                               #n_dishes_ew, n_dishes_ns, spacing_ew, spacing_ns,
                               #dish_diameter, ndays=ndays)

#btm.get_beam_transfer_matrices()


############# getting visibilities ##################

print('getting vis')

maps_tag = 'HIcatalog_foregrounds'  # a tag to remember which components were in the iput maps
map_filepaths = [output_directory+upchan_filename]

#vis = obs.Visibilities(output_directory, btm_directory, maps_tag, map_filepaths)
#vis.get_visibilities()

############# adding noise and calibration errors ##############

print('adding errors')

amplitude_errors_filepath = '/home/rebeccac/scratch/H-GASP/notebooks/visibility_amplitude_errors.npy'
phase_errors_filepath = '/home/rebeccac/scratch/H-GASP/notebooks/visibility_phase_errors.npy'

real_vis_obs = obs.RealisticVisibilities(ndays, btm_directory, output_directory, maps_tag)    
real_vis = real_vis_obs.add_noise_calibration_errors(amplitude_errors_filepath,
                                                     phase_errors_filepath,
                                                       norm_filepath=output_directory+norm_filename)

############# getting dirty map #################

print('getting dirty map')

dirty_map_filename = 'dirty_map.h5'

dm = obs.DirtyMap(real_vis, 
                  output_directory+dirty_map_filename,
                  fstate, nside, btm_directory)

dm.get_dirty_map()

print('done')


######## DONE ###########