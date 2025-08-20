import dask.dataframe as dd
import numpy as np
import torch
from torch_geometric.data import Data
from tqdm import tqdm
import ast
from dask.distributed import Client
from dask.diagnostics import ProgressBar

def main():
    # Initialize Dask client to fully utilize CPU and memory
    client = Client(n_workers=5, threads_per_worker=1, memory_limit='18GB')

    # Define default embeddings for missing data
    default_inhibitor_embedding = np.zeros(2048 + 17)
    default_kinase_embedding = np.zeros(200 + 2)
    default_phosphosite_embedding = np.zeros(200 + 4)

    # Default edge embeddings
    default_ik_edge_embedding = np.zeros(2)
    default_kp_edge_embedding = np.zeros(4)

    # File paths
    inhibitor_kinase_file = '/Users/jdoe/Documents/New_Project/inhibitors_kinases_edge_table_normalized.csv'
    kinase_phosphosite_file = '/Users/jdoe/Documents/New_Project/normalized_kinase_phosphosite_edge_table.csv'
    kinase_embeddings_file = '/Users/jdoe/Documents/New_Project/kinases_with_embeddings.csv'
    phosphosite_embeddings_file = '/Users/jdoe/Documents/New_Project/human_phosphosites_with_embeddings.csv'
    inhibitor_embeddings_file = '/Users/jdoe/Documents/New_Project/inhibitors_node_embeddings_with_fingerprints.csv'

    # Load the data files with specified dtypes using Dask and persist them in memory
    inhibitors_kinases_ddf = dd.read_csv(inhibitor_kinase_file, dtype={
        'Compound_ID': 'object',
        'Kinase_Name': 'object',
        'Compound_CAS#': 'object',
        'Inhibition (%)': 'float64',
        'Log_Concentration': 'float64'
    }).persist()

    kinase_phosphosite_ddf = dd.read_csv(kinase_phosphosite_file, dtype={
        'Phosphosite_ID': 'object',
        'Kinase_Name': 'object',
        'percentile': 'float64',
        'rank': 'float64',
        'SIDIC': 'float64',
        'PTMscore (P > 075)': 'float64'
    }).persist()

    kinases_embeddings_ddf = dd.read_csv(kinase_embeddings_file, dtype={
        'Kinase_Name': 'object',
        'Uniprot_ID': 'object',
        'Sequence_Embedding': 'object',
        'Active_Site_Embedding': 'object',
        'Normalized_Length': 'float64',
        'Normalized_Mass': 'float64'
    }).persist()

    phosphosites_embeddings_ddf = dd.read_csv(phosphosite_embeddings_file, dtype={
        'Phosphosite_ID': 'object',
        'SITE_+/-7_AA_Embedding': 'object',
        'Sequence_Embedding': 'object',
        'median_percentile_embedding': 'float64',
        'promiscuity_index_embedding': 'float64',
        'Length_embedding': 'float64',
        'Mass_embedding': 'float64'
    }).persist()

    inhibitors_embeddings_ddf = dd.read_csv(inhibitor_embeddings_file, dtype={
        'Compound_ID': 'object',
        'compound_CAS#': 'object',
        'structure_embeddings': 'object',
        'Molecular_Weight_embedding': 'float64',
        'Number_of_Atoms_embedding': 'float64',
        'Number_of_Rings_embedding': 'float64',
        'Number_of_Rotatable_Bonds_embedding': 'float64',
        'Number_of_H-Bond_Donors_embedding': 'float64',
        'Number_of_H-Bond_Acceptors_embedding': 'float64',
        'Topological_Polar_Surface_Area_embedding': 'float64',
        'Balaban_Index_embedding': 'float64',
        'LogP_embedding': 'float64',
        'Molar_Refractivity_embedding': 'float64',
        'Number_of_Aromatic_Rings_embedding': 'float64',
        'Number_of_Aromatic_Heterocycles_embedding': 'float64',
        'Number_of_Aromatic_Carbo-cycles_embedding': 'float64',
        'Number_of_Aliphatic_Rings_embedding': 'float64',
        'Number_of_Saturated_Rings_embedding': 'float64',
        'Number_of_Saturated_Heterocycles_embedding': 'float64',
        'Number_of_Saturated_Carbocycles_embedding': 'float64'
    }).persist()

    # Convert Dask dataframes to Pandas for full dataset processing
    inhibitors_kinases_df = inhibitors_kinases_ddf.compute()
    kinase_phosphosite_df = kinase_phosphosite_ddf.compute()
    kinases_embeddings_df = kinases_embeddings_ddf.compute()
    phosphosites_embeddings_df = phosphosites_embeddings_ddf.compute()
    inhibitors_embeddings_df = inhibitors_embeddings_ddf.compute()

    # Extract unique lists of inhibitors, kinases, and phosphosites from their embedding files
    all_inhibitors = inhibitors_embeddings_df['Compound_ID'].unique().tolist()
    all_kinases = kinases_embeddings_df['Kinase_Name'].unique().tolist()
    all_phosphosites = phosphosites_embeddings_df['Phosphosite_ID'].unique().tolist()

    # Convert edge dataframes to dictionaries keyed by edge to quickly access attributes
    inhibitor_kinase_edges = {
        (row['Compound_ID'], row['Kinase_Name']): (row['Inhibition (%)'], row['Log_Concentration'])
        for _, row in inhibitors_kinases_df.iterrows()
    }
    kinase_phosphosite_edges = {
        (row['Kinase_Name'], row['Phosphosite_ID']): (row['percentile'], row['rank'], row['SIDIC'], row['PTMscore (P > 075)'])
        for _, row in kinase_phosphosite_df.iterrows()
    }

    # Helper function to handle NaN values in embeddings
    def handle_nan_values(embedding, default_embedding=None):
        if default_embedding is None:
            default_embedding = np.zeros_like(embedding)
        return np.nan_to_num(embedding, nan=0.0)

    # Aggregating functions with NaN handling
    def aggregate_inhibitor_embeddings(compound_id):
        try:
            row = inhibitors_embeddings_df[inhibitors_embeddings_df['Compound_ID'] == compound_id]
            if row.empty:
                return default_inhibitor_embedding
            row = row.iloc[0]
            structure_embeddings = handle_nan_values(
                np.array(ast.literal_eval(row['structure_embeddings']), dtype=float),
                default_inhibitor_embedding[:2048]
            )
            scalar_embeddings = handle_nan_values(
                row[['Molecular_Weight_embedding', 'Number_of_Atoms_embedding', 'Number_of_Rings_embedding',
                    'Number_of_Rotatable_Bonds_embedding', 'Number_of_H-Bond_Donors_embedding',
                    'Number_of_H-Bond_Acceptors_embedding', 'Topological_Polar_Surface_Area_embedding',
                    'Balaban_Index_embedding', 'LogP_embedding', 'Molar_Refractivity_embedding',
                    'Number_of_Aromatic_Rings_embedding', 'Number_of_Aromatic_Heterocycles_embedding',
                    'Number_of_Aromatic_Carbo-cycles_embedding', 'Number_of_Aliphatic_Rings_embedding',
                    'Number_of_Saturated_Rings_embedding', 'Number_of_Saturated_Heterocycles_embedding',
                    'Number_of_Saturated_Carbocycles_embedding']].values.flatten()
            )
            return np.concatenate([structure_embeddings, scalar_embeddings])
        except (IndexError, KeyError, ValueError) as e:
            print(f"Error processing inhibitor {compound_id}: {e}")
            return default_inhibitor_embedding

    def aggregate_kinase_embeddings(kinase_name):
        try:
            row = kinases_embeddings_df[kinases_embeddings_df['Kinase_Name'] == kinase_name]
            if row.empty:
                return default_kinase_embedding
            row = row.iloc[0]
            sequence_embeddings = handle_nan_values(
                np.array(ast.literal_eval(row['Sequence_Embedding']), dtype=float),
                default_kinase_embedding[:100]
            )
            active_site_embeddings = handle_nan_values(
                np.array(ast.literal_eval(row['Active_Site_Embedding']), dtype=float),
                default_kinase_embedding[100:200]
            )
            scalar_embeddings = handle_nan_values(
                row[['Normalized_Length', 'Normalized_Mass']].values.flatten()
            )
            return np.concatenate([sequence_embeddings, active_site_embeddings, scalar_embeddings])
        except (IndexError, KeyError, ValueError) as e:
            print(f"Error processing kinase {kinase_name}: {e}")
            return default_kinase_embedding

    def aggregate_phosphosite_embeddings(phosphosite_id):
        try:
            row = phosphosites_embeddings_df[phosphosites_embeddings_df['Phosphosite_ID'] == phosphosite_id]
            if row.empty:
                return default_phosphosite_embedding
            row = row.iloc[0]
            site_embedding = handle_nan_values(
                np.array(ast.literal_eval(row['SITE_+/-7_AA_Embedding']), dtype=float),
                default_phosphosite_embedding[:100]
            )
            sequence_embedding = handle_nan_values(
                np.array(ast.literal_eval(row['Sequence_Embedding']), dtype=float),
                default_phosphosite_embedding[100:200]
            )
            scalar_embeddings = handle_nan_values(
                row[['median_percentile_embedding', 'promiscuity_index_embedding', 'Length_embedding', 'Mass_embedding']].values.flatten()
            )
            return np.concatenate([site_embedding, sequence_embedding, scalar_embeddings])
        except (IndexError, KeyError, ValueError) as e:
            print(f"Error processing phosphosite {phosphosite_id}: {e}")
            return default_phosphosite_embedding

    # Initialize the placeholders for node/edge data
    node_inhibitor_embeddings = []
    node_kinase_embeddings = []
    node_phosphosite_embeddings = []
    edge_index_ik = []
    edge_attr_ik = []
    edge_index_kp = []
    edge_attr_kp = []

    # Node dictionaries to map nodes to indices
    inhibitor_node_map = {}
    kinase_node_map = {}
    phosphosite_node_map = {}

    # Add all inhibitors with their embeddings (ensuring each inhibitor node is created)
    for inhibitor_id in tqdm(all_inhibitors, desc="Processing Inhibitor Nodes"):
        node_inhibitor_embeddings.append(aggregate_inhibitor_embeddings(inhibitor_id))
        inhibitor_node_map[inhibitor_id] = len(inhibitor_node_map)

    # Add all kinases with their embeddings (ensuring each kinase node is created)
    for kinase_id in tqdm(all_kinases, desc="Processing Kinase Nodes"):
        node_kinase_embeddings.append(aggregate_kinase_embeddings(kinase_id))
        kinase_node_map[kinase_id] = len(kinase_node_map)

    # Add all phosphosites with their embeddings (ensuring each phosphosite node is created)
    for phosphosite_id in tqdm(all_phosphosites, desc="Processing Phosphosite Nodes"):
        node_phosphosite_embeddings.append(aggregate_phosphosite_embeddings(phosphosite_id))
        phosphosite_node_map[phosphosite_id] = len(phosphosite_node_map)

    # Ensure all possible edges are covered:
    # 1. Inhibitor-Kinase edges
    for inhibitor_id in tqdm(all_inhibitors, desc="Creating Inhibitor-Kinase Edges"):
        for kinase_id in all_kinases:
            if (inhibitor_id, kinase_id) in inhibitor_kinase_edges:
                # Use existing edge attributes
                inhibition, log_concentration = inhibitor_kinase_edges[(inhibitor_id, kinase_id)]
                edge_attr_ik.append(handle_nan_values(
                    np.array([inhibition, log_concentration], dtype=float),
                    default_ik_edge_embedding
                ))
            else:
                # Use default edge attributes
                edge_attr_ik.append(default_ik_edge_embedding)
            edge_index_ik.append([inhibitor_node_map[inhibitor_id], kinase_node_map[kinase_id]])

    # 2. Kinase-Phosphosite edges
    for kinase_id in tqdm(all_kinases, desc="Creating Kinase-Phosphosite Edges"):
        for phosphosite_id in all_phosphosites:
            if (kinase_id, phosphosite_id) in kinase_phosphosite_edges:
                # Use existing edge attributes
                percentile, rank, SIDIC, PTMscore = kinase_phosphosite_edges[(kinase_id, phosphosite_id)]
                edge_attr_kp.append(handle_nan_values(
                    np.array([percentile, rank, SIDIC, PTMscore], dtype=float),
                    default_kp_edge_embedding
                ))
            else:
                # Use default edge attributes
                edge_attr_kp.append(default_kp_edge_embedding)
            edge_index_kp.append([kinase_node_map[kinase_id], phosphosite_node_map[phosphosite_id]])

    # Convert lists to numpy arrays first, then to tensors
    edge_attr_ik = torch.tensor(np.array(edge_attr_ik, dtype=np.float32))
    edge_attr_kp = torch.tensor(np.array(edge_attr_kp, dtype=np.float32))

    edge_index_ik = torch.tensor(np.array(edge_index_ik, dtype=np.int64)).t().contiguous()
    edge_index_kp = torch.tensor(np.array(edge_index_kp, dtype=np.int64)).t().contiguous()

    x_inhibitor = torch.tensor(np.array(node_inhibitor_embeddings), dtype=torch.float32)
    x_kinase = torch.tensor(np.array(node_kinase_embeddings), dtype=torch.float32)
    x_phosphosite = torch.tensor(np.array(node_phosphosite_embeddings), dtype=torch.float32)

    # Create PyTorch Geometric Data object with separate edge attributes
    data = Data()
    data.edge_index_ik = edge_index_ik
    data.edge_attr_ik = edge_attr_ik
    data.edge_index_kp = edge_index_kp
    data.edge_attr_kp = edge_attr_kp
    data.x_inhibitor = x_inhibitor
    data.x_kinase = x_kinase
    data.x_phosphosite = x_phosphosite

    # Save the data
    torch.save(data, '/Users/jdoe/Documents/New_Project/kinase_phosphosite_inhibitor_graph.pt')
    print(f"Graph saved to '/Users/jdoe/Documents/New_Project/kinase_phosphosite_inhibitor_graph.pt'")
    print(f"Number of inhibitor nodes: {len(inhibitor_node_map)}")
    print(f"Number of kinase nodes: {len(kinase_node_map)}")
    print(f"Number of phosphosite nodes: {len(phosphosite_node_map)}")
    print(f"Number of inhibitor-kinase edges: {edge_index_ik.shape[1]}")
    print(f"Number of kinase-phosphosite edges: {edge_index_kp.shape[1]}")

if __name__ == "__main__":
    main()
