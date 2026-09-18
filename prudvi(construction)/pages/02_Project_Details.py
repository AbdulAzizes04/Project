"""
BuildVerse AI — Phase 1: Step 1 Project Details & Room Configuration
"""

import streamlit as st
from config import ASSETS_DIR
from database.db import save_project, save_floors_and_rooms, get_project

st.set_page_config(
    page_title="Project Details — BuildVerse AI",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

css_path = ASSETS_DIR / "css" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1>Phase 1 — Project & Room Specifications</h1>
    <p>Enter plot details, number of floors, and room dimensions to initiate AI house planning.</p>
</div>
""", unsafe_allow_html=True)

# Step 1 Form: Basic Project Info
with st.form("project_info_form"):
    st.subheader("1. General Project Details")
    c1, c2, c3 = st.columns(3)
    with c1:
        p_name = st.text_input("Project Name", value="Cyber Skyline Villa")
        p_owner = st.text_input("Owner Name", value="Alex Morgan")
    with c2:
        p_location = st.text_input("Location / Site Address", value="Sector 42, Innovation Bay")
        p_budget = st.number_input("Total Budget ($)", value=250000.0, step=5000.0)
    with c3:
        p_area = st.number_input("Plot Area", value=2400.0, step=100.0)
        p_unit = st.selectbox("Unit", ["sq.ft", "sq.m"])
        p_num_floors = st.number_input("Number of Floors", min_value=1, max_value=4, value=2)

    submit_pinfo = st.form_submit_button("Save & Proceed to Floor Details")

if submit_pinfo:
    p_data = {
        "name": p_name,
        "owner_name": p_owner,
        "location": p_location,
        "plot_area": p_area,
        "plot_unit": p_unit,
        "budget": p_budget,
        "num_floors": p_num_floors
    }
    pid = save_project(p_data)
    st.session_state.current_project_id = pid
    st.success(f"Project '{p_name}' created successfully (ID: {pid})! Now configure room specifications below.")

# Step 2 Form: Floor & Room Specifications
if st.session_state.get("current_project_id"):
    curr_pid = st.session_state.current_project_id
    project = get_project(curr_pid)
    
    if project:
        st.divider()
        st.subheader("2. Floor & Room Dimension Details")
        
        num_floors = project["num_floors"]
        floors_config = []
        
        ROOM_TYPES = ["Bedrooms", "Kitchen", "Hall", "Dining", "Bathrooms", "Balcony", "Parking", "Staircase", "Utility Room", "Store Room", "Garden"]
        
        for f_idx in range(num_floors):
            floor_label = "Ground Floor" if f_idx == 0 else f"Floor {f_idx}"
            with st.expander(f"🏢 {floor_label} Configuration", expanded=(f_idx == 0)):
                st.markdown(f"##### Select Rooms for {floor_label}")
                selected_rooms = st.multiselect(
                    f"Select Room Types on {floor_label}:",
                    options=ROOM_TYPES,
                    default=["Bedrooms", "Kitchen", "Hall", "Bathrooms"] if f_idx == 0 else ["Bedrooms", "Bathrooms", "Balcony"],
                    key=f"ms_rooms_{f_idx}"
                )
                
                rooms_data = []
                if selected_rooms:
                    st.markdown("##### Room Dimensions & Orientations")
                    for r_idx, r_name in enumerate(selected_rooms):
                        rc1, rc2, rc3, rc4, rc5 = st.columns(5)
                        with rc1:
                            st.text(f"**{r_name}**")
                        with rc2:
                            r_len = st.number_input(f"Length (ft)", min_value=3.0, max_value=60.0, value=14.0 if "Bed" in r_name or "Hall" in r_name else 10.0, key=f"len_{f_idx}_{r_idx}")
                        with rc3:
                            r_wid = st.number_input(f"Width (ft)", min_value=3.0, max_value=60.0, value=12.0 if "Bed" in r_name or "Hall" in r_name else 8.0, key=f"wid_{f_idx}_{r_idx}")
                        with rc4:
                            r_pos = st.selectbox("Position", ["North", "South", "East", "West", "Center"], key=f"pos_{f_idx}_{r_idx}")
                        with rc5:
                            r_win = st.number_input("Windows", 0, 4, 1, key=f"win_{f_idx}_{r_idx}")
                            r_door = st.number_input("Doors", 1, 3, 1, key=f"door_{f_idx}_{r_idx}")
                            
                        rooms_data.append({
                            "room_type": r_name,
                            "length": r_len,
                            "width": r_wid,
                            "position": r_pos,
                            "windows": r_win,
                            "doors": r_door
                        })
                        
                floors_config.append({
                    "floor_name": floor_label,
                    "floor_level": f_idx,
                    "rooms": rooms_data
                })

        if st.button("Save Floor & Room Specifications", type="primary"):
            save_floors_and_rooms(curr_pid, floors_config)
            st.success("All Floor & Room details saved! Move to **03 AI Floor Planner** to view 2D/3D layouts.")
