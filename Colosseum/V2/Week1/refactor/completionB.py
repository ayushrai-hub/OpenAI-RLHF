# graft/main.py

import numpy as np
import os
import networkx as nx
import pandas as pd
import pickle
import matplotlib.pyplot as plt

from graft import utilsF

def create_output_dirs(output_dir):
    """Ensure that the given output directory incl. subdirectories exists."""
    for subdir_name in ('n_graphs', 'circ_stat', 'mov', 'plots'):
        subdir_path = os.path.join(output_dir, subdir_name)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)

def process_graph(img, params):
    """
    Processes a single image to generate a graph and related components.
    Returns graph, position list, skeleton image, additional images, and mask.
    """
    graph, pos_list, img_skel, img_af, img_bl, mask, df_pos = utilsF.creategraph(
        img, size=params['size'], eps=params['eps'], thresh_top=params['thresh_top'],
        sigma=params['sigma'], small=params['small']
    )
    return graph, pos_list, img_skel, img_af, img_bl, mask, df_pos

def save_graph(graph, pos_list, output_dir, index=0, title=''):
    """
    Saves a single graph based on position list and title for future visualization.
    """
    utilsF.draw_graph_filament_nocolor(graph, pos_list, title=title, label='filament')
    plt.savefig(os.path.join(output_dir, f'graph{index}.png'))
    plt.close('all')

def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    create_output_dirs(pathsave)
    img_padded = np.pad(img_o, ((0, 0), (1, 1), (1, 1)), 'constant')
    params = {
        'size': size, 'eps': eps, 'thresh_top': thresh_top, 'sigma': sigma, 'small': small
    }
    
    for idx, img in enumerate(img_padded):
        graph, pos_list, img_skel, img_af, img_bl, mask, df_pos = process_graph(img, params)
        save_graph(graph, pos_list, os.path.join(pathsave, 'n_graphs'), idx, title=f"Graph {idx}")
    
    # Additional tagged graph processing as per original code
    process_tagged_graphs(pathsave, img_o, maskDraw, params, angleA, overlap, max_cost)

def create_all_still(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, name_cell):
    create_output_dirs(pathsave)
    img_padded = np.pad(img_o, (1, 1), 'constant')
    params = {
        'size': size, 'eps': eps, 'thresh_top': thresh_top, 'sigma': sigma, 'small': small
    }
    
    graph, pos_list, img_skel, img_af, img_bl, mask, df_pos = process_graph(img_padded, params)
    save_graph(graph, pos_list, os.path.join(pathsave, 'n_graphs'), title="Graph")
    
    # Additional tagged graph processing as per original code
    process_tagged_graphs(pathsave, [img_o], maskDraw, params, angleA, overlap)

def process_tagged_graphs(pathsave, img_o, maskDraw, params, angleA, overlap, max_cost=None):
    M, N, P = img_o.shape
    graphs = []
    pos_lists = []
    for idx in range(len(img_o)):
        graph, pos_list, img_skel, img_af, img_bl, mask, df_pos = process_graph(img_o[idx], params)
        graphs.append(graph)
        pos_lists.append(pos_list)
    
    # Process linear graph and DFS on all images
    g_tagged = [0] * len(img_o)
    g_tagged[0] = utilsF.dfs_constrained(graphs[0], pos_lists[0], img_bl, pos_lists[0], angleA, overlap)

    cost = [0] * (len(img_o) - 1)
    tag_new = [np.max(list(g_tagged[0].edges(data='filament')), axis=0)[2]] + [0] * (len(img_o) - 1)
    
    for i in range(len(img_o) - 1):
        g_tagged[i + 1], cost[i], tag_new[i + 1], _ = utilsF.filament_tag(
            g_tagged[i], graphs[i + 1], pos_lists[i], pos_lists[i + 1], tag_new[i], max_cost, [], 20
        )

    pickle.dump(g_tagged, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))

    # Visualization of processed tagged graphs
    for i, tagged_graph in enumerate(g_tagged):
        utilsF.draw_graph_filament_track_nocolor(
            img_o[i], tagged_graph, pos_lists[i], f"Graph {i + 1}", max(tag_new), padv=50
        )
        plt.savefig(os.path.join(pathsave, "mov", f"trackgraph{i+1}.png"))
        plt.close('all')

    analyze_filaments(pathsave, pos_lists, g_tagged)

def analyze_filaments(pathsave, pos_list, tagged_graphs):
    densities, lengths, intensities = [], [], []
    for idx, tagged_graph in enumerate(tagged_graphs):
        densities.append(utilsF.filament_density(tagged_graph))
        lengths.append(np.median(utilsF.filament_lengths(tagged_graph)))
        intensities.append(np.median(utilsF.filament_intensity(tagged_graph)))

    df_angles2 = pd.DataFrame({
        'angles': list(utilsF.mean_angle(tagged_graphs)),
        'var': list(utilsF.circular_variance(tagged_graphs)),
        'frame density': densities,
        'filament median length': lengths,
        'fl/len per length': intensities,
        'name': ''
    })
    
    df_angles2.to_csv(os.path.join(pathsave, 'value_per_frame.csv'), index=False)

