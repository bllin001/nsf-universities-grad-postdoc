import streamlit as st
import plotly.graph_objects as go
from utils import *

st.set_page_config(layout="wide",initial_sidebar_state="expanded")

# Load data for each sheet
# Graduate Students Data
graduate_data = load_and_concatenate_data("Graduate Students")

# Source Data
source_data = load_and_concatenate_data("Source")

# Postdoctorates Data
postdoctorates_data = load_and_concatenate_data("Postdoctorates")

# Define macro categories for Graduate Students
graduate_macro_categories = ["All full-time students", "Science", "Engineering", "Health"]
# Build hierarchy for Graduate Students
graduate_hierarchy = build_hierarchy_by_positions(graduate_data, graduate_macro_categories)

# Define macro categories for Source
source_macro_categories = [
    "All types and sources of support",
    "Fellowships",
    "Research assistantships",
    "Teaching assistantships",
    "Other types of support",
    "Personal resources"
]
# Build hierarchy for Source
source_hierarchy = build_hierarchy_by_positions(source_data, source_macro_categories)

# Define macro categories for Postdoctorates
postdoctorates_macro_categories = ["Science", "Engineering", "Health"]
# Build hierarchy for Postdoctorates
postdoctorates_hierarchy = build_hierarchy_by_positions(postdoctorates_data, postdoctorates_macro_categories)


# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", ["Graduate Students", "Source", "Postdoctorates"])




# Page for Graduate Students
if page == "Graduate Students":
    st.title("Graduate Students Information")
    data = graduate_data
    hierarchy = graduate_hierarchy
    macro_categories = graduate_macro_categories

    available_universities = data['University'].unique()

    analysis_level = st.radio("Select analysis level:", ["Macro (Comparison between Universities)", "Micro (Individual Analysis)"])

    if analysis_level == "Macro (Comparison between Universities)":
        selected_macro_category = st.selectbox("Select macro category:", macro_categories)
        plot_macro_level(selected_macro_category, data, "Graduate Students")
    else:
        selected_macro_category = st.selectbox("Select macro category:", macro_categories)
        subcategories = hierarchy.get(selected_macro_category, [])
        if not subcategories:
            st.write("No subcategories available for the selected macro category.")
        else:
            selected_subcategories = st.multiselect("Select subcategories to compare:", subcategories)
            if not selected_subcategories:
                st.write("Please select at least one subcategory to compare.")
            else:
                selected_university = 'Old Dominion U'
                comparison_university = st.selectbox(
                    "Select a university to compare with Old Dominion U:",
                    [u.title() for u in available_universities if u != 'Old Dominion U']
                )
                comparison_university_lower = comparison_university.lower()
                plot_micro_level_multiple_subcategories(
                    selected_macro_category, selected_university, comparison_university_lower,
                    data, "Graduate Students", selected_subcategories
                )

# Page for Source
elif page == "Source":
    st.title("Financial Support Information")
    data = source_data
    hierarchy = source_hierarchy
    macro_categories = source_macro_categories

    if not data.empty:
        available_universities = data['University'].unique()

        analysis_level = st.radio("Select analysis level:", ["Macro (Comparison between Universities)", "Micro (Individual Analysis)"])

        if analysis_level == "Macro (Comparison between Universities)":
            selected_macro_category = st.selectbox("Select macro category:", macro_categories)
            plot_macro_level(selected_macro_category, data, "Financial Support")
        else:
            selected_macro_category = st.selectbox("Select macro category:", macro_categories)
            subcategories = hierarchy.get(selected_macro_category, [])
            if not subcategories:
                st.write(f"No subcategories available for the selected macro category '{selected_macro_category}'.")
            else:
                selected_subcategories = st.multiselect("Select subcategories to compare:", subcategories)
                if not selected_subcategories:
                    st.write("Please select at least one subcategory to compare.")
                else:
                    selected_university = 'Old Dominion U'
                    comparison_university = st.selectbox(
                        "Select a university to compare with Old Dominion U:",
                        [u.title() for u in available_universities if u != 'Old Dominion U']
                    )
                    comparison_university_lower = comparison_university.lower()
                    plot_micro_level_multiple_subcategories(
                        selected_macro_category, selected_university, comparison_university_lower,
                        data, "Financial Support", selected_subcategories
                    )
                    
# Page for Postdoctorates
elif page == "Postdoctorates":
    st.title("Postdoctorates Information")
    data = postdoctorates_data
    hierarchy = postdoctorates_hierarchy
    macro_categories = postdoctorates_macro_categories

    if not data.empty:
        available_universities = data['University'].unique()

        analysis_level = st.radio("Select analysis level:", ["Macro (Comparison between Universities)", "Micro (Individual Analysis)"])

        if analysis_level == "Macro (Comparison between Universities)":
            selected_macro_category = st.selectbox("Select macro category:", macro_categories)
            plot_macro_level(selected_macro_category, data, "Postdoctorates")
        else:
            selected_macro_category = st.selectbox("Select macro category:", macro_categories)
            subcategories = hierarchy.get(selected_macro_category, [])
            if not subcategories:
                st.write(f"No subcategories available for the selected macro category '{selected_macro_category}'.")
            else:
                # **Changed from selectbox to multiselect**
                selected_subcategories = st.multiselect("Select subcategories to compare:", subcategories)
                if not selected_subcategories:
                    st.write("Please select at least one subcategory to compare.")
                else:
                    # Standardize university names to lowercase
                    available_universities = [u.strip().lower() for u in available_universities]
                    selected_university = 'Old Dominion U'
                    comparison_university = st.selectbox(
                        "Select a university to compare with Old Dominion U:",
                        [u.title() for u in available_universities if u != 'Old Dominion U']
                    )
                    comparison_university_lower = comparison_university.lower()
                    # **Use the multiple subcategories plotting function**
                    plot_micro_level_multiple_subcategories(
                        selected_macro_category, selected_university, comparison_university_lower,
                        data, "Postdoctorates", selected_subcategories
                    )
    else:
        st.write("No data available for Postdoctorates.")
