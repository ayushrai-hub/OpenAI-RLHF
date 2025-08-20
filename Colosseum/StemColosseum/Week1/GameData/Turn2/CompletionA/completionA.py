def display_data_insights(data_frame):
    print("Data Insights:")
    print("-" * 50)
    
    # Number of games
    print(f"Number of games: {data_frame.shape[0]}")
    
    # Unique years and gameweeks
    print(f"Unique years: {data_frame['year'].nunique()}")
    print(f"Unique gameweeks: {data_frame['gameweek'].nunique()}")
    
    # Number of unique squads
    print(f"Unique squads: {pd.concat([data_frame['squad1_name'], data_frame['squad2_name']]).nunique()}")
    
    # Event timeline
    print(f"Event timeline: {data_frame['event_date'].min()} to {data_frame['event_date'].max()}")

    # Max and min year+gameweek combinations
    print("\nYear-Gameweek summary:")
    print("-" * 50)
    
    # Group by year and gameweek
    grouped = data_frame.groupby(['year', 'gameweek'])

    # Get min and max for relevant columns
    agg_min = grouped[['squad1_final_points', 'squad2_final_points']].min().reset_index()
    agg_max = grouped[['squad1_final_points', 'squad2_final_points']].max().reset_index()

    print("Min aggregate for year-gameweek combination:")
    print(agg_min)

    print("\nMax aggregate for year-gameweek combination:")
    print(agg_max)

    # Display broad data summary
    print("\nBroad Summary:")
    print("-" * 50)
    print(data_frame.describe(include='all'))

    # Result summary
    print("\nResult Summary:")
    print("-" * 50)
    print(data_frame['result'].value_counts())
