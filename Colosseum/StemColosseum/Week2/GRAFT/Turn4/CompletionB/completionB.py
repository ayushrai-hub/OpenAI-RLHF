# graft/main.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def process_graph(img, params):
    """
    Process a single image to create and tag a graph based on given parameters.

    Parameters:
        img (np.ndarray): The input image.
        params (dict): Dictionary of parameters.

    Returns:
        dict: A dictionary containing processed graph data.
    """
    # Unpack parameters
    size = params['size']
    eps = params['eps']
    thresh_top = params['thresh_top']
    sigma = params['sigma']
    small = params['small']
    angleA = params['angleA']
    overlap = params['overlap']

    # 0) create graph
    graph_s, posL, imgSkel, imgAF, imgBl, imF, mask, df_pos = utilsF.creategraph(
        img, size=size, eps=eps, thresh_top=thresh_top, sigma=sigma, small=small
    )
    # 1) find all dangling edges and mark them
    graphD = utilsF.dangling_edges(graph_s.copy())
    # 2) create line graph
    lgG = nx.line_graph(graph_s.copy())
    # 3) calculate the angles between two edges from the graph that is now represented by edges in the line graph
    lgG_V = utilsF.lG_edgeVal(lgG.copy(), graphD, posL)
    # 4) run depth first search
    graphTagg = utilsF.dfs_constrained(
        graph_s.copy(), lgG_V.copy(), imgBl, posL, angleA, overlap
    )

    return {
        'graph_s': graph_s,
        'posL': posL,
        'imgSkel': imgSkel,
        'imgAF': imgAF,
        'imgBl': imgBl,
        'imF': imF,
        'mask': mask,
        'df_pos': df_pos,
        'graphTagg': graphTagg
    }

def draw_and_save_graph(img, graphTagg, posL, output_path, filename):
    """
    Draws and saves the graph.

    Parameters:
        img (np.ndarray): The input image.
        graphTagg (networkx.Graph): The tagged graph.
        posL (dict): Positions of nodes.
        output_path (str): The path to save the image.
        filename (str): The filename for the saved image.
    """
    utilsF.draw_graph_filament_nocolor(img, graphTagg, posL, '', 'filament')
    plt.savefig(os.path.join(output_path, filename))
    plt.close('all')

