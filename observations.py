"""
Classes and functions for mock observation steps

- up-channelization
- visibilities
- noisy visibilities
- visibilities with calibration errors
- dirty maps
"""

import channelization_functions as cf
import h5py
import numpy as np
import frequencies as fr

class UpchannelizedMap():

    def __init__(self, U, map_paths, output_directory, output_filename, R_filepath='', norm_filepath='') -> None:
        
        self.U = U
        self.map_paths = map_paths
        self.output_name = output_filename
        self.output_directory = output_directory
        self.R_filepath = R_filepath
        self.norm_filepath = norm_filepath


    def get_R_norm(self, fstate, fmin, fmax):
        # if the R and norm matrices have not already been computed, do it here
        fine_freqs = cf.get_fine_freqs(fstate.frequencies)
        R, chans, norm = cf.get_response_matrix(fine_freqs,
                                                self.U,
                                                fmin,
                                                fmax)
        
        np.save(self.output_directory+'/R.npy')
        np.save(self.output_directory+'/norm.npy')

        print('Up-channelization matrix with shape {} saved to {}.'.format(R.shape,
                                                                           self.output_directory+'/R.npy'))
        print('Normalization vector with shape {} saved to {}.'.format(norm.shape,
                                                                           self.output_directory+'/norm.npy'))

    def upchannelize(self, fstate, catalog=False, catalog_filepath='', nside=128):

        fine_freqs = cf.get_fine_freqs(fstate.frequencies)

        open_maps(self.map_paths,
                  self.output_directory + '/full_input.h5')

        if catalog:
            # need to add something that complains if they have chosen a catalog and have not specified the nside
            # or catalog filepath

            cf.channelize_catalogue(self.U,
                                    fstate,
                                    nside,
                                    catalog_filepath,
                                    self.R_filepath,
                                    self.norm_filepath,
                                    fine_freqs,
                                    self.output_directory + self.output_name)

        else:
            cf.channelize_map(self.U,
                            fstate,
                            self.output_directory + '/full_input.h5',
                            self.R_filepath,
                            self.norm_filepath,
                            fine_freqs,
                            self.output_directory + self.output_name)

        



class Visibilities():

    def __init__(self, map_path) -> None:
        
        self.map = map_path

    def get_visibilities(self):

        # code to get visibilities
        pass

    def _add_noise(self):
        pass

    def _add_calibration_errors(self):
        pass


class NoisyVisibilities(Visibilities):

    def __init__(self, map_path) -> None:
        super().__init__(map_path)

    def _add_noise(self):
        return super()._add_noise()
    

class CalibrationErrorVisibilities(Visibilities):

    def __init__(self, map_path) -> None:
        super().__init__(map_path)

    def _add_calibration_errors(self):
        return super()._get_visibilities()


class RealisticVisibilities(Visibilities):

    def _add_noise(self):
        return super()._add_noise()

    def _add_calibration_errors(self):
        return super()._add_calibration_errors()    


class DirtyMap():

    def __init__(self, nside, beam_path, auto_correlations=False) -> None:

        self.nside = nside
        self.auto_correlations = auto_correlations
        self.beam_path = beam_path

    
    def compute_mmodes(self, visibilities_path):



        pass

    def compute_dirty_mao(self):

        pass



def load_map(map_path):

    f = h5py.File(map_path)
    sky_map = np.array(f['map'])
    ff = np.array(f['index_map']['freq'])
    freqs = np.array([ii[0] for ii in ff])
    f_width = np.abs(freqs[0] - freqs[1])
    f.close()

    return freqs, f_width, sky_map

def open_maps(map_paths, output_name):

    if type(map_paths) == str:
        freqs, f_width, sky_map = load_map(map_paths)

    elif type(map_paths) == list:
        freqs, f_width, sky_map = load_map(map_paths[0])

        for i in range(1,len(map_paths)-1):
            freqs, f_width, new_map = load_map(map_paths[i])
            sky_map += new_map

    print('Writing file {} containing the input maps {}.'.format(output_name,
                                                                 map_paths))

    write_map(output_name,
                sky_map,
                freqs,
                f_width)


def write_map(map_filepath, sky_map, freqs, f_width, include_pol=True):

    pass