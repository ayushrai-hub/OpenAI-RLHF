import pandas as pd

def import_data(csv_path, min_gameweek, min_year, max_gameweek=0, max_year=0):
    # Import data from the CSV file
    data_frame = pd.read_csv("/Users/ekanshgayakwad/OpenAi/StemColosseum/Task1/Turn1/CompletionA/sample_game_data.csv")

    # Implement the refining conditions
    data_frame_filtered = data_frame[
        (data_frame['gameweek'] >= min_gameweek) &
        (data_frame['year'] >= min_year) &
        (data_frame['game_is_done'] == 1) &
        (
            ((data_frame['gameweek'] <= max_gameweek) & ((data_frame['year'] <= max_year) | (max_year == 0))) |
            (max_gameweek == 0)
        ) &
        ((data_frame['year'] <= max_year) | (max_year == 0))
    ]

    return data_frame_filtered

# Example usage
csv_path = 'your_data_file.csv'  # swap with your true CSV file path
min_gameweek = 1
min_year = 2022
max_gameweek = 10
max_year = 2022

# Import data
data_frame_filtered = import_data(csv_path, min_gameweek, min_year, max_gameweek, max_year)

# You can continue to use the display_data_insights function as previously to retrieve insights
