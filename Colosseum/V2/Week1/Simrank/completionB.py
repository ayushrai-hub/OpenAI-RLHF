def normalized_simrank(graph, C=0.8, iterations=10):
    # Implement standard SimRank
    sim = standard_simrank(graph, C, iterations)
    
    # Find max SimRank score (excluding self-similarities)
    max_sim = max(sim[a][b] for a in graph.nodes for b in graph.nodes if a != b)
    
    # Normalize
    normalized_sim = {a: {b: (sim[a][b] / max_sim if a != b else 1) 
                          for b in graph.nodes} 
                      for a in graph.nodes}
    
    return normalized_sim
