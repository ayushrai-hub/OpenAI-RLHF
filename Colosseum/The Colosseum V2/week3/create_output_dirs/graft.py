
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd
from collections import Counter
import pickle

from graft import utilsF


def create_output_dirs(output_dir):
    """Ensure that the given output directory incl. subdirectories exists."""
    for subdir_name in ('n_graphs', 'circ_stat', 'mov', 'plots'):
        subdir_path = os.path.join(output_dir, subdir_name)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)


def generate_default_mask(image_shape):
    """Generate a default mask of ones based on the image shape."""
    if len(image_shape) == 3:  # Time-series image
        return np.ones(image_shape[1:])
    elif len(image_shape) == 2:  # Still image
        return np.ones(image_shape)
    else:
        raise ValueError("Unsupported image shape. Expected 2 or 3 dimensions.")


def create_all(pathsave,img_o,maskDraw,size,eps,thresh_top,sigma,small,angleA,overlap,max_cost,name_cell):
    create_output_dirs(pathsave)
    
    graph_s = [0]*len(img_o)
    posL = [0]*len(img_o)
    imgSkel = [0]*len(img_o)
    imgAF = [0]*len(img_o)
    imgBl = [0]*len(img_o)
    imF = [0]*len(img_o)
    mask = [0]*len(img_o)
    df_pos = [0]*len(img_o)
    graphD = [0]*len(img_o)
    lgG = [0]*len(img_o)
    lgG_V = [0]*len(img_o)
    graphTagg = [0]*len(img_o)
    no_filaments = [0]*len(img_o)
    
    M,N,P = (img_o.shape)
    imgP=np.zeros((M,N+2,P+2))
    
    for m in range(len(img_o)):
        imgP[m] = np.pad(img_o[m], 1, 'constant')
        
    for q in range(len(imgP)):
        
        print(q)
        # 0) create graph
        graph_s[q], posL[q], imgSkel[q], imgAF[q], imgBl[q],imF[q],mask[q],df_pos[q] = utilsF.creategraph(imgP[q],size=size,eps=eps,thresh_top=thresh_top,sigma=sigma,small=small)
        utilsF.draw_graph(imgSkel[q],graph_s[q],posL[q],"untagged graph")

        # 1) find all dangling edges and mark them
        graphD[q] = utilsF.dangling_edges(graph_s[q].copy())
        # 2) create line graph
        lgG[q] = nx.line_graph(graph_s[q].copy())
        # 3) calculate the angles between two edges from the graph that is now represented by edges in the line graph
        lgG_V[q] = utilsF.lG_edgeVal(lgG[q].copy(),graphD[q],posL[q])
        # 4) run depth first search
        graphTagg[q] = utilsF.dfs_constrained(graph_s[q].copy(),lgG_V[q].copy(),imgBl[q],posL[q],angleA,overlap) 
        
        utilsF.draw_graph_filament_nocolor(imgP[q],graphTagg[q],posL[q],"",'filament')
        plt.savefig(os.path.join(pathsave, 'n_graphs', f'graph{q}.png'))
    
        plt.close('all')
        no_filaments[q] = len(np.unique(np.asarray(list(graphTagg[q].edges(data='filament')))[:,2]))
        print('filament defined: ',len(np.unique(np.asarray(list(graphTagg[q].edges(data='filament')))[:,2])))
         
    pickle.dump(posL, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))
    ###############################################################################
    #
    # data
    # tracking 
    #
    ###############################################################################
    # if already saved this, then load in
    #g_tagged = nx.read_gpickle(pathsave+'tagged_graph.gpickle')
    #graphTagg = g_tagged.copy()
    
    if(len(img_o)<20):
        memKeep = len(img_o)
    else:
        memVal = 20
        memKeep = utilsF.signMem(graphTagg[0:memVal],posL[0:memVal])
    
    # first graph needs unique tags
    for node1, node2, property in graphTagg[0].edges(data=True):
        for n in range(len(graphTagg[0][node1][node2])):
            graphTagg[0][node1][node2][n]['tags'] = property['filament']
        
        
    list(graphTagg[0].edges(data='filament'))
        
    max_tag = np.max(list(graphTagg[0].edges(data='filament')),axis=0)[2] 
    
    g_tagged = [0]*(len(img_o))
    g_tagged[0] = graphTagg[0]
    cost = [0]*(len(img_o)-1)
    tag_new = [0]*(len(img_o))
    tag_new[0] = max_tag
    filamentsNU = []
    
    for i in range(len(img_o)-1):
        g_tagged[i+1],cost[i],tag_new[i+1],filamentsNU = utilsF.filament_tag(g_tagged[i],graphTagg[i+1],posL[i],posL[i+1],tag_new[i],max_cost,filamentsNU,memKeep)
    
    pickle.dump(g_tagged, open(os.path.join(pathsave, 'tagged_graph.gpickle'), 'wb'))
    
    
    for i in range(len(img_o)):
        title = "graph {}".format(i+1)
        utilsF.draw_graph_filament_track_nocolor(imgP[i],g_tagged[i],posL[i],title,max(tag_new),padv=50)
        pathsave_taggraph = os.path.join(pathsave, "mov", f"trackgraph{i+1}.png")
        plt.savefig(pathsave_taggraph)
        plt.close('all')
    
    
    ###############################################################################
    #
    # data analysis
    #
    ###############################################################################
    
    plt.rc('xtick', labelsize=24) 
    plt.rc('ytick', labelsize=24) 
        
        
        
    unique_filaments = [0]*len(img_o)
    unique_frames = []
    
    for i in range(len(img_o)):
        unique_filaments[i] = len(np.unique(np.asarray(list(g_tagged[i].edges(data='tags')))[:,2]))
        unique_frames.extend(list(np.unique(np.asarray(list(g_tagged[i].edges(data='tags')))[:,2])))
    
    
    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,len(unique_filaments)),unique_filaments)
    plt.xlabel('frames',size=24)
    plt.ylabel('# filaments',size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filaments_per_frame.png'))
    
    
    ###############################################################################
    #
    # data analysis - one frame at a time
    #
    ###############################################################################
    
    pd_fil_info = utilsF.filament_info_time(imgP, g_tagged, posL, pathsave, imF, maskDraw)
    
    pd_fil_info = pd.read_csv(os.path.join(pathsave, 'tracked_filaments_info.csv'))

    vals = Counter(pd_fil_info['filament']).values()
    
    counts,bins = np.histogram(list(vals),20)
    plt.figure(figsize=(10,7))
    plt.hist(bins[:-1], bins, weights=counts,color='green')
    plt.xlabel('frames',size=24)
    plt.ylabel('filaments survival',size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments.png'))
    
    counts,bins = np.histogram(list(vals),20,density='True')
    plt.figure(figsize=(10,7))
    plt.hist(bins[:-1], bins, weights=counts,color='green')
    plt.xlabel('frames',size=24)
    plt.ylabel('filaments survival',size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments_normalized.png'))
    
    dens = np.zeros(len(img_o))
    fil_len = np.zeros(len(img_o))
    fil_I = np.zeros(len(img_o))
    for i in range(len(img_o)):
        dens[i] = pd_fil_info[pd_fil_info['frame number']==i]['filament density'].values[0]
        fil_len[i] =np.median(pd_fil_info[pd_fil_info['frame number']==i]['filament length'])
        fil_I[i] = np.median(pd_fil_info[pd_fil_info['frame number']==i]['filament intensity per length'])
        
        
    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,len(img_o)),dens)
    plt.xlabel('frames',size=24)
    plt.ylabel('filament density',size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filament_density.png'))
    
    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,len(img_o)),fil_len)
    plt.xlabel('frames',size=24)
    plt.ylabel('filament median length',size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'filamentlength.png'))
    
    
    mean_angle,var_val = utilsF.circ_stat_plot(pathsave,pd_fil_info)
    
    line_mean = np.mean(mean_angle)
    
    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,len(mean_angle)),mean_angle)
    plt.plot(np.arange(0,len(mean_angle)),np.ones(len(mean_angle))*line_mean,color='black',linestyle='dashed')
    plt.xlabel('Frames',size=24)
    plt.ylabel('Circular mean angle',size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_mean.png'))
    
    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,len(var_val)),var_val)
    plt.xlabel('frames',size=24)
    plt.ylabel('circular variance of angles',size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_var.png'))
    
    tagsU = pd_fil_info['filament'].unique()
    vals = np.zeros(len(tagsU))
    lives = np.zeros(len(tagsU))
    plt.figure(figsize=(10,10))
    for s,m in zip(tagsU,range(len(tagsU))):
        fil = pd_fil_info[pd_fil_info['filament']==s]['filament length'].values
        #print(fil)np.median(fil
        vals[m]=np.median(fil)
        lives[m]=len(fil)
        plt.plot(np.arange(0,len(fil)),fil)
    plt.xlabel('Survival frames',size=24)
    plt.ylabel('filament length',size=24)
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_len.png'))
    
    ###############################################################################
    #
    # mean/median value per frame
    #
    ###############################################################################
    
    df_angles2 = pd.DataFrame()
    df_angles2['angles'] = mean_angle
    df_angles2['var'] = var_val
    df_angles2['frame density'] = dens
    df_angles2['filament median length'] = fil_len
    df_angles2['filament mediam intensity per length'] = fil_I
    df_angles2['name'] = name_cell
    
    df_angles2.to_csv(os.path.join(pathsave, 'value_per_frame.csv'),index=False)
    
    return


def create_all_still(pathsave,img_o,maskDraw,size,eps,thresh_top,sigma,small,angleA,overlap,name_cell):
    create_output_dirs(pathsave)    
    
    N,P = (img_o.shape)
    imgP=np.zeros((N+2,P+2))
    

    imgP = np.pad(img_o, 1, 'constant')
        
    # 0) create graph
    graph_s, posL, imgSkel, imgAF, imgBl,imF,mask,df_pos = utilsF.creategraph(imgP,size=size,eps=eps,thresh_top=thresh_top,sigma=sigma,small=small)
    #utilsF.draw_graph(imgSkel[q],graph_s[q],posL[q],"untagged graph")
    #plt.savefig(pathsave+'n_graphs/untaggedgraph{0}.png'.format(q))
    # 1) find all dangling edges and mark them
    graphD = utilsF.dangling_edges(graph_s.copy())
    # 2) create line graph
    lgG = nx.line_graph(graph_s.copy())
    # 3) calculate the angles between two edges from the graph that is now represented by edges in the line graph
    lgG_V = utilsF.lG_edgeVal(lgG.copy(),graphD,posL)
    # 4) run depth first search
    graphTagg = utilsF.dfs_constrained(graph_s.copy(),lgG_V.copy(),imgBl,posL,angleA,overlap) 
    
    utilsF.draw_graph_filament_nocolor(imgP,graphTagg,posL,"",'filament')
    plt.savefig(os.path.join(pathsave, 'n_graphs', 'graph.png'))

    plt.close('all')
    print('filament defined: ',len(np.unique(np.asarray(list(graphTagg.edges(data='filament')))[:,2])))
    
    
    ###############################################################################
    #
    # data analysis - one frame at a time
    #
    ###############################################################################
    
    pd_fil_info = utilsF.filament_info(imgP, graphTagg, posL, pathsave,imF,maskDraw)
    
    
    pd_fil_info = pd.read_csv(os.path.join(pathsave, 'traced_filaments_info.csv'))
    
    mean_len = np.mean(pd_fil_info['filament length'])
    
    list_len = np.sort(pd_fil_info['filament length'])
    plt.figure()
    plt.scatter( np.arange(0,len(list_len)),list_len)
    
    
    mean_angle,var_val = utilsF.circ_stat(pd_fil_info,pathsave)
    
    print('mean angle: ', mean_angle, 'circ var: ', var_val, 'mean length: ', mean_len)
    
    return


"""
This module contains regression tests for the function `graft.main.create_all`.
"""

import os
import shutil
import pickle

import networkx as nx
import numpy as np
import skimage.io as io
import pytest

from graft.main import create_all
from tests import assert_csv_files_equal, compare_images


@pytest.fixture(scope="module")  # fixture to setup and teardown test env
def test_env():
    # get the path of the directory that contains this script
    test_dir = os.path.dirname(os.path.realpath(__file__))

    image_path = os.path.join(test_dir, "..", "graft", "tiff", "timeseries.tif")
    test_output_dir = os.path.join(test_dir, "..", "test_output", "create_all")
    expected_output_dir = os.path.join(test_dir, "expected_output", "create_all")

    os.makedirs(test_output_dir, exist_ok=True)

    img_o = io.imread(os.path.abspath(image_path))
    create_all(pathsave=os.path.abspath(test_output_dir),
               img_o=img_o,
               maskDraw = np.ones((img_o.shape[1:3])),
               size=6, eps=200, thresh_top=0.5, sigma=1.0, small=50.0,
               angleA=140, overlap=4, max_cost=100,
               name_cell='in silico time')

    # Provide the paths that the test_regression function needs.
    yield test_output_dir, expected_output_dir

    # Teardown test environment
    shutil.rmtree(test_output_dir)

def test_regression_csv_files(test_env):
    output_dir, expected_dir = test_env

    for csv_fname in ("tracked_filaments_info.csv", "value_per_frame.csv"):
        generated_file = os.path.join(output_dir, csv_fname)
        expected_file = os.path.join(expected_dir, csv_fname)
        assert_csv_files_equal(generated_file, expected_file)

def test_posL_pickle_file(test_env):
    output_dir, expected_dir = test_env

    fname = 'posL.gpickle'
    with open(os.path.join(output_dir, fname), 'rb') as f:
        generated_posL = pickle.load(f)
    with open(os.path.join(expected_dir, fname), 'rb') as f:
        expected_posL = pickle.load(f)

    assert len(generated_posL) == len(expected_posL), \
        "{fname}: number of frames does not match expected output."

    for frame_index, (generated_frame_pos, expected_frame_pos) in enumerate(zip(generated_posL, expected_posL)):
        assert np.array_equal(generated_frame_pos, expected_frame_pos), \
        f"Node positions don't match for frame {frame_index}."

def compare_edge_attributes(generated_edges, expected_edges):
    for ((key1, attr1), (key2, attr2)) in zip(generated_edges, expected_edges):
        assert key1 == key2, "Edge keys do not match."
        assert attr1 == attr2, "Edge attributes do not match for key {}".format(key1)

def test_tagged_graph_pickle_file(test_env):
    output_dir, expected_dir = test_env

    with open(os.path.join(output_dir, 'tagged_graph.gpickle'), 'rb') as f:
        generated_graphs = pickle.load(f)
    with open(os.path.join(expected_dir, 'tagged_graph.gpickle'), 'rb') as f:
        expected_graphs = pickle.load(f)

    assert len(generated_graphs) == len(expected_graphs), "Number of graphs does not match."

    for generated_graph, expected_graph in zip(generated_graphs, expected_graphs):
        assert set(generated_graph.nodes()) == set(expected_graph.nodes()), "Graph nodes do not match."
        assert nx.number_of_edges(generated_graph) == nx.number_of_edges(expected_graph), "Number of edges do not match."

        # Compare all edges and attributes for each pair of nodes
        for (u, v) in generated_graph.edges():
            generated_edges = sorted(generated_graph.get_edge_data(u, v).items(), key=lambda x: x[0])
            expected_edges = sorted(expected_graph.get_edge_data(u, v).items(), key=lambda x: x[0])

            assert len(generated_edges) == len(expected_edges), f"Edges between nodes {u} and {v} do not match in count."
            compare_edge_attributes(generated_edges, expected_edges)

def test_plot_images(test_env):
    """
    Test that all generated images are structurally similar to the
    expected output images.
    
    TODO / FIXME: replace this stopgap test with a real test that
    compares the underlying data structures instead of the generated images.
    """
    output_dir, expected_dir = test_env

    for plot_dir in ('circ_stat', 'mov', 'n_graphs', 'plots'):
        output_plot_dir = os.path.join(output_dir, plot_dir)
        expected_plot_dir = os.path.join(expected_dir, plot_dir)

        for plot_fname in os.listdir(expected_plot_dir):
            if plot_fname.endswith('.png'):
                generated_plot_path = os.path.join(output_plot_dir, plot_fname)
                expected_plot_path = os.path.join(expected_plot_dir, plot_fname)

                assert compare_images(generated_plot_path, expected_plot_path, method='ssim', tolerance=0.95),
                    f"{plot_fname} does not match the expected output."
