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

def configure_plotting():
    """Configure preferred plot formatting"""
    plt.rc('xtick', labelsize=24) 
    plt.rc('ytick', labelsize=24)
    plt.rc('axes', titlesize=26)     
    plt.rc('axes', labelsize=24) 

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

def save_unique_filaments_plot(g_tagged, img_o, pathsave):
    """Compute and plot unique filaments by frame"""
    if len(img_o.shape) != 3:
        raise Exception(f"save_unique_filaments must be called with a 3D img_o; got shape {img_o.shape}")
    
    unique_filaments = [0]*len(img_o)
    unique_frames = []
    
    for i in range(len(img_o)):
        unique_filaments[i] = len(np.unique(np.asarray(list(g_tagged[i].edges(data='tags')))[:,2]))
        unique_frames.extend(list(np.unique(np.asarray(list(g_tagged[i].edges(data='tags')))[:,2])))
    
    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,len(unique_filaments)),unique_filaments)
    plt.xlabel('frames')
    plt.ylabel('# filaments')
    plt.savefig(os.path.join(pathsave, 'plots', 'filaments_per_frame.png'))
    # FIXME - if unique_filaments or unique_frames are used later, return them.

def compute_filament_stats(pd_fil_info, frame_number=0):
    """ Compute filament statistics from pd_fil_info Dataframe. """
    dens = pd_fil_info[pd_fil_info['frame number']==frame_number]['filament density'].values[0]
    fil_len =np.median(pd_fil_info[pd_fil_info['frame number']==frame_number]['filament length'])
    fil_I = np.median(pd_fil_info[pd_fil_info['frame number']==frame_number]['filament intensity per length'])
    return dens, fil_len, fil_I

# FIXME - complete imlementation of survival filaments plot
def save_survival_filaments_plot(vals, pathsave):
    """ Plot and save survival filaments. """
    counts, bins = np.histogram(list(vals),20)
    plt.figure(figsize=(10,7))
    plt.hist(bins[:-1], bins, weights=counts, color='green')
    plt.xlabel('frames')
    plt.ylabel('filaments survival')
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments.png'))

# FIXME - complete imlementation of survival filaments normalized plot
def save_survival_filaments_normalized_plot(vals, pathsave):
    """ Plot and save normalized survival filaments. """
    counts, bins = np.histogram(list(vals),20,density='True')
    plt.figure(figsize=(10,7))
    plt.hist(bins[:-1], bins, weights=counts, color='green')
    plt.xlabel('frames')
    plt.ylabel('filaments survival')
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_filaments_normalized.png'))

def save_filament_density_plot(dens, pathsave, frame_count=1):
    """ Plot and save filament density by frame. """
    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,frame_count), dens)
    plt.xlabel('frames')
    plt.ylabel('filament density')
    plt.savefig(os.path.join(pathsave, 'plots', 'filament_density.png'))

def save_filament_median_length_plot(fil_len, pathsave, frame_count=1):
    """ Plot and save filament length by frame. """
    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,frame_count), fil_len)
    plt.xlabel('frames')
    plt.ylabel('filament median length')
    # FIXME - missing underscore?
    plt.savefig(os.path.join(pathsave, 'plots', 'filamentlength.png'))

def save_filament_circular_median_angle_plot(mean_angle, pathsave, frame_count=1):
    """ Plot and save filament circular mean angle. """
    line_mean = np.mean(mean_angle)
    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0,frame_count), mean_angle)
    plt.plot(np.arange(0,frame_count), np.ones(frame_count)*line_mean, color='black', linestyle='dashed')
    plt.xlabel('Frames')
    plt.ylabel('Circular mean angle')
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_mean.png'))

def save_filament_circular_angle_variance_plot(var_val, pathsave):
    """ Plot and save variance of filament circular mean angle. """
    plt.figure(figsize=(10,10))
    plt.scatter(np.arange(0, len(var_val)), var_val)
    plt.xlabel('frames')
    plt.ylabel('circular variance of angles')
    plt.savefig(os.path.join(pathsave, 'plots', 'angles_var.png'))

