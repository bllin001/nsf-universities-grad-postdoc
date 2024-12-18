import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

# Get all Excel files in the 'data' directory
file_paths = glob.glob("data/*.xlsx")

# Define the sheets and columns to plot (we'll refer to entries in the first column here)
sheets_to_plot = {
    "Earned Doctorates": ["Science", "Engineering", "Non-science and engineering"],
    "Graduate Students": ["Science", "Engineering", "Health"],
    "Source": ["Fellowships", "Research assistantships", "Teaching assistantships", "Other types of support", "Personal resources"],
    "Postdoctorates": ["Science", "Engineering", "Health"]
}

# Define custom y-axis labels for each sheet
y_axis_labels = {
    "Earned Doctorates": "Total of earned doctorates",
    "Graduate Students": "Total of full and part-time students",
    "Source": "Full-time grad students with federal support",
    "Postdoctorates": "Total of postdoctorates"
}

# Directory to save the plots
output_dir = 'pictures'
os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

# Set a consistent style for the plots
plt.style.use('ggplot')  # Use a built-in style

# Loop through each Excel file in the 'data' directory
for file_path in file_paths:
    # Extract the filename without extension and format the university name
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    university_name = file_name.replace('-', ' ')

    # Load the Excel file
    excel_data = pd.ExcelFile(file_path)

    # Loop through each sheet and specified entries in the first column
    for sheet_name, entries in sheets_to_plot.items():
        # Check if the sheet exists in the file
        if sheet_name in excel_data.sheet_names:
            # Load the data from the sheet, setting the first column as the index
            data = pd.read_excel(excel_data, sheet_name=sheet_name, index_col=0)

            # Transpose the data so that years are on the x-axis
            data = data.transpose()

            # Clean up column names in the DataFrame by stripping whitespace
            data.columns = data.columns.str.strip()

            # Filter only existing columns to avoid KeyError
            available_entries = [entry for entry in entries if entry in data.columns]
            if not available_entries:
                print(f"No matching columns found for '{sheet_name}' in '{file_name}'. Skipping plot.")
                continue

            # Filter the data to include only the specified existing entries
            data_to_plot = data[available_entries]

            # Create the plot with improved style
            plt.figure(figsize=(12, 8))  # Set a consistent figure size
            data_to_plot.plot(linewidth=2)  # Increase line width for better visibility
            plt.title(f"{university_name} - {sheet_name}", fontsize=16, fontweight='bold')
            plt.xlabel("Year", fontsize=12)

            # Set the custom y-axis label for each sheet
            y_label = y_axis_labels.get(sheet_name, "Values")
            plt.ylabel(y_label, fontsize=12)

            plt.xticks(fontsize=10)
            plt.yticks(fontsize=10)

            # Customize the legend to be on the right side, outside the plot area
            plt.legend(title="Categories", loc="center left", bbox_to_anchor=(1.05, 0.5), fontsize=10, title_fontsize=12, frameon=True, shadow=True)

            # Enable grid for better readability
            plt.grid(True, linestyle='--', linewidth=0.5)

            # Save the plot in the "pictures" directory with automated naming format
            output_filename = os.path.join(output_dir, f"{file_name}_{sheet_name.replace(' ', '-')}.png")
            plt.savefig(output_filename, dpi=300, bbox_inches='tight')  # Save with high resolution
            plt.close()
        else:
            print(f"Sheet '{sheet_name}' not found in file '{file_name}'.")