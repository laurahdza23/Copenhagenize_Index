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
    sim_pop = col2.number_input("Population", value=3685265, placeholder="N/A")
    
    st.markdown("---")
    
    # PILLAR 1: Safe & Connected Infrastructure
    st.subheader("🚧 Pillar 1: Safe & Connected Infrastructure")
    
    st.markdown("**Infrastructure & Traffic Calming**")
    col_i1, col_i2, col_i3 = st.columns(3)
    sim_prot_km = col_i1.number_input(
        "Protected Bicycle Infrastructure (Km)",
        value=36.9,
        help="Km of physically protected cycling space",
        placeholder="N/A"
    )
    sim_street_km = col_i2.number_input(
        "Total Roadway Network (Km)",
        value=5350.0,
        help="Total length of all streets in the city",
        placeholder="N/A"
    )
    sim_30_km = col_i3.number_input(
        "Streets with 30km/h Limit (Km)",
        value=3820.0,
        help="Km of streets with speed limit of 30 km/h or less",
        placeholder="N/A"
    )
    
    st.markdown("**Parking & Safety**")
    col_i4, col_i5, col_i6 = st.columns(3)
    sim_pub_park = col_i4.number_input(
        "Public Bike Parking Spaces",
        value=6100,
        help="Total number of public bike parking stands",
        placeholder="N/A"
    )
    sim_enc_park = col_i5.number_input(
        "Enclosed Parking Spaces",
        value=467,
        help="Secure/roofed bike parking spaces",
        placeholder="N/A"
    )
    sim_deaths = col_i6.number_input(
        "Average Annual Biking Fatalities (past 5 years)",
        value=12.0,
        help="Average yearly cyclist deaths",
        placeholder="N/A"
    )

    st.markdown("---")
    
    # PILLAR 2: Usage & Reach
    st.subheader("🚲 Pillar 2: Usage & Reach")
    
    st.markdown("**Modal Share**")
    col_u1, col_u2, col_u3 = st.columns(3)
    sim_modal_now = col_u1.number_input(
        "Current Modal Share (%)",
        value=18.0,
        help="% of trips made by bicycle (current year)",
        placeholder="N/A"

    )
    sim_modal_past = col_u2.number_input(
        "Pre-Covid Modal Share (%)",
        value=18.0,
        help="% of trips made by bicycle (2019 or baseline)",
        placeholder="N/A"
    )
    sim_women = col_u3.number_input(
        "Women Share of bicycle trips (%)",
        value=47.0,
        help="% of bicycle trips made by women",
        placeholder="N/A"
    )

    st.markdown("**Bike Share**")
    col_u4, col_u5, col_u6 = st.columns(3)
    sim_bs_fleet = col_u4.number_input(
        "Bike Share Fleet Size",
        value=6300,
        help="Total number of bikes in bike-sharing system",
        placeholder="N/A"
    )
    sim_bs_trips = col_u5.number_input(
        "Daily Bike Share Trips",
        value=10685,
        help="Average bike-share trips per day",
        placeholder="N/A"
    )
    pol_pt_integ = col_u6.checkbox(
        "Public Transit Integration (Bike Share)",
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
    sim_budget = col_p1.number_input(
        "Total 5-Year Bicycle Budget (€)",
        value=142100000,
        help="Average total municipal budget for cycling infrastructure/programs (5 years)",
        placeholder="N/A"
    )
    sim_3yr_km = col_p2.number_input(
        "New Lanes Built in Last 3 Years (Km)",
        value=22.3,
        help="Km of new protected bike lanes built recently",
        placeholder="N/A"
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
    bs_usage = safe_div(sim_bs_trips, sim_bs_fleet, 1)  # Trips per bike per day
    
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
    n_bs_cov = normalize(bs_cov, 'Bike_share_cov_density (bikes/1K pop)')
    n_bs_use = normalize(bs_usage, 'Bike_share_usage (trips/bike/day)')
    n_pt_integ = 100 if pol_pt_integ else 0  # Binary: integrated or not
    
    n_spend = normalize(spending_pc, 'Spending_per_capita (€/capita/year)')
    n_urb_inc = normalize(infra_inc, 'Infra_increase (km of bicycle infra/100 km of roadway)')

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
        score_bike_share = np.nanmean([n_bs_cov, n_bs_use, n_pt_integ])
        
        # Policy & Support scores (Pillar 3 components)
        score_political = n_spend
        score_advocacy = sum([pol_ngo_exists, pol_ngo_events, pol_ngo_policy]) / 3 * 100
        score_image = sum([pol_media, pol_brand, pol_school]) / 3 * 100
        plan_bin = sum([pol_masterplan, pol_unit, pol_standards, pol_monitor]) / 4 * 100
        
        # Urban planning appears in both Pillar 1 and Pillar 3 (Infrastructure + Policy)
        score_urban_plan = np.nanmean([n_urb_inc, plan_bin])

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
        #   - Actual adoption by residents (modal share, women participation)
        #   - Specialized services (cargo bikes, bike share)
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
            /* Hide interactive elements during print */
            header, h1, .hide-on-print, div[data-testid="stForm"], iframe { 
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
        # Radar Chart: Simulated City vs. Global Top 10
        radar_columns = [
            'Bicycle Infrastructure Score', 'Bicycle Parking Score', 'Traffic Calming Score', 'Safety Score',
            'Women Share Score', 'Modal Share Score', 'Modal Share Increase Score', 'Image of the Bicycle Score',
            'Cargo Bikes Score', 'Advocacy Score', 'Politics Score', 'Bike Share Score', 'Urban Planning Score'
        ]
        radar_labels = [c.replace(' Score', '') for c in radar_columns]
        
        simulated_values = [
            score_infrastructure, score_parking, score_traffic, score_safety,
            score_women_final, score_modal_final, score_mod_inc_final, score_image,
            score_cargo_bikes, score_advocacy, score_political, score_bike_share, score_urban_plan
        ]
        
        # Calculate average scores of top 10 cities for comparison
        top_10_avg = []
        if 'Rank' in df.columns:
            top_10_df = df.nsmallest(10, 'Rank')
        else:
            top_10_df = df.head(10)
        
        for col in radar_columns:
            alt_col = "Score " + col.replace(" Score", "")
            target_col = col if col in top_10_df.columns else (alt_col if alt_col in top_10_df.columns else None)
                
            if target_col:
                # Clean string values (replace commas with periods for European decimal format)
                clean_series = top_10_df[target_col].astype(str).str.replace(',', '.').str.strip()
                mean_val = pd.to_numeric(clean_series, errors='coerce').mean()
                top_10_avg.append(mean_val if pd.notna(mean_val) else None)
            else:
                top_10_avg.append(None) 
        
        # Create closed polygon by repeating first point
        closed_theta = radar_labels + [radar_labels[0]]
        closed_sim = [None if pd.isna(v) else v for v in (simulated_values + [simulated_values[0]])]
        
        closed_top10 = [None if pd.isna(v) else v for v in top_10_avg]
        if closed_top10: 
            closed_top10.append(closed_top10[0]) 
        
        # Build radar chart
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=closed_sim, theta=closed_theta,
            fill='toself', name=sim_city, line=dict(color='#1BBBEC', width=3),
            connectgaps=True 
        ))
        
        # Add top 10 average trace if data exists
        if any(v is not None for v in top_10_avg):
            fig_radar.add_trace(go.Scatterpolar(
                r=closed_top10, theta=closed_theta,
                fill='none', name='Global Top 10 Avg', line=dict(color='#D53C4C', width=2, dash='dash'),
                connectgaps=True
            ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True, height=400, margin=dict(t=20, b=20, l=40, r=40)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ====================================================================
    # STRENGTHS, AREAS FOR IMPROVEMENT, GLOBAL CONTEXT
    # ====================================================================
    # Identify the top 3 scoring and lowest scoring indicators to help cities
    # understand where they excel and where to focus improvement efforts.
    
    st.markdown("---")
    
    score_dict = dict(zip(radar_labels, simulated_values))
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
            # Use Pandas Styling to highlight the simulated row
            def highlight_simulated(row):
                if "(Simulated)" in row['City']:
                    return ['background-color: #1BBBEC; color: white'] * len(row)
                return [''] * len(row)
                
            styled_table = context_table.style.apply(highlight_simulated, axis=1).hide(axis="index")
            st.write(styled_table.to_html(), unsafe_allow_html=True)
        else:
            st.write("Ranking data unavailable.")

    # ====================================================================
    # EXPORT TO PDF
    # ====================================================================
    # Summary card that users can save as PDF.
    
    components.html(
        '''
        <div style="text-align: center; margin-top: 50px;">
            <button onclick="window.parent.print()" 
                    style="padding: 12px 24px; font-size: 16px; font-weight: bold; 
                           background-color: #1BBBEC; color: white; border: none; 
                           border-radius: 5px; cursor: pointer; 
                           box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">
                🖨️ Print Summary Card
            </button>
            <p style="font-family: sans-serif; color: #666; font-size: 12px; margin-top: 10px;">
                💡 Tip: Use landscape orientation and enable "Background graphics" in your print settings.
            </p>
        </div>
        ''',
        height=100
    )
