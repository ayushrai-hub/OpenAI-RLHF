# graft/main.py

import numpy as np
import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd
import pickle

from graft import utilsF

def create_output_dirs(output_dir):
    """Ensure that the given output directory incl. subdirectories exists."""
    for subdir_name in ('n_graphs', 'circ_stat', 'mov', 'plots'):
        subdir_path = os.path.join(output_dir, subdir_name)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)

def process_graphs(image_series, params):
    """
    Processes a series of images to generate and tag graphs based on given parameters.
    Returns graphs and other metadata.
    """
    graphs, pos_lists, skel_images, af_images, bl_images, masks, df_positions = [], [], [], [], [], [], []
    for img in image_series:
        graph, pos_list, skel_image, af_image, bl_image, mask, df_pos = utilsF.creategraph(
            img, size=params['size'], eps=params['eps'], thresh_top=params['thresh_top'],
            sigma=params['sigma'], small=params['small']
        )
        graphs.append(graph)
        pos_lists.append(pos_list)
        skel_images.append(skel_image)
        af_images.append(af_image)
        bl_images.append(bl_image)
        masks.append(mask)
        df_positions.append(df_pos)
    return graphs, pos_lists, skel_images, af_images, bl_images, masks, df_positions

def save_graphs(graphs, pos_lists, output_dir):
    """
    Saves graphs as images to the specified directory.
    """
    for idx, (graph, pos_list) in enumerate(zip(graphs, pos_lists)):
        utilsF.draw_graph_filament_nocolor(graph, pos_list, title='', label='filament')
        plt.savefig(os.path.join(output_dir, f'graph{idx}.png'))
        plt.close('all')

def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    create_output_dirs(pathsave)
    img_padded = np.pad(img_o, ((0,0), (1,1), (1,1)), 'constant')
    params = {
        'size': size, 'eps': eps, 'thresh_top': thresh_top, 'sigma': sigma, 'small': small
    }
    graphs, pos_lists, _, _, _, _, _ = process_graphs(img_padded, params)
    save_graphs(graphs, pos_lists, os.path.join(pathsave, 'n_graphs'))
    # Continue with further specific processing...

def create_all_still(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, name_cell):
    create_output_dirs(pathsave)
    img_padded = np.pad(img_o, (1,1), 'constant')
    params = {
        'size': size, 'eps': eps, 'thresh_top': thresh_top, 'sigma': sigma, 'small': small
    }
    graph, pos_list, _, _, _, _, _ = process_graphs([img_padded], params)
    save_graphs([graph], [pos_list], os.path.join(pathsave, 'n_graphs'))
    # Continue with further specific processing...