def save_survival_len_plot(pd_fil_info, pathsave):
    """ Plot and save survival len. """    
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
    plt.xlabel('Survival frames')
    plt.ylabel('filament length')
    plt.savefig(os.path.join(pathsave, 'plots', 'survival_len.png'))   

def save_graphTagg_plot(imgP, graphTagg, posL, pathsave, idx=0):
    """ Draw and save the tagged graph. """
    utilsF.draw_graph_filament_nocolor(imgP, graphTagg, posL, "", 'filament')
    graph_name = f'graph{idx}.png' if idx>=0 else 'graph.png'
    plt.savefig(os.path.join(pathsave, 'n_graphs', graph_name))
    plt.close()  

def create_graphTagg(imgP, size, eps, thresh_top, sigma, small, angleA, overlap, visualize=True):
    """Create and analyze the graph"""
    # 0) create graph
    graph_s, posL, imgSkel, imgAF, imgBl, imF, mask, df_pos = \
      utilsF.creategraph(imgP, size=size, eps=eps, thresh_top=thresh_top, sigma=sigma, small=small)
    # optionally visualize untagged graph
    if visualize:
      utilsF.draw_graph(imgSkel, graph_s, posL,"untagged graph")

    # 1) find all dangling edges and mark them
    graphD = utilsF.dangling_edges(graph_s.copy())
    # 2) create line graph
    lgG = nx.line_graph(graph_s.copy())
    # 3) calculate the angles between two edges from the graph that is now represented by edges in the line graph
    lgG_V = utilsF.lG_edgeVal(lgG.copy(),graphD,posL)
    # 4) run depth first search
    graphTagg = utilsF.dfs_constrained(
        graph_s.copy(), lgG_V.copy(), imgBl, posL, angleA, overlap) 
    
    # clean up after optional visualization
    if visualize:
      plt.close()

    no_filaments = len(np.unique(np.asarray(list(graphTagg.edges(data='filament')))[:,2]))
    print('filament defined: ',len(np.unique(np.asarray(list(graphTagg.edges(data='filament')))[:,2])))

    return graph_s, posL, imgSkel, imgAF, imgBl, imF, mask, df_pos, graphD, lgG, lgG_V, graphTagg, no_filaments    

