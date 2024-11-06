import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

# Get all Excel files in the 'data' directory
file_paths = glob.glob("data/*.xlsx")

# Define the specific columns to plot for each sheet
sheets_to_plot = {
    "Earned Doctorates": ["All fields"],
    "Graduate Students": ["All students"],
    "Source": ["All types and sources of support"],
    "Postdoctorates": ["Science", "Engineering", "Health"]  # Sum these for total postdoctorates
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

# Loop through each sheet to generate combined plots
for sheet_name, columns in sheets_to_plot.items():
    plt.figure(figsize=(12, 8))  # Set a consistent figure size for each sheet
    for file_path in file_paths:
        # Extract the filename without extension and format the university name
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        university_name = file_name.replace('-', ' ')

        # Load the Excel file
        excel_data = pd.ExcelFile(file_path)

        # Check if the sheet exists in the file
        if sheet_name in excel_data.sheet_names:
            # Load the data from the sheet, setting the first column as the index
            data = pd.read_excel(excel_data, sheet_name=sheet_name, index_col=0)

            # Transpose the data so that years are on the x-axis
            data = data.transpose()

            # Clean up column names by stripping whitespace
            data.columns = data.columns.str.strip()

            # Prepare data to plot based on the specific column(s)
            if sheet_name == "Postdoctorates":
                # Sum columns for "Postdoctorates"
                if all(col in data.columns for col in columns):
                    data_to_plot = data[columns].sum(axis=1)
                    label = "Total postdoctorates"
                else:
                    print(f"Columns for total postdoctorates not found in '{file_name}'. Skipping.")
                    continue
            else:
                # Use specified column for other sheets
                if columns[0] in data.columns:
                    data_to_plot = data[columns[0]]
                    label = columns[0]
                else:
                    print(f"Column '{columns[0]}' not found in '{sheet_name}' for '{file_name}'. Skipping.")
                    continue

            # Plot each university with specified line style and transparency
            line_style = '-' if university_name == "Old Dominion U" else '--'
            opacity = 1.0 if university_name == "Old Dominion U" else 0.5
            data_to_plot.plot(
                label=university_name,
                linestyle=line_style,
                linewidth=2,
                alpha=opacity
            )

    # Set plot titles, labels, and legend
    plt.title(f"Global Comparison - {sheet_name}", fontsize=16, fontweight='bold')
    plt.xlabel("Year", fontsize=12)
    plt.ylabel(y_axis_labels.get(sheet_name, "Values"), fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    # Customize the legend to be on the right side, outside the plot area
    plt.legend(title="University", loc="center left", bbox_to_anchor=(1.05, 0.5), fontsize=10, title_fontsize=12, frameon=True, shadow=True)

    # Enable grid for better readability
    plt.grid(True, linestyle='--', linewidth=0.5)

    # Save the plot in the "pictures" directory with automated naming format
    output_filename = os.path.join(output_dir, f"Global-Comparison_{sheet_name.replace(' ', '_')}.png")
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')  # Save with high resolution
    plt.close()