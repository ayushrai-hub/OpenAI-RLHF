import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def calculate_swing_ratio(df):
    """Calculate the swing ratio from a DataFrame with a 'Call' column."""
    if df.empty:
        return 0.0
    
    swing_calls = {'Foul', 'FoulNotPlayable', 'FoulPlayable', 'Hit', 'Missed'}
    swings = df['Call'].isin(swing_calls).sum()
    return (swings / len(df)) * 100

def calculate_connection_ratio(df):
    """Calculate the connection ratio from a DataFrame with a 'Call' column."""
    swing_calls = {'Foul', 'FoulNotPlayable', 'FoulPlayable', 'Hit', 'Missed'}
    contact_calls = {'Hit', 'Foul', 'FoulPlayable', 'FoulNotPlayable'}
    
    total_swings = df['Call'].isin(swing_calls).sum()
    if total_swings == 0:
        return 0.0
    
    contacts = df['Call'].isin(contact_calls).sum()
    return (contacts / total_swings) * 100

def generate_table_images(metrics_df, output_directory):
    """Generate table images with input validation."""
    if metrics_df.empty:
        raise ValueError("DataFrame cannot be empty")

    required_columns = {
        'Player', 'Swing%', '1ST%', 'Contact%', 'Miss%', 
        'Zone Contact%', 'Outside Swing%', 'Max Speed', 
        '90th Percentile Speed', 'Average Speed', 
        'Average Launch Angle', 'PitchTypeMetrics'
    }
    
    missing_columns = required_columns - set(metrics_df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    numeric_columns = required_columns - {'Player', 'PitchTypeMetrics'}
    
    # Validate numeric columns
    for col in numeric_columns:
        if not pd.to_numeric(metrics_df[col], errors='coerce').notna().all():
            raise ValueError(f"Column {col} contains non-numeric values")

    # Create output directory
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    for _, row in metrics_df.iterrows():
        # Create table data
        metrics_data = [
            ['Metric', 'Value'],
            *[[col, f'{row[col]:.1f}{"%" if "%" in col else ""}'] 
              for col in numeric_columns]
        ]

        # Create figure and subplots
        fig, axs = plt.subplots(2, 1, figsize=(6, 8))

        # Main metrics table
        main_table = axs[0].table(
            cellText=metrics_data,
            cellLoc='center',
            loc='center',
            colWidths=[0.4, 0.6]
        )
        main_table.auto_set_font_size(False)
        main_table.set_fontsize(10)
        main_table.scale(1.2, 1.2)
        axs[0].axis('off')

        # Pitch type metrics table
        if row['PitchTypeMetrics']:
            try:
                pitch_type_data = [
                    [
                        item['Pitch Type'],
                        f"{item['Swing%']:.1f}%",
                        f"{item['Contact%']:.1f}%",
                        f"{item['Miss%']:.1f}%",
                        f"{item['Zone Contact%']:.1f}%",
                        f"{item['Outside Swing%']:.1f}%"
                    ]
                    for item in row['PitchTypeMetrics']
                ]
                
                pitch_table = axs[1].table(
                    cellText=pitch_type_data,
                    colLabels=['Pitch Type', 'Swing%', 'Contact%', 'Miss%', 
                              'Zone Contact%', 'Outside Swing%'],
                    loc='center',
                    cellLoc='center'
                )
                pitch_table.auto_set_font_size(False)
                pitch_table.set_fontsize(8)
                pitch_table.scale(1.0, 1.0)
            except (KeyError, TypeError) as e:
                raise ValueError(f"Invalid pitch type metrics format: {str(e)}")
        
        axs[1].axis('off')

        # Sanitize player name and save figure
        player_name = str(row['Player'])
        if not player_name or player_name.isspace():
            output_filename = 'table.png'
        else:
            sanitized_name = ''.join(c for c in player_name if c.isalnum() or c == '-')
            output_filename = f'{sanitized_name}.png'

        output_path = output_directory / output_filename
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()