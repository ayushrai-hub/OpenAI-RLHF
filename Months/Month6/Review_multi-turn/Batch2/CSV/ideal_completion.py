import csv
import os

def drop_column_from_csv(input_file_name: str, output_file_name: str, column_to_drop: str) -> None:
    # Read the CSV from input_file_name
    # Determine the index of the column to drop from the header
    # Write the rest to output_file_name
    with open(input_file_name, newline='') as infile:
        reader = csv.reader(infile)
        rows = list(reader)
    if not rows:
        # write empty output 
        with open(output_file_name, mode='w', newline='') as outfile:
            pass
        return
    header = rows[0]
    try:
        drop_index = header.index(column_to_drop)
    except ValueError:
        # If the column isn't found, just copy original file
        with open(output_file_name, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(rows)
        return
    # Compose filtered rows
    filtered_rows = []
    for row in rows:
        # If row is shorter than drop_index, skip removal
        if drop_index < len(row):
            new_row = row[:drop_index] + row[drop_index+1:]
        else:
            new_row = row
        filtered_rows.append(new_row)
    # Write out
    with open(output_file_name, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(filtered_rows)