def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    create_output_dirs(pathsave)

    num_frames = len(img_o)
    
    # Prepare lists to store results
    graph_s_list = []
    posL_list = []
    imgSkel_list = []
    imgAF_list = []
    imgBl_list = []
    imF_list = []
    mask_list = []
    df_pos_list = []
    graphTagg_list = []
    no_filaments = []

    # Pad images
    imgP = np.pad(img_o, ((0, 0), (1, 1), (1, 1)), 'constant')

    params = {
        'size': size,
        'eps': eps,
        'thresh_top': thresh_top,
        'sigma': sigma,
        'small': small,
        'angleA': angleA,
        'overlap': overlap
    }

    for idx, img in enumerate(imgP):
        print(idx)
        result = process_graph(img, params)
        graph_s_list.append(result['graph_s'])
        posL_list.append(result['posL'])
        imgSkel_list.append(result['imgSkel'])
        imgAF_list.append(result['imgAF'])
        imgBl_list.append(result['imgBl'])
        imF_list.append(result['imF'])
        mask_list.append(result['mask'])
        df_pos_list.append(result['df_pos'])
        graphTagg_list.append(result['graphTagg'])

        draw_and_save_graph(img, result['graphTagg'], result['posL'], os.path.join(pathsave, 'n_graphs'), f'graph{idx}.png')

        filament_edges = list(result['graphTagg'].edges(data='filament'))
        filaments = np.unique(np.asarray(filament_edges)[:, 2])
        no_filaments.append(len(filaments))
        print('filament defined: ', len(filaments))

    pickle.dump(posL_list, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))
    ###############################################################################
    #
    # Data tracking
    #
    ###############################################################################

    if num_frames < 20:
        memKeep = num_frames
    else:
        memVal = 20
        memKeep = utilsF.signMem(graphTagg_list[0:memVal], posL_list[0:memVal])

    # First graph needs unique tags
    first_graph = graphTagg_list[0]
    for node1, node2, property in first_graph.edges(data=True):
        for n in range(len(first_graph[node1][node2])):
            first_graph[node1][node2][n]['tags'] = property['filament']

    max_tag = np.max(np.asarray(list(first_graph.edges(data='filament')))[:, 2])

    g_tagged = [first_graph]
    cost = []
    tag_new = [max_tag]
    filamentsNU = []

    for i in range(num_frames - 1):
        g_tagged_next, cost_i, tag_new_i, filamentsNU = utilsF.filament_tag(
            g_tagged[i], graphTagg_list[i + 1], posL_list[i], posL_list[i + 1], tag_new[i], max_cost, filamentsNU, memKeep
        )
        g_tagged.append(g_tagged_next)
        cost.append(cost_i)
        tag_new.append(tag_new_i)

    pickle.dump(g_tagged, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))

    # Draw and save the tracked graphs
    for i in range(num_frames):
        title = f"graph {i + 1}"
        utilsF.draw_graph_filament_track_nocolor(imgP[i], g_tagged[i], posL_list[i], title, max(tag_new), padv=50)
        plt.savefig(os.path.join(pathsave, "mov", f"trackgraph{i + 1}.png"))
        plt.close('all')

    ###############################################################################
    #
    # Data analysis
    #
    ###############################################################################

    plt.rc('xtick', labelsize=24)
    plt.rc('ytick', labelsize=24)

    unique_filaments = []
    unique_frames = []

    for i in range(num_frames):
        filament_tags = np.asarray(list(g_tagged[i].edges(data='tags')))[:, 2]
        unique_filaments.append(len(np.unique(filament_tags)))
        unique_frames.extend(np.unique(filament_tags))

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(len(unique_filaments)), unique_filaments)
    plt.xlabel('frames', size=24)
    plt.ylabel('# filaments', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filaments_per_frame.png'))
    plt.close('all')

    # Data analysis - one frame at a time
    pd_fil_info = utilsF.filament_info_time(imgP, g_tagged, posL_list, pathsave, imF_list, maskDraw)
    pd_fil_info.to_csv(os.path.join(pathsave, 'tracked_filaments_info.csv'), index=False)

    vals = pd_fil_info['filament'].value_counts().values

    counts, bins = np.histogram(vals, 20)
    plt.figure(figsize=(10, 7))
    plt.hist(bins[:-1], bins, weights=counts, color='green')
    plt.xlabel('frames', size=24)
    plt.ylabel('filaments survival', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments.png'))
    plt.close('all')

    counts, bins = np.histogram(vals, 20, density=True)
    plt.figure(figsize=(10, 7))
    plt.hist(bins[:-1], bins, weights=counts, color='green')
    plt.xlabel('frames', size=24)
    plt.ylabel('filaments survival', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments_normalized.png'))
    plt.close('all')

    dens = np.zeros(num_frames)
    fil_len = np.zeros(num_frames)
    fil_I = np.zeros(num_frames)
    for i in range(num_frames):
        frame_data = pd_fil_info[pd_fil_info['frame number'] == i]
        dens[i] = frame_data['filament density'].values[0]
        fil_len[i] = np.median(frame_data['filament length'])
        fil_I[i] = np.median(frame_data['filament intensity per length'])

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(num_frames), dens)
    plt.xlabel('frames', size=24)
    plt.ylabel('filament density', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filament_density.png'))
    plt.close('all')

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(num_frames), fil_len)
    plt.xlabel('frames', size=24)
    plt.ylabel('filament median length', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filamentlength.png'))
    plt.close('all')

    mean_angle, var_val = utilsF.circ_stat_plot(pathsave, pd_fil_info)

    line_mean = np.mean(mean_angle)

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(len(mean_angle)), mean_angle)
    plt.plot(np.arange(len(mean_angle)), np.ones(len(mean_angle)) * line_mean, color='black', linestyle='dashed')
    plt.xlabel('Frames', size=24)
    plt.ylabel('Circular mean angle', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_mean.png'))
    plt.close('all')

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(len(var_val)), var_val)
    plt.xlabel('frames', size=24)
    plt.ylabel('circular variance of angles', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_var.png'))
    plt.close('all')

    tagsU = pd_fil_info['filament'].unique()
    plt.figure(figsize=(10, 10))
    for s in tagsU:
        fil = pd_fil_info[pd_fil_info['filament'] == s]['filament length'].values
        plt.plot(np.arange(len(fil)), fil)
    plt.xlabel('Survival frames', size=24)
    plt.ylabel('filament length', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_len.png'))
    plt.close('all')

    ###############################################################################
    #
    # Mean/Median value per frame
    #
    ###############################################################################

    df_angles2 = pd.DataFrame({
        'angles': mean_angle,
        'var': var_val,
        'frame density': dens,
        'filament median length': fil_len,
        'filament median intensity per length': fil_I,
        'name': name_cell
    })

    df_angles2.to_csv(os.path.join(pathsave, 'value_per_frame.csv'), index=False)

def create_all_still(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, name_cell):
    create_output_dirs(pathsave)

    # Pad image
    imgP = np.pad(img_o, 1, 'constant')

    params = {
        'size': size,
        'eps': eps,
        'thresh_top': thresh_top,
        'sigma': sigma,
        'small': small,
        'angleA': angleA,
        'overlap': overlap
    }

    result = process_graph(imgP, params)
    draw_and_save_graph(imgP, result['graphTagg'], result['posL'], os.path.join(pathsave, 'n_graphs'), 'graph.png')

    print('filament defined: ', len(np.unique(np.asarray(list(result['graphTagg'].edges(data='filament')))[:, 2])))

    ###############################################################################
    #
    # Data analysis - one frame
    #
    ###############################################################################

    pd_fil_info = utilsF.filament_info(imgP, result['graphTagg'], result['posL'], pathsave, result['imF'], maskDraw)
    pd_fil_info.to_csv(os.path.join(pathsave, 'traced_filaments_info.csv'), index=False)
    
    mean_len = np.mean(pd_fil_info['filament length'])
    list_len = np.sort(pd_fil_info['filament length'])
    plt.figure()
    plt.scatter(np.arange(len(list_len)), list_len)
    plt.xlabel('Filament Index')
    plt.ylabel('Filament Length')
    plt.savefig(os.path.join(pathsave, 'plots', 'filament_lengths.png'))
    plt.close('all')

    mean_angle, var_val = utilsF.circ_stat(pd_fil_info, pathsave)
    print('mean angle: ', mean_angle, 'circ var: ', var_val, 'mean length: ', mean_len)

    # Save summary data
    df_summary = pd.DataFrame({
        'mean angle': [mean_angle],
        'circular variance': [var_val],
        'mean filament length': [mean_len],
        'name': [name_cell]
    })
    df_summary.to_csv(os.path.join(pathsave, 'value_per_frame.csv'), index=False)
