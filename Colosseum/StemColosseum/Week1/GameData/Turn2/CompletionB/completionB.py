import pandas as pd

def import_data(csv_path, min_gameweek, min_year, max_gameweek=0, max_year=0):
    # Import data from the CSV file
    data_frame = pd.read_csv("/Users/ekanshgayakwad/OpenAi/StemColosseum/Task1/Turn1/CompletionB1.py/sample_game_data.csv")

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
    
    # Aggregate on year and gameweek
    print("\nYear-Gameweek Aggregations:")
    print("-" * 50)
    # Group the data by 'year' and 'gameweek'
    grouped = data_frame.groupby(['year', 'gameweek'])
    # Compute desired aggregates
    aggregated = grouped.agg({
        'game_code': 'count',
        'squad1_goal_stats_net': 'sum',
        'squad2_goal_stats_net': 'sum'
    }).rename(columns={'game_code': 'num_games'})
    
    # Calculate total goals per group
    aggregated['total_goals'] = aggregated['squad1_goal_stats_net'] + aggregated['squad2_goal_stats_net']
    
    # Find max and min total goals
    max_total_goals = aggregated['total_goals'].max()
    min_total_goals = aggregated['total_goals'].min()
    
    max_goals_combinations = aggregated[aggregated['total_goals'] == max_total_goals].index.tolist()
    min_goals_combinations = aggregated[aggregated['total_goals'] == min_total_goals].index.tolist()
    
    print("\nYear-Gameweek with Maximum Total Goals:")
    for combo in max_goals_combinations:
        print(f"Year: {combo[0]}, Gameweek: {combo[1]}, Total Goals: {max_total_goals}")
    
    print("\nYear-Gameweek with Minimum Total Goals:")
    for combo in min_goals_combinations:
        print(f"Year: {combo[0]}, Gameweek: {combo[1]}, Total Goals: {min_total_goals}")

# Example usage
csv_path = 'your_data_file.csv'  # Replace with your actual CSV file path
min_gameweek = 1
min_year = 2022
max_gameweek = 10
max_year = 2022

# Import data
data_frame_filtered = import_data(csv_path, min_gameweek, min_year, max_gameweek, max_year)

# Display insights
display_data_insights(data_frame_filtered)
