import numpy as np
import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd
import pickle
from graft import utilsF
from concurrent.futures import ThreadPoolExecutor

def create_output_dirs(output_dir):
    """Ensure that the given output directory incl. subdirectories exists."""
    for subdir_name in ('n_graphs', 'circ_stat', 'mov', 'plots'):
        subdir_path = os.path.join(output_dir, subdir_name)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)

def process_graph(img, params):
    """
    Generate graph structures for a single image based on given parameters.
    Returns graph, position list, skeleton image, and mask for further processing.
    """
    graph, pos, img_skel, img_AF, img_bl, mask, df_pos = utilsF.creategraph(
        img, size=params['size'], eps=params['eps'], 
        thresh_top=params['thresh_top'], sigma=params['sigma'], 
        small=params['small']
    )
    return graph, pos, img_skel, img_AF, img_bl, mask, df_pos

def save_graph(graph, pos_list, img_skel, output_dir, image_index):
    """Save visual representations of the graph and associated data."""
    utilsF.draw_graph_filament_nocolor(img_skel, graph, pos_list, "", "filament")
    plt.savefig(os.path.join(output_dir, f'graph{image_index}.png'))
    plt.close('all')

def save_graphs(graphs, pos_lists, skel_images, output_dir):
    """Saves all graphs and associated visualizations to specified directory."""
    for idx, (graph, pos_list, skel_img) in enumerate(zip(graphs, pos_lists, skel_images)):
        save_graph(graph, pos_list, skel_img, output_dir, idx)

def analyze_graphs(graphs, pos_lists, pathsave, img_padded, name_cell):
    """Main function for processing, analyzing, and saving graph data for multiple image slices."""
    graph_data = []
    for idx, (graph, pos) in enumerate(zip(graphs, pos_lists)):
        # 1) Save individual graphs for later analysis
        save_graph(graph, pos, img_padded, os.path.join(pathsave, 'n_graphs'), idx)

        # Calculate and store graph-related data
        graphD = utilsF.dangling_edges(graph.copy())  # 1) dangling edges
        lgG = nx.line_graph(graph)  # 2) line graph

        lgG_V = utilsF.lG_edgeVal(lgG.copy(), graphD, pos)  # 3) edge values for line graph
        graphTagg = utilsF.dfs_constrained(graph.copy(), lgG_V, img_padded, pos, params['angleA'], params['overlap'])  # 4) constrained DFS

        utilsF.draw_graph_filament_nocolor(img_padded, graphTagg, pos, '', 'filament')
        plt.savefig(os.path.join(pathsave, 'n_graphs', f'graph{idx}.png'))
        plt.close('all')

        # Compute number of filaments
        num_filaments = len(np.unique(np.asarray(list(graphTagg.edges(data='filament')))[:, 2]))
        print('Filament defined:', num_filaments)
        graph_data.append((graphTagg, num_filaments))

    return graph_data

def create_all(pathsave, img_o, maskDraw, **params):
    create_output_dirs(pathsave)
    M, N, P = img_o.shape
    imgP = np.zeros((M, N+2, P+2))
    imgP[:, :, :] = np.pad(img_o, ((0,0), (1,1), (1,1)), 'constant')

    # Concurrently process each time-slice in the image stack
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_graph, imgP[m], params) for m in range(M)]
        results = [future.result() for future in futures]

    graphs, pos_lists, imgSkel, imgAF, imgBl, masks, df_positions = zip(*results)
    save_graphs(graphs, pos_lists, imgSkel, os.path.join(pathsave, 'n_graphs'))

    # Further analysis across processed graphs
    graph_data = analyze_graphs(graphs, pos_lists, pathsave, imgP, params['name_cell'])

    g_tagged = [0] * len(img_o)
    cost, tag_new = [0] * (len(img_o)-1), [0] * len(img_o)
    tag_new[0] = np.max(list(graph_data[0][0].edges(data='filament')), axis=0)[2]

    # Filament tagging across image slices
    for i in range(len(img_o) - 1):
        g_tagged[i+1], cost[i], tag_new[i+1], _ = utilsF.filament_tag(
            g_tagged[i], graph_data[i+1][0], pos_lists[i], pos_lists[i+1], tag_new[i], params['max_cost']
        )

    # Save the tagged graph data
    pickle.dump(g_tagged, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))

    # Analysis and saving of graphs based on the tagged data
    for i, graph in enumerate(g_tagged):
        utilsF.draw_graph_filament_track_nocolor(imgP[i], graph, pos_lists[i], f"graph {i+1}", np.max(tag_new), padv=50)
        plt.savefig(os.path.join(pathsave, "mov", f"trackgraph{i+1}.png"))
        plt.close('all')

    # Data analysis for each individual frame
    pd_fil_info = utilsF.filament_info(imgP, g_tagged, pos_lists, pathsave, masks, maskDraw)
    pd_fil_info = pd.read_csv(os.path.join(pathsave, 'tracked_filaments_info.csv'))

    # Analysis plots
    mean_angle, var_val = utilsF.circ_stat(pd_fil_info, pathsave)
    mean_len = np.mean(pd_fil_info['filament length'])

    unique_filaments = pd_fil_info['filament'].unique()
    values = np.zeros(len(unique_filaments))
    survival = np.zeros(len(unique_filaments))

    plt.figure(figsize=(10, 10))
    for s, m in zip(unique_filaments, range(len(unique_filaments))):
        filament_data = pd_fil_info[pd_fil_info['filament'] == s]['filament length'].values
        values[m] = np.median(filament_data)
        survival[m] = len(filament_data)
        plt.plot(np.arange(len(filament_data)), filament_data)
    plt.xlabel('Survival frames', size=24)
    plt.ylabel('Filament length', size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_len.png'))

    # Compile metrics into a DataFrame and save
    df_angles = pd.DataFrame()
    df_angles['angles'] = mean_angle
    df_angles['circular_variance'] = var_val
    df_angles['frame_density'] = [np.mean(pd_fil_info[pd_fil_info['frame number'] == i]['filament density']) for i in range(len(img_o))]
    df_angles['filament_median_length'] = [np.median(pd_fil_info[pd_fil_info['frame number'] == i]['filament length']) for i in range(len(img_o))]
    df_angles['filament_median_intensity'] = [np.median(pd_fil_info[pd_fil_info['frame number'] == i]['filament intensity per length']) for i in range(len(img_o))]
    df_angles['name'] = params['name_cell']

    df_angles.to_csv(os.path.join(pathsave, 'value_per_frame.csv'), index=False)

# Example usage:
# create_all(pathsave="output_directory", img_o=image_stack, maskDraw=mask, size=6, eps=200, thresh_top=0.5, sigma=1.0, small=50.0, angleA=140, overlap=4, max_cost=100, name_cell='in silico time')
