import pandas as pd
import glob
import os

# Get all Excel files in the 'data' directory
file_paths = glob.glob("data/*.xlsx")

# Process each file
for file_path in file_paths:
    try:
        # Load the two sheets from each Excel file
        part_time_df = pd.read_excel(file_path, sheet_name="Part-time Graduate Students")
        full_time_df = pd.read_excel(file_path, sheet_name="Full-time Graduate Students")

        # Sum up the two dataframes
        combined_df = part_time_df.add(full_time_df, fill_value=0)

        # Write the combined dataframe to a new sheet in the same Excel file
        with pd.ExcelWriter(file_path, mode="a", engine="openpyxl") as writer:
            combined_df.to_excel(writer, sheet_name="Graduate Students", index=False)
        
        print(f"Processed and saved 'Graduate Students' sheet in {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")