def create_all(pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap, max_cost, name_cell):
    
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
        
        graph_s[q], posL[q], imgSkel[q], imgAF[q], imgBl[q], imF[q], mask[q], \
        df_pos[q], graphD[q], lgG[q], lgG_V[q], graphTagg[q], no_filaments[q] = \
          create_graphTagg(imgP[q], size, eps, thresh_top, sigma, small, angleA, overlap)
        
        save_graphTagg_plot(imgP[q], graphD[q], posL[q], pathsave, idx=q)
    
    # dump posL results to pickle
    pickle.dump(posL, open(os.path.join(pathsave, 'posL.gpickle'), 'wb'))
    ###############################################################################
    #
    # data
    # tracking 
    #
    ###############################################################################
    # if already saved this, then load in
    # g_tagged = nx.read_gpickle(pathsave+'tagged_graph.gpickle')
    # graphTagg = g_tagged.copy()
    if(len(img_o)<20):
        memKeep = len(img_o)
    else:
        memVal = 20
        memKeep = utilsF.signMem(graphTagg[0:memVal],posL[0:memVal])
    
    # first graph needs unique tags
    for node1, node2, property in graphTagg[0].edges(data=True):
        for n in range(len(graphTagg[0][node1][node2])):
            graphTagg[0][node1][node2][n]['tags'] = property['filament']
        
    # FIXME - remove unused code? (is this from debugging?)   
    list(graphTagg[0].edges(data='filament'))

    max_tag = np.max(list(graphTagg[0].edges(data='filament')),axis=0)[2] 
    
    g_tagged = [0]*(len(img_o))
    g_tagged[0] = graphTagg[0]
    cost = [0]*(len(img_o)-1)
    tag_new = [0]*(len(img_o))
    tag_new[0] = max_tag
    filamentsNU = []
    
    for i in range(len(img_o)-1):
        g_tagged[i+1],cost[i],tag_new[i+1],filamentsNU = \
          utilsF.filament_tag(
              g_tagged[i],graphTagg[i+1],posL[i],posL[i+1],tag_new[i],max_cost,filamentsNU,memKeep)
    
    # Save the updated tagged graph output as a pickle.
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
    configure_plotting()

    # NOTE - unique_filaments and unique_frames are not referenced later in the function
    # they can be returned from `save_unique_filaments` if necessary.
    save_unique_filaments_plot(g_tagged, img_o, pathsave)

    ###############################################################################
    #
    # data analysis - one frame at a time
    #
    ###############################################################################
    # FIXME - pick one or the other; or add a parameter to the function interface to choose
    pd_fil_info = utilsF.filament_info_time(imgP, g_tagged, posL, pathsave, imF, maskDraw)
    pd_fil_info = pd.read_csv(os.path.join(pathsave, 'tracked_filaments_info.csv'))

    vals = Counter(pd_fil_info['filament']).values()

    # FIXME - see notes on these functions; original implementations appeared incomplete
    save_survival_filaments_plot(vals, pathsave)
    save_survival_filaments_normalized_plot(vals, pathsave)
    
    dens = np.zeros(len(img_o))
    fil_len = np.zeros(len(img_o))
    fil_I = np.zeros(len(img_o))
    for i in range(len(img_o)):
        dens[i], fil_len[i], fil_I[i] = compute_filament_stats(pd_fil_info, frame_number=i)
    
    save_filament_density_plot(dens, pathsave, frame_count=len(img_o))
    save_filament_median_length_plot(fil_len, pathsave, frame_count=len(img_o))
    
    mean_angle, var_val = utilsF.circ_stat_plot(pathsave,pd_fil_info)

    save_filament_circular_median_angle_plot(mean_angle, pathsave, frame_count=len(mean_angle))
    save_filament_circular_angle_variance_plot(var_val, pathsave)

    save_survival_len_plot(pd_fil_info, pathsave)    
    
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
    # FIXME - type-o in mediam --> median
    df_angles2['filament mediam intensity per length'] = fil_I
    df_angles2['name'] = name_cell
    df_angles2.to_csv(os.path.join(pathsave, 'value_per_frame.csv'), index=False)
    
    return

# NOTE - unused argument name_cell was removed
def create_all_still(
        pathsave, img_o, maskDraw, size, eps, thresh_top, sigma, small, angleA, overlap):
  
    create_output_dirs(pathsave)    
    
    N,P = (img_o.shape)
    imgP=np.zeros((N+2,P+2))
    
    imgP = np.pad(img_o, 1, 'constant')

    _, posL, _, _, _, imF, _, _, graphD, _, _, graphTagg, _ = \
        create_graphTagg(imgP, size, eps, thresh_top, sigma, small, angleA, overlap, pathsave)
    save_graphTagg_plot(imgP, graphD, posL, pathsave, idx=-1) # don't include index in graph name
        
    ###############################################################################
    #
    # data analysis - one frame at a time
    #
    ###############################################################################

    # FIXME - pick one or the other; or add a parameter to the function interface to choose
    pd_fil_info = utilsF.filament_info(imgP, graphTagg, posL, pathsave, imF, maskDraw)
    pd_fil_info = pd.read_csv(os.path.join(pathsave, 'traced_filaments_info.csv'))
    
    # FIXME - this appears to be for debugging only (the plot is never saved; should it be?)
    mean_len = np.mean(pd_fil_info['filament length'])
    list_len = np.sort(pd_fil_info['filament length'])

    plt.figure()
    plt.scatter( np.arange(0,len(list_len)),list_len)
    
    mean_angle, var_val = utilsF.circ_stat(pd_fil_info,pathsave)
    print('mean angle: ', mean_angle, 'circ var: ', var_val, 'mean length: ', mean_len)
    return
