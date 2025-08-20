import csv
import os

def drop_column_from_csv(input_file: str, output_file: str, column_to_delete: str):
    if os.path.getsize(input_file) == 0:
        open(output_file, 'w', encoding='utf-8').close()
        return

    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        try:
            header = next(reader)
        except StopIteration:
            return

        if column_to_delete in header:
            index_to_remove = header.index(column_to_delete)
            header.pop(index_to_remove)
            writer.writerow(header)
            
            for row in reader:
                row.pop(index_to_remove)
                writer.writerow(row)
        else:
            writer.writerow(header)
            for row in reader:
                writer.writerow(row)
