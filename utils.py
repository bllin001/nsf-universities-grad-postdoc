import streamlit as st
import glob
import os
import pandas as pd
import plotly.express as px

# Adjusted function with checks for 'Category'
@st.cache_data
def load_and_concatenate_data(sheet_name):
    all_data = []
    file_paths = glob.glob("data/*.xlsx")
    for file in file_paths:
        try:
            data = pd.read_excel(file, sheet_name=sheet_name, dtype=str)
            if data.empty:
                continue

            # Ensure the first column is renamed to 'Category'
            data.rename(columns={data.columns[0]: 'Category'}, inplace=True)

            # Check if 'Category' column exists after renaming
            if 'Category' not in data.columns:
                print(f"'Category' column is missing in {file} after renaming.")
                continue

            data['Category'] = data['Category'].fillna(method='ffill')
            data = data.dropna(subset=data.columns.difference(['Category']), how='all')
            value_vars = [col for col in data.columns if col != 'Category']
            data = data.melt(id_vars=['Category'], value_vars=value_vars, var_name='Year', value_name='Value')
            data['Year'] = data['Year'].astype(str)
            data['Value'] = pd.to_numeric(data['Value'].str.replace(',', ''), errors='coerce')
            university_name = os.path.splitext(os.path.basename(file))[0].replace("-", " ").strip().lower()
            data['University'] = university_name

            all_data.append(data)
        except Exception as e:
            print(f"Failed to process {file}: {e}")

    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# Function to build hierarchy with initial data check
def build_hierarchy_by_positions(data, macro_categories):
    if 'Category' not in data.columns:
        print("Error: 'Category' column not found in data passed to hierarchy builder.")
        return {}

    unique_categories_in_order = data['Category'].drop_duplicates().tolist()
    hierarchy = {}
    macro_indices = [unique_categories_in_order.index(macro) for macro in macro_categories if macro in unique_categories_in_order]
    macro_indices.append(len(unique_categories_in_order))

    for idx in range(len(macro_indices) - 1):
        macro_idx = macro_indices[idx]
        next_macro_idx = macro_indices[idx + 1]
        hierarchy[unique_categories_in_order[macro_idx]] = unique_categories_in_order[macro_idx + 1:next_macro_idx]

    return hierarchy

def plot_macro_level(selected_macro_category, data, y_label):
    filtered_data = data[data['Category'] == selected_macro_category].sort_values(by='Year')
    if filtered_data.empty:
        st.write(f"No data available for the category '{selected_macro_category}'.")
        return

    # Normalize university names for display
    filtered_data['University_Display'] = filtered_data['University'].apply(lambda x: x.title())

    # Ensure Old Dominion U is always included and cannot be removed
    odu_display_name = "Old Dominion U"  # Adjust if the display name differs
    available_universities = filtered_data['University_Display'].unique().tolist()
    if odu_display_name in available_universities:
        available_universities.remove(odu_display_name)

    # Multiselect option for universities with ODU always included
    selected_universities = st.multiselect(
        "Select universities to visualize (ODU is always included):",
        options=available_universities,
        default=available_universities  # Default to all universities except ODU
    )

    # Add ODU back to the list to ensure it's always plotted
    selected_universities.append(odu_display_name)

    # Button to reset and show all universities
    if st.button("Show All Universities"):
        selected_universities = available_universities + [odu_display_name]

    # Filter data based on selected universities
    if selected_universities:
        filtered_data = filtered_data[filtered_data['University_Display'].isin(selected_universities)]
    else:
        st.write("Please select at least one university to visualize.")
        return

    # Create a line plot using a colorblind-friendly palette
    fig = px.line(
        filtered_data,
        x='Year',
        y='Value',
        color='University_Display',
        title=f"{y_label} for {selected_macro_category}",
        labels={'University_Display': ''},
        color_discrete_sequence=px.colors.sequential.Viridis  # Using Viridis color palette
    )

    # Highlight Old Dominion U with a distinct color
    max_value = filtered_data['Value'].max()
    for trace in fig.data:
        if trace.name == 'Old Dominion U':
            trace.line = dict(color='rgba(255, 127, 14, 1)', width=6)  # Bright orange and thicker line for ODU
        else:
            trace.line = dict(dash='dash', width=2.5, color=trace.line.color.replace('0.8', '0.5'))  # Slightly transparent for others

    # Update layout for better readability and adjust legend positioning
    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
        legend=dict(
            title="Legend",
            orientation="h",
            yanchor="top",
            y=-0.3,  # Place the legend above the plot
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=40, b=20),  # Adjust margins to use space efficiently
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
        yaxis=dict(range=[0, max_value * 1.1])  # Dynamically adjust y-axis based on the maximum value
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_micro_level_multiple_subcategories(selected_macro_category, selected_university, comparison_university, data, y_label, subcategories):
    # Filter data for selected categories and universities (always including ODU)
    filtered_data = data[
        (data['Category'].isin(subcategories)) &
        (data['University'].isin([selected_university.lower(), comparison_university.lower()]))
    ]

    # Check if there is data to plot
    if filtered_data.empty:
        st.write("No data available for the selected options.")
        return

    # Standardize university names for display
    filtered_data['University'] = filtered_data['University'].str.strip().str.lower()
    university_display_names = {u: u.title() for u in filtered_data['University'].unique()}
    filtered_data['University_Display'] = filtered_data['University'].map(university_display_names)

    # Adjust the facet wrap based on the number of selected subcategories
    num_subcategories = len(subcategories)
    facet_col_wrap = 2 if num_subcategories > 1 else 1

    # Create the plot using a colorblind-friendly palette
    fig = px.line(
        filtered_data,
        x='Year',
        y='Value',
        color='University_Display',
        facet_col='Category',
        facet_col_wrap=facet_col_wrap,
        height=400 if num_subcategories <= 2 else 800,  # Adjust height based on number of subcategories
        title=f"Comparison of Selected Subcategories under {selected_macro_category}",
        labels={'Value': y_label, 'Year': 'Year'},
        color_discrete_map={
            'Old Dominion U': 'rgba(255, 127, 14, 1)',  # Bright orange for ODU
            'Notre Dame U': 'rgba(128, 177, 211, 1)'    # Lighter blue for better contrast
        }
    )

    # Highlight Old Dominion U with a distinct color
    max_value = filtered_data['Value'].max()
    for trace in fig.data:
        if trace.name == 'Old Dominion U':
            trace.line = dict(color='rgba(255, 127, 14, 1)', width=6)  # Bright orange and thicker line for ODU
        else:
            trace.line = dict(dash='dash', width=2.5, color=trace.line.color.replace('0.8', '0.7'))  # Adjust color for better contrast

    # Update layout for better readability and adjust legend positioning
    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
        legend=dict(
            title="Legend",
            orientation="h",
            yanchor="top",
            y=-0.3,  # Place the legend above the plot
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=60, b=20),  # Increased top margin to prevent overlap with titles
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
        yaxis=dict(range=[0, max_value * 1.1]),  # Dynamically adjust y-axis based on the maximum value
        font=dict(color="white")  # Ensure the font contrasts well against the dark background
    )

    st.plotly_chart(fig, use_container_width=True)