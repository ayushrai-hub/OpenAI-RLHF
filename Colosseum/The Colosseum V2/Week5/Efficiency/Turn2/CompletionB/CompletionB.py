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
    """Ensure that specified output directories and their subdirectories exist."""
    subdirs = ['n_graphs', 'circ_stat', 'mov', 'plots']
    for subdir in subdirs:
        subdir_path = os.path.join(output_dir, subdir)
        os.makedirs(subdir_path, exist_ok=True)

def process_graph(image, params):
    """
    Process a single image to generate and return the graph and associated data.

    Parameters:
        image (numpy.ndarray): Input image to process.
        params (dict): Dictionary of processing parameters.

    Returns:
        dict: A dictionary containing the graph and related data.
    """
    graph, pos_list, img_skel, img_af, img_bl, im_f, mask, df_pos = utilsF.creategraph(
        image, size=params['size'], eps=params['eps'], thresh_top=params['thresh_top'],
        sigma=params['sigma'], small=params['small']
    )
    
    # Determine dangling edges, compute line graph, and perform constrained DFS
    graph_dangling = utilsF.dangling_edges(graph.copy())
    line_graph = nx.line_graph(graph.copy())
    lg_edge_values = utilsF.lG_edgeVal(line_graph.copy(), graph_dangling, pos_list)
    graph_tagged = utilsF.dfs_constrained(
        graph.copy(), lg_edge_values, img_bl, pos_list, params['angleA'], params['overlap']
    )
    
    # Count the number of defined filaments
    filament_edges = np.asarray(list(graph_tagged.edges(data='filament')))
    num_filaments = len(np.unique(filament_edges[:, 2])) if filament_edges.size else 0
    
    result = {
        "graph": graph_tagged,
        "positions": pos_list,
        "img_bl": img_bl,
        "num_filaments": num_filaments
    }
    
    return result

def save_graph(graph_data, img, output_dir, index):
    """
    Saves the processed graph and its visualization.

    Parameters:
        graph_data (dict): Processed graph data from `process_graph`.
        img (numpy.ndarray): Original image associated with the graph.
        output_dir (str): Directory where outputs will be saved.
        index (int): Frame index or identifier for naming files uniquely.
    """
    graph = graph_data['graph']
    positions = graph_data['positions']

    # Save the graph visualization
    plt.figure()
    utilsF.draw_graph_filament_nocolor(img, graph, positions, title=f"Graph {index}", label="filament")
    graph_image_path = os.path.join(output_dir, 'n_graphs', f'graph_{index}.png')
    plt.savefig(graph_image_path)
    plt.close()

    # Serialize the graph using pickle for further analysis or reuse
    graph_pickle_path = os.path.join(output_dir, 'n_graphs', f'graph_{index}.gpickle')
    with open(graph_pickle_path, 'wb') as pickle_file:
        pickle.dump(graph, pickle_file)

def aggregate_filament_info(all_graphs, output_dir):
    """
    Aggregates filament information over multiple frames and saves related plots.

    Parameters:
        all_graphs (list): List of processed graph dictionaries from `process_graph`.
        output_dir (str): Directory to save the aggregated data and plots.
    """
    filament_counts = [graph_data['num_filaments'] for graph_data in all_graphs]

    plt.figure(figsize=(10, 7))
    plt.scatter(range(len(filament_counts)), filament_counts, c='b')
    plt.xlabel('Frame')
    plt.ylabel('Number of Filaments')
    plt.title('Number of Filaments per Frame')
    plot_path = os.path.join(output_dir, 'plots', 'filaments_per_frame.png')
    plt.savefig(plot_path)
    plt.close()
    
    # Create and save a CSV report
    filament_report = pd.DataFrame({'Frame': range(len(filament_counts)), 'Filaments': filament_counts})
    report_path = os.path.join(output_dir, 'plots', 'filament_report.csv')
    filament_report.to_csv(report_path, index=False)

def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    """
    Process a sequence of images, generate graphs, and produce comprehensive analysis.

    Parameters:
        pathsave (str): Directory to save the outputs.
        img_o (numpy.ndarray): Sequence of input images.
        maskDraw (numpy.ndarray): Mask image for drawing operations.
        size, eps, thresh_top, sigma, small, angleA, overlap, max_cost: Processing parameters.
        name_cell (str): Identifier for the data set or source.
    """
    create_output_dirs(pathsave)

    params = {
        'size': size, 'eps': eps, 'thresh_top': thresh_top, 
        'sigma': sigma, 'small': small, 'angleA': angleA, 'overlap': overlap
    }

    all_graphs = []
    for idx, image in enumerate(img_o):
        print(f"Processing frame {idx + 1}/{len(img_o)}")
        padded_img = np.pad(image, ((1, 1), (1, 1)), 'constant')
        graph_data = process_graph(padded_img, params)
        save_graph(graph_data, padded_img, pathsave, idx)
        all_graphs.append(graph_data)

    aggregate_filament_info(all_graphs, pathsave)

def create_all_still(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, name_cell):
    """
    Process a single image (still) to generate a graph and associated analysis.

    Parameters are identical to `create_all`, but without max_cost since tracking isn't needed.
    """
    create_output_dirs(pathsave)

    params = {
        'size': size, 'eps': eps, 'thresh_top': thresh_top, 
        'sigma': sigma, 'small': small, 'angleA': angleA, 'overlap': overlap
    }

    padded_img = np.pad(img_o, ((1, 1), (1, 1)), 'constant')
    graph_data = process_graph(padded_img, params)
    save_graph(graph_data, padded_img, pathsave, 0)
    
    # For a single frame, aggregate filament info is still meaningful (in this context it'll be a single data point)
    aggregate_filament_info([graph_data], pathsave)
