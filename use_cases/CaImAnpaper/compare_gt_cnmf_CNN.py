#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 14:49:36 2017

@author: agiovann
"""

"""

"""
from __future__ import division
from __future__ import print_function
from builtins import zip
from builtins import str
from builtins import map
from builtins import range
from past.utils import old_div
import cv2
import glob

try:
    cv2.setNumThreads(1)
except:
    print('Open CV is naturally single threaded')

try:
    if __IPYTHON__:
        print(1)
        # this is used for debugging purposes only. allows to reload classes
        # when changed
        get_ipython().magic('load_ext autoreload')
        get_ipython().magic('autoreload 2')
except NameError:
    print('Not IPYTHON')
    pass
import caiman as cm
import numpy as np
import os
import time
import pylab as pl
import psutil
import sys
from ipyparallel import Client
from skimage.external.tifffile import TiffFile
import scipy
import copy

from caiman.utils.utils import download_demo
from caiman.base.rois import extract_binary_masks_blob
from caiman.utils.visualization import plot_contours, view_patches_bar
from caiman.source_extraction.cnmf import cnmf as cnmf
from caiman.motion_correction import MotionCorrect
from caiman.components_evaluation import estimate_components_quality
from caiman.cluster import setup_cluster
from caiman.components_evaluation import evaluate_components

from caiman.tests.comparison import comparison
from caiman.motion_correction import tile_and_correct, motion_correction_piecewise

#%%
params_movie = {'fname': '/mnt/ceph/neuro/labeling/neurofinder.03.00.test/images/final_map/Yr_d1_498_d2_467_d3_1_order_C_frames_2250_.mmap',
                 'p': 1,  # order of the autoregressive system
                 'merge_thresh': 0.8,  # merging threshold, max correlation allow
                 'rf': 25,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
                 'stride_cnmf': 10,  # amounpl.it of overlap between the patches in pixels
                 'K': 4,  # number of components per patch
                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
                 'init_method': 'greedy_roi',
                 'gSig': [8,8],  # expected half size of neurons
                 'alpha_snmf': None,  # this controls sparsity
                 'final_frate': 10,
                 'r_values_min_patch': .5,  # threshold on space consistency
                 'fitness_min_patch': -10,  # threshold on time variability
                 # threshold on time variability (if nonsparse activity)
                 'fitness_delta_min_patch': -5,
                 'Npeaks': 5,
                 'r_values_min_full': .8,
                 'fitness_min_full': - 40,
                 'fitness_delta_min_full': - 40,
                 'only_init_patch': True,
                 'gnb': 2,
                 'memory_fact': 1,
                 'n_chunks': 10,
                 'update_background_components': True,# whether to update the background components in the spatial phase
                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
                                     #(to be used with one background per patch)  
                 'swap_dim':False,
                                     
                 }
#%%
params_movie = {'fname': '/mnt/ceph/neuro/labeling/neurofinder.04.00.test/images/final_map/Yr_d1_512_d2_512_d3_1_order_C_frames_3000_.mmap',
                 'p': 1,  # order of the autoregressive system
                 'merge_thresh': 0.8,  # merging threshold, max correlation allow
                 'rf': 20,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
                 'stride_cnmf': 10,  # amounpl.it of overlap between the patches in pixels
                 'K': 5,  # number of components per patch
                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
                 'init_method': 'greedy_roi',
                 'gSig': [5,5],  # expected half size of neurons
                 'alpha_snmf': None,  # this controls sparsity
                 'final_frate': 10,
                 'r_values_min_patch': .5,  # threshold on space consistency
                 'fitness_min_patch': -10,  # threshold on time variability
                 # threshold on time variability (if nonsparse activity)
                 'fitness_delta_min_patch': -10,
                 'Npeaks': 5,
                 'r_values_min_full': .8,
                 'fitness_min_full': - 40,
                 'fitness_delta_min_full': - 40,
                 'only_init_patch': True,
                 'gnb': 2,
                 'memory_fact': 1,
                 'n_chunks': 10,
                 'update_background_components': True,# whether to update the background components in the spatial phase
                 'low_rank_background': True #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
                                     #(to be used with one background per patch)          
                 }

#%% neurofinder 02.00
params_movie = {'fname': '/mnt/ceph/neuro/labeling/neurofinder.02.00/images/final_map/Yr_d1_512_d2_512_d3_1_order_C_frames_8000_.mmap',
                 'p': 1,  # order of the autoregressive system
                 'merge_thresh': 0.8,  # merging threshold, max correlation allow
                 'rf': 20,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
                 'stride_cnmf': 10,  # amounpl.it of overlap between the patches in pixels
                 'K': 6,  # number of components per patch
                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
                 'init_method': 'greedy_roi',
                 'gSig': [5,5],  # expected half size of neurons
                 'alpha_snmf': None,  # this controls sparsity
                 'final_frate': 10,
                 'r_values_min_patch': .5,  # threshold on space consistency
                 'fitness_min_patch': -10,  # threshold on time variability
                 # threshold on time variability (if nonsparse activity)
                 'fitness_delta_min_patch': -10,
                 'Npeaks': 5,
                 'r_values_min_full': .8,
                 'fitness_min_full': - 40,
                 'fitness_delta_min_full': - 40,
                 'only_init_patch': True,
                 'gnb': 2,
                 'memory_fact': 1,
                 'n_chunks': 10,
                 'update_background_components': True,# whether to update the background components in the spatial phase
                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
                                     #(to be used with one background per patch)     
                'swap_dim':False,
                'crop_pix':10
                 }

#%% packer
#params_movie = {'fname': '/mnt/ceph/neuro/labeling/packer.001/images/final_map/Yr_d1_512_d2_512_d3_1_order_C_frames_9900_.mmap',
#                 'p': 1,  # order of the autoregressive system
#                 'merge_thresh': 0.99,  # merging threshold, max correlation allow
#                 'rf': 25,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
#                 'stride_cnmf': 10,  # amounpl.it of overlap between the patches in pixels
#                 'K': 6,  # number of components per patch
#                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
#                 'init_method': 'greedy_roi',
#                 'gSig': [6,6],  # expected half size of neurons
#                 'alpha_snmf': None,  # this controls sparsity
#                 'final_frate': 30,
#                 'r_values_min_patch': .5,  # threshold on space consistency
#                 'fitness_min_patch': -10,  # threshold on time variability
#                 # threshold on time variability (if nonsparse activity)
#                 'fitness_delta_min_patch': -10,
#                 'Npeaks': 5,
#                 'r_values_min_full': .8,
#                 'fitness_min_full': - 40,
#                 'fitness_delta_min_full': - 40,
#                 'only_init_patch': True,
#                 'gnb': 2,
#                 'memory_fact': 1,
#                 'n_chunks': 10,
#                 'update_background_components': False,# whether to update the background components in the spatial phase
#                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
#                                     #(to be used with one background per patch)     
#                'swap_dim':False,
#                'crop_pix':0
#                 }
#%% yuste
params_movie = {'fname': '/mnt/ceph/neuro/labeling/yuste.Single_150u/images/final_map/Yr_d1_200_d2_256_d3_1_order_C_frames_3000_.mmap',
                 'p': 1,  # order of the autoregressive system
                 'merge_thresh': 0.8,  # merging threshold, max correlation allow
                 'rf': 15,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
                 'stride_cnmf': 10,  # amounpl.it of overlap between the patches in pixels
                 'K': 8,  # number of components per patch
                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
                 'init_method': 'greedy_roi',
                 'gSig': [5,5],  # expected half size of neurons
                 'alpha_snmf': None,  # this controls sparsity
                 'final_frate': 10,
                 'r_values_min_patch': .5,  # threshold on space consistency
                 'fitness_min_patch': -10,  # threshold on time variability
                 # threshold on time variability (if nonsparse activity)
                 'fitness_delta_min_patch': -10,
                 'Npeaks': 5,
                 'r_values_min_full': .8,
                 'fitness_min_full': - 40,
                 'fitness_delta_min_full': - 40,
                 'only_init_patch': True,
                 'gnb': 2,
                 'memory_fact': 1,
                 'n_chunks': 10,
                 'update_background_components': True,# whether to update the background components in the spatial phase
                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
                                     #(to be used with one background per patch)     
                 'swap_dim':False,
                 'crop_pix':0
                 }


#%% neurofinder 00.00
params_movie = {'fname': '/mnt/ceph/neuro/labeling/neurofinder.00.00/images/final_map/Yr_d1_512_d2_512_d3_1_order_C_frames_2936_.mmap',
                 'p': 1,  # order of the autoregressive system
                 'merge_thresh': 0.8,  # merging threshold, max correlation allow
                 'rf': 20,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
                 'stride_cnmf': 10,  # amounpl.it of overlap between the patches in pixels
                 'K': 6,  # number of components per patch
                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
                 'init_method': 'greedy_roi',
                 'gSig': [6,6],  # expected half size of neurons
                 'alpha_snmf': None,  # this controls sparsity
                 'final_frate': 10,
                 'r_values_min_patch': .5,  # threshold on space consistency
                 'fitness_min_patch': -10,  # threshold on time variability
                 # threshold on time variability (if nonsparse activity)
                 'fitness_delta_min_patch': -10,
                 'Npeaks': 5,
                 'r_values_min_full': .8,
                 'fitness_min_full': - 40,
                 'fitness_delta_min_full': - 40,
                 'only_init_patch': True,
                 'gnb': 2,
                 'memory_fact': 1,
                 'n_chunks': 10,
                 'update_background_components': True,# whether to update the background components in the spatial phase
                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
                                     #(to be used with one background per patch)     
                 'swap_dim':False,
                 'crop_pix':10
                 }
#%% neurofinder 01.01
params_movie = {'fname': '/mnt/ceph/neuro/labeling/neurofinder.01.01/images/final_map/Yr_d1_512_d2_512_d3_1_order_C_frames_1825_.mmap',
                 'p': 1,  # order of the autoregressive system
                 'merge_thresh': 0.9,  # merging threshold, max correlation allow
                 'rf': 20,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
                 'stride_cnmf': 10,  # amounpl.it of overlap between the patches in pixels
                 'K': 6,  # number of components per patch
                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
                 'init_method': 'greedy_roi',
                 'gSig': [6,6],  # expected half size of neurons
                 'alpha_snmf': None,  # this controls sparsity
                 'final_frate': 10,
                 'r_values_min_patch': .5,  # threshold on space consistency
                 'fitness_min_patch': -10,  # threshold on time variability
                 # threshold on time variability (if nonsparse activity)
                 'fitness_delta_min_patch': -10,
                 'Npeaks': 5,
                 'r_values_min_full': .8,
                 'fitness_min_full': - 40,
                 'fitness_delta_min_full': - 40,
                 'only_init_patch': True,
                 'gnb': 2,
                 'memory_fact': 1,
                 'n_chunks': 10,
                 'update_background_components': True,# whether to update the background components in the spatial phase
                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
                                     #(to be used with one background per patch)     
                 'swap_dim':False,
                 'crop_pix':2,
                 'filter_after_patch':True
                 }
#%% Sue Ann k56
params_movie = {'fname': '/opt/local/Data/labeling/k53_20160530/Yr_d1_512_d2_512_d3_1_order_C_frames_116043_.mmap',
                'gtname':'/mnt/ceph/neuro/labeling/k53_20160530/regions/joined_consensus_active_regions.npy',
                 'p': 1,  # order of the autoregressive system
                 'merge_thresh': 0.8,  # merging threshold, max correlation allow
                 'rf': 20,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
                 'stride_cnmf': 10,  # amounpl.it of overlap between the patches in pixels
                 'K': 9,  # number of components per patch
                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
                 'init_method': 'greedy_roi',
                 'gSig': [6,6],  # expected half size of neurons
                 'alpha_snmf': None,  # this controls sparsity
                 'final_frate': 30,
                 'r_values_min_patch': .5,  # threshold on space consistency
                 'fitness_min_patch': -10,  # threshold on time variability
                 # threshold on time variability (if nonsparse activity)
                 'fitness_delta_min_patch': -10,
                 'Npeaks': 5,
                 'r_values_min_full': .8,
                 'fitness_min_full': - 40,
                 'fitness_delta_min_full': - 40,
                 'only_init_patch': True,
                 'gnb': 2,
                 'memory_fact': 1,
                 'n_chunks': 10,
                 'update_background_components': True,# whether to update the background components in the spatial phase
                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
                                     #(to be used with one background per patch)     
                 'swap_dim':False,
                 'crop_pix':2,
                 'filter_after_patch':True
                 }

#%% J115
params_movie = {'fname': '/mnt/ceph/neuro/labeling/J115_2015-12-09_L01_ELS/images/final_map/Yr_d1_463_d2_472_d3_1_order_C_frames_90000_.mmap',
                'gtname':'/mnt/ceph/neuro/labeling/J115_2015-12-09_L01_ELS/regions/joined_consensus_active_regions.npy',
                 'p': 1,  # order of the autoregressive system
                 'merge_thresh': 0.8,  # merging threshold, max correlation allow
                 'rf': 20,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
                 'stride_cnmf': 10,  # amounpl.it of overlap between the patches in pixels
                 'K': 7,  # number of components per patch
                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
                 'init_method': 'greedy_roi',
                 'gSig': [7,7],  # expected half size of neurons
                 'alpha_snmf': None,  # this controls sparsity
                 'final_frate': 30,
                 'r_values_min_patch': .5,  # threshold on space consistency
                 'fitness_min_patch': -10,  # threshold on time variability
                 # threshold on time variability (if nonsparse activity)
                 'fitness_delta_min_patch': -10,
                 'Npeaks': 5,
                 'r_values_min_full': .8,
                 'fitness_min_full': - 40,
                 'fitness_delta_min_full': - 40,
                 'only_init_patch': True,
                 'gnb': 2,
                 'memory_fact': 1,
                 'n_chunks': 10,
                 'update_background_components': True,# whether to update the background components in the spatial phase
                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
                                     #(to be used with one background per patch)     
                 'swap_dim':False,
                 'crop_pix':2,
                 'filter_after_patch':True
                 }

#%% J123
params_movie = {'fname': '/mnt/ceph/neuro/labeling/J123_2015-11-20_L01_0/images/final_map/Yr_d1_458_d2_477_d3_1_order_C_frames_41000_.mmap',
                'gtname':'/mnt/ceph/neuro/labeling/J123_2015-11-20_L01_0/regions/joined_consensus_active_regions.npy',
                 'p': 1,  # order of the autoregressive system
                 'merge_thresh': 0.8,  # merging threshold, max correlation allow
                 'rf': 40,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
                 'stride_cnmf': 20,  # amounpl.it of overlap between the patches in pixels
                 'K': 10,  # number of components per patch
                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
                 'init_method': 'greedy_roi',
                 'gSig': [12,12],  # expected half size of neurons
                 'alpha_snmf': None,  # this controls sparsity
                 'final_frate': 15,
                 'r_values_min_patch': .5,  # threshold on space consistency
                 'fitness_min_patch': -10,  # threshold on time variability
                 # threshold on time variability (if nonsparse activity)
                 'fitness_delta_min_patch': -10,
                 'Npeaks': 5,
                 'r_values_min_full': .8,
                 'fitness_min_full': - 40,
                 'fitness_delta_min_full': - 40,
                 'only_init_patch': True,
                 'gnb': 2,
                 'memory_fact': 1,
                 'n_chunks': 10,
                 'update_background_components': True,# whether to update the background components in the spatial phase
                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
                                     #(to be used with one background per patch)     
                 'swap_dim':False,
                 'crop_pix':2,
                 'filter_after_patch':True
                 }

#%% Jan AMG
params_movie = {'fname': '/opt/local/Data/Jan/Jan-AMG_exp3_001/Yr_d1_512_d2_512_d3_1_order_C_frames_115897_.mmap',
                'gtname':'/mnt/ceph/neuro/labeling/Jan-AMG_exp3_001/regions/joined_consensus_active_regions.npy',
                 'p': 1,  # order of the autoregressive system
                 'merge_thresh': 0.8,  # merging threshold, max correlation allow
                 'rf': 25,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
                 'stride_cnmf': 10,  # amounpl.it of overlap between the patches in pixels
                 'K': 6,  # number of components per patch
                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
                 'init_method': 'greedy_roi',
                 'gSig': [7,7],  # expected half size of neurons
                 'alpha_snmf': None,  # this controls sparsity
                 'final_frate':30,
                 'r_values_min_patch': .5,  # threshold on space consistency
                 'fitness_min_patch': -10,  # threshold on time variability
                 # threshold on time variability (if nonsparse activity)
                 'fitness_delta_min_patch': -10,
                 'Npeaks': 5,
                 'r_values_min_full': .8,
                 'fitness_min_full': - 40,
                 'fitness_delta_min_full': - 40,
                 'only_init_patch': True,
                 'gnb': 2,
                 'memory_fact': 1,
                 'n_chunks': 30,
                 'update_background_components': True,# whether to update the background components in the spatial phase
                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
                                     #(to be used with one background per patch)     
                 'swap_dim':False,
                 'crop_pix':8,
                 'filter_after_patch':True
                 }
#%%
params_movie = {'fname': '/mnt/ceph/neuro/labeling/k37_20160109_AM_150um_65mW_zoom2p2_00001_1-16/images/final_map/Yr_d1_512_d2_512_d3_1_order_C_frames_48000_.mmap',
                'gtname':'/mnt/ceph/neuro/labeling/k37_20160109_AM_150um_65mW_zoom2p2_00001_1-16/regions/joined_consensus_active_regions.npy',
                 'p': 1,  # order of the autoregressive system
                 'merge_thresh': 0.8,  # merging threshold, max correlation allow
                 'rf': 20,  # half-size of the patches in pixels. rf=25, patches are 50x50    20
                 'stride_cnmf': 10,  # amounpl.it of overlap between the patches in pixels
                 'K': 5,  # number of components per patch
                 'is_dendrites': False,  # if dendritic. In this case you need to set init_method to sparse_nmf
                 'init_method': 'greedy_roi',
                 'gSig': [6,6],  # expected half size of neurons
                 'alpha_snmf': None,  # this controls sparsity
                 'final_frate':30,
                 'r_values_min_patch': .5,  # threshold on space consistency
                 'fitness_min_patch': -10,  # threshold on time variability
                 # threshold on time variability (if nonsparse activity)
                 'fitness_delta_min_patch': -10,
                 'Npeaks': 5,
                 'r_values_min_full': .8,
                 'fitness_min_full': - 40,
                 'fitness_delta_min_full': - 40,
                 'only_init_patch': True,
                 'gnb': 2,
                 'memory_fact': 1,
                 'n_chunks': 30,
                 'update_background_components': True,# whether to update the background components in the spatial phase
                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
                                     #(to be used with one background per patch)     
                 'swap_dim':False,
                 'crop_pix':8,
                 'filter_after_patch':True
                 }
#%% yuste: sue ann
#params_movie = {'fname': '/mnt/ceph/neuro/labeling/yuste.Single_150u/images/final_map/Yr_d1_200_d2_256_d3_1_order_C_frames_3000_.mmap',
#                'seed_name':'/mnt/xfs1/home/agiovann/Downloads/yuste_sue_masks.mat',
#                 'p': 1,  # order of the autoregressive system
#                 'merge_thresh': 1,  # merging threshold, max correlation allow
#                 'final_frate': 10,
#                 'gnb': 1,
#                 'update_background_components': True,# whether to update the background components in the spatial phase
#                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
#                                     #(to be used with one background per patch)  
#                 'swap_dim':False, #for some movies needed
#                 'kernel':None,
#                 'Npeaks': 5,
#                 'r_values_min_full': .8,
#                 'fitness_min_full': - 40,
#                 'fitness_delta_min_full': - 40,
#                 }
##%% SUE neuronfinder00.00
#params_movie = {'fname': '/mnt/ceph/neuro/labeling/neurofinder.00.00/images/final_map/Yr_d1_512_d2_512_d3_1_order_C_frames_2936_.mmap',
#                'seed_name':'/mnt/xfs1/home/agiovann/Downloads/neurofinder_00.00_sue_masks.mat',
#                 'p': 1,  # order of the autoregressive system
#                 'merge_thresh': 1,  # merging threshold, max correlation allow
#                 'final_frate': 10,
#                 'gnb': 1,
#                 'update_background_components': True,# whether to update the background components in the spatial phase
#                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
#                                     #(to be used with one background per patch)  
#                 'swap_dim':False, #for some movies needed
#                 'kernel':None,
#                 'Npeaks': 5,
#                 'r_values_min_full': .8,
#                 'fitness_min_full': - 40,
#                 'fitness_delta_min_full': - 40,
#                 }
##%% SUE neuronfinder02.00
#params_movie = {'fname': '/mnt/ceph/neuro/labeling/neurofinder.02.00/images/final_map/Yr_d1_512_d2_512_d3_1_order_C_frames_8000_.mmap',
#                'seed_name':'/mnt/xfs1/home/agiovann/Downloads/neurofinder_02.00_sue_masks.mat',
#                 'p': 1,  # order of the autoregressive system
#                 'merge_thresh': 1,  # merging threshold, max correlation allow
#                 'final_frate': 10,
#                 'gnb': 1,
#                 'update_background_components': True,# whether to update the background components in the spatial phase
#                 'low_rank_background': True, #whether to update the using a low rank approximation. In the False case all the nonzero elements of the background components are updated using hals    
#                                     #(to be used with one background per patch)  
#                 'swap_dim':False, #for some movies needed
#                 'kernel':None,
#                 'Npeaks': 5,
#                 'r_values_min_full': .8,
#                 'fitness_min_full': - 40,
#                 'fitness_delta_min_full': - 40,
#                 }
#%%
params_display = {
    'downsample_ratio': .2,
    'thr_plot': 0.8
}
# TODO: do find&replace on those parameters and delete this paragrph

# @params fname name of the movie
fname_new = params_movie['fname']
# %% RUN ANALYSIS
c, dview, n_processes = setup_cluster(
    backend='local', n_processes=None, single_thread=False)
# %% LOAD MEMMAP FILE
# fname_new='Yr_d1_501_d2_398_d3_1_order_F_frames_369_.mmap'
Yr, dims, T = cm.load_memmap(fname_new)
d1, d2 = dims
images = np.reshape(Yr.T, [T] + list(dims), order='F')
# TODO: needinfo
Y = np.reshape(Yr, dims + (T,), order='F')
m_images = cm.movie(images)

# TODO: show screenshot 10
# %% correlation image
if m_images.shape[0]<10000:
    Cn = m_images.local_correlations(swap_dim = params_movie['swap_dim'], frames_per_chunk = 1500)
    Cn[np.isnan(Cn)] = 0
    check_nan = False
else:
    Cn = np.array(cm.load(('/'.join(params_movie['gtname'].split('/')[:-2]+['projections','correlation_image.tif'])))).squeeze()
    check_nan = False
pl.imshow(Cn, cmap='gray', vmax=.95)
#%%
if 'seed_name' in params_movie:
    import cv2
    if not '.mat' in params_movie['seed_name']:
        roi_cons = np.load(params_movie['seed_name'])
    else:
        roi_cons = scipy.io.loadmat(params_movie['seed_name'])['comps'].reshape((dims[1],dims[0],-1),order='F').transpose([2,1,0])*1.
        
    radius  = np.int(np.median(np.sqrt(np.sum(roi_cons,(1,2))/np.pi)))
    
    print(radius)
    #roi_cons = caiman.base.rois.nf_read_roi_zip('/mnt/ceph/neuro/labeling/neurofinder.03.00.test/regions/ben_active_regions_nd_sonia_active_regions_nd__lindsey_active_regions_nd_matches.zip',dims)
    #roi_cons = np.concatenate([roi_cons, caiman.base.rois.nf_read_roi_zip('/mnt/ceph/neuro/labeling/neurofinder.03.00.test/regions/intermediate_regions/ben_active_regions_nd_sonia_active_regions_nd__lindsey_active_regions_nd_1_mismatches.zip',dims)],0)
    
    print(roi_cons.shape)
    pl.imshow(roi_cons.sum(0))
    
    if params_movie['kernel'] is not None: # kernel usually two
        kernel = np.ones((radius//params_movie['kernel'],radius//params_movie['kernel']),np.uint8)
        roi_cons = np.vstack([cv2.dilate(rr,kernel,iterations = 1)[np.newaxis,:,:]>0 for rr in roi_cons])*1.
        pl.imshow(roi_cons.sum(0),alpha = 0.5)
    
    A_in = np.reshape(roi_cons.transpose([2,1,0]),(-1,roi_cons.shape[0]),order = 'C')
    pl.figure()
    crd = plot_contours(A_in, Cn, thr=.99999)    
    # %% some parameter settings
    # order of the autoregressive fit to calcium imaging in general one (slow gcamps) or two (fast gcamps fast scanning)
    p = params_movie['p']
    # merging threshold, max correlation allowed
    merge_thresh = params_movie['merge_thresh']
    
    # %% Extract spatial and temporal components
    # TODO: todocument
    t1 = time.time()
    if images.shape[0]>10000:
        check_nan = False
    else:
        check_nan = True
        
    cnm = cnmf.CNMF(check_nan = check_nan, n_processes=1, k=A_in.shape[-1], gSig=[radius,radius], merge_thresh=params_movie['merge_thresh'], p=params_movie['p'], Ain = A_in.astype(np.bool),
                    dview=dview, rf=None, stride=None, gnb=params_movie['gnb'], method_deconvolution='oasis',border_pix = 0, low_rank_background = params_movie['low_rank_background'], n_pixels_per_process = 1000) 
    cnm = cnm.fit(images)
    
    A = cnm.A
    C = cnm.C
    YrA = cnm.YrA
    b = cnm.b
    f = cnm.f
    sn = cnm.sn
    print(('Number of components:' + str(A.shape[-1])))
    t_patch = time.time() - t1
    # %% again recheck quality of components, stricter criteria
    final_frate = params_movie['final_frate']
    r_values_min = params_movie['r_values_min_full']  # threshold on space consistency
    fitness_min = params_movie['fitness_min_full']  # threshold on time variability
    # threshold on time variability (if nonsparse activity)
    fitness_delta_min = params_movie['fitness_delta_min_full']
    Npeaks = params_movie['Npeaks']
    traces = C + YrA
    idx_components, idx_components_bad, fitness_raw, fitness_delta, r_values = estimate_components_quality(
        traces, Y, A, C, b, f, final_frate=final_frate, Npeaks=Npeaks, r_values_min=r_values_min, fitness_min=fitness_min,
        fitness_delta_min=fitness_delta_min, return_all=True)
    print(' ***** ')
    print((len(traces)))
    print((len(idx_components)))
#%%    
else:
    # %% some parameter settings
    # order of the autoregressive fit to calcium imaging in general one (slow gcamps) or two (fast gcamps fast scanning)
    p = params_movie['p']
    # merging threshold, max correlation allowed
    merge_thresh = params_movie['merge_thresh']
    # half-size of the patches in pixels. rf=25, patches are 50x50
    rf = params_movie['rf']
    # amounpl.it of overlap between the patches in pixels
    stride_cnmf = params_movie['stride_cnmf']
    # number of components per patch
    K = params_movie['K']
    # if dendritic. In this case you need to set init_method to sparse_nmf
    is_dendrites = params_movie['is_dendrites']
    # iinit method can be greedy_roi for round shapes or sparse_nmf for denritic data
    init_method = params_movie['init_method']
    # expected half size of neurons
    gSig = params_movie['gSig']
    # this controls sparsity
    alpha_snmf = params_movie['alpha_snmf']
    # frame rate of movie (even considering eventual downsampling)
    final_frate = params_movie['final_frate']
    
    if params_movie['is_dendrites'] == True:
        if params_movie['init_method'] is not 'sparse_nmf':
            raise Exception('dendritic requires sparse_nmf')
        if params_movie['alpha_snmf'] is None:
            raise Exception('need to set a value for alpha_snmf')
    # %% Extract spatial and temporal components on patches
    t1 = time.time()
    # TODO: todocument
    # TODO: warnings 3
    cnm = cnmf.CNMF(n_processes=1, nb_patch = 1, k=K, gSig=gSig, merge_thresh=params_movie['merge_thresh'], p=params_movie['p'],
                    dview=dview, rf=rf, stride=stride_cnmf, memory_fact=1,
                    method_init=init_method, alpha_snmf=alpha_snmf, only_init_patch=params_movie['only_init_patch'],
                    gnb=params_movie['gnb'], method_deconvolution='oasis',border_pix =  params_movie['crop_pix'], 
                    low_rank_background = params_movie['low_rank_background'], rolling_sum = True, check_nan=check_nan) 
    cnm = cnm.fit(images)
    
    A_tot = cnm.A
    C_tot = cnm.C
    YrA_tot = cnm.YrA
    b_tot = cnm.b
    f_tot = cnm.f
    sn_tot = cnm.sn
    print(('Number of components:' + str(A_tot.shape[-1])))
    t_patch = time.time() - t1

    c, dview, n_processes = cm.cluster.setup_cluster(
    backend='local', n_processes=None, single_thread=False)
    # %%
    pl.figure()
    # TODO: show screenshot 12`
    # TODO : change the way it is used
    crd = plot_contours(A_tot, Cn, thr=params_display['thr_plot'])
    
    # %% DISCARD LOW QUALITY COMPONENT
    if params_movie['filter_after_patch']:
        final_frate = params_movie['final_frate']
        r_values_min = params_movie['r_values_min_patch']  # threshold on space consistency
        fitness_min = params_movie['fitness_delta_min_patch']  # threshold on time variability
        # threshold on time variability (if nonsparse activity)
        fitness_delta_min = params_movie['fitness_delta_min_patch']
        Npeaks = params_movie['Npeaks']
        traces = C_tot + YrA_tot
        # TODO: todocument
        idx_components, idx_components_bad = estimate_components_quality(
            traces, Y, A_tot, C_tot, b_tot, f_tot, final_frate=final_frate, Npeaks=Npeaks, r_values_min=r_values_min,
            fitness_min=fitness_min, fitness_delta_min=fitness_delta_min, dview = dview)
        print(('Keeping ' + str(len(idx_components)) +
               ' and discarding  ' + str(len(idx_components_bad))))
        # %%
        # TODO: show screenshot 13
        pl.figure()
        crd = plot_contours(A_tot.tocsc()[:, idx_components], Cn, thr=params_display['thr_plot'])
        #%%
        idds = idx_components
        view_patches_bar(Yr, scipy.sparse.coo_matrix(A_tot.tocsc()[:, idds]), C_tot[idds, :], b_tot, f_tot, dims[0],
                     dims[1], YrA=YrA_tot[idds, :], img=Cn)
        # %%
        A_tot = A_tot.tocsc()[:, idx_components]
        C_tot = C_tot[idx_components]
    # %% rerun updating the components to refine
    t1 = time.time()
    cnm = cnmf.CNMF(n_processes=1, k=A_tot.shape, gSig=gSig, merge_thresh=merge_thresh, p=p, dview=dview, Ain=A_tot,
                    Cin=C_tot, b_in = b_tot,
                    f_in=f_tot, rf=None, stride=None, method_deconvolution='oasis',gnb = params_movie['gnb'],
                    low_rank_background = params_movie['low_rank_background'], 
                    update_background_components = params_movie['update_background_components'], check_nan=check_nan)
    
    cnm = cnm.fit(images)
    t_refine = time.time() - t1

    #%
    A, C, b, f, YrA, sn = cnm.A, cnm.C, cnm.b, cnm.f, cnm.YrA, cnm.sn
    # %% again recheck quality of components, stricter criteria
    t1 = time.time()
    final_frate = params_movie['final_frate']
    r_values_min = params_movie['r_values_min_full']  # threshold on space consistency
    fitness_min = params_movie['fitness_min_full']  # threshold on time variability
    # threshold on time variability (if nonsparse activity)
    fitness_delta_min = params_movie['fitness_delta_min_full']
    Npeaks = params_movie['Npeaks']
    traces = C + YrA
    idx_components, idx_components_bad, fitness_raw, fitness_delta, r_values = estimate_components_quality(
        traces, Y, A, C, b, f, final_frate=final_frate, Npeaks=Npeaks, r_values_min=r_values_min, fitness_min=fitness_min,
        fitness_delta_min=fitness_delta_min, return_all=True, dview = dview, num_traces_per_group = 50)
    t_eva_comps = time.time() - t1
    print(' ***** ')
    print((len(traces)))
    print((len(idx_components)))
    # %% save results
    np.savez(os.path.join(os.path.split(fname_new)[0], os.path.split(fname_new)[1][:-4] + 'results_analysis.npz'), Cn=Cn, fname_new = fname_new,
             A=A,
             C=C, b=b, f=f, YrA=YrA, sn=sn, d1=d1, d2=d2, idx_components=idx_components,
             idx_components_bad=idx_components_bad,
             fitness_raw=fitness_raw, fitness_delta=fitness_delta, r_values=r_values)
    
# we save it
# %%
# TODO: show screenshot 14
pl.subplot(1, 2, 1)
crd = plot_contours(A.tocsc()[:, idx_components], Cn, thr=params_display['thr_plot'])
pl.subplot(1, 2, 2)
crd = plot_contours(A.tocsc()[:, idx_components_bad], Cn, thr=params_display['thr_plot'])
# %%
# TODO: needinfo
view_patches_bar(Yr, scipy.sparse.coo_matrix(A.tocsc()[:, idx_components]), C[idx_components, :], b, f, dims[0], dims[1],
                 YrA=YrA[idx_components, :], img=Cn)
# %%
view_patches_bar(Yr, scipy.sparse.coo_matrix(A.tocsc()[:, idx_components_bad]), C[idx_components_bad, :], b, f, dims[0],
                 dims[1], YrA=YrA[idx_components_bad, :], img=Cn)

#%% LOAD DATA
params_display = {
    'downsample_ratio': .2,
    'thr_plot': 0.8
}
fn_old = fname_new 
#analysis_file = '/mnt/ceph/neuro/jeremie_analysis/neurofinder.03.00.test/Yr_d1_498_d2_467_d3_1_order_C_frames_2250_._results_analysis.npz'
with np.load(os.path.join(os.path.split(fname_new)[0], os.path.split(fname_new)[1][:-4] + 'results_analysis.npz'), encoding = 'latin1') as ld:
    print(ld.keys())
    locals().update(ld) 
    dims_off = d1,d2    
    A = scipy.sparse.coo_matrix(A[()])
    dims = (d1,d2)
    gSig = params_movie['gSig']
    fname_new = fn_old

#%%
all_matches = False
filter_SNR = False
gt_file = os.path.join(os.path.split(fname_new)[0], os.path.split(fname_new)[1][:-4] + 'match_masks.npz')
with np.load(gt_file, encoding = 'latin1') as ld:
    print(ld.keys())
    locals().update(ld)
    A_gt = scipy.sparse.coo_matrix(A_gt[()])
    dims = (d1,d2)
    try:
        fname_new = fname_new[()].decode('unicode_escape')    
    except:
        fname_new = fname_new[()]        
    if all_matches:
        roi_all_match = cm.base.rois.nf_read_roi_zip(glob.glob('/'.join(os.path.split(fname_new)[0].split('/')[:-2]+['regions/*nd_matches.zip']))[0],dims)
#        roi_1_match = cm.base.rois.nf_read_roi_zip('/mnt/ceph/neuro/labeling/neurofinder.02.00/regions/intermediate_regions/ben_active_regions_nd_natalia_active_regions_nd__sonia_active_regions_nd__lindsey_active_regions_nd_1_mismatches.zip',dims)
#        roi_all_match = roi_1_match#np.concatenate([roi_all_match, roi_1_match],axis = 0)
        A_gt_thr = roi_all_match.transpose([1,2,0]).reshape((np.prod(dims),-1),order = 'F')
        A_gt = A_gt_thr 
    else:   
        if filter_SNR:
            final_frate = params_movie['final_frate']        
            Npeaks = params_movie['Npeaks']
            traces_gt = C_gt + YrA_gt
            idx_filter_snr, idx_filter_snr_bad, fitness_raw_gt, fitness_delta_gt, r_values_gt = estimate_components_quality(
                traces_gt, Y, A_gt, C_gt, b_gt, f_gt, final_frate=final_frate, Npeaks=Npeaks, r_values_min=1, fitness_min=-10,
                fitness_delta_min=-10, return_all=True)
            
            print(len(idx_filter_snr))
            print(len(idx_filter_snr_bad))
            A_gt, C_gt, b_gt, f_gt, traces_gt, YrA_gt = A_gt.tocsc()[:,idx_filter_snr], C_gt[idx_filter_snr], b_gt, f_gt, traces_gt[idx_filter_snr], YrA_gt[idx_filter_snr]
        
        A_gt_thr = cm.source_extraction.cnmf.spatial.threshold_components(A_gt.tocsc()[:,:].toarray(), dims, medw=None, thr_method='max', maxthr=0.2, nrgthr=0.99, extract_cc=True,
                         se=None, ss=None, dview=None) 

#%%
pl.figure()
crd = plot_contours(A_gt_thr, Cn, thr=.99)
        
#%%
from caiman.components_evaluation import evaluate_components_CNN
predictions,final_crops = evaluate_components_CNN(A,dims,gSig,model_name = 'use_cases/CaImAnpaper/cnn_model')
#%%
threshold = .95
from caiman.utils.visualization import matrixMontage
pl.figure()
matrixMontage(np.squeeze(final_crops[np.where(predictions[:,1]>=threshold)[0]]))
pl.figure()
matrixMontage(np.squeeze(final_crops[np.where(predictions[:,0]>=threshold)[0]]))

#%%
cm.movie(final_crops).play(gain=3,magnification = 6,fr=5)
#%%
cm.movie(np.squeeze(final_crops[np.where(predictions[:,1]>=0.95)[0]])).play(gain=2., magnification = 8,fr=5)
#%%
cm.movie(np.squeeze(final_crops[np.where(predictions[:,0]>=0.95)[0]])).play(gain=4., magnification = 8,fr=5)
#%%
min_size_neuro = 3*2*np.pi
max_size_neuro = (2*gSig[0])**2*np.pi
A_thr = cm.source_extraction.cnmf.spatial.threshold_components(A.tocsc()[:,:].toarray(), dims, medw=None, thr_method='max', maxthr=0.2, nrgthr=0.99, extract_cc=True,
                         se=None, ss=None, dview=dview) 

A_thr = A_thr > 0  
size_neurons = A_thr.sum(0)
idx_size_neuro = np.where((size_neurons>min_size_neuro) & (size_neurons<max_size_neuro) )[0]
#A_thr = A_thr[:,idx_size_neuro]
print(A_thr.shape)
#%%
thresh = .95
idx_components_cnn = np.where(predictions[:,1]>=thresh)[0]

print(' ***** ')
print((len(final_crops)))
print((len(idx_components_cnn)))
#print((len(idx_blobs)))    
#%
idx_components_r = np.where((r_values >= .8))[0]
idx_components_raw = np.where(fitness_raw < -20)[0]
idx_components_delta = np.where(fitness_delta < -20)[0]   

bad_comps = np.where((r_values <= 0) | (fitness_raw >= -4) | (predictions[:,1]<=.1))[0]
#idx_and_condition_1 = np.where((r_values >= .65) & ((fitness_raw < -20) | (fitness_delta < -20)) )[0]

idx_components = np.union1d(idx_components_r, idx_components_raw)
idx_components = np.union1d(idx_components, idx_components_delta)
idx_components = np.union1d(idx_components,idx_components_cnn)
idx_components = np.setdiff1d(idx_components,bad_comps)
#idx_components = np.intersect1d(idx_components,idx_size_neuro)
#idx_components = np.union1d(idx_components, idx_and_condition_1)
#idx_components = np.union1d(idx_components, idx_and_condition_2)

#idx_blobs = np.intersect1d(idx_components, idx_blobs)
idx_components_bad = np.setdiff1d(list(range(len(r_values))), idx_components)

print(' ***** ')
print((len(r_values)))
print((len(idx_components)))  
#%%
pl.figure()
pl.subplot(1, 2, 1)
crd = plot_contours(A.tocsc()[:, idx_components], Cn, thr=params_display['thr_plot'], vmax = 0.85)
pl.subplot(1, 2, 2)
crd = plot_contours(A.tocsc()[:, idx_components_bad], Cn, thr=params_display['thr_plot'], vmax = 0.85)
#%%
#from sklearn.preprocessing import normalize
#
#dist_A = (normalize(A_gt.tocsc()[:,:],axis = 0).T.dot(normalize(A.tocsc()[:,idx_components],axis = 0))).toarray()
#dist_C = normalize(C_gt[:],axis = 1).dot(normalize(C[idx_components],axis = 1).T)
#dist_A = dist_A*(dist_A>0)
#plot_results = True
#if plot_results:
#    pl.figure(figsize=(30,20))
#    
#tp_gt, tp_comp, fn_gt, fp_comp, performance_cons_off =  cm.base.rois.nf_match_neurons_in_binary_masks(A_gt.toarray()[:,:].reshape([dims[0],dims[1],-1],order = 'F').transpose([2,0,1]),
#                                                                              A.toarray()[:,idx_components].reshape([dims[0],dims[1],-1],order = 'F').transpose([2,0,1]),thresh_cost=.7, min_dist = 10,
#                                                                              print_assignment= False,plot_results=plot_results,Cn=Cn, labels = ['GT','Offline'], D = [1 - dist_A*(dist_C>.8)])
#pl.rcParams['pdf.fonttype'] = 42
#font = {'family' : 'Arial',
#        'weight' : 'regular',
#        'size'   : 20}
#pl.rc('font', **font)
#from sklearn.preprocessing import normalize


#%%
plot_results = True
if plot_results:
    pl.figure(figsize=(30,20))

#tp_gt, tp_comp, fn_gt, fp_comp, performance_cons_off =  cm.base.rois.nf_match_neurons_in_binary_masks(A_gt_thr[:,idx_components_gt].reshape([dims[0],dims[1],-1],order = 'F').transpose([2,0,1])*1.,
#                                                                              A_thr[:,idx_components].reshape([dims[0],dims[1],-1],order = 'F').transpose([2,0,1])*1.,thresh_cost=.7, min_dist = 10,
#                                                                              print_assignment= False,plot_results=plot_results,Cn=Cn, labels = ['GT','Offline'])  

tp_gt, tp_comp, fn_gt, fp_comp, performance_cons_off =  cm.base.rois.nf_match_neurons_in_binary_masks(A_gt_thr[:,:].reshape([dims[0],dims[1],-1],order = 'F').transpose([2,0,1])*1.,
                                                                              A_thr[:,idx_components].reshape([dims[0],dims[1],-1],order = 'F').transpose([2,0,1])*1.,thresh_cost=.7, min_dist = 10,
                                                                              print_assignment= False,plot_results=plot_results,Cn=Cn, labels = ['GT','Offline'])

pl.rcParams['pdf.fonttype'] = 42
font = {'family' : 'Arial',
        'weight' : 'regular',
        'size'   : 20}

pl.rc('font', **font)
print({a:b.astype(np.float16) for a,b in performance_cons_off.items()})
#%%
np.savez(os.path.join(os.path.split(fname_new)[0], os.path.split(fname_new)[1][:-4] + 'results_comparison_cnn.npz'),tp_gt = tp_gt, tp_comp = tp_comp, fn_gt = fn_gt, fp_comp = fp_comp, performance_cons_off = performance_cons_off,idx_components = idx_components, A_gt = A_gt, C_gt = C_gt
        , b_gt = b_gt , f_gt = f_gt, dims = dims, YrA_gt = YrA_gt, A = A, C = C, b = b, f = f, YrA = YrA, Cn = Cn)
#%%
view_patches_bar(Yr, scipy.sparse.coo_matrix(A_gt.tocsc()[:, fn_gt]), C_gt[fn_gt, :], b_gt, f_gt, dims[0], dims[1],
                 YrA=YrA_gt[fn_gt, :], img=Cn)

#%%
view_patches_bar(Yr, scipy.sparse.coo_matrix(A.tocsc()[:, idx_components[fp_comp]]), C[idx_components[fp_comp]], b, f, dims[0], dims[1],
                 YrA=YrA[idx_components[fp_comp]], img=Cn)
