# ideal_completion.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import unicodedata
import numpy as np
from matplotlib.table import Table

def validate_numeric_columns(df, numeric_columns):
    """Validate numeric columns in DataFrame"""
    for col in numeric_columns:
        if col not in df.columns:
            return False
        if not pd.to_numeric(df[col], errors='coerce').notnull().all():
            raise ValueError(f"Column {col} contains non-numeric or null values")
    return True

def validate_pitch_metrics(metrics):
    """Validate PitchTypeMetrics format"""
    if not isinstance(metrics, list):
        raise TypeError("PitchTypeMetrics must be a list")
    
    if not metrics:  # Empty list is valid
        return True
        
    required_keys = {'Pitch Type', 'Swing%', 'Contact%', 'Miss%', 'Zone Contact%', 'Outside Swing%'}
    for item in metrics:
        if not isinstance(item, dict):
            raise TypeError("Each PitchTypeMetrics item must be a dictionary")
        if set(item.keys()) != required_keys:
            raise ValueError(f"Invalid keys in PitchTypeMetrics. Required: {required_keys}")
        if not isinstance(item['Pitch Type'], str):
            raise TypeError("Pitch Type must be a string")
        for key in required_keys - {'Pitch Type'}:
            if not isinstance(item[key], (int, float)):
                raise TypeError(f"{key} must be numeric")

def check_disk_space(directory):
    """Check if there's enough disk space"""
    try:
        statvfs = os.statvfs(directory)
        free_space = statvfs.f_frsize * statvfs.f_bfree
        if free_space < 1024 * 1024:  # Less than 1MB
            raise OSError("Insufficient disk space")
    except (AttributeError, OSError):
        # Handle both Windows systems and permission issues
        pass

def calculate_swing_ratio(df):
    """Calculate swing ratio from DataFrame"""
    valid_calls = {'Foul', 'FoulNotPlayable', 'FoulPlayable', 'Hit', 'Missed', 
                  'BallCalled', 'StrikeCalled'}
    
    if not all(call in valid_calls for call in df['Call'].unique()):
        raise ValueError(f"Invalid call types found. Valid types are: {valid_calls}")
    
    total_pitches = len(df)
    if total_pitches == 0:
        return 0.0
        
    swings = df['Call'].isin(['Foul', 'FoulNotPlayable', 'FoulPlayable', 'Hit', 'Missed']).sum()
    return (swings / total_pitches) * 100

def calculate_connection_ratio(df):
    """Calculate connection ratio from DataFrame"""
    valid_calls = {'Foul', 'FoulNotPlayable', 'FoulPlayable', 'Hit', 'Missed', 
                  'BallCalled', 'StrikeCalled'}
    
    if not all(call in valid_calls for call in df['Call'].unique()):
        raise ValueError(f"Invalid call types found. Valid types are: {valid_calls}")
    
    total_swings = df['Call'].isin(['Foul', 'FoulNotPlayable', 'FoulPlayable', 'Hit', 'Missed']).sum()
    if total_swings == 0:
        return 0.0
        
    total_contacts = df['Call'].isin(['Hit', 'Foul', 'FoulPlayable', 'FoulNotPlayable']).sum()
    return (total_contacts / total_swings) * 100

def generate_table_images(metrics_df, output_directory):
    """Generate table images for player metrics"""
    required_columns = {
        'Player', 'Swing%', '1ST%', 'Contact%', 'Miss%', 'Zone Contact%',
        'Outside Swing%', 'Max Speed', '90th Percentile Speed',
        'Average Speed', 'Average Launch Angle', 'PitchTypeMetrics'
    }
    
    # Validate DataFrame
    if not set(metrics_df.columns).issuperset(required_columns):
        missing = required_columns - set(metrics_df.columns)
        raise KeyError(f"Missing required columns: {missing}")

    # Validate numeric columns
    numeric_columns = required_columns - {'Player', 'PitchTypeMetrics'}
    if not validate_numeric_columns(metrics_df, numeric_columns):
        raise ValueError("Invalid numeric columns")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for _, row in metrics_df.iterrows():
        try:
            validate_pitch_metrics(row['PitchTypeMetrics'])
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid PitchTypeMetrics for player {row['Player']}: {str(e)}")

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8))
        
        # Create main metrics table
        metrics_data = [
            ['Metric', 'Value'],
            ['Swing%', f'{float(row["Swing%"]):.1f}%'],
            ['1ST%', f'{float(row["1ST%"]):.1f}%'],
            ['Contact%', f'{float(row["Contact%"]):.1f}%'],
            ['Miss%', f'{float(row["Miss%"]):.1f}%'],
            ['Zone Contact%', f'{float(row["Zone Contact%"]):.1f}%'],
            ['Outside Swing%', f'{float(row["Outside Swing%"]):.1f}%'],
            ['Max Speed', f'{float(row["Max Speed"]):.1f}'],
            ['90th Percentile Speed', f'{float(row["90th Percentile Speed"]):.1f}'],
            ['Average Speed', f'{float(row["Average Speed"]):.1f}'],
            ['Average Launch Angle', f'{float(row["Average Launch Angle"]):.1f}']
        ]

        table1 = ax1.table(cellText=metrics_data, cellLoc='center', loc='center')
        table1.auto_set_font_size(False)
        table1.set_fontsize(10)
        table1.scale(1.2, 1.2)
        ax1.axis('off')

        # Create pitch type metrics table if data exists
        if row['PitchTypeMetrics']:
            headers = ['Pitch Type', 'Swing%', 'Contact%', 'Miss%', 
                      'Zone Contact%', 'Outside Swing%']
            
            pitch_data = [
                [item['Pitch Type']] + [f"{item[h]}%" if h.endswith('%') else str(item[h])
                                      for h in headers[1:]]
                for item in row['PitchTypeMetrics']
            ]
            
            table2 = ax2.table(cellText=pitch_data, 
                             colLabels=headers,
                             cellLoc='center', 
                             loc='center')
            table2.auto_set_font_size(False)
            table2.set_fontsize(8)
            table2.scale(1.0, 1.0)
        ax2.axis('off')

        # Save figure
        output_file = os.path.join(output_directory, 
                                 f"{row['Player'].replace(' ', '').replace('_', '')}table.png")
        plt.savefig(output_file, bbox_inches='tight', dpi=300)
        plt.close(fig)