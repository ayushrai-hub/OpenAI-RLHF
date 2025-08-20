#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd
from collections import Counter
import pickle
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from graft import utilsF

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingParameters:
    """Parameters for image and graph processing."""
    size: int
    eps: float
    thresh_top: float
    sigma: float
    small: int
    angleA: float
    overlap: float
    max_cost: float

class GraphProcessor:
    """Handles the processing of graphs from images."""
    
    def __init__(self, params: ProcessingParameters, output_dir: str):
        self.params = params
        self.output_dir = output_dir
        self.create_output_dirs()

    def create_output_dirs(self) -> None:
        """Create necessary output directories."""
        for subdir_name in ('n_graphs', 'circ_stat', 'mov', 'plots'):
            subdir_path = os.path.join(self.output_dir, subdir_name)
            os.makedirs(subdir_path, exist_ok=True)

    def process_single_graph(self, img: np.ndarray) -> Tuple[nx.Graph, Dict, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
        """Process a single image to create and analyze a graph."""
        try:
            # Create initial graph
            graph, pos_list, img_skel, img_af, img_bl, im_f, mask, df_pos = utilsF.creategraph(
                img,
                size=self.params.size,
                eps=self.params.eps,
                thresh_top=self.params.thresh_top,
                sigma=self.params.sigma,
                small=self.params.small
            )

            # Process graph
            graph_d = utilsF.dangling_edges(graph.copy())
            lg_g = nx.line_graph(graph.copy())
            lg_g_v = utilsF.lG_edgeVal(lg_g.copy(), graph_d, pos_list)
            graph_tagged = utilsF.dfs_constrained(
                graph.copy(),
                lg_g_v.copy(),
                img_bl,
                pos_list,
                self.params.angleA,
                self.params.overlap
            )

            return graph_tagged, pos_list, img_skel, img_af, img_bl, im_f, mask, df_pos

        except Exception as e:
            logger.error(f"Error processing graph: {str(e)}")
            raise

    def save_graph(self, graph: nx.Graph, pos_list: Dict, img: np.ndarray, index: int) -> None:
        """Save a single graph visualization."""
        try:
            utilsF.draw_graph_filament_nocolor(img, graph, pos_list, "", 'filament')
            plt.savefig(os.path.join(self.output_dir, 'n_graphs', f'graph{index}.png'))
            plt.close('all')
        except Exception as e:
            logger.error(f"Error saving graph {index}: {str(e)}")
            raise

    def analyze_tracking_results(self, g_tagged: List[nx.Graph], tag_new: List[int], img_series: np.ndarray) -> None:
        """Analyze and save tracking results."""
        try:
            # Save tracking visualizations
            for i, (graph, img) in enumerate(zip(g_tagged, img_series)):
                utilsF.draw_graph_filament_track_nocolor(
                    img, graph, pos_list[i], f"graph {i+1}", max(tag_new), padv=50
                )
                plt.savefig(os.path.join(self.output_dir, "mov", f"trackgraph{i+1}.png"))
                plt.close('all')

            # Analyze filament statistics
            self._analyze_filament_statistics(g_tagged, img_series)

        except Exception as e:
            logger.error(f"Error in tracking analysis: {str(e)}")
            raise

    def _analyze_filament_statistics(self, g_tagged: List[nx.Graph], img_series: np.ndarray) -> None:
        """Analyze and plot filament statistics."""
        unique_filaments = [len(np.unique(np.asarray(list(g.edges(data='tags')))[:,2])) 
                          for g in g_tagged]

        # Plot filaments per frame
        plt.figure(figsize=(10,10))
        plt.scatter(np.arange(len(unique_filaments)), unique_filaments)
        plt.xlabel('frames', size=24)
        plt.ylabel('# filaments', size=24)
        plt.savefig(os.path.join(self.output_dir, 'plots', 'filaments_per_frame.png'))
        plt.close()

def create_all(pathsave: str, img_o: np.ndarray, maskDraw: np.ndarray, **kwargs) -> None:
    """Process a sequence of images and track filaments over time."""
    params = ProcessingParameters(**kwargs)
    processor = GraphProcessor(params, pathsave)
    
    # Pad images
    img_padded = np.pad(img_o, ((0,0), (1,1), (1,1)), 'constant')
    
    # Process all frames
    results = []
    graphs = []
    pos_lists = []
    
    for i, img in enumerate(img_padded):
        logger.info(f"Processing frame {i+1}/{len(img_padded)}")
        result = processor.process_single_graph(img)
        graphs.append(result[0])
        pos_lists.append(result[1])
        processor.save_graph(result[0], result[1], img, i)
        results.append(result)
    
    # Track filaments
    g_tagged, tag_new = track_filaments(graphs, pos_lists, params.max_cost)
    
    # Save results
    pickle.dump(pos_lists, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))
    pickle.dump(g_tagged, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))
    
    # Analyze results
    processor.analyze_tracking_results(g_tagged, tag_new, img_padded)

def create_all_still(pathsave: str, img_o: np.ndarray, maskDraw: np.ndarray, **kwargs) -> None:
    """Process a single image."""
    params = ProcessingParameters(**kwargs)
    processor = GraphProcessor(params, pathsave)
    
    # Pad image
    img_padded = np.pad(img_o, (1,1), 'constant')
    
    # Process single image
    graph, pos_list, *_ = processor.process_single_graph(img_padded)
    processor.save_graph(graph, pos_list, img_padded, 0)
    
    # Save results
    pickle.dump(pos_list, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))
    pickle.dump(graph, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))
