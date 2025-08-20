#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pickle
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

from graft import utilsF

def create_output_dirs(output_dir: str):
    """Ensure that the given output directory including subdirectories exists."""
    for subdir_name in ('n_graphs', 'circ_stat', 'mov', 'plots'):
        subdir_path = os.path.join(output_dir, subdir_name)
        os.makedirs(subdir_path, exist_ok=True)

def process_graph(
    img: np.ndarray, 
    size: int, eps: int, thresh_top: float, sigma: float, small: float, 
    angleA: float, overlap: int
):
    """
    Process a single image to:
      0) create the initial graph and other relevant images
      1) find dangling edges
      2) create line graph
      3) calculate angles between edges
      4) run DFS to tag filaments

    Returns:
        A dictionary with processed results, including:
        - graphTagg: Tagged graph with filaments
        - posL: Positions of nodes
        - mask: Binary mask used
        - imgBl: Processed image
        - filaments_count: Number of unique filaments
    """
    # Step 0: Create initial graph and related structures
    graph_s, posL, imgSkel, imgAF, imgBl, imF, mask, df_pos = utilsF.creategraph(
        img, size=size, eps=eps, thresh_top=thresh_top, sigma=sigma, small=small
    )
    utilsF.draw_graph(imgSkel, graph_s, posL, "untagged graph")

    # Step 1: Find dangling edges
    graphD = utilsF.dangling_edges(graph_s.copy())

    # Step 2: Create line graph
    lgG = nx.line_graph(graph_s.copy())

    # Step 3: Calculate angles between edges
    lgG_V = utilsF.lG_edgeVal(lgG.copy(), graphD, posL)

    # Step 4: Run DFS to tag filaments
    graphTagg = utilsF.dfs_constrained(graph_s.copy(), lgG_V.copy(), imgBl, posL, angleA, overlap)

    # Count unique filaments
    filaments_count = len(np.unique(np.asarray(list(graphTagg.edges(data='filament')))[:,2]))

    return {
        'graphTagg': graphTagg,
        'posL': posL,
        'mask': mask,
        'imgBl': imgBl,
        'imF': imF,
        'df_pos': df_pos,
        'filaments_count': filaments_count
    }

def save_graph(img: np.ndarray, graphTagg: nx.Graph, posL: np.ndarray, path: str, filename: str):
    """Draw and save the graph to a PNG file."""
    utilsF.draw_graph_filament_nocolor(img, graphTagg, posL, "", 'filament')
    plt.savefig(os.path.join(path, filename))
    plt.close('all')

def track_filaments_through_frames(graphTagg_list, posL_list, max_cost: int):
    """
    Assign and track filament tags through frames in a time series.
    Updates and returns graphs with consistent filament IDs across frames.
    """
    # Initialize tags on first frame
    g_tagged = [0]*len(graphTagg_list)
    g_tagged[0] = graphTagg_list[0].copy()
    max_tag = np.max(list(g_tagged[0].edges(data='filament')), axis=0)[2]
    tag_new = [0]*len(graphTagg_list)
    tag_new[0] = max_tag
    filamentsNU = []
    cost = [0]*(len(graphTagg_list)-1)

    for i in range(len(graphTagg_list)-1):
        g_tagged[i+1], cost[i], tag_new[i+1], filamentsNU = utilsF.filament_tag(
            g_tagged[i], graphTagg_list[i+1], posL_list[i], posL_list[i+1],
            tag_new[i], max_cost, filamentsNU, memKeep=len(graphTagg_list)
        )

    return g_tagged, tag_new

