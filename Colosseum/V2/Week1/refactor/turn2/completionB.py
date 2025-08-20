# graft/main.py

import numpy as np
import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd
import pickle
from collections import Counter
from graft import utilsF

def create_output_dirs(output_dir):
    """Ensure that the given output directory and its subdirectories exist."""
    for subdir_name in ('n_graphs', 'circ_stat', 'mov', 'plots'):
        subdir_path = os.path.join(output_dir, subdir_name)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)

def process_graph(image, params):
    """
    Process a single image and create its corresponding graph and associated structures.
    """
    img_padded = np.pad(image, ((1, 1), (1, 1)), 'constant')
    graph, pos_list, skel_image, af_image, bl_image, mask, df_pos = utilsF.creategraph(
        img_padded,
        size=params['size'],
        eps=params['eps'],
        thresh_top=params['thresh_top'],
        sigma=params['sigma'],
        small=params['small']
    )
    return graph, pos_list, skel_image, af_image, bl_image, mask, df_pos

def save_graph(graph, pos_list, output_dir, filename):
    """
    Save the graph as an image file.
    """
    utilsF.draw_graph_filament_nocolor(graph, pos_list, title='', label='filament')
    plt.savefig(os.path.join(output_dir, filename))
    plt.close('all')

def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    create_output_dirs(pathsave)
    params = {
        'size': size,
        'eps': eps,
        'thresh_top': thresh_top,
        'sigma': sigma,
        'small': small
    }
    
    for idx, img in enumerate(img_o):
        graph, pos_list, _, _, _, _, _ = process_graph(img, params)
        save_graph(graph, pos_list, os.path.join(pathsave, 'n_graphs'), f'graph{idx}.png')

        # Additional processing for tagged graphs
        graph_dangles = utilsF.dangling_edges(graph.copy())
        line_graph = nx.line_graph(graph.copy())
        lgG_V = utilsF.lG_edgeVal(line_graph.copy(), graph_dangles, pos_list)
        graph_tagged = utilsF.dfs_constrained(graph.copy(), lgG_V.copy(), None, pos_list, angleA, overlap)
        
        # Save various visualizations and data
        save_graph(graph_tagged, pos_list, os.path.join(pathsave, 'n_graphs'), f'tagged_graph{idx}.png')
        
        pickle.dump(pos_list, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))

    # Further processing and analysis as required for additional tests and plots
    analyze_data(img_o, pathsave, maskDraw, pos_list, graph_tagged)

def create_all_still(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, name_cell):
    create_output_dirs(pathsave)
    params = {
        'size': size,
        'eps': eps,
        'thresh_top': thresh_top,
        'sigma': sigma,
        'small': small
    }
    
    graph, pos_list, skel_image, af_image, bl_image, mask, df_pos = process_graph(np.expand_dims(img_o, axis=0), params)
    save_graph(graph, pos_list, os.path.join(pathsave, 'n_graphs'), 'graph.png')

    # Further processing and analysis specific to still images
    analyzed_pd_fil_info = utilsF.filament_info(np.expand_dims(img_o, axis=0), graph, pos_list, pathsave, af_image, maskDraw)

def analyze_data(img_o, pathsave, maskDraw, pos_list, graph_tagged):
    # Analysis of data over multiple frames
    pd_fil_info = utilsF.filament_info_time(img_o, graph_tagged, pos_list, pathsave, None, maskDraw)
    
    pd_fil_info.to_csv(os.path.join(pathsave, 'tracked_filaments_info.csv'), index=False)
    
    unique_filaments = [len(np.unique([data[2] for data in graph.edges(data='tags')])) for graph in graph_tagged]
    
    plt.figure()
    plt.scatter(range(len(unique_filaments)), unique_filaments)
    plt.xlabel('Frames')
    plt.ylabel('Number of Filaments')
    plt.savefig(os.path.join(pathsave, 'plots', 'filaments_per_frame.png'))
    
    # Further analysis code as per requirements
    
