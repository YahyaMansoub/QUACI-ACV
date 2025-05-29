import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid import GridUpdateMode, DataReturnMode
import io
import numpy as np
from typing import List, Dict, Tuple
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns


def main():

    # Set environmental theme colors
    primary_green = "#2e7d32"
    light_green = "#e8f5e9"
    accent_green = "#4CAF50"
    bg_color = "#f5f9f0"

    # Add this function to display the logo
    def get_base64_encoded_image(image_path):
        import base64
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    # Path to your logo image
    logo_path = "logo_gep.png"

    # Set page config first
    st.set_page_config(
        page_title="Eco-Building Materials Tracker",
        page_icon=logo_path,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add company logo to the top of the page (above the hero section)
    logo_html = f"""
    <div style="text-align: center; padding-bottom: 20px;">
        <img src="data:image/png;base64,{get_base64_encoded_image(logo_path)}" width="150px">
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)

    # Continue with your existing CSS styling...
    st.markdown("""
    <style>
        /* Main background and text colors */
        .stApp {
            background-color: """ + bg_color + """;
            color: #2c3e50;
        }
        
        /* Rest of your styling... */
    </style>
    """, unsafe_allow_html=True)

    # Add this function to display the logo

    st.markdown("""
    <style>
        /* Main background and text colors */
        .stApp {
            background-color: """ + bg_color + """;
            color: #2c3e50;
        }
        
        /* Header styling */
        h1, h2, h3, h4, h5, h6 {
            color: """ + primary_green + """ !important;
            font-weight: 600 !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg, .css-hxt7ib {
            background-color: """ + light_green + """;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: """ + accent_green + """;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        
        .stButton > button:hover {
            background-color: #388E3C;
        }
        
        /* Input fields */
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input {
            border-color: #81c784;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: """ + light_green + """;
            color: """ + primary_green + """ !important;
            border-radius: 4px;
        }
        
        /* DataFrames */
        .dataframe {
            border: 1px solid #a5d6a7;
        }
        
        .dataframe th {
            background-color: #c8e6c9;
            color: """ + primary_green + """;
        }
        
        /* Card styling for sections */
        div.stBlock {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
        }
        
        /* Info/success/warning/error boxes */
        .stInfo {
            background-color: #e1f5fe;
            border-left-color: #03a9f4;
        }
        
        .stSuccess {
            background-color: """ + light_green + """;
            border-left-color: """ + accent_green + """;
        }
        
        .stWarning {
            background-color: #fff8e1;
            border-left-color: #ffc107;
        }
        
        .stError {
            background-color: #ffebee;
            border-left-color: #f44336;
        }
        
        /* Add custom divider */
        hr {
            border: 0;
            height: 1px;
            background-image: linear-gradient(to right, rgba(76, 175, 80, 0), rgba(76, 175, 80, 0.75), rgba(76, 175, 80, 0));
            margin: 30px 0;
        }
        
        /* Plotly graphs */
        .plotly-graph-div {
            overflow-x: auto;
            background-color: white !important;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            padding: 10px;
        }
        
        /* AgGrid styling */
        .ag-root-wrapper {
            border: 1px solid #a5d6a7 !important;
            border-radius: 8px;
        }
        
        .ag-header {
            background-color: #c8e6c9 !important;
        }
        
        .ag-header-cell {
            color: """ + primary_green + """ !important;
        }
        
        /* Card-like containers for major sections */
        .section-container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Create hero section with environmental imagery
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <div style="margin-right: 20px;">
            <img src="https://img.icons8.com/color/96/000000/forest.png" width="80">
        </div>
        <div>
            <h1 style="margin: 0; padding: 0;"> Life Cycle Assessment</h1>
            <p style="margin: 0; padding: 0; color: #388E3C; font-size: 1.2em;">Sustainable construction through data-driven decisions</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Intro message with environmental theme
    st.markdown("""
    <div style="background-color: """ + light_green + """; padding: 15px; border-radius: 10px; margin-bottom: 25px; border-left: 5px solid """ + accent_green + """;">
        <h4 style="margin-top: 0; color: """ + primary_green + """;">🌿 Building a greener future through material selection</h4>
        <p>Track material quantities, analyze environmental impact, and make sustainable decisions for your construction projects.</p>
    </div>
    """, unsafe_allow_html=True)

    material_names = [
        "ExternalWood", "OSB", "Poutrelle", "Beam", "Parquet", "Steel",
        "Glazing", "Wool", "WaterProofing", "Polystyrene", "Gypsum", "Aluminium", "Paint",
        "Mortar", "Cinderblock", "FiredBricks", "Earth", "Hemp", "Concrete",
        "PV Systems", "Battery", "HVAC", "DHW"
    ]

    # Initialize session state for storing buildings data and input state
    if 'buildings_data' not in st.session_state:
        st.session_state.buildings_data = pd.DataFrame(
            columns=['Building_Name'] + material_names)
    if 'building_name' not in st.session_state:
        st.session_state.building_name = ""
    if 'material_values' not in st.session_state:
        st.session_state.material_values = {
            material: 0.0 for material in material_names}
    if 'api_url' not in st.session_state:
        # Update with your API URL
        st.session_state.api_url = "http://localhost:5000/api/simulations/quaci"
    if 'selected_houses' not in st.session_state:
        st.session_state.selected_houses = []  # Initialize as empty list
    if 'Impact_Data' not in st.session_state:
        st.session_state.Impact_Data = {}

    # Main title
    st.title("Building Materials Tracker")
    st.write("Track material quantities for different buildings")

    # Input section in main page
    st.header("Add New Building")

    # Building name input
    building_name = st.text_input(
        "Building Name", value=st.session_state.building_name)

    # Excel-like input for materials
    st.subheader("Material Quantities")

    # Create a dataframe for input that looks like Excel
    input_df = pd.DataFrame({
        'Material': material_names,
        'Quantity': [st.session_state.material_values.get(material, 0.0) for material in material_names]
    })

    # Configure grid options for input
    gb_input = GridOptionsBuilder.from_dataframe(input_df)
    gb_input.configure_column("Material", editable=False)
    gb_input.configure_column("Quantity", editable=True, type=[
                              "numericColumn", "numberColumnFilter"])
    gb_input.configure_grid_options(domLayout='normal')
    grid_options_input = gb_input.build()

    # Display the input grid
    input_grid_response = AgGrid(
        input_df,
        gridOptions=grid_options_input,
        height=400,
        width='100%',
        data_return_mode=DataReturnMode.AS_INPUT,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        fit_columns_on_grid_load=True,
    )

    # Add building button
    if st.button("Add Building"):
        if building_name:
            # Get updated values from the grid
            updated_input_df = input_grid_response['data']

            # Create a new row with building data
            new_building = {'Building_Name': building_name}
            for idx, row in updated_input_df.iterrows():
                material = row['Material']
                quantity = row['Quantity']
                new_building[material] = quantity

            # Add to dataframe
            st.session_state.buildings_data = pd.concat([
                st.session_state.buildings_data,
                pd.DataFrame([new_building])
            ], ignore_index=True)

            # Clear inputs after adding
            st.session_state.building_name = ""
            st.session_state.material_values = {
                material: 0.0 for material in material_names}

            st.success(f"Added building: {building_name}")
            st.rerun()
        else:
            st.error("Please enter a building name")

    st.divider()

    # Add CSV upload option
    st.subheader("Or Upload Buildings from CSV")
    st.write("Upload a CSV file with building data. The CSV should have columns for 'Building_Name' and all materials.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        try:
            # Read CSV file
            csv_data = pd.read_csv(uploaded_file)

            # Validate CSV structure
            required_columns = ['Building_Name'] + material_names
            missing_columns = [
                col for col in required_columns if col not in csv_data.columns]

            if missing_columns:
                st.error(
                    f"CSV is missing required columns:n{', '.join(missing_columns)}")
            else:
                # Show preview of data
                st.write("Preview of uploaded data:")
                st.dataframe(csv_data.head())

                # Add to existing buildings data
                if st.button("Add CSV Data to Existing Buildings"):
                    # Filter to include only the required columns
                    filtered_csv_data = csv_data[required_columns]

                    # Add to dataframe
                    st.session_state.buildings_data = pd.concat([
                        st.session_state.buildings_data,
                        filtered_csv_data
                    ], ignore_index=True)

                    st.success(
                        f"Added {len(filtered_csv_data)} buildings from CSV")
                    st.rerun()
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")

    st.divider()

    # Display the buildings data
    st.header("Buildings Data")

    if len(st.session_state.buildings_data) > 0:
        # Configure grid options
        gb = GridOptionsBuilder.from_dataframe(st.session_state.buildings_data)

        # Add selection capability
        gb.configure_selection(selection_mode='multiple', use_checkbox=True)

        gb.configure_column("Building_Name", editable=True)
        for material in material_names:
            gb.configure_column(material, editable=True, type=[
                                "numericColumn", "numberColumnFilter"])

        gb.configure_grid_options(domLayout='normal')
        grid_options = gb.build()

        # Display the grid
        grid_response = AgGrid(
            st.session_state.buildings_data,
            gridOptions=grid_options,
            height=400,
            width='100%',
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=False,
        )

        # Save selected rows to session state
        st.session_state.selected_houses = grid_response['selected_rows']

        # Update the buildings data with edited values
        st.session_state.buildings_data = grid_response['data']

        st.subheader("Selected Houses")
        if st.session_state.selected_houses is not None and len(st.session_state.selected_houses) > 0:
            st.write(st.session_state.selected_houses)
        else:
            st.write("No houses selected")
        selected = st.session_state.selected_houses

        st.header("Environmental Impact Analysis")

        with st.expander("Environmental Impact Analysis"):
            st.write("Analyze environmental impact for selected house")

            # Get lifespan parameters
            dur_vie_mean = st.number_input(
                "Mean Lifespan (years)", min_value=1.0, value=50.0)
            dur_vie_std_dev = st.number_input(
                "Lifespan Standard Deviation", min_value=0.1, value=2.5)

            if st.button("Get Environmental Impact"):
                if len(st.session_state.selected_houses) > 0:
                    # Get first selected house
                    selected_house = st.session_state.selected_houses.iloc[0].to_dict(
                    )

                    try:
                        # Prepare request data
                        request_data = {
                            "comp_quantity": {k: v for k, v in selected_house.items() if k in material_names},
                            "building_type": selected_house['Building_Name'],
                            "dur_vie_mean": dur_vie_mean,
                            "dur_vie_std_dev": dur_vie_std_dev
                        }

                        # Call API
                        response = requests.post(
                            st.session_state.api_url,
                            json=request_data
                        )

                        if response.status_code == 200:
                            results = response.json()
                            result_df = pd.DataFrame(results)
                            st.session_state.Impact_Data[selected_house['Building_Name']] = result_df

                            # Display results
                            st.subheader("Analysis Results")
                            st.dataframe(result_df)

                            # Add download button
                            csv = result_df.to_csv(
                                index=False).encode('utf-8')
                            st.download_button(
                                label="Download Impact Results",
                                data=csv,
                                file_name=f"{selected_house['Building_Name']}_impact.csv",
                                mime="text/csv"
                            )
                        else:
                            st.error(
                                f"API Error: {response.json().get('error', 'Unknown error')}")

                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
                else:
                    st.error("Please select a house to analyze")

        # Download button for the data
        csv_data = st.session_state.buildings_data.to_csv(
            index=False).encode('utf-8')
        st.download_button(
            label="Download Buildings Data as CSV",
            data=csv_data,
            file_name="buildings_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No buildings added yet. Add your first building above.")

    st.header("Impact Data")
    st.write(st.session_state.Impact_Data)
    impact_data_dict = st.session_state.Impact_Data

    # Extract the matrix
    impact_matrix_df = create_impact_matrices(impact_data_dict)
    st.write(impact_matrix_df)

    st.header("Monte Carlo Simulations")

    # Add user input for simulation parameters
    num_simulations = st.number_input(
        "Number of simulations", min_value=1, value=1000, step=100)
    std = st.number_input("Standard deviation",
                          min_value=0.0, value=50.0, step=1.0)

    # Run the simulation only when needed (e.g., after selecting buildings or pressing a button)
    if st.button("Run Simulation"):
        simulations = simulate_monte_carlo(
            impact_matrix_df, num_simulations=int(num_simulations), std=std)
        # Display all simulations in dictionary format
        st.session_state.simulations = simulations
        st.subheader("All Monte Carlo Simulations:")
        st.write(simulations)

    if not impact_matrix_df.empty:
        render_discernibility_analysis(impact_matrix_df)
    else:
        st.info("No impact data available for discernibility analysis")
    render_radar_comparison()
    render_ranking_analysis()
    render_k4_comparison()
    render_smd_analysis()
    sensitivity_analysis()


def simulate_monte_carlo(impact_matrix_df, num_simulations=1000, std=0.1):

    simulations_dict = {}

    for building_name, row in impact_matrix_df.iterrows():
        means = row.values.astype(float)
        num_impacts = len(means)

        # Simulate normal distributions
        sims = np.random.normal(loc=means, scale=std,
                                size=(num_simulations, num_impacts))
        simulations_dict[building_name] = sims

    return simulations_dict


def create_impact_matrices(impact_data_dict):
    """
    Extracts an environmental impact matrix from a dictionary of simulation results.

    Each value in the dict may be a DataFrame or a string representation of a DataFrame.

    Returns:
        pd.DataFrame: Rows = simulation names, Columns = impact categories.
    """
    simulation_matrix = {}
    impact_categories = [
        "Acidification",
        "Climate change",
        "Climate change - Biogenic",
        "Climate change - Fossil",
        "Climate change - Land use and LU change",
        "Ecotoxicity, freshwater - inorganics",
        "Ecotoxicity, freshwater - organics - p.1",
        "Ecotoxicity, freshwater - organics - p.2",
        "Ecotoxicity, freshwater - part 1",
        "Ecotoxicity, freshwater - part 2",
        "Eutrophication, freshwater",
        "Eutrophication, marine",
        "Eutrophication, terrestrial",
        "Human toxicity, cancer",
        "Human toxicity, cancer - inorganics",
        "Human toxicity, cancer - organics",
        "Human toxicity, non-cancer",
        "Human toxicity, non-cancer - inorganics",
        "Human toxicity, non-cancer - organics",
        "Ionising radiation",
        "Land use",
        "Ozone depletion",
        "Particulate matter",
        "Photochemical ozone formation",
        "Resource use, fossils",
        "Resource use, minerals and metals",
        "Water use"
    ]

    for sim_name, data in impact_data_dict.items():
        try:
            # Handle if already a DataFrame
            if isinstance(data, pd.DataFrame):
                df = data
            # Handle string data (convert to DataFrame)
            elif isinstance(data, str):
                df = pd.read_csv(io.StringIO(
                    data), sep=r"\s{2,}", engine='python')
            else:
                raise TypeError(
                    f"Unexpected type for simulation '{sim_name}': {type(data)}")

            # Set categories from the first valid simulation
            if impact_categories is None:
                impact_categories = df["Impact Category"].tolist()

            # Extract "Row Total" values
            simulation_matrix[sim_name] = df["Row Total"].tolist()

        except Exception as e:
            st.error(f"Failed to parse simulation '{sim_name}': {e}")

    # Construct DataFrame from collected data
    if simulation_matrix:
        return pd.DataFrame.from_dict(simulation_matrix, orient='index', columns=impact_categories)
    else:
        return pd.DataFrame()


def plot_discernibility_heatmap(
    matrices: List[np.ndarray],
    labels: List[str],
    factor_names: List[str],
    heatmap_theme: str = "Viridis",
    annot_fontsize: int = 14,
    label_fontsize: int = 14,
    title_fontsize: int = 16,
):
    """
    Creates an interactive Plotly heatmap for discernibility analysis.
    Returns a Plotly Figure object for Streamlit display.
    """
    n_alternatives = len(matrices)
    n_factors = matrices[0].shape[1]

    # Initialize heatmap data and row labels
    heatmap_data = np.zeros(
        (n_alternatives * (n_alternatives - 1) // 2, n_factors))
    row_labels = []
    idx = 0

    # Calculate discernibility probabilities (replace with your actual calculation)
    for i in range(n_alternatives):
        for j in range(i + 1, n_alternatives):
            row_labels.append(f"{labels[i]} vs {labels[j]}")
            # Example random data - replace with actual discernibility calculation
            heatmap_data[idx, :] = np.random.rand(n_factors)
            idx += 1

    # Create Plotly figure
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=factor_names,
        y=row_labels,
        colorscale=heatmap_theme,
        hoverongaps=False,
        text=np.around(heatmap_data, decimals=2),
        texttemplate="%{text}",
    ))

    # Update layout for better readability
    fig.update_layout(
        title='Discernibility Analysis Heatmap',
        xaxis=dict(
            title='Factors',
            tickfont=dict(size=label_fontsize),
            tickangle=-45,
            automargin=True,
        ),
        yaxis=dict(
            title='Alternative Comparisons',
            tickfont=dict(size=label_fontsize)
        ),
        font=dict(size=annot_fontsize),
        margin=dict(b=150),
        height=600 + len(row_labels)*25,  # Keep just one height setting
        width=800 + len(factor_names)*50  # Keep just one width setting
    )

    return fig


def render_discernibility_analysis(impact_matrix_df: pd.DataFrame):
    """Handles discernibility analysis UI and calculations."""
    st.header("Discernibility Analysis")

    # Get list of available buildings from impact data
    available_buildings = list(st.session_state.Impact_Data.keys())

    if len(available_buildings) >= 2:
        # UI Components
        col1, col2 = st.columns(2)

        with col1:
            # Building selection
            selected_buildings = st.multiselect(
                "Select buildings to compare",
                options=available_buildings,
                default=available_buildings[:2],
                max_selections=5
            )

        with col2:
            # Factor selection
            all_factors = list(impact_matrix_df.columns)
            selected_factors = st.multiselect(
                "Select factors to include",
                options=all_factors,
                default=all_factors[:5],
                key='factor_select'
            )

        # Sidebar settings
        st.sidebar.subheader("Heatmap Settings")
        heatmap_theme = st.sidebar.selectbox(
            "Color Theme",
            options=["Viridis", "Plasma", "Inferno", "Magma", "Cividis"],
            index=0
        )

        # Filter impact matrix based on selected factors
        filtered_matrix = impact_matrix_df[selected_factors]

        # Analysis execution
        if st.button("Generate Discernibility Heatmap"):
            if len(selected_buildings) >= 2 and len(selected_factors) >= 1:
                try:
                    # Prepare matrices for selected buildings and factors
                    matrices = [
                        filtered_matrix.loc[building].values.reshape(
                            -1, len(selected_factors))
                        for building in selected_buildings
                    ]

                    # Generate and display heatmap
                    fig = plot_discernibility_heatmap(
                        matrices=matrices,
                        labels=selected_buildings,
                        factor_names=selected_factors,
                        heatmap_theme=heatmap_theme
                    )
                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
            else:
                st.warning("Please select at least 2 buildings and 1 factor")
    else:
        st.info(
            "Need at least 2 buildings with impact data to perform discernibility analysis")


def render_radar_comparison():
    """Handles UI and logic for radar chart comparison of selected houses."""
    st.header("Radar Chart Comparison")

    # Check if simulation data exists
    if 'simulations' not in st.session_state or not st.session_state.simulations:
        st.info(
            "No simulation data available. Please run Monte Carlo simulations first.")
        return

    # Get available buildings and impact categories
    available_buildings = list(st.session_state.simulations.keys())
    impact_categories = [
        "Acidification",
        "Climate change",
        "Climate change - Biogenic",
        "Climate change - Fossil",
        "Climate change - Land use and LU change",
        "Ecotoxicity, freshwater - inorganics",
        "Ecotoxicity, freshwater - organics - p.1",
        "Ecotoxicity, freshwater - organics - p.2",
        "Ecotoxicity, freshwater - part 1",
        "Ecotoxicity, freshwater - part 2",
        "Eutrophication, freshwater",
        "Eutrophication, marine",
        "Eutrophication, terrestrial",
        "Human toxicity, cancer",
        "Human toxicity, cancer - inorganics",
        "Human toxicity, cancer - organics",
        "Human toxicity, non-cancer",
        "Human toxicity, non-cancer - inorganics",
        "Human toxicity, non-cancer - organics",
        "Ionising radiation",
        "Land use",
        "Ozone depletion",
        "Particulate matter",
        "Photochemical ozone formation",
        "Resource use, fossils",
        "Resource use, minerals and metals",
        "Water use"
    ]

    if len(available_buildings) < 1:
        st.info("Need at least 1 building with simulation data for radar chart")
        return

    # UI Components
    col1, col2 = st.columns(2)

    with col1:
        # Building selection
        selected_buildings = st.multiselect(
            "Select 1 or 2 houses to compare",
            options=available_buildings,
            default=available_buildings[:1],
            max_selections=2
        )

    with col2:
        # Factor selection
        selected_factors = st.multiselect(
            "Select impact categories to include",
            options=impact_categories,
            default=impact_categories[:5]
        )

    # Sidebar settings
    st.sidebar.subheader("Radar Chart Settings")
    show_median = st.sidebar.checkbox("Show Median", value=True)
    show_mean = st.sidebar.checkbox("Show Mean", value=False)
    show_iqr = st.sidebar.checkbox("Show IQR Range", value=True)
    color_palette = st.sidebar.selectbox(
        "Color Palette",
        options=["Viridis", "Plasma", "Inferno", "Magma", "Cividis"],
        index=0
    )

    # Analysis execution
    if st.button("Generate Radar Chart"):
        if len(selected_buildings) == 0:
            st.warning("Please select at least 1 house")
            return

        try:
            # Prepare data matrices with correct impact category indices
            matrices = []
            labels = []

            for building in selected_buildings:
                # Get column indices for selected factors
                factor_indices = [impact_categories.index(
                    f) for f in selected_factors]
                # Get simulation data for this building
                matrix = st.session_state.simulations[building][:,
                                                                factor_indices]
                matrices.append(matrix)
                labels.append(building)

            # Generate and display radar chart
            fig = plot_radar_comparison(
                matrices=matrices,
                labels=selected_factors,
                matrix_names=labels,
                show_median=show_median,
                show_mean=show_mean,
                show_iqr=show_iqr,
                color_palette=color_palette
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Radar chart generation failed: {str(e)}")


def plot_radar_comparison(
    matrices: List[np.ndarray],
    labels: List[str],
    matrix_names: List[str],
    show_median: bool = True,
    show_mean: bool = False,
    show_iqr: bool = True,
    color_palette: str = "Viridis",
    title: str = "Environmental Impact Comparison"
) -> go.Figure:
    """
    Creates an interactive radar chart comparing median, mean, and IQR of impact categories.

    Parameters:
        matrices (List[np.ndarray]): List of 2D arrays containing impact data for each building
        labels (List[str]): Impact category names
        matrix_names (List[str]): Building names for legend
        show_median (bool): Whether to display median values
        show_mean (bool): Whether to display mean values
        show_iqr (bool): Whether to display IQR ranges
        color_palette (str): Plotly color palette name
        title (str): Chart title

    Returns:
        go.Figure: Plotly Figure object
    """
    fig = go.Figure()
    colors = getattr(px.colors.sequential, color_palette)

    for idx, (matrix, name) in enumerate(zip(matrices, matrix_names)):
        # Calculate statistics
        median = np.median(matrix, axis=0)
        mean = np.mean(matrix, axis=0)
        q1 = np.percentile(matrix, 25, axis=0)
        q3 = np.percentile(matrix, 75, axis=0)

        # Close the loop for radar chart
        theta = labels + [labels[0]]
        median = np.concatenate((median, [median[0]]))
        mean = np.concatenate((mean, [mean[0]]))
        q1 = np.concatenate((q1, [q1[0]]))
        q3 = np.concatenate((q3, [q3[0]]))

        color = colors[idx % len(colors)]

        # Add traces
        if show_median:
            fig.add_trace(go.Scatterpolar(
                r=median,
                theta=theta,
                name=f"{name} Median",
                line=dict(color=color, width=2),
                showlegend=True
            ))

        if show_mean:
            fig.add_trace(go.Scatterpolar(
                r=mean,
                theta=theta,
                name=f"{name} Mean",
                line=dict(color=color, width=2, dash='dash'),
                showlegend=True
            ))

        if show_iqr:
            fig.add_trace(go.Scatterpolar(
                r=q3,
                theta=theta,
                fill='toself',
                fillcolor=f"rgba{hex_to_rgb(color) + (0.2,)}",
                line=dict(color='rgba(0,0,0,0)'),
                name=f"{name} IQR",
                showlegend=True
            ))

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showticklabels=False,
                range=[0, max([np.max(mat) for mat in matrices]) * 1.1]
            ),
            angularaxis=dict(
                direction="clockwise",
                rotation=90
            )
        ),
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=20)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
        margin=dict(t=100, b=100)
    )

    return fig


def hex_to_rgb(hex_color: str) -> tuple:
    """Converts hex color code to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def RP_with_probabilities_and_names(matrices, factors, matrix_names=None):
    """
    Calculate ranking probabilities for each factor across multiple matrices.

    Parameters:
    matrices (Union[List[np.ndarray], Dict[str, np.ndarray]]): List or dictionary of matrices.
    factors (List[str]): List of factor names.
    matrix_names (List[str], optional): List of matrix names. If None, default names are used.

    Returns:
    Dict[str, Dict[Tuple[int], float]]: Ranking probabilities for each factor.
    """
    if isinstance(matrices, dict):
        matrix_names = list(matrices.keys())
        matrices = list(matrices.values())
    elif matrix_names is None:
        matrix_names = [f"Matrix {i+1}" for i in range(len(matrices))]

    n, m = matrices[0].shape
    result = {factor: [] for factor in factors}
    for j in range(m):
        for i in range(n):
            values = [matrix[i, j] for matrix in matrices]
            ranks = tuple(np.argsort(values) + 1)
            result[factors[j]].append(ranks)

    probabilities = {factor: {} for factor in factors}
    for factor, rankings in result.items():
        total_rankings = len(rankings)
        for ranking in rankings:
            if ranking not in probabilities[factor]:
                probabilities[factor][ranking] = 0
            probabilities[factor][ranking] += 1
        for ranking in probabilities[factor]:
            probabilities[factor][ranking] /= total_rankings

    # Convert rank tuples to matrix names
    named_probabilities = {factor: {} for factor in factors}
    for factor, rank_dict in probabilities.items():
        for rank_tuple, prob in rank_dict.items():
            named_rank_tuple = tuple(
                matrix_names[rank - 1] for rank in rank_tuple)
            named_probabilities[factor][named_rank_tuple] = prob

    return named_probabilities


def render_ranking_analysis():
    """Handles UI and logic for ranking probability analysis."""
    st.header("Ranking Probability Analysis")

    # Check if simulation data exists
    if 'simulations' not in st.session_state or not st.session_state.simulations:
        st.info(
            "No simulation data available. Please run Monte Carlo simulations first.")
        return

    # Get available buildings and impact categories
    available_buildings = list(st.session_state.simulations.keys())
    impact_categories = [
        "Acidification",
        "Climate change",
        "Climate change - Biogenic",
        "Climate change - Fossil",
        "Climate change - Land use and LU change",
        "Ecotoxicity, freshwater - inorganics",
        "Ecotoxicity, freshwater - organics - p.1",
        "Ecotoxicity, freshwater - organics - p.2",
        "Ecotoxicity, freshwater - part 1",
        "Ecotoxicity, freshwater - part 2",
        "Eutrophication, freshwater",
        "Eutrophication, marine",
        "Eutrophication, terrestrial",
        "Human toxicity, cancer",
        "Human toxicity, cancer - inorganics",
        "Human toxicity, cancer - organics",
        "Human toxicity, non-cancer",
        "Human toxicity, non-cancer - inorganics",
        "Human toxicity, non-cancer - organics",
        "Ionising radiation",
        "Land use",
        "Ozone depletion",
        "Particulate matter",
        "Photochemical ozone formation",
        "Resource use, fossils",
        "Resource use, minerals and metals",
        "Water use"
    ]

    # UI Components
    col1, col2 = st.columns(2)

    with col1:
        # Building selection
        selected_buildings = st.multiselect(
            "Select houses to compare",
            options=available_buildings,
            default=available_buildings[:2]
        )

    with col2:
        # Factor selection
        selected_factors = st.multiselect(
            "Select impact categories to rank",
            options=impact_categories,
            default=impact_categories[:3],
            max_selections=5
        )

    # Sidebar settings
    st.sidebar.subheader("Heatmap Settings")
    heatmap_theme = st.sidebar.selectbox(
        "Color Theme",
        options=["Viridis", "Plasma", "Inferno", "Magma", "Cividis"],
        index=0,
        key="heatmap_theme_1"
    )

    # Analysis execution
    if st.button("Generate Ranking Analysis"):
        if len(selected_buildings) < 1:
            st.warning("Please select at least 1 building")
            return
        if len(selected_factors) < 2:
            st.warning("Please select at least 2 factors")
            return

        try:
            # Prepare matrices for selected buildings
            matrices = []
            for building in selected_buildings:
                # Get column indices for selected factors
                factor_indices = [impact_categories.index(
                    f) for f in selected_factors]
                # Get simulation data for this building
                matrix = st.session_state.simulations[building][:,
                                                                factor_indices]
                matrices.append(matrix)

            # Calculate ranking probabilities
            probabilities = RP_with_probabilities_and_names(
                matrices,
                factors=selected_factors,
                matrix_names=selected_buildings
            )

            # Generate and display heatmap
            fig = plot_ranking_probabilities_heatmap(
                probabilities, selected_factors, heatmap_theme)
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Ranking analysis failed: {str(e)}")


def plot_ranking_probabilities_heatmap(probabilities, factors, heatmap_theme="Viridis"):
    """
    Creates an interactive Plotly heatmap of ranking probabilities.
    """
    # Prepare data for heatmap
    factor_names = list(factors)
    ranking_labels = sorted(
        {ranking for factor in factors for ranking in probabilities[factor]})

    heatmap_data = np.array([
        [probabilities[factor].get(ranking, 0) for ranking in ranking_labels]
        for factor in factors
    ])

    # Convert rankings to human-readable strings
    formatted_rankings = [" < ".join(ranking) for ranking in ranking_labels]

    # Create Plotly figure
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=formatted_rankings,
        y=factor_names,
        colorscale=heatmap_theme,
        hoverongaps=False,
        text=np.around(heatmap_data, decimals=2),
        texttemplate="%{text}",
        colorbar=dict(title="Probability")
    ))

    # Update layout
    fig.update_layout(
        title="Ranking Probabilities Heatmap",
        xaxis=dict(
            title="Rankings",
            tickangle=45,
            automargin=True,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title="Factors",
            tickfont=dict(size=12)
        ),
        margin=dict(l=100, r=50, b=150, t=50),
        height=600 + len(factors)*20,
        width=800 + len(ranking_labels)*50
    )

    return fig


def render_k4_comparison():
    """Handles UI and logic for K4 performance comparison."""
    st.header("K4 Performance Comparison")

    # Check if simulation data exists
    if 'simulations' not in st.session_state or not st.session_state.simulations:
        st.info(
            "No simulation data available. Please run Monte Carlo simulations first.")
        return

    # Get available buildings and impact categories
    available_buildings = list(st.session_state.simulations.keys())
    impact_categories = [
        "Acidification",
        "Climate change",
        "Climate change - Biogenic",
        "Climate change - Fossil",
        "Climate change - Land use and LU change",
        "Ecotoxicity, freshwater - inorganics",
        "Ecotoxicity, freshwater - organics - p.1",
        "Ecotoxicity, freshwater - organics - p.2",
        "Ecotoxicity, freshwater - part 1",
        "Ecotoxicity, freshwater - part 2",
        "Eutrophication, freshwater",
        "Eutrophication, marine",
        "Eutrophication, terrestrial",
        "Human toxicity, cancer",
        "Human toxicity, cancer - inorganics",
        "Human toxicity, cancer - organics",
        "Human toxicity, non-cancer",
        "Human toxicity, non-cancer - inorganics",
        "Human toxicity, non-cancer - organics",
        "Ionising radiation",
        "Land use",
        "Ozone depletion",
        "Particulate matter",
        "Photochemical ozone formation",
        "Resource use, fossils",
        "Resource use, minerals and metals",
        "Water use"
    ]

    # UI Components
    col1, col2 = st.columns(2)

    with col1:
        # Building selection
        selected_buildings = st.multiselect(
            "Select 2 houses to compare",
            options=available_buildings,
            default=available_buildings[:2]
        )

    with col2:
        # Factor selection
        selected_factors = st.multiselect(
            "Select impact categories to include",
            options=impact_categories,
            default=impact_categories[:5],
            key='k4_factor_select'
        )

    # Sidebar settings
    st.sidebar.subheader("K4 Chart Settings")

    # Color theme selection
    color_theme = st.sidebar.selectbox(
        "Color Theme",
        options=["Blue/Orange", "Green/Red", "Purple/Yellow", "Teal/Pink"],
        index=0,
        key="k4_color_theme"
    )

    # Threshold input
    lamb = st.sidebar.slider(
        "Significance threshold (λ)",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.5,
        format="%.1f%%"
    )

    if st.button("Generate K4 Comparison"):
        if len(selected_buildings) != 2:
            st.warning("Please select exactly 2 houses")
            return

        try:
            # Get simulation data
            mat1 = st.session_state.simulations[selected_buildings[0]]
            mat2 = st.session_state.simulations[selected_buildings[1]]

            # Get indices of selected factors
            factor_indices = [impact_categories.index(
                f) for f in selected_factors]

            # Filter matrices by selected factors
            mat1 = mat1[:, factor_indices]
            mat2 = mat2[:, factor_indices]

            # Generate plot
            fig = plot_K4_histogram(
                mat1, mat2, lamb/100,
                indicator_names=selected_factors,
                building_names=selected_buildings,
                color_theme=color_theme
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"K4 comparison failed: {str(e)}")


def K4(mat1: np.ndarray, mat2: np.ndarray, lamb: float) -> List[float]:
    """
    Example implementation - replace with your actual K4 calculation
    Returns normalized K4 values between -1 and 1
    """
    # Calculate mean differences
    diffs = np.mean(mat1, axis=0) - np.mean(mat2, axis=0)

    # Normalize to [-1, 1]
    max_diff = np.max(np.abs(diffs))
    normalized = diffs / (max_diff if max_diff != 0 else 1)

    # Apply threshold
    return [v if abs(v) > lamb else 0 for v in normalized]


def plot_K4_histogram(mat1: np.ndarray, mat2: np.ndarray, lamb: float,
                      indicator_names: List[str], building_names: List[str],
                      color_theme: str = "Blue/Orange"):
    """
    Creates an interactive Plotly histogram of K4 values.
    """
    # Define color themes
    color_themes = {
        "Blue/Orange": ["#1f77b4", "#ff7f0e"],
        "Green/Red": ["#2ca02c", "#d62728"],
        "Purple/Yellow": ["#9467bd", "#bcbd22"],
        "Teal/Pink": ["#17becf", "#e377c2"]
    }

    # Get colors from selected theme
    colors = color_themes.get(color_theme, color_themes["Blue/Orange"])

    # Calculate K4 values
    k4_values = K4(mat1, mat2, lamb)

    # Create DataFrame for plotting
    df = pd.DataFrame({
        'Indicator': indicator_names,
        'K4': k4_values,
        'Comparison': [building_names[0] if v >= 0 else building_names[1] for v in k4_values]
    })

    # Create figure
    fig = px.bar(
        df,
        x='Indicator',
        y='K4',
        color='Comparison',
        color_discrete_map={
            building_names[0]: colors[0],
            building_names[1]: colors[1]
        },
        range_y=[-1.1, 1.1],
        title=f'K4 Performance Comparison (λ = {lamb*100:.1f}%)'
    )

    # Add reference line and annotations
    fig.add_hline(y=0, line_dash="dash", line_color="black")

    # Update traces for better visualization
    fig.update_traces(
        marker_line_width=1.5,
        marker_line_color="darkgray",
        hovertemplate="<b>%{x}</b><br>K4 Value: %{y:.2f}<extra></extra>",
        width=0.7  # Adjust bar width
    )

    # Add custom annotations
    annotations = []
    for i, (ind, val) in enumerate(zip(indicator_names, k4_values)):
        annotations.append(dict(
            x=ind,
            y=val + 0.05 if val >= 0 else val - 0.05,
            text=f"{building_names[0] if val >= 0 else building_names[1]} better<br>by {abs(val):.2f}",
            showarrow=False,
            font=dict(color='white' if abs(val) > 0.5 else 'black'),
            bgcolor="rgba(0,0,0,0.5)",
            xanchor='center'
        ))

    # Update layout
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="Environmental Indicators",
        yaxis_title="Performance (Normalized K4 Value)",
        hoverlabel=dict(bgcolor="white"),
        annotations=annotations,
        showlegend=True,
        legend_title_text='Better Performance'
    )

    # Customize axes
    fig.update_xaxes(
        tickangle=45,
        tickfont=dict(size=10),
        type='category'  # Ensure categorical treatment
    )
    fig.update_yaxes(
        tickvals=np.linspace(-1, 1, 5),
        ticktext=['-1 (Dominant)', '-0.5', '0', '0.5', '1 (Dominant)'],
        gridcolor='lightgray'
    )

    return fig


def calculate_smd(matrix1: np.ndarray, matrix2: np.ndarray) -> np.ndarray:
    """
    Calculate the Standardized Mean Difference (Cohen's d) between two matrices of simulations.

    For each factor (column), calculates:
    d = mean(a₁ - a₂) / std(a₁ - a₂)

    Args:
        matrix1: Matrix of simulations for first building (n_simulations x n_factors)
        matrix2: Matrix of simulations for second building (n_simulations x n_factors)

    Returns:
        Array of SMD values for each factor
    """
    # Calculate pairwise differences for each simulation
    pairwise_diff = matrix1 - matrix2

    # Calculate mean of pairwise differences
    mean_diff = np.mean(pairwise_diff, axis=0)

    # Calculate standard deviation of pairwise differences
    # ddof=1 for sample standard deviation
    std_diff = np.std(pairwise_diff, axis=0, ddof=1)

    # Calculate SMD (Cohen's d)
    # Avoid division by zero
    smd = np.zeros_like(mean_diff)
    non_zero_indices = std_diff != 0
    smd[non_zero_indices] = mean_diff[non_zero_indices] / \
        std_diff[non_zero_indices]

    return smd


def render_smd_analysis():
    """Handles UI and logic for Standardized Mean Difference (Cohen's d) analysis."""
    st.header("Standardized Mean Difference (SMD) Analysis")

    # Check if simulation data exists
    if 'simulations' not in st.session_state or not st.session_state.simulations:
        st.info(
            "No simulation data available. Please run Monte Carlo simulations first.")
        return

    # Get available buildings and impact categories
    available_buildings = list(st.session_state.simulations.keys())
    impact_categories = [
        "Acidification",
        "Climate change",
        "Climate change - Biogenic",
        "Climate change - Fossil",
        "Climate change - Land use and LU change",
        "Ecotoxicity, freshwater - inorganics",
        "Ecotoxicity, freshwater - organics - p.1",
        "Ecotoxicity, freshwater - organics - p.2",
        "Ecotoxicity, freshwater - part 1",
        "Ecotoxicity, freshwater - part 2",
        "Eutrophication, freshwater",
        "Eutrophication, marine",
        "Eutrophication, terrestrial",
        "Human toxicity, cancer",
        "Human toxicity, cancer - inorganics",
        "Human toxicity, cancer - organics",
        "Human toxicity, non-cancer",
        "Human toxicity, non-cancer - inorganics",
        "Human toxicity, non-cancer - organics",
        "Ionising radiation",
        "Land use",
        "Ozone depletion",
        "Particulate matter",
        "Photochemical ozone formation",
        "Resource use, fossils",
        "Resource use, minerals and metals",
        "Water use"
    ]

    if len(available_buildings) < 2:
        st.info("Need at least 2 buildings with simulation data for SMD analysis")
        return

    # UI Components
    col1, col2 = st.columns(2)

    with col1:
        # Building selection
        selected_buildings = st.multiselect(
            "Select houses to compare",
            options=available_buildings,
            default=available_buildings[:2],
            help="Select at least 2 buildings to calculate pairwise SMD values"
        )

    with col2:
        # Factor selection
        selected_factors = st.multiselect(
            "Select impact categories to analyze",
            options=impact_categories,
            default=impact_categories[:5],
            help="Select the environmental impact categories to include in the analysis"
        )

    # Settings for SMD interpretation
    with st.expander("SMD Interpretation Guide"):
        st.markdown("""
        ### Cohen's d Interpretation:
        - **|d| < 0.2**: Negligible difference
        - **0.2 ≤ |d| < 0.5**: Small difference
        - **0.5 ≤ |d| < 0.8**: Medium difference
        - **|d| ≥ 0.8**: Large difference
        
        Positive values indicate the first building has higher impact, negative values indicate the second building has higher impact.
        """)

    # Analysis execution
    if st.button("Calculate SMD Values"):
        if len(selected_buildings) < 2:
            st.warning("Please select at least 2 houses")
            return
        if len(selected_factors) < 1:
            st.warning("Please select at least 1 impact category")
            return

        try:
            # Prepare all pairwise comparisons
            smd_results = {}
            for i, building1 in enumerate(selected_buildings):
                for building2 in selected_buildings[i+1:]:
                    # Get column indices for selected factors
                    factor_indices = [impact_categories.index(
                        f) for f in selected_factors]

                    # Get simulation data for these buildings
                    matrix1 = st.session_state.simulations[building1][:,
                                                                      factor_indices]
                    matrix2 = st.session_state.simulations[building2][:,
                                                                      factor_indices]

                    # Calculate SMD
                    smd_values = calculate_smd(matrix1, matrix2)

                    # Store results with building pair as key
                    comparison_key = f"{building1} vs {building2}"
                    smd_results[comparison_key] = dict(
                        zip(selected_factors, smd_values))

            # Convert results to a DataFrame for easier visualization
            # Reshape to have comparisons as rows and impacts as columns
            smd_df = pd.DataFrame.from_dict(smd_results, orient='index')

            # Display results
            st.subheader("SMD (Cohen's d) Results")

            # Apply conditional formatting
            def color_smd(val):
                """Apply color based on SMD value magnitude"""
                if pd.isna(val):
                    return ''

                abs_val = abs(val)
                if abs_val < 0.2:
                    color = '#CCCCCC'  # Gray for negligible
                elif abs_val < 0.5:
                    color = '#FFDD99'  # Light orange for small
                elif abs_val < 0.8:
                    color = '#FFB266'  # Medium orange for medium
                else:
                    color = '#FF8000'  # Dark orange for large

                return f'background-color: {color}'

            # Display the styled dataframe
            st.dataframe(smd_df.style.applymap(color_smd).format("{:.3f}"))

            # Generate heatmap visualization
            fig = px.imshow(
                smd_df.values,
                x=smd_df.columns,
                y=smd_df.index,
                color_continuous_scale="RdBu_r",  # Red-Blue scale, reversed so negative is blue
                labels=dict(x="Impact Category",
                            y="Building Comparison", color="Cohen's d"),
                range_color=[-max(1, abs(smd_df.values).max()),
                             # Symmetric scale
                             max(1, abs(smd_df.values).max())]
            )

            # Update layout
            fig.update_layout(
                title="SMD (Cohen's d) Heatmap",
                xaxis=dict(tickangle=-45),
                margin=dict(l=50, r=50, t=50, b=100),
                coloraxis_colorbar=dict(
                    title="Cohen's d",
                    tickvals=[-0.8, -0.5, -0.2, 0, 0.2, 0.5, 0.8],
                    ticktext=["< -0.8 (Large)", "-0.5 (Medium)", "-0.2 (Small)", "0",
                              "0.2 (Small)", "0.5 (Medium)", "> 0.8 (Large)"]
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            # Add download button for SMD results
            csv = smd_df.to_csv().encode('utf-8')
            st.download_button(
                label="Download SMD Results as CSV",
                data=csv,
                file_name="smd_analysis.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"SMD analysis failed: {str(e)}")
            st.exception(e)  # Show detailed exception for debugging


def calculate_drd(matrix1: np.ndarray, matrix2: np.ndarray) -> np.ndarray:
    """
    Calculate the Distribution of Relative Differences (DRD) between two matrices.

    For each pair of simulations, calculates:
    DRD = (a₁ - a₂) / max(a₁, a₂)

    Args:
        matrix1: Matrix of simulations for first building (n_simulations x n_factors)
        matrix2: Matrix of simulations for second building (n_simulations x n_factors)

    Returns:
        Array of DRD values for each simulation and factor (n_simulations x n_factors)
    """
    # Calculate differences
    diff = matrix1 - matrix2

    # Calculate maximum values
    max_values = np.maximum(matrix1, matrix2)

    # Calculate DRD (avoid division by zero)
    drd = np.zeros_like(diff)
    non_zero_indices = max_values != 0
    drd[non_zero_indices] = diff[non_zero_indices] / \
        max_values[non_zero_indices]

    return drd


def render_drd_analysis():
    """Handles UI and logic for Distribution of Relative Differences analysis."""
    st.header("Distribution of Relative Differences (DRD) Analysis")

    # Check if simulation data exists
    if 'simulations' not in st.session_state or not st.session_state.simulations:
        st.info(
            "No simulation data available. Please run Monte Carlo simulations first.")
        return

    # Get available buildings and impact categories
    available_buildings = list(st.session_state.simulations.keys())
    impact_categories = [
        "Acidification",
        "Climate change",
        "Climate change - Biogenic",
        "Climate change - Fossil",
        "Climate change - Land use and LU change",
        "Ecotoxicity, freshwater - inorganics",
        "Ecotoxicity, freshwater - organics - p.1",
        "Ecotoxicity, freshwater - organics - p.2",
        "Ecotoxicity, freshwater - part 1",
        "Ecotoxicity, freshwater - part 2",
        "Eutrophication, freshwater",
        "Eutrophication, marine",
        "Eutrophication, terrestrial",
        "Human toxicity, cancer",
        "Human toxicity, cancer - inorganics",
        "Human toxicity, cancer - organics",
        "Human toxicity, non-cancer",
        "Human toxicity, non-cancer - inorganics",
        "Human toxicity, non-cancer - organics",
        "Ionising radiation",
        "Land use",
        "Ozone depletion",
        "Particulate matter",
        "Photochemical ozone formation",
        "Resource use, fossils",
        "Resource use, minerals and metals",
        "Water use"
    ]

    if len(available_buildings) < 2:
        st.info("Need at least 2 buildings with simulation data for DRD analysis")
        return

    # UI Components
    col1, col2 = st.columns(2)

    with col1:
        # Building selection for comparison (exactly 2)
        selected_buildings = st.multiselect(
            "Select 2 buildings to compare",
            options=available_buildings,
            default=available_buildings[:min(2, len(available_buildings))],
            help="Select exactly 2 buildings to compare with DRD analysis",
            key="SXbhjv"
        )

    with col2:
        # Factor selection
        selected_factors = st.multiselect(
            "Select impact categories to analyze",
            options=impact_categories,
            default=impact_categories[:5],
            help="Select the environmental impact categories to include in the analysis",
            key="SASDdcdfv"
        )

    # Additional settings
    st.sidebar.subheader("DRD Analysis Settings")

    indifference_threshold = st.sidebar.slider(
        "Indifference threshold (±λ%)",
        min_value=1.0,
        max_value=10.0,
        value=5.0,
        step=0.5,
        help="Threshold around the indifference line (0-axis) where alternatives are considered similar"
    )

    plot_height = st.sidebar.slider(
        "Plot height",
        min_value=400,
        max_value=1000,
        value=600,
        step=50
    )

    # Settings for DRD interpretation
    with st.expander("DRD Interpretation Guide"):
        st.markdown("""
        ### Distribution of Relative Differences Interpretation:
        
        - **Values > 0**: First building has higher impact than second building
        - **Values < 0**: Second building has higher impact than first building
        - **Values in ±λ% range** (yellow zone): Buildings have similar impacts for that category
        
        #### About the boxplot:
        - The **red line** is the indifference line (0-axis) where both buildings have equal impact
        - The **yellow zone** is the indifference zone (±λ%)
        - The **box** shows the interquartile range (25th to 75th percentile)
        - The **line inside box** is the median
        - The **whiskers** extend to the 2.5th and 97.5th percentiles
        
        #### Interpreting the shape:
        - **Thick boxplot**: The uncertain factors strongly affect the results
        - **Flattened boxplot**: The impact difference is consistent regardless of uncertainty
        - **Boxplot centered on 0**: Both alternatives have similar impacts
        - **Boxplot clearly above/below 0**: One alternative is clearly preferred
        """)

    # Analysis execution
    if st.button("Generate DRD Boxplots"):
        if len(selected_buildings) != 2:
            st.warning("Please select exactly 2 buildings")
            return
        if len(selected_factors) < 1:
            st.warning("Please select at least 1 impact category")
            return

        try:
            # Get column indices for selected factors
            factor_indices = [impact_categories.index(
                f) for f in selected_factors]

            # Get simulation data for these buildings
            building1, building2 = selected_buildings
            matrix1 = st.session_state.simulations[building1][:,
                                                              factor_indices]
            matrix2 = st.session_state.simulations[building2][:,
                                                              factor_indices]

            # Calculate DRD
            drd_values = calculate_drd(matrix1, matrix2)

            # Create boxplot
            fig = create_drd_boxplot(
                drd_values=drd_values,
                factor_names=selected_factors,
                building_names=selected_buildings,
                indifference_threshold=indifference_threshold/100,  # Convert to proportion
                height=plot_height
            )

            # Display plot
            st.plotly_chart(fig, use_container_width=True)

            # Create summary statistics table
            summary_stats = create_drd_summary(
                drd_values, selected_factors, selected_buildings, indifference_threshold/100)
            st.subheader("DRD Summary Statistics")
            st.dataframe(summary_stats.style.format({
                'Median': '{:.2%}',
                'Mean': '{:.2%}',
                'Min': '{:.2%}',
                'Max': '{:.2%}',
                'Q1 (25%)': '{:.2%}',
                'Q3 (75%)': '{:.2%}',
                '2.5%': '{:.2%}',
                '97.5%': '{:.2%}',
                '% Below Zero': '{:.1%}',
                '% In Indifference Zone': '{:.1%}'
            }))

            # Add download options
            csv_drd = pd.DataFrame(
                drd_values,
                columns=selected_factors
            ).to_csv().encode('utf-8')

            st.download_button(
                label="Download DRD Values as CSV",
                data=csv_drd,
                file_name=f"drd_values_{building1}_vs_{building2}.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"DRD analysis failed: {str(e)}")
            st.exception(e)  # Show detailed exception for debugging


def create_drd_boxplot(
    drd_values: np.ndarray,
    factor_names: List[str],
    building_names: List[str],
    indifference_threshold: float = 0.05,
    height: int = 600
) -> go.Figure:
    """
    Create a boxplot visualization of the Distribution of Relative Differences.

    Args:
        drd_values: Array of DRD values (n_simulations x n_factors)
        factor_names: Names of the impact factors
        building_names: Names of the buildings being compared
        indifference_threshold: Threshold for the indifference zone (default: 0.05 or 5%)
        height: Height of the plot in pixels

    Returns:
        Plotly figure object
    """
    # Create figure
    fig = go.Figure()

    # Add boxplot traces for each factor
    for i, factor in enumerate(factor_names):
        fig.add_trace(go.Box(
            y=drd_values[:, i],
            name=factor,
            boxpoints='outliers',  # Only show outliers
            jitter=0.3,
            whiskerwidth=0.2,
            fillcolor='lightgray',
            marker_color='darkgray',
            line_color='black',
            # Show the 2.5th and 97.5th percentiles as whiskers
            quartilemethod="linear",
            q1=[np.percentile(drd_values[:, i], 25)],
            median=[np.percentile(drd_values[:, i], 50)],
            q3=[np.percentile(drd_values[:, i], 75)],
            lowerfence=[np.percentile(drd_values[:, i], 2.5)],
            upperfence=[np.percentile(drd_values[:, i], 97.5)],
            hoverinfo='y+name',
            hovertemplate=f"{factor}<br>Value: %{{y:.2%}}<extra></extra>"
        ))

    # Add reference line at y=0 (indifference line)
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=0,
        x1=len(factor_names) - 0.5,
        y1=0,
        line=dict(
            color="red",
            width=2,
            dash="solid",
        ),
        name="Indifference Line"
    )

    # Add indifference zone
    fig.add_shape(
        type="rect",
        x0=-0.5,
        y0=-indifference_threshold,
        x1=len(factor_names) - 0.5,
        y1=indifference_threshold,
        fillcolor="yellow",
        opacity=0.2,
        line_width=0,
        name=f"Indifference Zone (±{indifference_threshold:.0%})"
    )

    # Add annotation for indifference zone
    fig.add_annotation(
        x=len(factor_names) - 0.5,
        y=indifference_threshold / 2,
        text=f"Indifference Zone (±{indifference_threshold:.0%})",
        showarrow=False,
        xanchor="right",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="black",
        borderwidth=1
    )

    # Add indicators for which building is better
    fig.add_annotation(
        x=len(factor_names) - 0.5,
        y=indifference_threshold * 1.5,
        text=f"{building_names[0]} has higher impact",
        showarrow=False,
        xanchor="right",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="black",
        borderwidth=1
    )

    fig.add_annotation(
        x=len(factor_names) - 0.5,
        y=-indifference_threshold * 1.5,
        text=f"{building_names[1]} has higher impact",
        showarrow=False,
        xanchor="right",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="black",
        borderwidth=1
    )

    # Update layout
    fig.update_layout(
        title=f"Distribution of Relative Differences: {building_names[0]} vs {building_names[1]}",
        xaxis_title="Impact Categories",
        yaxis_title="Relative Difference (DRD)",
        yaxis=dict(
            tickformat=".0%",  # Format as percentage
            zeroline=False,
            gridcolor='lightgray'
        ),
        boxmode='group',
        height=height,
        margin=dict(l=50, r=50, t=80, b=80),
        plot_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="closest"
    )

    return fig


def create_drd_summary(
    drd_values: np.ndarray,
    factor_names: List[str],
    building_names: List[str],
    indifference_threshold: float = 0.05
) -> pd.DataFrame:
    """
    Create a summary statistics DataFrame for the DRD analysis.

    Args:
        drd_values: Array of DRD values (n_simulations x n_factors)
        factor_names: Names of the impact factors
        building_names: Names of the buildings being compared
        indifference_threshold: Threshold for the indifference zone

    Returns:
        DataFrame with summary statistics
    """
    summary_data = []

    for i, factor in enumerate(factor_names):
        factor_values = drd_values[:, i]

        # Calculate statistics
        median = np.median(factor_values)
        mean = np.mean(factor_values)
        min_val = np.min(factor_values)
        max_val = np.max(factor_values)
        q1 = np.percentile(factor_values, 25)
        q3 = np.percentile(factor_values, 75)
        p2_5 = np.percentile(factor_values, 2.5)
        p97_5 = np.percentile(factor_values, 97.5)

        # Calculate percentage of values below zero (building 2 better)
        pct_below_zero = np.mean(factor_values < 0)

        # Calculate percentage in indifference zone
        pct_indifference = np.mean(
            (factor_values >= -indifference_threshold) &
            (factor_values <= indifference_threshold)
        )

        # Determine which building is better overall
        if median < -indifference_threshold:
            better_building = building_names[1]
        elif median > indifference_threshold:
            better_building = building_names[0]
        else:
            better_building = "Similar"

        # Assess reliability based on IQR and indifference zone
        iqr = q3 - q1
        if iqr < indifference_threshold:
            reliability = "High (consistent results)"
        elif iqr < indifference_threshold * 3:
            reliability = "Medium"
        else:
            reliability = "Low (high variability)"

        summary_data.append({
            'Impact Category': factor,
            'Median': median,
            'Mean': mean,
            'Min': min_val,
            'Max': max_val,
            'Q1 (25%)': q1,
            'Q3 (75%)': q3,
            '2.5%': p2_5,
            '97.5%': p97_5,
            '% Below Zero': pct_below_zero,
            '% In Indifference Zone': pct_indifference,
            'Better Building': better_building,
            'Reliability': reliability
        })

    return pd.DataFrame(summary_data)


def render_sensitivity_analysis_api():
    material_names = [
        "ExternalWood", "OSB", "Poutrelle", "Beam", "Parquet", "Steel",
        "Glazing", "Wool", "WaterProofing", "Polystyrene", "Gypsum", "Aluminium", "Paint",
        "Mortar", "Cinderblock", "FiredBricks", "Earth", "Hemp", "Concrete",
        "PV Systems", "Battery", "HVAC", "DHW"
    ]
    st.header("Sensitivity Analysis")

    if 'api_sensitivity_url' not in st.session_state:
        st.session_state.api_sensitivity_url = "http://localhost:5000/api/simulations/quaci/sensitivity"

    if len(st.session_state.selected_houses) > 0:
        with st.expander("Sensitivity Analysis Parameters", expanded=True):
            st.write("Analyze parameter influence on environmental impact")

            # Get first selected house
            selected_house = st.session_state.selected_houses[0]

            # Create form for parameters
            with st.form("sensitivity_parameters"):
                col1, col2 = st.columns(2)

                with col1:
                    perturbation = st.number_input(
                        "Perturbation Percentage",
                        min_value=0.01,
                        max_value=1.0,
                        value=0.1,
                        step=0.01,
                        format="%.2f"
                    )

                with col2:
                    st.write("Current Lifespan Parameters")
                    st.write(
                        f"Mean: {selected_house.get('dur_vie_mean', 50.0)}")
                    st.write(
                        f"Std Dev: {selected_house.get('dur_vie_std_dev', 2.5)}")

                if st.form_submit_button("Run Sensitivity Analysis"):
                    try:
                        # Prepare request data
                        request_data = {
                            "comp_quantity": {k: v for k, v in selected_house.items()
                                              if k in material_names and isinstance(v, (int, float))},
                            "building_type": selected_house['Building_Name'],
                            "dur_vie_mean": float(selected_house.get('dur_vie_mean', 50.0)),
                            "dur_vie_std_dev": float(selected_house.get('dur_vie_std_dev', 2.5)),
                            "perturbation_percent": float(perturbation)
                        }

                        # Call sensitivity API
                        response = requests.post(
                            st.session_state.api_sensitivity_url,
                            json=request_data
                        )

                        if response.status_code == 200:
                            results = response.json()
                            st.session_state.sensitivity_results = results
                        else:
                            st.error(
                                f"API Error: {response.json().get('error', 'Unknown error')}")

                    except Exception as e:
                        st.error(f"Sensitivity analysis failed: {str(e)}")

        # Display results if available
        if 'sensitivity_results' in st.session_state:
            results = st.session_state.sensitivity_results

            st.subheader("Sensitivity Analysis Results")

            # Show baseline and parameters
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Baseline Impact", f"{results['baseline']:.2f}")
            with col2:
                st.metric("Perturbation Used",
                          f"{results['perturbation_percent']*100:.1f}%")

            # Create dataframe from results
            df = pd.DataFrame(results['results'])

            # Show top 10 parameters
            st.write("### Most Influential Parameters")
            top_params = df.head(10)

            # Display bar chart
            fig = px.bar(top_params,
                         x='RI',
                         y='Parameter',
                         orientation='h',
                         title="Relative Influence of Parameters",
                         labels={'RI': 'Relative Influence'})
            st.plotly_chart(fig, use_container_width=True)

            # Show full table
            st.write("### Complete Sensitivity Results")
            st.dataframe(df)

    else:
        st.info(
            "Select a building from the table above to perform sensitivity analysis")


def sensitivity_analysis():

    material_names = [
        "ExternalWood", "OSB", "Poutrelle", "Beam", "Parquet", "Steel",
        "Glazing", "Wool", "WaterProofing", "Polystyrene", "Gypsum", "Aluminium", "Paint",
        "Mortar", "Cinderblock", "FiredBricks", "Earth", "Hemp", "Concrete",
        "PV Systems", "Battery", "HVAC", "DHW"
    ]
    st.subheader("Sensitivity Analysis")

    with st.expander("Configure Sensitivity Analysis"):
        perturbation = st.number_input(
            "Perturbation Percentage (%)",
            min_value=1.0,
            max_value=100.0,
            value=10.0
        ) / 100

        if st.button("Run Sensitivity Analysis"):
            if len(st.session_state.selected_houses) == 0:
                st.error("Please select a house to analyze first!")
                return

            if 'Impact_Data' not in st.session_state:
                st.error("Please run Environmental Impact Analysis first!")
                return

            selected_house = st.session_state.selected_houses.iloc[0].to_dict()
            baseline_data = {
                "comp_quantity": {k: v for k, v in selected_house.items() if k in material_names},
                "building_type": selected_house['Building_Name'],
                "dur_vie_mean": st.session_state.get('dur_vie_mean', 50.0),
                "dur_vie_std_dev": st.session_state.get('dur_vie_std_dev', 2.5)
            }

            # Get baseline result
            try:
                baseline_response = requests.post(
                    st.session_state.api_url,
                    json=baseline_data
                )
                baseline_result = pd.DataFrame(baseline_response.json())
                baseline_value = baseline_result['Row Total'].mean()
            except Exception as e:
                st.error(f"Baseline analysis failed: {str(e)}")
                return

            # Prepare parameters to test
            parameters = list(baseline_data['comp_quantity'].keys()) + \
                ['dur_vie_mean', 'dur_vie_std_dev']

            results = []
            progress_bar = st.progress(0)
            total_params = len(parameters)

            for idx, param in enumerate(parameters):
                progress_bar.progress((idx + 1) / total_params)

                modified_data = baseline_data.copy()

                try:
                    if param in ['dur_vie_mean', 'dur_vie_std_dev']:
                        original_value = modified_data[param]
                        modified_value = original_value * (1 + perturbation)
                        modified_data[param] = modified_value
                    else:
                        original_value = modified_data['comp_quantity'][param]
                        modified_value = original_value * (1 + perturbation)
                        modified_data['comp_quantity'][param] = modified_value

                    # Call API with modified parameter
                    response = requests.post(
                        st.session_state.api_url,
                        json=modified_data
                    )

                    if response.status_code == 200:
                        result = pd.DataFrame(response.json())
                        perturbed_value = result['Row Total'].mean()
                        delta_y = perturbed_value - baseline_value
                        sensitivity_index = (
                            delta_y / baseline_value) / perturbation
                        results.append({
                            'Parameter': param,
                            'Baseline Value': original_value,
                            'Perturbed Value': modified_value,
                            'Delta (%)': delta_y / baseline_value * 100,
                            'Sensitivity Index': sensitivity_index
                        })
                    else:
                        st.warning(
                            f"Failed to analyze {param}: {response.text}")

                except Exception as e:
                    st.warning(f"Error analyzing {param}: {str(e)}")
                    continue

            if results:
                # Calculate relative influence
                df = pd.DataFrame(results)
                df['Absolute Sensitivity'] = df['Sensitivity Index'].abs()
                total_sensitivity = df['Absolute Sensitivity'].sum()
                df['Relative Influence (%)'] = (
                    df['Absolute Sensitivity'] / total_sensitivity) * 100
                df = df.sort_values('Relative Influence (%)', ascending=False)

                # Store and display results
                st.session_state.sensitivity_results = df
                st.subheader("Sensitivity Analysis Results")
                st.dataframe(df)

                # Show top parameters
                st.subheader("Most Influential Parameters")
                top_params = df.head(5)
                st.bar_chart(top_params.set_index('Parameter')
                             ['Relative Influence (%)'])

                # Download button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Sensitivity Results",
                    data=csv,
                    file_name=f"{selected_house['Building_Name']}_sensitivity.csv",
                    mime="text/csv"
                )
            else:
                st.error("Sensitivity analysis failed for all parameters")


# Add this to your existing Environmental Impact Analysis section
# Right after the existing download button:


if __name__ == "__main__":
    main()
