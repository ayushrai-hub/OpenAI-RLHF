#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd
import pickle

from collections import Counter
from graft import utilsF


def create_output_dirs(output_dir):
    """Ensure that the given output directory incl. subdirectories exists."""
    for subdir_name in ('n_graphs', 'circ_stat', 'mov', 'plots'):
        subdir_path = os.path.join(output_dir, subdir_name)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)


def generate_default_mask(image_shape):
    """Generate a default mask of ones based on the image shape."""
    if len(image_shape) == 3:  # Time-series image
        return np.ones(image_shape[1:])
    elif len(image_shape) == 2:  # Still image
        return np.ones(image_shape)
    else:
        raise ValueError("Unsupported image shape. Expected 2 or 3 dimensions.")


def process_graph(image, params):
    """
    Process a single image to generate a graph and associated metadata.
    """
    graph, pos_list, img_skel, img_af, img_bl, img_f, mask, df_pos = utilsF.creategraph(
        image, size=params['size'], eps=params['eps'], thresh_top=params['thresh_top'],
        sigma=params['sigma'], small=params['small']
    )
    return {
        'graph': graph,
        'pos_list': pos_list,
        'img_skel': img_skel,
        'img_af': img_af,
        'img_bl': img_bl,
        'img_f': img_f,
        'mask': mask,
        'df_pos': df_pos,
    }


def save_graph(graph, pos_list, img, output_dir, idx):
    """
    Save a graph image to the specified directory.
    """
    utilsF.draw_graph_filament_nocolor(img, graph, pos_list, title='', label='filament')
    plt.savefig(os.path.join(output_dir, f'graph{idx}.png'))
    plt.close('all')


def run_graph_analysis(graph, img_bl, pos_list, angleA, overlap):
    """
    Perform the main graph analysis steps.
    """
    graph_d = utilsF.dangling_edges(graph.copy())
    lgG = nx.line_graph(graph.copy())
    lgG_V = utilsF.lG_edgeVal(lgG.copy(), graph_d, pos_list)
    graph_tagg = utilsF.dfs_constrained(graph.copy(), lgG_V.copy(), img_bl, pos_list, angleA, overlap)
    return graph_tagg


def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    create_output_dirs(pathsave)

    num_frames = len(img_o)
    img_padded = np.pad(img_o, ((0, 0), (1, 1), (1, 1)), 'constant')

    params = {'size': size, 'eps': eps, 'thresh_top': thresh_top, 'sigma': sigma, 'small': small}

    # Initialize lists to store results
    graph_results = [None] * num_frames
    graph_tagg = [None] * num_frames

    # Process each frame
    for idx in range(num_frames):
        print(f"Processing frame {idx + 1}/{num_frames}")
        result = process_graph(img_padded[idx], params)
        graph_results[idx] = result
        graph_tagg[idx] = run_graph_analysis(result['graph'], result['img_bl'], result['pos_list'], angleA, overlap)
        save_graph(graph_tagg[idx], result['pos_list'], img_padded[idx], os.path.join(pathsave, 'n_graphs'), idx)

        num_filaments = len(np.unique(np.asarray(list(graph_tagg[idx].edges(data='filament')))[:, 2]))
        print(f"Frame {idx} - Filaments defined: {num_filaments}")

    pickle.dump([res['pos_list'] for res in graph_results], open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))
    pickle.dump(graph_tagg, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))


def create_all_still(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, name_cell):
    create_output_dirs(pathsave)

    img_padded = np.pad(img_o, (1, 1), 'constant')
    params = {'size': size, 'eps': eps, 'thresh_top': thresh_top, 'sigma': sigma, 'small': small}

    result = process_graph(img_padded, params)
    graph_tagg = run_graph_analysis(result['graph'], result['img_bl'], result['pos_list'], angleA, overlap)
    save_graph(graph_tagg, result['pos_list'], img_padded, os.path.join(pathsave, 'n_graphs'), idx=0)

    num_filaments = len(np.unique(np.asarray(list(graph_tagg.edges(data='filament')))[:, 2]))
    print(f"Filaments defined: {num_filaments}")

    pickle.dump(result['pos_list'], open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))
    pickle.dump(graph_tagg, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))
    return


