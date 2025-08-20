import pandas as pd

def import_data(csv_path, min_gameweek, min_year, max_gameweek=0, max_year=0):
    # Import the data from the CSV file
    data_frame = pd.read_csv("/Users/ekanshgayakwad/OpenAi/StemColosseum/Task1/Turn1/CompletionA/sample_game_data.csv")

    # Implement the refining parameters
    data_frame_filtered = data_frame[
        (data_frame['gameweek'] >= min_gameweek) &
        (data_frame['year'] >= min_year) &
        (data_frame['game_is_done'] == 1) &
        ((data_frame['gameweek'] <= max_gameweek) & ((data_frame['year'] <= max_year) | (max_year == 0)) | (max_gameweek == 0)) &
        ((data_frame['year'] <= max_year) | (max_year == 0))
    ]

    return data_frame_filtered

def display_data_insights(data_frame):
    print("Data Insights:")
    print("-" * 50)
    print(f"Number of games: {data_frame.shape[0]}")
    print(f"Unique years: {data_frame['year'].nunique()}")
    print(f"Unique gameweeks: {data_frame['gameweek'].nunique()}")
    print(f"Unique squads: {pd.concat([data_frame['squad1_name'], data_frame['squad2_name']]).nunique()}")
    print(f"Event timeline: {data_frame['event_date'].min()} to {data_frame['event_date'].max()}")
    print("\nBroad Summary:")
    print("-" * 50)
    print(data_frame.describe(include='all'))
    print("\nResult Summary:")
    print("-" * 50)
    print(data_frame['result'].value_counts())

# Example usage
csv_path = 'your_data_file.csv'  # substitute with your actual CSV file path
min_gameweek = 1
min_year = 2022
max_gameweek = 10
max_year = 2022

# Import data
data_frame_filtered = import_data(csv_path, min_gameweek, min_year, max_gameweek, max_year)

# Display insights
display_data_insights(data_frame_filtered)