def analyze_time_series(pathsave: str, img_o: np.ndarray, g_tagged_list, posL_list, imF_list, maskDraw, name_cell: str):
    """
    Perform data analysis on tracked filaments across all frames and generate plots and CSV outputs.
    """
    # Extract and save filament info over time
    pd_fil_info = utilsF.filament_info_time(img_o, g_tagged_list, posL_list, pathsave, imF_list, maskDraw)
    pd_fil_info = pd.read_csv(os.path.join(pathsave, 'tracked_filaments_info.csv'))

    # Survival analysis
    vals = Counter(pd_fil_info['filament']).values()
    counts, bins = np.histogram(list(vals), 20)
    plt.figure(figsize=(10,7))
    plt.hist(bins[:-1], bins, weights=counts, color='green')
    plt.xlabel('frames', size=24)
    plt.ylabel('filaments survival', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments.png'))
    plt.close('all')

    counts, bins = np.histogram(list(vals), 20, density=True)
    plt.figure(figsize=(10,7))
    plt.hist(bins[:-1], bins, weights=counts, color='green')
    plt.xlabel('frames', size=24)
    plt.ylabel('filaments survival (normalized)', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments_normalized.png'))
    plt.close('all')

    # Calculate and plot density, length, intensity
    dens = np.zeros(len(img_o))
    fil_len = np.zeros(len(img_o))
    fil_I = np.zeros(len(img_o))
    for i in range(len(img_o)):
        dens[i] = pd_fil_info[pd_fil_info['frame number']==i]['filament density'].values[0]
        fil_len[i] = np.median(pd_fil_info[pd_fil_info['frame number']==i]['filament length'])
        fil_I[i] = np.median(pd_fil_info[pd_fil_info['frame number']==i]['filament intensity per length'])

    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,len(img_o)), dens)
    plt.xlabel('frames', size=24)
    plt.ylabel('filament density', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filament_density.png'))
    plt.close('all')

    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,len(img_o)), fil_len)
    plt.xlabel('frames', size=24)
    plt.ylabel('filament median length', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filamentlength.png'))
    plt.close('all')

    mean_angle, var_val = utilsF.circ_stat_plot(pathsave, pd_fil_info)
    line_mean = np.mean(mean_angle)

    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,len(mean_angle)), mean_angle)
    plt.plot(np.arange(0,len(mean_angle)), np.ones(len(mean_angle))*line_mean, color='black', linestyle='dashed')
    plt.xlabel('Frames', size=24)
    plt.ylabel('Circular mean angle', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_mean.png'))
    plt.close('all')

    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,len(var_val)), var_val)
    plt.xlabel('frames', size=24)
    plt.ylabel('circular variance of angles', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_var.png'))
    plt.close('all')

    # Per filament survival length analysis
    tagsU = pd_fil_info['filament'].unique()
    plt.figure(figsize=(10,10))
    for s in tagsU:
        fil_lengths = pd_fil_info[pd_fil_info['filament']==s]['filament length'].values
        plt.plot(np.arange(len(fil_lengths)), fil_lengths)
    plt.xlabel('Survival frames', size=24)
    plt.ylabel('filament length', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_len.png'))
    plt.close('all')

    # Save summary data as CSV
    df_angles2 = pd.DataFrame({
        'angles': mean_angle,
        'var': var_val,
        'frame density': dens,
        'filament median length': fil_len,
        'filament median intensity per length': fil_I,
        'name': name_cell
    })
    df_angles2.to_csv(os.path.join(pathsave, 'value_per_frame.csv'), index=False)

def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    create_output_dirs(pathsave)

    # Pad images for processing
    M, N, P = img_o.shape
    img_padded = np.zeros((len(img_o), M+2, N+2))
    for i in range(len(img_o)):
        img_padded[i] = np.pad(img_o[i], 1, 'constant')

    # Process each frame
    graphTagg_list = []
    posL_list = []
    imF_list = []
    for i, img in enumerate(img_padded):
        print(f"Processing frame {i}")
        result = process_graph(img, size, eps, thresh_top, sigma, small, angleA, overlap)
        graphTagg_list.append(result['graphTagg'])
        posL_list.append(result['posL'])
        imF_list.append(result['imF'])
        # Save the graph image
        save_graph(img, result['graphTagg'], result['posL'], os.path.join(pathsave, 'n_graphs'), f'graph{i}.png')
        print('filament defined:', result['filaments_count'])

    # Save posL
    pickle.dump(posL_list, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))

    # Track filaments through frames
    g_tagged_list, tag_new = track_filaments_through_frames(graphTagg_list, posL_list, max_cost)

    # Save the tracked graphs
    pickle.dump(g_tagged_list, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))

    # Draw and save tracked graphs
    max_tag = max(tag_new)
    for i, g in enumerate(g_tagged_list):
        title = f"graph {i+1}"
        utilsF.draw_graph_filament_track_nocolor(img_padded[i], g, posL_list[i], title, max_tag, padv=50)
        plt.savefig(os.path.join(pathsave, 'mov', f'trackgraph{i+1}.png'))
        plt.close('all')

    # Perform analysis
    analyze_time_series(pathsave, img_padded, g_tagged_list, posL_list, imF_list, maskDraw, name_cell)

def create_all_still(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, name_cell):
    create_output_dirs(pathsave)

    # Pad single image
    N, P = img_o.shape
    img_padded = np.pad(img_o, 1, 'constant')

    # Process the single image
    result = process_graph(img_padded, size, eps, thresh_top, sigma, small, angleA, overlap)
    save_graph(img_padded, result['graphTagg'], result['posL'], os.path.join(pathsave, 'n_graphs'), 'graph.png')
    print('filament defined:', result['filaments_count'])

    # Analyze the still image (no time tracking)
    pd_fil_info = utilsF.filament_info(img_padded, result['graphTagg'], result['posL'], pathsave, result['imF'], maskDraw)
    pd_fil_info = pd.read_csv(os.path.join(pathsave, 'traced_filaments_info.csv'))

    mean_len = np.mean(pd_fil_info['filament length'])
    list_len = np.sort(pd_fil_info['filament length'])
    plt.figure()
    plt.scatter(np.arange(0, len(list_len)), list_len)
    plt.savefig(os.path.join(pathsave, 'plots', 'filament_length_distribution.png'))
    plt.close('all')

    mean_angle, var_val = utilsF.circ_stat(pd_fil_info, pathsave)
    print('mean angle:', mean_angle, 'circ var:', var_val, 'mean length:', mean_len)
