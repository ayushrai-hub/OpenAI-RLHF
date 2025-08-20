# ideal_completion.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_swing_ratio(df):
    total_pitches = len(df)
    if total_pitches == 0:
        return 0  # Prevent division by zero
    swings = df['Call'].isin(['Foul', 'FoulNotPlayable', 'FoulPlayable', 'Hit', 'Missed']).sum()
    return (swings / total_pitches) * 100

def calculate_connection_ratio(df):
    total_swings = df['Call'].isin(['Foul', 'FoulNotPlayable', 'FoulPlayable', 'Hit', 'Missed']).sum()
    if total_swings == 0:
        return 0  # Return 0% if no swings occurred
    total_contacts = df['Call'].isin(['Hit', 'Foul', 'FoulPlayable', 'FoulNotPlayable']).sum()
    return (total_contacts / total_swings) * 100

def generate_table_images(metrics_df, output_directory):
    """Generate table images with input validation."""
    # Input validation
    if metrics_df.empty:
        raise ValueError("DataFrame cannot be empty")

    # Validate required columns
    required_columns = [
        'Player', 'Swing%', '1ST%', 'Contact%', 'Miss%', 
        'Zone Contact%', 'Outside Swing%', 'Max Speed', 
        '90th Percentile Speed', 'Average Speed', 
        'Average Launch Angle', 'PitchTypeMetrics'
    ]
    missing_columns = [col for col in required_columns if col not in metrics_df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Validate data types
    numeric_columns = [
        'Swing%', '1ST%', 'Contact%', 'Miss%', 
        'Zone Contact%', 'Outside Swing%', 'Max Speed', 
        '90th Percentile Speed', 'Average Speed', 
        'Average Launch Angle'
    ]
    for col in numeric_columns:
        if not pd.to_numeric(metrics_df[col], errors='coerce').notnull().all():
            raise ValueError(f"Column {col} contains non-numeric values")

    # Check for NaN/null values
    if metrics_df[numeric_columns].isnull().any().any():
        raise ValueError("DataFrame contains null values in numeric columns")

    # Check for infinite values
    if not metrics_df[numeric_columns].replace([np.inf, -np.inf], np.nan).notnull().all().all():
        raise ValueError("DataFrame contains infinite values")

    os.makedirs(output_directory, exist_ok=True)

    for _, row in metrics_df.iterrows():
        player = str(row['Player'])
        metrics_data = [
            ['Metric', 'Value'],
            ['Swing%', f'{row["Swing%"]:.1f}%'],
            ['1ST%', f'{row["1ST%"]:.1f}%'],
            ['Contact%', f'{row["Contact%"]:.1f}%'],
            ['Miss%', f'{row["Miss%"]:.1f}%'],
            ['Zone Contact%', f'{row["Zone Contact%"]:.1f}%'],
            ['Outside Swing%', f'{row["Outside Swing%"]:.1f}%'],
            ['Max Speed', f'{row["Max Speed"]:.1f}'],
            ['90th Percentile Speed', f'{row["90th Percentile Speed"]:.1f}'],
            ['Average Speed', f'{row["Average Speed"]:.1f}'],
            ['Average Launch Angle', f'{row["Average Launch Angle"]:.1f}']
        ]

        fig, axs = plt.subplots(2, 1, figsize=(6, 8))

        # Table for general statistics
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

        # Table for pitch type-specific statistics
        pitch_type_metrics = row['PitchTypeMetrics']
        if pitch_type_metrics:
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
                    for item in pitch_type_metrics
                ]
                axs[1].axis('tight')
                pitch_table = axs[1].table(
                    cellText=pitch_type_data,
                    colLabels=['Pitch Type', 'Swing%', 'Contact%', 'Miss%', 'Zone Contact%', 'Outside Swing%'],
                    loc='center',
                    cellLoc='center'
                )
                pitch_table.auto_set_font_size(False)
                pitch_table.set_fontsize(8)
                pitch_table.scale(1.0, 1.0)
            except (KeyError, TypeError) as e:
                raise KeyError(f"Invalid pitch type metrics format: {str(e)}")
        axs[1].axis('off')

        # Sanitize player name
        if not player or player.isspace():
            # For empty or whitespace-only names
            output_filename = 'table.png'
        else:
            # Remove special characters but keep alphanumeric and hyphens
            sanitized_player = ''.join(char for char in player if char.isalnum() or char == '-')
            # Truncate if too long
            if len(sanitized_player) > 50:
                sanitized_player = sanitized_player[:50]
            output_filename = f'{sanitized_player}.png'

        output_png_path = os.path.join(output_directory, output_filename)
        plt.savefig(output_png_path, bbox_inches='tight')
        plt.close()