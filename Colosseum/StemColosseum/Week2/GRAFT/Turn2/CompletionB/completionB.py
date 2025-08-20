# graft/main.py

import numpy as np
import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd
import pickle

from graft import utilsF


# Utility Functions

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


# Modularized specific steps

def process_graph(image, size, eps, thresh_top, sigma, small):
    """Create and process a graph based on the input image."""
    graph, pos_list, img_skel, img_af, img_bl, img_f, mask, df_pos = utilsF.creategraph(
        image, size=size, eps=eps, thresh_top=thresh_top, sigma=sigma, small=small
    )
    return graph, pos_list, img_skel, img_af, img_bl, img_f, mask, df_pos


def tag_and_save_graph(graph, pos_list, image_pad, angleA, overlap, pathsave, graph_index):
    """Tags graph filaments, visualizes and saves the graph image."""
    # 1. Find dangling edges
    graph_d = utilsF.dangling_edges(graph.copy())

    # 2. Create line graph
    lg_graph = nx.line_graph(graph.copy())

    # 3. Calculate the angles between edges
    lg_graph_values = utilsF.lG_edgeVal(lg_graph.copy(), graph_d, pos_list)

    # 4. Depth-first search to tag filaments
    graph_tagg = utilsF.dfs_constrained(graph.copy(), lg_graph_values.copy(), image_pad, pos_list, angleA, overlap)

    # Save the visualized graph
    utilsF.draw_graph_filament_nocolor(image_pad, graph_tagg, pos_list, '', 'filament')
    plt.savefig(os.path.join(pathsave, 'n_graphs', f'graph{graph_index}.png'))
    plt.close('all')

    return graph_tagg


def save_tagged_graph_to_file(g_tagged, pathsave):
    """Save tagged graphs to a file."""
    with open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb') as f:
        pickle.dump(g_tagged, f)


def save_analysis_plots(unique_filaments, pathsave):
    """Generate and save plots based on the unique filament data."""
    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(0, len(unique_filaments)), unique_filaments)
    plt.xlabel('frames', size=24)
    plt.ylabel('# filaments', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filaments_per_frame.png'))
    plt.close('all')


# Main Processing Logic for Time-Series

def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    """Create and process graphs for time-series (multi-frame) data."""
    create_output_dirs(pathsave)

    img_padded = np.pad(img_o, ((0, 0), (1, 1), (1, 1)), 'constant')
    num_frames = len(img_o)
    g_tagged = [None] * num_frames
    pos_list_collection = [None] * num_frames

    for frame_idx in range(num_frames):
        print(f"Processing frame {frame_idx + 1} of {num_frames}")
        
        # Process the frame graph
        graph, pos_list, _, _, img_bl, _, _, _ = process_graph(
            img_padded[frame_idx], size=size, eps=eps, thresh_top=thresh_top, sigma=sigma, small=small
        )
        pos_list_collection[frame_idx] = pos_list

        # Tag and save the graph
        g_tagged[frame_idx] = tag_and_save_graph(graph, pos_list, img_bl, angleA, overlap, pathsave, frame_idx)

    save_tagged_graph_to_file(g_tagged, pathsave)

    # Data analysis and plotting of filaments per frame
    unique_filaments_per_frame = [
        len(np.unique(np.asarray(list(g.edges(data='filament')))[:, 2]))
        for g in g_tagged
    ]
    save_analysis_plots(unique_filaments_per_frame, pathsave)

    # Calculate and save filament tracking data
    pd_fil_info = utilsF.filament_info_time(img_padded, g_tagged, pos_list_collection, pathsave, maskDraw)
    pd_fil_info.to_csv(os.path.join(pathsave, 'tracked_filaments_info.csv'))


# Main Processing Logic for Still Images (Single Frame)

def create_all_still(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, name_cell):
    """Create and process graph for a single (still) image."""
    create_output_dirs(pathsave)

    img_padded = np.pad(img_o, 1, 'constant')

    # Process graph for the still image
    graph, pos_list, _, _, img_bl, _, _, _ = process_graph(
        img_padded, size=size, eps=eps, thresh_top=thresh_top, sigma=sigma, small=small
    )

    # Tag and save the graph
    graph_tagg = tag_and_save_graph(graph, pos_list, img_bl, angleA, overlap, pathsave, 0)

    # Data analysis and plotting for single frame
    pd_fil_info = utilsF.filament_info(img_padded, graph_tagg, pos_list, pathsave, maskDraw)
    pd_fil_info.to_csv(os.path.join(pathsave, 'traced_filaments_info.csv'))

    # Additional statistics generation for the single frame
    save_analysis_plots([len(np.unique(np.asarray(list(graph_tagg.edges(data='filament')))[:, 2]))], pathsave)


