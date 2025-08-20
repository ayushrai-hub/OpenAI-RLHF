#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd
from collections import Counter
import pickle
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple, Dict, Any

from graft import utilsF

def create_output_dirs(output_dir: str) -> None:
    """Ensure that the specific output dir incl. subdirs exists."""
    for subdir_name in ('n_graphs', 'circ_stat', 'mov', 'plots'):
        subdir_path = os.path.join(output_dir, subdir_name)
        os.makedirs(subdir_path, exist_ok=True)

def process_graph(img: np.ndarray, params: Dict[str, Any]) -> Tuple:
    """Process a single image to create a graph and related data."""
    graph, pos_list, skel_img, af_img, bl_img, mask, df_pos = utilsF.creategraph(
        img, size=params['size'], eps=params['eps'], 
        thresh_top=params['thresh_top'], sigma=params['sigma'], 
        small=params['small']
    )
    graph_d = utilsF.dangling_edges(graph.copy())
    lg_g = nx.line_graph(graph.copy())
    lg_g_v = utilsF.lG_edgeVal(lg_g.copy(), graph_d, pos_list)
    graph_tagged = utilsF.dfs_constrained(graph.copy(), lg_g_v.copy(), bl_img, 
                                          pos_list, params['angleA'], params['overlap'])
    
    return graph_tagged, pos_list, skel_img, af_img, bl_img, mask, df_pos

def save_graph(graph: nx.Graph, pos_list: Dict, img: np.ndarray, 
               output_path: str, index: int) -> None:
    """Save a single graph as an image."""
    utilsF.draw_graph_filament_nocolor(img, graph, pos_list, "", 'filament')
    plt.savefig(os.path.join(output_path, f'graph{index}.png'))
    plt.close('all')

def process_and_save_graphs(imgs: List[np.ndarray], params: Dict[str, Any], 
                            output_dir: str) -> List[Tuple]:
    """Process and save graphs for a list of images."""
    results = []
    with ProcessPoolExecutor() as executor:
        future_to_index = {executor.submit(process_graph, img, params): i 
                           for i, img in enumerate(imgs)}
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
                save_graph(result[0], result[1], imgs[index], 
                           os.path.join(output_dir, 'n_graphs'), index)
                results.append(result)
            except Exception as exc:
                print(f'Image {index} generated an exception: {exc}')
    return results

def track_filaments(graphs: List[nx.Graph], pos_lists: List[Dict], 
                    max_cost: float) -> List[nx.Graph]:
    """Track filaments across frames."""
    g_tagged = [graphs[0]]
    max_tag = max(list(graphs[0].edges(data='filament')), key=lambda x: x[2])[2]
    
    for i in range(len(graphs) - 1):
        g_tagged_next, cost, max_tag, _ = utilsF.filament_tag(
            g_tagged[i], graphs[i+1], pos_lists[i], pos_lists[i+1], 
            max_tag, max_cost, [], 20
        )
        g_tagged.append(g_tagged_next)
    
    return g_tagged

def analyze_filaments(g_tagged: List[nx.Graph], imgs: List[np.ndarray], 
                      pos_lists: List[Dict], output_dir: str) -> pd.DataFrame:
    """Analyze filaments and save results."""
    pd_fil_info = utilsF.filament_info_time(imgs, g_tagged, pos_lists, output_dir, None, None)
    
    # Plot filament statistics
    plot_filament_statistics(pd_fil_info, output_dir)
    
    return pd_fil_info

def plot_filament_statistics(pd_fil_info: pd.DataFrame, output_dir: str) -> None:
    """Plot various filament statistics."""
    plt.figure(figsize=(10, 7))
    vals = Counter(pd_fil_info['filament']).values()
    plt.hist(list(vals), bins=20, color='green')
    plt.xlabel('Frames', fontsize=24)
    plt.ylabel('Filaments Survival', fontsize=24)
    plt.savefig(os.path.join(output_dir, 'plots', 'survival_filaments.png'))
    plt.close()

    # Add more plots as needed...

def create_all(pathsave: str, img_o: np.ndarray, maskDraw: np.ndarray, 
               size: int, eps: float, thresh_top: float, sigma: float, 
               small: int, angleA: float, overlap: float, max_cost: float, 
               name_cell: str) -> None:
    """Main function to process time-series images."""
    create_output_dirs(pathsave)
    
    params = {
        'size': size, 'eps': eps, 'thresh_top': thresh_top, 
        'sigma': sigma, 'small': small, 'angleA': angleA, 'overlap': overlap
    }
    
    img_padded = np.pad(img_o, ((0,0), (1,1), (1,1)), 'constant')
    
    results = process_and_save_graphs(img_padded, params, pathsave)
    graphs, pos_lists, _, _, _, _, _ = zip(*results)
    
    g_tagged = track_filaments(graphs, pos_lists, max_cost)
    
    pickle.dump(pos_lists, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))
    pickle.dump(g_tagged, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))
    
    pd_fil_info = analyze_filaments(g_tagged, img_padded, pos_lists, pathsave)
    
    # You can add more specific processing here if needed

def create_all_still(pathsave: str, img_o: np.ndarray, maskDraw: np.ndarray, 
                     size: int, eps: float, thresh_top: float, sigma: float, 
                     small: int, angleA: float, overlap: float, 
                     name_cell: str) -> None:
    """Main function to process a single image."""
    create_output_dirs(pathsave)
    
    params = {
        'size': size, 'eps': eps, 'thresh_top': thresh_top, 
        'sigma': sigma, 'small': small, 'angleA': angleA, 'overlap': overlap
    }
    
    img_padded = np.pad(img_o, ((1,1), (1,1)), 'constant')
    
    graph, pos_list, skel_img, af_img, bl_img, mask, df_pos = process_graph(img_padded, params)
    save_graph(graph, pos_list, img_padded, os.path.join(pathsave, 'n_graphs'), 0)
    
    pickle.dump(pos_list, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))
    pickle.dump(graph, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))
    
    # You can add more specific processing for single image here if needed

if __name__ == "__main__":
    # Add any main execution code here
    pass
