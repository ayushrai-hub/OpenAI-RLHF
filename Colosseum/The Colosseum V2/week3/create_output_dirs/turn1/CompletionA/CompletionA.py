# graft/main.py

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
        os.makedirs(subdir_path, exist_ok=True)


def pad_images(img_o):
    """
    Pads the images appropriately.

    Args:
        img_o (numpy.ndarray): Original images.

    Returns:
        numpy.ndarray: Padded images.
    """
    if img_o.ndim == 3:  # Time-series image
        M, N, P = img_o.shape
        imgP = np.zeros((M, N + 2, P + 2))
        for m in range(len(img_o)):
            imgP[m] = np.pad(img_o[m], 1, 'constant')
    elif img_o.ndim == 2:  # Still image
        N, P = img_o.shape
        imgP = np.pad(img_o, 1, 'constant')
    else:
        raise ValueError("Unsupported image shape.")

    return imgP


def process_image(img, params):
    """
    Processes a single image to create a graph.

    Args:
        img (numpy.ndarray): Padded image.
        params (dict): Parameters required for processing.

    Returns:
        tuple: graph, positions, skeleton image, altered feature image, blurred image, filtered image, mask, position DataFrame
    """
    graph_s, posL, imgSkel, imgAF, imgBl, imF, mask, df_pos = utilsF.creategraph(
        img,
        size=params['size'],
        eps=params['eps'],
        thresh_top=params['thresh_top'],
        sigma=params['sigma'],
        small=params['small']
    )
    return graph_s, posL, imgSkel, imgAF, imgBl, imF, mask, df_pos


def process_graph(graph_s, imgBl, posL, params):
    """
    Processes a graph: finds dangling edges, creates line graph, calculates angles, tags graph.

    Args:
        graph_s (networkx.Graph): The initial graph.
        imgBl (numpy.ndarray): Blurred image.
        posL (dict): Positions of nodes.
        params (dict): Parameters required for processing.

    Returns:
        networkx.Graph: Tagged graph.
    """
    # 1) find all dangling edges and mark them
    graphD = utilsF.dangling_edges(graph_s.copy())
    # 2) create line graph
    lgG = nx.line_graph(graph_s.copy())
    # 3) calculate the angles between two edges from the graph that is now represented by edges in the line graph
    lgG_V = utilsF.lG_edgeVal(lgG.copy(), graphD, posL)
    # 4) run depth first search
    graphTagg = utilsF.dfs_constrained(
        graph_s.copy(),
        lgG_V.copy(),
        imgBl,
        posL,
        params['angleA'],
        params['overlap']
    )
    return graphTagg


def save_graph(imgP, graphTagg, posL, output_path, idx=None):
    """
    Saves the graph visualization.

    Args:
        imgP (numpy.ndarray): Padded image.
        graphTagg (networkx.Graph): Tagged graph.
        posL (dict): Positions of nodes.
        output_path (str): Path to save the image.
        idx (int, optional): Index of the graph.
    """
    utilsF.draw_graph_filament_nocolor(imgP, graphTagg, posL, "", 'filament')
    if idx is not None:
        filename = f'graph{idx}.png'
    else:
        filename = 'graph.png'
    plt.savefig(os.path.join(output_path, filename))
    plt.close('all')


def tag_graphs(graphTagg_list, posL_list, max_cost, memKeep):
    """
    Tags the graphs across frames for tracking filaments.

    Args:
        graphTagg_list (list): List of graphs to tag.
        posL_list (list): List of positions corresponding to graphs.
        max_cost (float): Maximum cost for tracking.
        memKeep (int): Memory frames to keep for tracking.

    Returns:
        tuple: Tagged graphs list and tag numbers.
    """
    # Initialize
    g_tagged = [None] * len(graphTagg_list)
    g_tagged[0] = graphTagg_list[0]
    tag_new = [0] * len(graphTagg_list)

    # First graph needs unique tags
    for node1, node2, property in g_tagged[0].edges(data=True):
        for n in range(len(g_tagged[0][node1][node2])):
            g_tagged[0][node1][node2][n]['tags'] = property['filament']

    max_tag = np.max(np.asarray(list(g_tagged[0].edges(data='filament')))[:, 2])

    filamentsNU = []
    cost = [0] * (len(graphTagg_list) - 1)

    for i in range(len(graphTagg_list) - 1):
        g_tagged[i + 1], cost[i], tag_new[i + 1], filamentsNU = utilsF.filament_tag(
            g_tagged[i],
            graphTagg_list[i + 1],
            posL_list[i],
            posL_list[i + 1],
            tag_new[i],
            max_cost,
            filamentsNU,
            memKeep
        )

    return g_tagged, tag_new


