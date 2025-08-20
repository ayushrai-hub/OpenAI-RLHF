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
    """Processes a single image to generate a graph based on the given parameters."""
    graph, posL, imgSkel, imgAF, imgBl, imF, mask, df_pos = utilsF.creategraph(
        img, size=size, eps=eps, thresh_top=thresh_top, sigma=sigma, small=small)
    return {
        'graph': graph,
        'posL': posL,
        'imgSkel': imgSkel,
        'imgAF': imgAF,
        'imgBl': imgBl,
        'imF': imF,
        'mask': mask,
        'df_pos': df_pos
    }

def save_graph(img, graph, posL, output_path):
    """Draws and saves a graph overlay on an image."""
    utilsF.draw_graph_filament_nocolor(img, graph, posL, title='', label='filament')
    plt.savefig(output_path)
    plt.close()

def process_and_tag_graphs(graph_data_list, angleA, overlap, max_cost, pathsave):
    """Processes and tags all graphs from a list of graph data."""
    graphTagg = []
    for data in graph_data_list:
        graphD = utilsF.dangling_edges(data['graph'].copy())
        lgG = nx.line_graph(data['graph'].copy())
        lgG_V = utilsF.lG_edgeVal(lgG.copy(), graphD, data['posL'])
        gTag = utilsF.dfs_constrained(data['graph'].copy(), lgG_V.copy(), data['imgBl'], 
                                      data['posL'], angleA, overlap)
        graphTagg.append(gTag)
    posL = [data['posL'] for data in graph_data_list]

    # Tagging and tracking filaments
    memKeep = len(graphTagg) if len(graphTagg) < 20 else utilsF.signMem(graphTagg[:20], posL[:20])

    for node1, node2, property in graphTagg[0].edges(data=True):
        for n in range(len(graphTagg[0][node1][node2])):
            graphTagg[0][node1][node2][n]['tags'] = property['filament']

    max_tag = np.max(list(graphTagg[0].edges(data='filament')), axis=0)[2]
    
    g_tagged = [graphTagg[0]]
    cost = [0]*(len(graphTagg)-1)
    tag_new = [max_tag]
    filamentsNU = []

    for i in range(len(graphTagg) - 1):
        g_tag, cost[i], tag_n, filamentsNU = utilsF.filament_tag(
            g_tagged[i], graphTagg[i+1], posL[i], posL[i+1], tag_new[i], max_cost, filamentsNU, memKeep)
        g_tagged.append(g_tag)
        tag_new.append(tag_n)

    pickle.dump(g_tagged, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))
    return g_tagged, posL, tag_new

def analyze_data(img_padded, g_tagged, posL, pathsave, imF, maskDraw, name_cell):
    """Performs data analysis and saves plots and data to files."""
    pd_fil_info = utilsF.filament_info_time(img_padded, g_tagged, posL, pathsave, imF, maskDraw)

    pd_fil_info = pd.read_csv(os.path.join(pathsave, 'tracked_filaments_info.csv'))
    vals = Counter(pd_fil_info['filament']).values()

    counts, bins = np.histogram(list(vals), 20)
    plt.figure(figsize=(10, 7))
    plt.hist(bins[:-1], bins, weights=counts, color='green')
    plt.xlabel('frames', size=24)
    plt.ylabel('filaments survival', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments.png'))

    counts, bins = np.histogram(list(vals), 20, density=True)
    plt.figure(figsize=(10, 7))
    plt.hist(bins[:-1], bins, weights=counts, color='green')
    plt.xlabel('frames', size=24)
    plt.ylabel('filaments survival', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments_normalized.png'))

    dens, fil_len, fil_I = [], [], []
    for i in range(len(img_padded)):
        frame_info = pd_fil_info[pd_fil_info['frame number'] == i]
        dens.append(frame_info['filament density'].values[0])
        fil_len.append(np.median(frame_info['filament length']))
        fil_I.append(np.median(frame_info['filament intensity per length']))

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(len(img_padded)), dens)
    plt.xlabel('frames', size=24)
    plt.ylabel('filament density', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filament_density.png'))

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(len(img_padded)), fil_len)
    plt.xlabel('frames', size=24)
    plt.ylabel('filament median length', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filamentlength.png'))

    mean_angle, var_val = utilsF.circ_stat_plot(pathsave, pd_fil_info)
    line_mean = np.mean(mean_angle)

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(len(mean_angle)), mean_angle)
    plt.plot(np.arange(len(mean_angle)), np.ones(len(mean_angle)) * line_mean, color='black', linestyle='dashed')
    plt.xlabel('Frames', size=24)
    plt.ylabel('Circular mean angle', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_mean.png'))

    plt.figure(figsize=(10, 10))
    plt.scatter(np.arange(len(var_val)), var_val)
    plt.xlabel('frames', size=24)
    plt.ylabel('circular variance of angles', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_var.png'))

    tagsU = pd_fil_info['filament'].unique()
    plt.figure(figsize=(10, 10))
    for s in tagsU:
        fil = pd_fil_info[pd_fil_info['filament'] == s]['filament length'].values
        plt.plot(np.arange(len(fil)), fil)
    plt.xlabel('Survival frames', size=24)
    plt.ylabel('filament length', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_len.png'))

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
    img_padded = np.pad(img_o, ((0, 0), (1, 1), (1, 1)), 'constant')
    
    graph_data_list = []
    for img in img_padded:
        graph_data = process_graph(img, size, eps, thresh_top, sigma, small)
        graph_data_list.append(graph_data)

    for idx, data in enumerate(graph_data_list):
        save_path = os.path.join(pathsave, 'n_graphs', f'graph{idx}.png')
        save_graph(data['imgSkel'], data['graph'], data['posL'], save_path)

    g_tagged, posL, tag_new = process_and_tag_graphs(graph_data_list, angleA, overlap, max_cost, pathsave)
    pickle.dump(posL, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))

    for i in range(len(img_o)):
        title = f"graph {i + 1}"
        utilsF.draw_graph_filament_track_nocolor(img_padded[i], g_tagged[i], posL[i], title, max(tag_new
