# graft/main.py
import numpy as np
import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd  
from collections import Counter
import pickle

from graft import utilsF

def create_output_dirs(output_dir):
    """
    Ensure the specified output directory and its subdirectories exist.

    Args:
        output_dir (str): Root directory for output.
    """
    subdirs = ('n_graphs', 'circ_stat', 'mov', 'plots')
    for subdir_name in subdirs:
        subdir_path = os.path.join(output_dir, subdir_name)
        os.makedirs(subdir_path, exist_ok=True)

def process_graph(img, params):
    """
    Process a single image to construct and tag graphs.

    Args:
        img (ndarray): Image array to process.
        params (dict): Dictionary of parameters for graph creation.

    Returns:
        dict: Contains graph, position list, and other metadata.
    """
    graph, pos_list, img_skel, img_af, img_bl, img_f, mask, df_pos = utilsF.creategraph(
        img,
        size=params['size'],
        eps=params['eps'],
        thresh_top=params['thresh_top'],
        sigma=params['sigma'],
        small=params['small']
    )
    return {
        "graph": graph,
        "pos_list": pos_list,
        "img_skel": img_skel,
        "img_af": img_af,
        "img_bl": img_bl,
        "img_f": img_f,
        "mask": mask,
        "df_pos": df_pos
    }

def save_graph(img, graph, pos_list, path, graph_name, title=""):
    """
    Draw and save a graph to the specified path.

    Args:
        img (ndarray): Image array to plot background.
        graph (networkx.Graph): Graph to draw.
        pos_list (dict): Position list for graph nodes.
        path (str): File path to save the image.
        graph_name (str): Filename of the saved graph.
        title (str, optional): Title of the plot. Defaults to "".
    """
    utilsF.draw_graph_filament_nocolor(img, graph, pos_list, title, label='filament')
    full_path = os.path.join(path, graph_name)
    plt.savefig(full_path)
    plt.close('all')

def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top,
               sigma, small, angleA, overlap, max_cost, name_cell):
    """
    Create and process graphs from a series of image frames.

    Args:
        pathsave (str): Path to save output files.
        img_o (ndarray): Input image series (M, N, P).
        maskDraw (ndarray): Drawing mask.
        size, eps, thresh_top, sigma, small (float): Graph parameters.
        angleA, overlap, max_cost (float): Graph operation parameters.
        name_cell (str): Cell name identifier.
    """
    create_output_dirs(pathsave)

    # Padding images
    M, N, P = img_o.shape  
    img_padded = np.pad(img_o, ((0, 0), (1, 1), (1, 1)), 'constant')

    # Parameters for graph creation
    params = {
        'size': size,
        'eps': eps,
        'thresh_top': thresh_top,
        'sigma': sigma,
        'small': small  
    }

    graphs_data = []
    for q, img in enumerate(img_padded):
        print(f"Processing frame {q}")
        graph_data = process_graph(img, params)
        graphs_data.append(graph_data)

        # Save the intermediate graph
        graph_save_path = os.path.join(pathsave, 'n_graphs')
        save_graph(img, graph_data['graph'], graph_data['pos_list'],
                   graph_save_path, f'graph{q}.png', title=f"Graph {q}")

    # Filament tagging and tracking (fully implemented)
    graph_sequences = [data['graph'] for data in graphs_data]
    pos_lists = [data['pos_list'] for data in graphs_data]

    mem_keep = utilsF.signMem(graph_sequences[:min(20, len(graph_sequences))], 
                              pos_lists[:min(20, len(pos_lists))])
    tag_new = 0
    filament_tracker = []

    for i in range(len(graph_sequences) - 1):
        graph_sequences[i + 1], _, tag_new, filament_tracker = utilsF.filament_tag(
            graph_sequences[i],
            graph_sequences[i + 1],
            pos_lists[i],
            pos_lists[i + 1],
            tag_new,
            max_cost,
            filament_tracker,
            mem_keep
        )

    # Save tracking results
    tracking_path = os.path.join(pathsave, 'mov')
    for i, graph in enumerate(graph_sequences):
        save_graph(img_padded[i], graph, pos_lists[i],
                   tracking_path, f'trackgraph{i + 1}.png', f"Tracked Graph {i + 1}")

    # Analyze filaments
    pd_fil_info = utilsF.filament_info_time(img_padded, graph_sequences, pos_lists,
                                           pathsave, [data['img_f'] for data in graphs_data],
                                           maskDraw)

def create_all_still(pathsave, img_o, maskDraw, size, eps, thresh_top,
                     sigma, small, angleA, overlap, name_cell):
    """
    Create and process graph from a single image frame (still image).

    Args:
        pathsave (str): Path to save output files.
        img_o (ndarray): Input image (2D).
    """
    create_output_dirs(pathsave)

    # Padding single image
    img_padded = np.pad(img_o, ((1, 1), (1, 1)), 'constant')

    # Parameters for graph creation
    params = {
        'size': size,
        'eps': eps,
        'thresh_top': thresh_top,
        'sigma': sigma,
        'small': small  
    }

    print("Processing still image")
    graph_data = process_graph(img_padded, params)

    # Save graph
    graph_save_path = os.path.join(pathsave, 'n_graphs')
    save_graph(img_padded, graph_data['graph'], graph_data['pos_list'],
               graph_save_path, 'graph_still.png', title="Still Graph")