def perform_data_analysis(imgP, g_tagged_list, posL_list, pathsave, imF_list, maskDraw, name_cell):
    """
    Performs data analysis on the tagged graphs.

    Args:
        imgP (list or numpy.ndarray): List of padded images.
        g_tagged_list (list): List of tagged graphs.
        posL_list (list): List of positions corresponding to graphs.
        pathsave (str): Output directory path.
        imF_list (list): List of filtered images.
        maskDraw (numpy.ndarray): Mask to draw.
        name_cell (str): Name of the cell.
    """
    plt.rc('xtick', labelsize=24)
    plt.rc('ytick', labelsize=24)

    unique_filaments = [0] * len(imgP)
    unique_frames = []

    for i in range(len(imgP)):
        unique_tags = np.unique(np.asarray(list(g_tagged_list[i].edges(data='tags')))[:, 2])
        unique_filaments[i] = len(unique_tags)
        unique_frames.extend(list(unique_tags))

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(0, len(unique_filaments)), unique_filaments)
    plt.xlabel('frames', size=24)
    plt.ylabel('# filaments', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filaments_per_frame.png'))

    # Data analysis per frame
    pd_fil_info = utilsF.filament_info_time(imgP, g_tagged_list, posL_list, pathsave, imF_list, maskDraw)

    vals = Counter(pd_fil_info['filament']).values()

    counts, bins = np.histogram(list(vals), 20)
    plt.figure(figsize=(10, 7))
    plt.hist(bins[:-1], bins, weights=counts, color='green')
    plt.xlabel('frames', size=24)
    plt.ylabel('filaments survival', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments.png'))

    counts, bins = np.histogram(list(vals), 20, density='True')
    plt.figure(figsize=(10, 7))
    plt.hist(bins[:-1], bins, weights=counts, color='green')
    plt.xlabel('frames', size=24)
    plt.ylabel('filaments survival', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments_normalized.png'))

    dens = np.zeros(len(imgP))
    fil_len = np.zeros(len(imgP))
    fil_I = np.zeros(len(imgP))
    for i in range(len(imgP)):
        dens[i] = pd_fil_info[pd_fil_info['frame number'] == i]['filament density'].values[0]
        fil_len[i] = np.median(pd_fil_info[pd_fil_info['frame number'] == i]['filament length'])
        fil_I[i] = np.median(pd_fil_info[pd_fil_info['frame number'] == i]['filament intensity per length'])

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(0, len(imgP)), dens)
    plt.xlabel('frames', size=24)
    plt.ylabel('filament density', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filament_density.png'))

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(0, len(imgP)), fil_len)
    plt.xlabel('frames', size=24)
    plt.ylabel('filament median length', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filamentlength.png'))

    mean_angle, var_val = utilsF.circ_stat_plot(pathsave, pd_fil_info)

    line_mean = np.mean(mean_angle)

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(0, len(mean_angle)), mean_angle)
    plt.plot(np.arange(0, len(mean_angle)), np.ones(len(mean_angle)) * line_mean, color='black', linestyle='dashed')
    plt.xlabel('Frames', size=24)
    plt.ylabel('Circular mean angle', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_mean.png'))

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(0, len(var_val)), var_val)
    plt.xlabel('frames', size=24)
    plt.ylabel('circular variance of angles', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_var.png'))

    tagsU = pd_fil_info['filament'].unique()
    vals = np.zeros(len(tagsU))
    lives = np.zeros(len(tagsU))
    plt.figure(figsize=(10, 10))
    for s, m in zip(tagsU, range(len(tagsU))):
        fil = pd_fil_info[pd_fil_info['filament'] == s]['filament length'].values
        vals[m] = np.median(fil)
        lives[m] = len(fil)
        plt.plot(np.arange(0, len(fil)), fil)
    plt.xlabel('Survival frames', size=24)
    plt.ylabel('filament length', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_len.png'))

    # Mean/median value per frame
    df_angles2 = pd.DataFrame()
    df_angles2['angles'] = mean_angle
    df_angles2['var'] = var_val
    df_angles2['frame density'] = dens
    df_angles2['filament median length'] = fil_len
    df_angles2['filament median intensity per length'] = fil_I
    df_angles2['name'] = name_cell

    df_angles2.to_csv(os.path.join(pathsave, 'value_per_frame.csv'), index=False)


def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    create_output_dirs(pathsave)

    # Pad images
    imgP = pad_images(img_o)

    # Set parameters
    params = {
        'size': size,
        'eps': eps,
        'thresh_top': thresh_top,
        'sigma': sigma,
        'small': small,
        'angleA': angleA,
        'overlap': overlap
    }

    # Lists to hold data
    graphs_s = []
    posL_list = []
    imgSkel_list = []
    imgAF_list = []
    imgBl_list = []
    imF_list = []
    mask_list = []
    df_pos_list = []
    graphTagg_list = []
    no_filaments = []

    # Process each image
    for idx, img in enumerate(imgP):
        print(f"Processing frame {idx}")
        # Process image to create initial graph
        graph_s, posL, imgSkel, imgAF, imgBl, imF, mask, df_pos = process_image(img, params)
        graphs_s.append(graph_s)
        posL_list.append(posL)
        imgSkel_list.append(imgSkel)
        imgAF_list.append(imgAF)
        imgBl_list.append(imgBl)
        imF_list.append(imF)
        mask_list.append(mask)
        df_pos_list.append(df_pos)

        # Process graph
        graphTagg = process_graph(graph_s, imgBl, posL, params)
        graphTagg_list.append(graphTagg)

        # Save graph
        save_graph(img, graphTagg, posL, os.path.join(pathsave, 'n_graphs'), idx)

        # Count filaments
        num_filaments = len(np.unique(np.asarray(list(graphTagg.edges(data='filament')))[:, 2]))
        no_filaments.append(num_filaments)
        print(f"Filaments defined: {num_filaments}")

    # Save posL using pickle
    pickle.dump(posL_list, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))

    # Filament tracking across frames

    # If less than 20 frames, keep all in memory
    memKeep = len(img_o) if len(img_o) < 20 else 20

    # Filament tagging across frames
    g_tagged_list, tag_new = tag_graphs(graphTagg_list, posL_list, max_cost, memKeep)

    # Save tagged graphs
    pickle.dump(g_tagged_list, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))

    # Save tracked graphs as images
    for idx, (g_tagged, img) in enumerate(zip(g_tagged_list, imgP)):
        title = f"graph {idx + 1}"
        utilsF.draw_graph_filament_track_nocolor(img, g_tagged, posL_list[idx], title, max(tag_new), padv=50)
        plt.savefig(os.path.join(pathsave, 'mov', f"trackgraph{idx + 1}.png"))
        plt.close('all')

    # Data analysis
    perform_data_analysis(imgP, g_tagged_list, posL_list, pathsave, imF_list, maskDraw, name_cell)


def create_all_still(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, name_cell):
    create_output_dirs(pathsave)

    # Pad image
    imgP = pad_images(img_o)

    # Set parameters
    params = {
        'size': size,
        'eps': eps,
        'thresh_top': thresh_top,
        'sigma': sigma,
        'small': small,
        'angleA': angleA,
        'overlap': overlap
    }

    # Process image
    graph_s, posL, imgSkel, imgAF, imgBl, imF, mask, df_pos = process_image(imgP, params)

    # Process graph
    graphTagg = process_graph(graph_s, imgBl, posL, params)

    # Save graph
    save_graph(imgP, graphTagg, posL, os.path.join(pathsave, 'n_graphs'))

    print('Filaments defined: ', len(np.unique(np.asarray(list(graphTagg.edges(data='filament')))[:, 2])))

    # Data analysis
    pd_fil_info = utilsF.filament_info(imgP, graphTagg, posL, pathsave, imF, maskDraw)

    mean_len = np.mean(pd_fil_info['filament length'])

    list_len = np.sort(pd_fil_info['filament length'])
    plt.figure()
    plt.scatter(np.arange(0, len(list_len)), list_len)
    plt.xlabel('Filaments', size=24)
    plt.ylabel('Length', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filament_lengths.png'))
    plt.close()

    mean_angle, var_val = utilsF.circ_stat(pd_fil_info, pathsave)

    print('Mean angle: ', mean_angle, 'Circular variance: ', var_val, 'Mean length: ', mean_len)

    # Save summary to a CSV file
    df_summary = pd.DataFrame({
        'mean_angle': [mean_angle],
        'circular_variance': [var_val],
        'mean_length': [mean_len],
        'name': [name_cell]
    })
    df_summary.to_csv(os.path.join(pathsave, 'summary.csv'), index=False)

