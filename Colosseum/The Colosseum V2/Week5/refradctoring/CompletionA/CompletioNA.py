import numpy as np
import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd
import pickle
from graft import utilsF


def create_output_dirs(output_dir):
    """Ensure that the given output directory and its subdirectories exist."""
    for subdir_name in ('n_graphs', 'circ_stat', 'mov', 'plots'):
        subdir_path = os.path.join(output_dir, subdir_name)
        os.makedirs(subdir_path, exist_ok=True)


def process_graph(image, params):
    """
    Process a single image and return generated graph and related outputs.

    Parameters:
        image (numpy.ndarray): Input image to process.
        params (dict): Dictionary of processing parameters.

    Returns:
        tuple: Processed outputs including graph, positions, and various image stages.
    """
    graph, pos, img_skel, img_af, img_bl, im_F, mask, df_pos = utilsF.creategraph(
        image,
        size=params['size'],
        eps=params['eps'],
        thresh_top=params['thresh_top'],
        sigma=params['sigma'],
        small=params['small']
    )

    graph_dangling = utilsF.dangling_edges(graph.copy())
    line_graph = nx.line_graph(graph.copy())
    line_graph_val = utilsF.lG_edgeVal(line_graph.copy(), graph_dangling, pos)

    graph_tagged = utilsF.dfs_constrained(
        graph.copy(), 
        line_graph_val.copy(), 
        img_bl, 
        pos, 
        params['angleA'], 
        params['overlap']
    )

    return {
        "graph": graph,
        "graph_tagged": graph_tagged,
        "positions": pos,
        "skeleton": img_skel,
        "binary_image": img_bl,
        "image_filtered": im_F,
        "mask": mask,
        "df_positions": df_pos
    }


def save_graph(graph_data, output_path, file_prefix):
    """
    Save the processed graph data as plotted images.

    Parameters:
        graph_data (dict): Processed data including graph, positions, and images.
        output_path (str): Directory path to save the images.
        file_prefix (str): Prefix for the saved file names.
    """
    utilsF.draw_graph_filament_nocolor(
        graph_data["binary_image"],
        graph_data["graph_tagged"],
        graph_data["positions"],
        title=f"{file_prefix} - Filament",
        label='filament'
    )
    plt.savefig(os.path.join(output_path, f'{file_prefix}.png'))
    plt.close('all')


def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    """Process an image sequence and perform analyses."""
    create_output_dirs(pathsave)

    # Padding image series appropriately
    img_padded = np.pad(img_o, ((0, 0), (1, 1), (1, 1)), 'constant')

    params = {
        'size': size, 'eps': eps, 'thresh_top': thresh_top,
        'sigma': sigma, 'small': small,
        'angleA': angleA, 'overlap': overlap
    }

    processed_images = []
    for idx, img in enumerate(img_padded):
        graph_data = process_graph(img, params)
        save_graph(graph_data, os.path.join(pathsave, 'n_graphs'), f'graph_{idx}')
        processed_images.append(graph_data)

    pos_lists = [data["positions"] for data in processed_images]
    graphs_tagged = [data["graph_tagged"] for data in processed_images]

    pickle.dump(pos_lists, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))

    memKeep = len(graphs_tagged) if len(graphs_tagged) < 20 else utilsF.signMem(graphs_tagged[:20], pos_lists[:20])

    tag_new = [np.max(list(graphs_tagged[0].edges(data='filament')), axis=0)[2]]

    graph_tracked = [graphs_tagged[0]]

    filamentsNU = []
    for i in range(len(graphs_tagged) - 1):
        graph_next, _, tag_val, filamentsNU = utilsF.filament_tag(
            graph_tracked[i], graphs_tagged[i+1],
            pos_lists[i], pos_lists[i+1],
            tag_new[-1], max_cost, filamentsNU, memKeep
        )
        graph_tracked.append(graph_next)
        tag_new.append(tag_val)

    pickle.dump(graph_tracked, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))


def create_all_still(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, name_cell):
    """Process a single image."""
    create_output_dirs(pathsave)

    # Padding single image appropriately
    img_padded = np.pad(img_o, ((1, 1), (1, 1)), 'constant')

    params = {
        'size': size, 'eps': eps, 'thresh_top': thresh_top,
        'sigma': sigma, 'small': small,
        'angleA': angleA, 'overlap': overlap
    }

    graph_data = process_graph(img_padded, params)
    save_graph(graph_data, os.path.join(pathsave, 'n_graphs'), 'graph_still')

