"""
Copenhagenize Index Simulator
==============================
Tool to simulate how a city would score on the Copenhagenize Index.

The simulator compares user-inputted city metrics against 100 established cities
across 13 key indicators organized into 3 pillars:
  1. Safe & Connected Infrastructure
  2. Usage & Reach
  3. Policy & Support

Author: Laura Hernández Alzate & Copenhagenize Design Co.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import warnings
import streamlit.components.v1 as components

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="City Simulator - Copenhagenize Index",
    page_icon="🧮",
    layout="wide"
)
st.markdown("""
    <style>
    .block-container {
        padding-top: 3.5rem !important; 
    }
    </style>
""", unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 15])
with col_logo:
    st.image("logo.png", width=100)
with col_title:
    st.title("Copenhagenize Index Simulator")
st.markdown(
    '<p class="hide-on-print">Input your city\'s data below to see how it would '
    'score and rank against the Global Top 100 cycling cities.</p>',
    unsafe_allow_html=True
)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_data():
    """
    Load baseline Copenhagenize Index data from CSV with encoding fallback.
    
    Returns:
        pd.DataFrame: Master data containing reference cities and their scores
        
    Raises:
        FileNotFoundError: If CSV file is not found in the working directory
    """
    try:
        df = pd.read_csv("master_copenhagenize_data.csv", encoding='utf-8')
    except UnicodeDecodeError:
        # Fallback to Windows encoding if UTF-8 fails
        df = pd.read_csv("master_copenhagenize_data.csv", encoding='cp1252')
    except FileNotFoundError:
        st.error("❌ Data file 'master_copenhagenize_data.csv' not found. "
                 "Please ensure it's in the working directory.")
        st.stop()
    return df

df = load_data()

# ============================================================================
# INPUT FORM - CITY SIMULATOR DATA
# ============================================================================

with st.form("simulator_form"):
    st.subheader("🏙️ City Basics")
    col1, col2 = st.columns(2)
    sim_city = col1.text_input("City Name", value="Berlin")
    sim_pop = col2.text_input(
        "Population", 
        value="3685265",

    )
    
    st.markdown("---")
    
    # PILLAR 1: Safe & Connected Infrastructure
    st.subheader("🚧 Pillar 1: Safe & Connected Infrastructure")
    
    st.markdown("**Infrastructure & Traffic Calming**")
    col_i1, col_i2, col_i3 = st.columns(3)
    
    sim_prot_km = col_i1.text_input(
        "Protected Bicycle Infrastructure (Km)",
        value="36.9",
        placeholder="N/A",
        help="Km of physically protected cycling space"
    )
    sim_street_km = col_i2.text_input(
        "Total Roadway Network (Km)",
        value="5350.0",
        placeholder="N/A",
        help="Total length of all streets in the city"
    )
    sim_30_km = col_i3.text_input(
        "Streets with 30km/h Limit (Km)",
        value="3820.0",
        placeholder="N/A",
        help="Km of streets with speed limit of 30 km/h or less"
    )
    
    st.markdown("**Parking & Safety**")
    col_i4, col_i5, col_i6 = st.columns(3)
    
    sim_pub_park = col_i4.text_input(
        "Public Bike Parking Spaces",
        value="6100",
        placeholder="N/A",
        help="Total number of public bike parking stands"
    )
    sim_enc_park = col_i5.text_input(
        "Enclosed Parking Spaces",
        value="467",
        placeholder="N/A",
        help="Secure/roofed bike parking spaces"
    )
    sim_deaths = col_i6.text_input(
        "Average Annual Biking Fatalities (past 5 years)",
        value="12.0",
        placeholder="N/A",
        help="Average yearly cyclist deaths"
    )

    st.markdown("---")
    
    # PILLAR 2: Usage & Reach
    st.subheader("🚲 Pillar 2: Usage & Reach")
    
    st.markdown("**Bicycle Modal Share**")
    col_u1, col_u2, col_u3 = st.columns(3)
    
    sim_modal_now = col_u1.text_input(
        "Current Modal Share (%)",
        value="18.0",
        placeholder="N/A",
        help="% of trips made by bicycle (current year)"
    )
    sim_modal_past = col_u2.text_input(
        "Pre-Covid Modal Share (%)",
        value="18.0",
        placeholder="N/A",
        help="% of trips made by bicycle (2019 or baseline)"
    )
    sim_women = col_u3.text_input(
        "Women Share of bicycle trips (%)",
        value="47.0",
        placeholder="N/A",
        help="% of bicycle trips made by women"
    )

    st.markdown("**Bike Share System**")
    col_u4, col_u5, col_u6 = st.columns(3)
    
    sim_bs_fleet = col_u4.text_input(
        "Bike Share Fleet Size",
        value="6300",
        placeholder="N/A",
        help="Total number of bikes in bike-sharing system"
    )
    sim_bs_trips = col_u5.text_input(
        "Annual Bike Share Trips",
        value="10685",
        placeholder="N/A",
        help="Bike share total annual trips"
    )
    pol_pt_integ = col_u6.checkbox(
        "Public Transit Integration (Bike Share System)",
        value=False,
        help="Can users use bike share with public transit passes?"
    )

    st.markdown("**Cargo Bikes**")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        pol_subsidy_hh = st.checkbox(
            "Household purchase subsidy",
            value=False,
            help="City subsidizes cargo bikes for residents"
        )
        pol_subsidy_biz = st.checkbox(
            "Logistics/business subsidy or dedicated support",
            value=True,
            help="City supports cargo bikes for logistics"
        )
    with col_c2:
        pol_cargo_biz = st.checkbox(
            "Cargo bike commercial or informal adoption",
            value=True,
            help="Businesses use cargo bikes in practice"
        )
        pol_cargo_infra = st.checkbox(
            "Cargo-bike infrastructure standards",
            value=True,
            help="City has dedicated cargo bike infrastructure"
        )
    
    st.markdown("---")
    
    # PILLAR 3: Policy & Support
    st.subheader("📜 Pillar 3: Policy & Support")
    
    st.markdown("**Political Commitment & Urban Planning**")
    col_p1, col_p2 = st.columns(2)
    
    sim_budget = col_p1.text_input(
        "Total 5-Year Bicycle Budget (€)",
        value="142100000",
        placeholder="N/A",
        help="Total municipal budget for cycling infrastructure/programs (5 years)"
    )
    sim_3yr_km = col_p2.text_input(
        "New Lanes Built in Last 3 Years (Km)",
        value="22.3",
        placeholder="N/A",
        help="Km of new protected bike lanes built recently"
    )

    col_p3, col_p4, col_p5 = st.columns(3)
    with col_p3:
        st.markdown("**Urban Planning Policies**")
        pol_masterplan = st.checkbox("Adopted Cycling Masterplan", value=True)
        pol_unit = st.checkbox("Dedicated Cycling Unit", value=True)
        pol_standards = st.checkbox("Official Design Standards", value=False)
        pol_monitor = st.checkbox("Annual Data Monitoring", value=True)
    with col_p4:
        st.markdown("**Advocacy & Community**")
        pol_ngo_exists = st.checkbox("Active Bicycle NGO", value=True)
        pol_ngo_events = st.checkbox("NGO Hosts Major Events", value=True)
        pol_ngo_policy = st.checkbox("NGO Influences City Policy", value=True)
    with col_p5:
        st.markdown("**Image of the Bicycle**")
        pol_media = st.checkbox("Media Tone 70%+ Positive", value=False)
        pol_brand = st.checkbox("Bicycle Brand/Network Identity", value=True)
        pol_school = st.checkbox("School Cycling Education Program", value=True)
        
    st.markdown("---")
    submit_button = st.form_submit_button(label="🚀 Simulate City's Score")

# ============================================================================
# CALCULATION ENGINE - SCORING LOGIC
# ============================================================================

if submit_button:
    st.session_state.simulation_submitted = True

if st.session_state.get('simulation_submitted', False):
    
    # ====================================================================
    # STEP 0: Convert text input to float or None (missing data handling)
    # ====================================================================
    def text_to_number(val):
        """Convert text input to float or None if empty/invalid."""
        if val is None or val.strip() == "":
            return None
        try:
            return float(val)
        except ValueError:
            return None
    
    # Convert all text inputs to numbers or None
    sim_pop = text_to_number(sim_pop)
    sim_prot_km = text_to_number(sim_prot_km)
    sim_street_km = text_to_number(sim_street_km)
    sim_30_km = text_to_number(sim_30_km)
    sim_pub_park = text_to_number(sim_pub_park)
    sim_enc_park = text_to_number(sim_enc_park)
    sim_deaths = text_to_number(sim_deaths)
    sim_modal_now = text_to_number(sim_modal_now)
    sim_modal_past = text_to_number(sim_modal_past)
    sim_women = text_to_number(sim_women)
    sim_bs_fleet = text_to_number(sim_bs_fleet)
    sim_bs_trips = text_to_number(sim_bs_trips)
    sim_budget = text_to_number(sim_budget)
    sim_3yr_km = text_to_number(sim_3yr_km)

    # CHECK MISSING DATA POINTS
    raw_inputs = [sim_pop, sim_prot_km, sim_street_km, sim_30_km, sim_pub_park, sim_enc_park, 
                  sim_deaths, sim_modal_now, sim_modal_past, sim_women, sim_bs_fleet, sim_bs_trips, 
                  sim_budget, sim_3yr_km]
    missing_count = sum(1 for x in raw_inputs if x is None)
    
    if missing_count > 4:
        st.warning(f"⚠️ **Low Reliability Warning:** {missing_count} numeric data points are missing. "
                   "The simulated score's accuracy and global ranking comparability are reduced.")
    
    def safe_div(num, den, multiplier=1.0):
        """
        Safely divide two numbers, handling None, NaN, and zero division.
        
        Args:
            num (float): Numerator
            den (float): Denominator
            multiplier (float): Multiplier to scale result (default: 1.0)
            
        Returns:
            float: Result of (num/den) * multiplier, or np.nan if calculation not possible
        """
        if num is None or den is None or pd.isna(num) or pd.isna(den) or den == 0:
            return np.nan
        return (num / den) * multiplier

    def normalize(val, col_name, invert=False):
        """
        Normalize a value to 0-100 scale based on min-max from reference cities.
        
        Uses min-max normalization: (value - min) / (max - min) * 100
        This makes scores comparable across different measurement units.
        
        Args:
            val (float): Value to normalize
            col_name (str): Column name in reference dataset
            invert (bool): If True, invert scale (lower values = better). Default False.
            
        Returns:
            float: Normalized score 0-100, or np.nan if normalization not possible
        """
        if pd.isna(val) or val is None: 
            return np.nan
        if col_name not in df.columns: 
            return np.nan
        
        # Get min-max range from reference cities
        c_max = df[col_name].max()
        c_min = df[col_name].min()
        if c_max == c_min:
            return 0
        
        # Min-max normalization
        score = ((val - c_min) / (c_max - c_min)) * 100
        if invert:
            score = 100 - score
        return max(0, min(100, score)) 
    
    # --- Specific indicators thresholds ---
    def get_bike_share_cov_score(val):
        
        if pd.isna(val): return 0
        if val >= 8: return 4
        if val >= 5: return 3
        if val >= 3: return 2
        if val >= 1: return 1
        return 0

    def get_bike_share_usage_score(val):
        
        if pd.isna(val): return 0
        if val > 5: return 4 
        if val >= 3: return 3
        if val >= 1.75: return 2
        if val >= 1: return 1
        return 0

    def get_infra_increase_score(val):
        
        if pd.isna(val): return 0
        if val == 0.0: return 0
        if val < 0.25: return 1
        if val < 0.75: return 2
        if val < 1.25: return 3
        if val < 2.0: return 4
        if val < 3.5: return 5
        return 6

    # ====================================================================
    # STEP A: Calculate Raw Metrics (Densities, Rates, Ratios)
    # ====================================================================
    # Raw metrics transform input data into comparable density/rate metrics:
    # - Densities normalize against total road km or population
    # - Rates normalize against population for fair comparison across city sizes
    
    infra_dens = safe_div(sim_prot_km, sim_street_km, 100)  # % of roads with protection
    
    # Parking: count both public spaces (×2 weight) + enclosed spaces for total capacity
    park_num = (sim_pub_park * 2) + sim_enc_park if (sim_pub_park is not None and sim_enc_park is not None) else None
    parking_dens = safe_div(park_num, sim_pop, 1000)  # Parks per 1K residents
    
    traffic_30_pct = safe_div(sim_30_km, sim_street_km, 100)  # % of roads with 30km/h limit
    safety_rate = safe_div(sim_deaths, sim_pop, 100000)  # Deaths per 100K residents
    
    modal_delta = (sim_modal_now - sim_modal_past) if (sim_modal_now is not None and sim_modal_past is not None) else np.nan
    
    bs_cov = safe_div(sim_bs_fleet, sim_pop, 1000)  # Bikes per 1K residents
    if sim_bs_trips == 0 and sim_bs_fleet == 0:
        bs_usage = 0
    elif sim_bs_fleet == 0 or sim_bs_fleet is None or pd.isna(sim_bs_fleet):
        bs_usage = np.nan
    else:
        # Convert annual trips to daily trips per bike
        bs_usage = safe_div(sim_bs_trips, sim_bs_fleet * 365, 1)
    
    # Budget per capita: average the 5-year budget over years then divide by population
    spending_pc = safe_div((sim_budget / 5) if sim_budget is not None else None, sim_pop, 1)
    infra_inc = safe_div(sim_3yr_km, sim_street_km, 100)  # % of roads upgraded recently
    
    # ====================================================================
    # STEP B: Normalize Metrics to 0-100 Scores
    # ====================================================================
    # Each metric is normalized using the baseline dataset as reference.
    
    n_infra = normalize(infra_dens, 'Infra_density (km of bicycle infra/100 km of roadway)')
    n_park = normalize(parking_dens, 'Parking_density (stands/1K pop)')
    n_traf = normalize(traffic_30_pct, 'Traffic_30 (% of km of roadway)')
    n_safe = normalize(safety_rate, 'Safety_rate (rate/100K pop)', invert=True)  # Inverted: lower deaths = better
    n_women = normalize(sim_women, 'Bike_trips_women_%')
    n_modal = normalize(sim_modal_now, 'Modal_share_2024_% \n(or nearest post-Covid)')
    n_mod_inc = normalize(modal_delta, 'Modal_delta (percentage points)')
    n_spend = normalize(spending_pc, 'Spending_per_capita (€/capita/year)')

    # ====================================================================
    # STEP C: Calculate 13 Indicator Scores
    # ====================================================================
    # Individual indicators are grouped into composite metrics for the 3 pillars.
    # Boolean policies are averaged to a 0-100 scale (e.g., 4 policies = 25 pts each if all yes).
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        
        # Infrastructure & Safety scores (Pillar 1 components)
        score_infrastructure = n_infra
        score_parking = n_park
        score_traffic = n_traf
        score_safety = n_safe
        
        # Usage & Reach scores (Pillar 2 components)
        score_women_final = n_women
        score_modal_final = n_modal
        score_mod_inc_final = n_mod_inc
        score_cargo_bikes = sum([pol_subsidy_hh, pol_subsidy_biz, pol_cargo_biz, pol_cargo_infra]) / 4 * 100
        
        # Bike Share System logic (0-9 scale converted to 0-100)
        if pd.isna(bs_cov) and pd.isna(bs_usage):
            score_bike_share = np.nan
        else:
            cov_score = get_bike_share_cov_score(bs_cov) if pd.notna(bs_cov) else 0
            use_score = get_bike_share_usage_score(bs_usage) if pd.notna(bs_usage) else 0
            pt_score = 1 if pol_pt_integ else 0
            # TEMPORARY verification outputs for bike share scoring logic
            #st.write(f"Raw Coverage Density: {bs_cov:.2f} -> Points: {cov_score}")
            #st.write(f"Raw Daily Usage Rate: {bs_usage:.2f} -> Points: {use_score}")
            #st.write(f"PT Points: {pt_score}")
            score_bike_share = ((cov_score + use_score + pt_score)) * 100/9
        
        # Policy & Support scores (Pillar 3 components)
        score_political = n_spend
        score_advocacy = sum([pol_ngo_exists, pol_ngo_events, pol_ngo_policy]) / 3 * 100
        score_image = sum([pol_media, pol_brand, pol_school]) / 3 * 100
                
        # Urban Planning logic (0-10 scale converted to 0-100)
        infra_inc_score = get_infra_increase_score(infra_inc) if pd.notna(infra_inc) else 0
        plan_bin = sum([pol_masterplan, pol_unit, pol_standards, pol_monitor])
        score_urban_plan = (infra_inc_score + plan_bin) * 10

        # ====================================================================
        # STEP D: Calculate 3 Pillars and Composite Index Score
        # ====================================================================
        # The overall Copenhagenize Index score is the average of 3 pillars:
        #
        # Pillar 1: Safe & Connected Infrastructure
        #   - Physical conditions for cycling (lanes, parking, safety)
        #   - Urban planning investment
        #
        # Pillar 2: Usage & Reach
        #   - Actual adoption by residents (Bicycle Modal Share, women participation)
        #   - Specialized services (cargo bikes, bike share system)
        #
        # Pillar 3: Policy & Support
        #   - Municipal financial commitment
        #   - Advocacy groups and community engagement
        #   - Public image and education
        
        score_modal_share_group = np.nanmean([score_women_final, score_modal_final, score_mod_inc_final])
        
        pillar_safe = np.nanmean([score_infrastructure, score_parking, score_traffic, score_safety, score_urban_plan])
        pillar_usage = np.nanmean([score_modal_share_group, score_cargo_bikes, score_bike_share])
        pillar_policy = np.nanmean([score_political, score_advocacy, score_image, score_urban_plan])
        
        composite_score = np.nanmean([pillar_safe, pillar_usage, pillar_policy])
        
    # ====================================================================
    # Determine Hypothetical Global Rank
    # ====================================================================
    # Rank the simulated city against all reference cities based on composite score.
    # Returns rank 1-100 based on how many reference cities score higher.
    
    hypothetical_rank = "N/A"
    context_table = None

    if pd.notna(composite_score):
        target_col = 'Composite Index Score' if 'Composite Index Score' in df.columns else 'Index Score'
        
        if target_col in df.columns:
            # Create a clean temp dataframe for ranking
            temp_df = df[['City', target_col]].dropna().copy()
            
            # Append our simulated city
            sim_name_label = f"📍 {sim_city} (Simulated)"
            sim_row = pd.DataFrame({'City': [sim_name_label], target_col: [composite_score]})
            temp_df = pd.concat([temp_df, sim_row], ignore_index=True)
            
            # Sort by score and generate dense ranks
            temp_df = temp_df.sort_values(by=target_col, ascending=False).reset_index(drop=True)
            temp_df['Rank'] = temp_df.index + 1
            
            # Find where the simulated city landed
            sim_idx = temp_df[temp_df['City'] == sim_name_label].index[0]
            hypothetical_rank = int(temp_df.loc[sim_idx, 'Rank'])
            
            # Extract 3 above and 3 below (safeguard against edges)
            start_idx = max(0, sim_idx - 3)
            end_idx = min(len(temp_df), sim_idx + 4)
            
            context_table = temp_df.iloc[start_idx:end_idx].copy()
            context_table[target_col] = context_table[target_col].map("{:.1f}".format)
            context_table.columns = ['City', 'Composite Score', 'Global Rank']
            context_table = context_table[['Global Rank', 'City', 'Composite Score']] # Reorder for display

            
    # ====================================================================
    # DISPLAY RESULTS - SUMMARY CARD & VISUALIZATIONS
    # ====================================================================
    
    st.markdown("""
        <style>
        /* Print layout optimization */
        @page {
            margin: 0.5cm;
        }
        .block-container {
            padding-top: 0rem !important; 
            padding-bottom: 0rem !important;
        }
        @media print {
            /* Added stDataFrame to the hidden list */
            header, h1, .hide-on-print, div[data-testid="stForm"], iframe, div[data-testid="stSelectbox"], div[data-testid="stDataFrame"] { 
                display: none !important; 
            }
            .stApp { margin-top: -80px; }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Results header
    st.header(f"Copenhagenize Index Simulation: {sim_city}")
    
    # Summary metrics in two columns
    res_col1, res_col2 = st.columns([1, 1.5])
    
    with res_col1:
        # Key Metrics & Pillar Scores
        m1, m2 = st.columns(2)
        m1.metric(
            label="Simulated Index Score",
            value=f"{composite_score:.1f} / 100" if pd.notna(composite_score) else "N/A"
        )
        m2.metric(
            label="Hypothetical Global Rank",
            value=f"#{hypothetical_rank}" if hypothetical_rank != "N/A" else "N/A"
        )
        
        st.markdown("<br> Pillar Breakdown", unsafe_allow_html=True)
        
        # Progress bar for each pillar with descriptive text
        p_safe_val = int(pillar_safe) if pd.notna(pillar_safe) else 0
        p_safe_text = f"Infrastructure & Safety: {pillar_safe:.1f}" if pd.notna(pillar_safe) else "Infrastructure & Safety: N/A"
        st.progress(p_safe_val, text=p_safe_text)
        
        p_use_val = int(pillar_usage) if pd.notna(pillar_usage) else 0
        p_use_text = f"Usage & Reach: {pillar_usage:.1f}" if pd.notna(pillar_usage) else "Usage & Reach: N/A"
        st.progress(p_use_val, text=p_use_text)
        
        p_pol_val = int(pillar_policy) if pd.notna(pillar_policy) else 0
        p_pol_text = f"Policy & Support: {pillar_policy:.1f}" if pd.notna(pillar_policy) else "Policy & Support: N/A"
        st.progress(p_pol_val, text=p_pol_text)
        
    with res_col2:
        
        # --- REGION SELECTOR FOR RADAR CHART ---
        if 'Continent' in df.columns:
            regions = sorted([str(x) for x in df['Continent'].dropna().unique()])
        else:
            regions = ["Europe", "North America", "South America", "Asia & Oceania", "Africa"]
            
        sim_region = st.selectbox("🌍 Select Regional Benchmark to Compare", ["None (Top 30 Only)"] + regions)
        
        # 1. ORGANIZE RADAR COLUMNS BY PILLAR
        radar_columns = [
            # Safe & Connected Infrastructure (Blue)
            'Bicycle Infrastructure Score', 'Bicycle Parking Score', 'Traffic Calming Score', 'Safety Score',
            # Usage & Reach (Orange)
            'Bicycle Modal Share Score', 'Modal Share Growth Score', 'Women Share Score', 'Bike Share System Score', 'Cargo Bikes Score',
            # Policy & Support (Purple)
            'Political Commitment Score', 'Cycling Advocacy Score', 'Image of the Bicycle Score', 'Urban Planning Score'
        ]
        
        simulated_values = [
            score_infrastructure, score_parking, score_traffic, score_safety,
            score_modal_final, score_mod_inc_final, score_women_final, score_bike_share, score_cargo_bikes,
            score_political, score_advocacy, score_image, score_urban_plan
        ]
        
        # 2. COLOR CODE LABELS USING HTML
        raw_labels = [c.replace(' Score', '') for c in radar_columns]
        radar_labels = [
            f"<span style='color:#1f77b4'><b>{l}</b></span>" for l in raw_labels[:4]    # Infrastructure: Blue
        ] + [
            f"<span style='color:#ff7f0e'><b>{l}</b></span>" for l in raw_labels[4:9]   # Usage: Orange
        ] + [
            f"<span style='color:#9467bd'><b>{l}</b></span>" for l in raw_labels[9:]    # Policy: Purple
        ]
        
        # 3. GET AVERAGES (Top 30 and Region)
        def get_radar_averages(df_subset, columns_list):
            avg_list = []
            for col in columns_list:
                alt_col = "Score " + col.replace(" Score", "")
                target_col = col if col in df_subset.columns else (alt_col if alt_col in df_subset.columns else None)
                if target_col:
                    clean_series = df_subset[target_col].astype(str).str.replace(',', '.').str.strip()
                    mean_val = pd.to_numeric(clean_series, errors='coerce').mean()
                    avg_list.append(mean_val if pd.notna(mean_val) else None)
                else:
                    avg_list.append(None)
            return avg_list

        # Top 30 Average
        top_30_df = df.nsmallest(30, 'Rank') if 'Rank' in df.columns else df.head(30)
        top_30_avg = get_radar_averages(top_30_df, radar_columns)

        # Selected Regional Average
        region_avg = []
        if sim_region != "None (Top 30 Only)" and 'Continent' in df.columns:
            region_df = df[df['Continent'] == sim_region]
            if not region_df.empty:
                region_avg = get_radar_averages(region_df, radar_columns)
        
        # 4. CLOSE POLYGONS
        closed_theta = radar_labels + [radar_labels[0]]
        closed_sim = [None if pd.isna(v) else v for v in (simulated_values + [simulated_values[0]])]
        
        closed_top30 = [None if pd.isna(v) else v for v in top_30_avg]
        if closed_top30: closed_top30.append(closed_top30[0]) 

        fig_radar = go.Figure()
        
        # Trace 1: Simulated City
        fig_radar.add_trace(go.Scatterpolar(
            r=closed_sim, theta=closed_theta,
            fill='toself', name=sim_city, line=dict(color='#1BBBEC', width=3), connectgaps=True 
        ))
        
        # Trace 2: Global Top 30
        if any(v is not None for v in top_30_avg):
            fig_radar.add_trace(go.Scatterpolar(
                r=closed_top30, theta=closed_theta,
                fill='none', name='Global Top 30 Avg', line=dict(color='#D53C4C', width=2, dash='dash'), connectgaps=True
            ))
            
        # Trace 3: Regional Average (If selected)
        if region_avg and any(v is not None for v in region_avg):
            closed_region = [None if pd.isna(v) else v for v in region_avg]
            closed_region.append(closed_region[0])
            fig_radar.add_trace(go.Scatterpolar(
                r=closed_region, theta=closed_theta,
                fill='none', name=f'{sim_region} Avg', line=dict(color='#28A745', width=2, dash='dot'), connectgaps=True
            ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True, 
            height=450, 
            margin=dict(t=30, b=30, l=60, r=60),
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5) 
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        

    # ====================================================================
    # STRENGTHS, AREAS FOR IMPROVEMENT, GLOBAL CONTEXT
    # ====================================================================
    # Identify the top 3 scoring and lowest scoring indicators to help cities
    # understand where they excel and where to focus improvement efforts.
    
    st.markdown("---")
    
    score_dict = dict(zip(raw_labels, simulated_values))
    valid_scores = {k: v for k, v in score_dict.items() if pd.notna(v)}
    sorted_scores = sorted(valid_scores.items(), key=lambda item: item[1], reverse=True)
    
    top_3 = sorted_scores[:3]
    bottom_3 = sorted_scores[-3:][::-1] 

    col_str, col_imp, col_rank = st.columns([1, 1, 1.5])
    
    with col_str:
        st.success("🌟 **Top 3 Strengths**")
        for idx, (label, score) in enumerate(top_3):
            st.markdown(f"**{idx+1}. {label}** ({score:.1f}/100)")
            
    with col_imp:
        st.error("📈 **Areas for Improvement**")
        for idx, (label, score) in enumerate(bottom_3):
            st.markdown(f"**{idx+1}. {label}** ({score:.1f}/100)")
            
    with col_rank:
        st.info("🏆 **Comparative Ranking**")
        if context_table is not None:
            def highlight_simulated(row):
                if "(Simulated)" in row['City']:
                    return ['background-color: #1BBBEC; color: white'] * len(row)
                return [''] * len(row)
                
            styled_table = context_table.style.apply(highlight_simulated, axis=1).hide(axis="index")
            st.write(styled_table.to_html(), unsafe_allow_html=True)
        else:
            st.write("Ranking data unavailable.")

    # ====================================================================
    # SCORING TABLE (Numeric Scores display)
    # ====================================================================
    st.markdown("---")
    st.markdown("### 📋 Scoring Table")
    
    # Create a cleaner DataFrame purely for displaying the values to the user
    display_df = pd.DataFrame({
        "Indicator": raw_labels,
        "Simulated Score (0-100)": simulated_values
    })
    display_df["Simulated Score (0-100)"] = display_df["Simulated Score (0-100)"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
    
    st.dataframe(display_df, width=500, hide_index=True)

    # ====================================================================
    # EXPORT TO PDF
    # ====================================================================
    # Summary card that users can save as PDF.
    
    components.html(
        '''
        <div style="text-align: center; margin-top: 50px;">
            <button onclick="window.parent.print()" 
                    style="padding: 14px 24px; font-size: 16px; font-weight: bold; 
                           background-color: #1BBBEC; color: white; border: none; 
                           border-radius: 5px; cursor: pointer; 
                           box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">
                🖨️ Print Summary Card
            </button>
            <p style="font-family: sans-serif; color: #666; font-size: 14px; margin-top: 10px;">
                💡 Tip: Use landscape orientation and enable "Background graphics" in your print settings.
            </p>
        </div>
        ''',
        height=100
    )
