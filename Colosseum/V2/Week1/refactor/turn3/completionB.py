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

def process_graph(img, size, eps, thresh_top, sigma, small):
    """
    Process a single image to generate a graph.
    
    Returns:
        - graph (networkx.Graph): Generated graph object.
        - pos_list (dict): Positions of nodes for visualization.
        - skel_image (np.array): Skeletonized image.
        - af_image (np.array): Image representing area fraction.
        - bl_image (np.array): Background-light image.
        - mask (np.array): Mask for image regions.
        - df_pos (DataFrame): DataFrame with node positions.
    """
    graph, pos_list, skel_image, af_image, bl_image, mask, df_pos = utilsF.creategraph(
        img, size=size, eps=eps, thresh_top=thresh_top,
        sigma=sigma, small=small
    )
    return graph, pos_list, skel_image, af_image, bl_image, mask, df_pos

def save_graph(graph, pos_list, output_dir, filename):
    """
    Save a graph as an image to the specified directory.
    Args:
        - graph (networkx.Graph): The graph to save.
        - pos_list (dict): Node positions for visualization.
        - output_dir (str): Directory to save the image.
        - filename (str): Name of the file to save.
    """
    utilsF.draw_graph_filament_nocolor(graph, pos_list, title='', label='filament')
    plt.savefig(os.path.join(output_dir, filename))
    plt.close('all')

def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    create_output_dirs(pathsave)
    img_padded = np.pad(img_o, ((0,0), (1,1), (1,1)), 'constant')
    
    graphs, pos_list = [], []
    skel_images, af_images, bl_images, masks, df_positions = [], [], [], [], []
    
    for img in img_padded:
        graph, pos, skel_img, af_img, bl_img, mask, df_pos = process_graph(img, size, eps, thresh_top, sigma, small)
        graphs.append(graph)
        pos_list.append(pos)
        skel_images.append(skel_img)
        af_images.append(af_img)
        bl_images.append(bl_img)
        masks.append(mask)
        df_positions.append(df_pos)
    
    for idx, graph in enumerate(graphs):
        save_graph(graph, pos_list[idx], os.path.join(pathsave, 'n_graphs'), f'graph{idx}.png')
    
    # Specific Processing Logic for further analysis and saving details
    process_additional_stats(graphs, pos_list, skel_images, af_images, bl_images, masks, df_positions, pathsave, angleA, overlap, max_cost)

def process_all_stills(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, name_cell):
    create_output_dirs(pathsave)
    img_padded = np.pad(img_o, (1,1), 'constant')
    
    graph, pos_list, skel_image, af_image, bl_image, mask, df_pos = process_graph(img_padded, size, eps, thresh_top, sigma, small)
    
    save_graph(graph, pos_list, os.path.join(pathsave, 'n_graphs'), 'graph.png')
    
    # Further processing related to still images
    process_additional_stats([graph], [pos_list], [skel_image], [af_image], [bl_image], [mask], [df_pos], pathsave, angleA, overlap, max_cost)

def process_additional_stats(graphs, pos_list, skel_images, af_images, bl_images, masks, df_positions, pathsave, angleA, overlap, max_cost):
    for graph, pos, skel_img, af_img, bl_img, mask, df_pos in zip(graphs, pos_list, skel_images, af_images, bl_images, masks, df_positions):
        # 1) Find dangling edges and mark them
        graphD = utilsF.dangling_edges(graph)

        # 2) Create line graph
        lgG = nx.line_graph(graph)

        # 3) Calculate the angles between two edges from the graph represented by edges in the line graph
        lgG_V = utilsF.lG_edgeVal(lgG, graphD, pos)

        # 4) Run depth-first search
        graphTagg = utilsF.dfs_constrained(graph, lgG_V, bl_img, pos, angleA, overlap)

        # Save and process additional analysis for each frame
        utilsF.draw_graph_filament_nocolor(skel_img, graphTagg, pos, '', 'filament')
        plt.savefig(os.path.join(pathsave, 'n_graphs', f'frame_{len(np.unique(np.asarray(list(graphTagg.edges(data="filament")))[:,2]))}.png'))
        plt.close('all')

        # Process tagged graph analysis here
        additional_tagging_logic(graphTagg, df_pos, pathsave)

def additional_tagging_logic(graph, df_pos, pathsave):
    # Additional logic specific to tagged graphs
    pass
