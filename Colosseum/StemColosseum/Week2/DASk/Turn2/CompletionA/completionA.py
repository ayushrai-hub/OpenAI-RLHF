# Step 1: Load all nodes from node files
all_inhibitor_ids = inhibitors_embeddings_ddf['Compound_ID'].compute().unique().tolist()
all_kinase_names = kinases_embeddings_ddf['Kinase_Name'].compute().unique().tolist()
all_phosphosite_ids = phosphosites_embeddings_ddf['Phosphosite_ID'].compute().unique().tolist()

# Step 2: Create node embeddings
for inhibitor_id in tqdm(all_inhibitor_ids, desc='Processing inhibitors'):
    x_inhibitor.append(aggregate_inhibitor_embeddings(inhibitor_id))
    inhibitor_node_map[inhibitor_id] = len(inhibitor_node_map)

for kinase_name in tqdm(all_kinase_names, desc='Processing kinases'):
    x_kinase.append(aggregate_kinase_embeddings(kinase_name))
    kinase_node_map[kinase_name] = len(kinase_node_map)

for phosphosite_id in tqdm(all_phosphosite_ids, desc='Processing phosphosites'):
    x_phosphosite.append(aggregate_phosphosite_embeddings(phosphosite_id))
    phosphosite_node_map[phosphosite_id] = len(phosphosite_node_map)

# Step 3: Process existing edges from edge files
# You may include the progress bar as shown before
with ProgressBar():
    inhibitors_kinases_ddf.map_partitions(lambda df: df.apply(process_inhibitor_kinase, axis=1)).compute()
    kinase_phosphosite_ddf.map_partitions(lambda df: df.apply(process_kinase_phosphosite, axis=1)).compute()
