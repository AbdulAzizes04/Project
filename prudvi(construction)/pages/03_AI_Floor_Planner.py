"""
BuildVerse AI — Phase 1: Step 2 AI Floor Plan Generator & 2D-to-3D Image Converter
"""

import streamlit as st
from pathlib import Path
from database.db import get_project, save_floors_and_rooms
from ai.planner.floor_plan_ai import generate_2d_floor_plan, generate_3d_house_preview
from ai.planner.dimension_validator import validate_floor_plan
from ai.planner.blueprint_parser import parse_2d_blueprint_image, convert_2d_blueprint_to_3d_mesh
from utils.file_handler import save_uploaded_file
from config import UPLOADS_2D, ASSETS_DIR

# Set Page Config for full-width layout
st.set_page_config(
    page_title="AI Floor Planner — BuildVerse AI",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
css_path = ASSETS_DIR / "css" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1>Phase 1 — AI Floor Plan Generator & 2D-to-3D Blueprint Converter</h1>
    <p>Upload your 2D architectural blueprint image (or choose from reference blueprints) to convert directly into interactive 3D house models and vector layouts.</p>
</div>
""", unsafe_allow_html=True)

curr_pid = st.session_state.get("current_project_id")

if not curr_pid:
    st.warning("Please select or create a project in **02 Project Details** first.")
else:
    project = get_project(curr_pid)
    
    if not project:
        st.error("Project data not found.")
    else:
        st.markdown(f"### Active Project: **{project['name']}** ({project['plot_area']} {project['plot_unit']})")
        
        # Tabs for 2D Blueprint Upload to 3D, 2D Vector Blueprints, 3D House Preview, and Structural Code Validation
        tab_convert, tab_2d, tab_3d, tab_val = st.tabs([
            "🖼️ Upload 2D Blueprint & Convert to 3D",
            "📐 2D Vector Architectural Blueprints",
            "🏠 Interactive 3D House Model",
            "📋 Structural Code Validation"
        ])
        
        with tab_convert:
            st.markdown("#### 1. Upload or Select 2D Architectural Blueprint Image")
            
            c_bp1, c_bp2 = st.columns([2, 1])
            
            with c_bp1:
                ref_2d_files = [f.name for f in UPLOADS_2D.glob("*") if f.is_file()]
                selected_2d_ref = st.selectbox(
                    "📂 Choose Reference 2D Blueprint Plan (Folder: uploads/2d/):",
                    options=["[Custom Upload]"] + ref_2d_files,
                    key="select_2d_blueprint_ref"
                )
                
                up_2d = st.file_uploader(
                    "Or Upload Custom 2D Blueprint Image (JPG, PNG)",
                    type=["jpg", "jpeg", "png"],
                    key="uploader_2d_blueprint"
                )
                
                parse_btn = st.button("⚡ Convert 2D Blueprint Image to 3D Model", type="primary")

            with c_bp2:
                st.markdown("""
                <div class="buildverse-card-accent">
                    <h5 style="color: #0891B2;">🤖 AI Blueprint Parser Engine</h5>
                    <p style="font-size: 0.85rem; color: #0F172A;">
                        • Detects structural wall contours and room boundaries.<br>
                        • Extracts room labels (Living Hall, Kitchen, Bed, Bath).<br>
                        • Automatically projects 2D image coordinates into multi-story 3D Digital Twin meshes.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            if parse_btn or up_2d is not None or selected_2d_ref != "[Custom Upload]":
                if up_2d:
                    bp_path = save_uploaded_file(up_2d, "floorplans")
                elif selected_2d_ref != "[Custom Upload]":
                    bp_path = str(UPLOADS_2D / selected_2d_ref)
                else:
                    bp_path = str(UPLOADS_2D / "ground_floor_blueprint.jpg")
                    
                st.divider()
                st.markdown("#### 2. Extracted Blueprint Rooms & Direct 3D Conversion")
                
                col_bp_img, col_3d_conv = st.columns([1, 1])
                
                parsed_data = parse_2d_blueprint_image(bp_path)
                ext_rooms = parsed_data["extracted_rooms"]
                
                with col_bp_img:
                    st.markdown("##### Uploaded 2D Architectural Plan")
                    st.image(bp_path, caption=f"Blueprint Resolution: {parsed_data['blueprint_resolution']} | AI Confidence: {parsed_data['confidence_score']}%", use_container_width=True)
                    
                    st.markdown("##### Extracted Room Specifications")
                    st.dataframe(ext_rooms, use_container_width=True)

                with col_3d_conv:
                    st.markdown("##### Generated 3D House Preview Model")
                    fig_conv_3d = convert_2d_blueprint_to_3d_mesh(ext_rooms, num_floors=project.get("num_floors", 2))
                    st.plotly_chart(fig_conv_3d, use_container_width=True)

                if st.button("💾 Apply Extracted 2D Blueprint Rooms to Working Project"):
                    floors_payload = []
                    for f_idx in range(project.get("num_floors", 2)):
                        floor_label = "Ground Floor" if f_idx == 0 else f"Floor {f_idx}"
                        floors_payload.append({
                            "floor_name": floor_label,
                            "floor_level": f_idx,
                            "rooms": ext_rooms
                        })
                    save_floors_and_rooms(curr_pid, floors_payload)
                    st.success("Extracted 2D Blueprint room layout applied to project database! Explore tabs above.")

        with tab_2d:
            floors = project.get("floors", [])
            if not floors:
                st.info("No floor configuration found. Convert a 2D Blueprint above or configure rooms in **02 Project Details**.")
            else:
                selected_floor_idx = st.selectbox(
                    "Select Floor to View Blueprint:",
                    options=range(len(floors)),
                    format_func=lambda i: floors[i]["floor_name"]
                )
                
                target_floor = floors[selected_floor_idx]
                rooms = target_floor.get("rooms", [])
                
                if rooms:
                    fig_2d = generate_2d_floor_plan(rooms=rooms, plot_width=40.0, plot_length=50.0, floor_name=target_floor["floor_name"])
                    st.plotly_chart(fig_2d, use_container_width=True)
                    st.dataframe(rooms, use_container_width=True)

        with tab_3d:
            st.markdown("#### Interactive 3D Digital House Mesh Preview")
            if project.get("floors"):
                fig_3d = generate_3d_house_preview(project["floors"], plot_width=40.0, plot_length=50.0)
                st.plotly_chart(fig_3d, use_container_width=True)
            else:
                st.info("Please convert a 2D Blueprint image or configure rooms first.")

        with tab_val:
            st.markdown("#### Architectural Setback & Coverage Verification")
            all_rooms = []
            for f in project.get("floors", []):
                all_rooms.extend(f.get("rooms", []))
                
            if all_rooms:
                val_results = validate_floor_plan(project["plot_area"], all_rooms)
                vcol1, vcol2, vcol3 = st.columns(3)
                vcol1.metric("Gross Built-Up Area", f"{val_results['gross_area']} sq.ft")
                vcol2.metric("Plot Coverage %", f"{val_results['coverage_pct']}%")
                vcol3.metric("Compliance Status", "PASSED" if val_results["valid"] else "WARNING", delta="Code Standard")
                
                if val_results["warnings"]:
                    for w in val_results["warnings"]:
                        st.warning(f"⚠️ {w}")
                else:
                    st.success("✅ All room dimensions and setback coverage meet architectural safety standards.")
