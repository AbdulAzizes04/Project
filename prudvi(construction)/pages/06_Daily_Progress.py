"""
BuildVerse AI — Phase 3: Virtual Construction Site Engineer & Multi-Media Progress Inspector
"""

import streamlit as st
import os
import textwrap
from pathlib import Path
from datetime import date
from database.db import get_project, save_monitoring_log, get_monitoring_logs
from utils.file_handler import save_uploaded_file
from api.monitoring_api import process_batch_monitoring_upload, process_monitoring_upload
from config import UPLOADS_IMAGES, UPLOADS_VIDEOS, UPLOADS_DRONE, ASSETS_DIR

st.set_page_config(
    page_title="Daily Progress — BuildVerse AI",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

css_path = ASSETS_DIR / "css" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1>Phase 3 — Virtual Construction Site Engineer</h1>
    <p>Upload single or multiple construction site images & videos. The AI acts as a Virtual Site Engineer to evaluate stage progress, generate engineering callout annotations, estimate remaining work, and compute recovery predictions.</p>
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
        st.subheader("1. Batch Upload Site Media & Specify Construction Zone")
        
        col_files, col_zone = st.columns([2, 1])
        
        with col_files:
            uploaded_files = st.file_uploader(
                "📁 Drag & Drop or Browse Multiple Construction Images & Videos",
                type=["jpg", "jpeg", "png", "mp4", "mov"],
                accept_multiple_files=True,
                key="batch_site_uploader",
                help="You can select multiple photos at once by holding Ctrl or Shift"
            )
            
            all_refs = [f.name for f in UPLOADS_IMAGES.glob("*") if f.is_file()]
            selected_presets = st.multiselect(
                "Or Choose Multiple Preset Sample Photos from Library:",
                options=all_refs,
                default=[] if uploaded_files else ["site_brickwork_real.jpg"],
                help="Select one or multiple sample site images to inspect together"
            )

            if uploaded_files:
                st.info(f"📸 **{len(uploaded_files)} Custom Image(s) Attached**")

        with col_zone:
            building_block = st.selectbox("Building Block / Structure:", ["Block A", "Block B", "Block C"])
            selected_area = st.selectbox(
                "Which Floor Level?",
                ["Ground Floor", "First Floor", "Foundation", "Roof", "Exterior"]
            )
            selected_zone = st.selectbox(
                "Which Room / Construction Zone?",
                ["Balcony", "Hall", "Kitchen", "Bedroom 1", "Bedroom 2", "Staircase", "Roof"]
            )
            
            analyze_btn = st.button("🚀 Run AI Inspection on All Selected Images", type="primary")

        if analyze_btn or uploaded_files or selected_presets:
            saved_paths = []
            
            if uploaded_files:
                for f in uploaded_files:
                    cat = "videos" if f.name.endswith(('.mp4', '.mov')) else "images"
                    p = save_uploaded_file(f, cat)
                    saved_paths.append(p)
            
            if selected_presets:
                for preset_name in selected_presets:
                    saved_paths.append(str(UPLOADS_IMAGES / preset_name))
                    
            if not saved_paths:
                saved_paths.append(str(UPLOADS_IMAGES / "site_brickwork_real.jpg"))
                
            # Remove duplicates preserving order
            saved_paths = list(dict.fromkeys(saved_paths))
                
            results = process_batch_monitoring_upload(
                file_paths=saved_paths,
                selected_area=selected_area,
                selected_zone=selected_zone,
                building_block=building_block
            )
            
            rep = results["engineer_report"]
            area_info = rep["area_header"]
            act_info = rep["current_activity"]
            work_info = rep["current_work"]
            rem_info = rep["remaining_work"]
            next_info = rep["next_stage"]
            time_info = rep["timeline_prediction"]
            breakdown = results["room_progress_breakdown"]
            media_list = results.get("annotated_media_list", [])

            st.divider()
            st.subheader(f"2. AI Construction Progress Inspection Report ({len(saved_paths)} Media Files)")
            
            r_col1, r_col2 = st.columns([1.1, 1])
            
            with r_col1:
                area_html = textwrap.dedent(f"""
                <div class="buildverse-card" style="border-left: 6px solid #0891B2;">
                    <h3 style="color: #0891B2; margin-top: 0;">📍 Construction Area</h3>
                    <p style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin: 0;">{area_info['full_location']}</p>
                    <hr style="margin: 0.8rem 0; border-color: #BAE6FD;">
                    
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.85rem; color: #64748B; font-weight: 600;">CURRENT ACTIVITY DETECTED</span><br>
                            <span style="font-size: 1.25rem; font-weight: 800; color: #0F172A;">{act_info['name']}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 0.85rem; color: #64748B; font-weight: 600;">CONFIDENCE</span><br>
                            <span style="font-size: 1.25rem; font-weight: 800; color: #0891B2;">{act_info['confidence_pct']:.0f}%</span>
                        </div>
                    </div>
                    
                    <div style="margin-top: 0.8rem; background-color: #E0F2FE; padding: 0.5rem 0.8rem; border-radius: 6px;">
                        <span style="font-weight: 700; color: #0369A1;">Construction Stage:</span> <span style="font-weight: 800; color: #0F172A;">{act_info['stage_text']}</span>
                    </div>
                </div>
                """)
                st.markdown(area_html, unsafe_allow_html=True)
                
                st.markdown("##### ✔️ Completed Stages")
                completed_tags = " • ".join([f"<b>✔ {s}</b>" for s in rep["completed_stages"]])
                comp_html = textwrap.dedent(f"""
                <div style="background-color: #D1FAE5; border: 1px solid #6EE7B7; padding: 0.75rem; border-radius: 8px; color: #065F46;">
                    {completed_tags}
                </div>
                """)
                st.markdown(comp_html, unsafe_allow_html=True)
                
                st.markdown("##### 🟢 Current Work Status")
                work_html = textwrap.dedent(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #BAE6FD; border-left: 5px solid #10B981; padding: 0.85rem; border-radius: 8px;">
                    <div style="font-size: 1.1rem; font-weight: 800; color: #0F172A;">{work_info['title']}</div>
                    <div style="font-size: 0.9rem; color: #475569; margin-top: 0.2rem;">
                        <b>Detected Height:</b> {work_info['detected_height']} | <b>Completion:</b> {work_info['completion_pct']:.0f}%
                    </div>
                </div>
                """)
                st.markdown(work_html, unsafe_allow_html=True)

            with r_col2:
                st.markdown("##### 📦 Remaining Work Items")
                rem_items = "".join([f"<li>{item}</li>" for item in rem_info["tasks"]])
                rem_html = textwrap.dedent(f"""
                <div style="background-color: #FEF3C7; border: 1px solid #FCD34D; padding: 0.85rem; border-radius: 8px; color: #92400E;">
                    <ul style="margin: 0; padding-left: 1.2rem; font-size: 0.9rem;">{rem_items}</ul>
                    <div style="margin-top: 0.5rem; font-weight: 700; color: #78350F;">
                        ⏱️ Estimated Remaining Duration: {rem_info['estimated_duration_days']} Days
                    </div>
                </div>
                """)
                st.markdown(rem_html, unsafe_allow_html=True)
                
                st.markdown("##### ⏭️ Next Stage")
                next_html = textwrap.dedent(f"""
                <div style="background-color: #E0F2FE; border: 1px solid #7DD3FC; padding: 0.85rem; border-radius: 8px; color: #0369A1;">
                    <div style="font-weight: 800; font-size: 1.05rem;">{next_info['title']}</div>
                    <div style="font-size: 0.85rem; margin-top: 0.2rem;">
                        <b>Expected Start:</b> {next_info['expected_start']} | <b>Duration:</b> {next_info['duration']}
                    </div>
                </div>
                """)
                st.markdown(next_html, unsafe_allow_html=True)

                st.markdown("##### ⏱️ Timeline & Recovery Prediction")
                time_html = textwrap.dedent(f"""
                <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; padding: 0.85rem; border-radius: 8px;">
                    <div style="font-size: 0.85rem; font-weight: 700; color: #64748B;">CURRENT PROGRESS: {time_info['current_progress']:.0f}%</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #0891B2;">██████████░░░░ 48%</div>
                    <div style="font-size: 0.85rem; color: #475569; margin-top: 0.4rem;">
                        • <b>Expected Today:</b> {time_info['expected_today']:.0f}%<br>
                        • <b>Delay Variance:</b> {time_info['delay_pct']:.0f}%<br>
                        • <b>Recovery Action:</b> {time_info['recovery_strategy']}<br>
                        • <b>Estimated Recovery Time:</b> {time_info['estimated_recovery']}
                    </div>
                </div>
                """)
                st.markdown(time_html, unsafe_allow_html=True)

            st.markdown("### 🤖 Virtual Site Engineer Recommendation")
            st.info(f"📋 **Site Recommendation:** {rep['ai_recommendation']}")

            st.divider()
            st.markdown(f"### 3. Engineering Site Inspection Overlays ({len(media_list)} Image(s) Inspected)")
            st.caption("Green: Completed | Cyan: Active Work | Red: Missing Work | Orange: Next Phase")

            if len(media_list) > 1:
                # Multi-Image Inspection with dedicated tab per image
                img_tabs = st.tabs([f"📸 #{i+1} {item['filename']}" for i, item in enumerate(media_list)])
                for idx, (t, item) in enumerate(zip(img_tabs, media_list)):
                    with t:
                        st.markdown(f"**Media #{idx+1}:** `{item['filename']}` — **Zone:** {selected_zone} | **Activity:** {item['activity']}")
                        c_orig, c_annot = st.columns(2)
                        with c_orig:
                            st.markdown("##### 📷 Original Site Photo")
                            st.image(item["original_pil"], caption=f"Raw Site Photo #{idx+1} ({item['filename']})", use_container_width=True)
                        with c_annot:
                            st.markdown("##### 🔍 AI Engineering Callout Overlay")
                            st.image(item["annotated_pil"], caption=f"AI Annotated Site Callouts ({item['filename']})", use_container_width=True)

                # Optional Gallery Grid
                with st.expander("🖼️ View All Inspected Images Side-by-Side Gallery", expanded=False):
                    grid_cols = st.columns(min(3, len(media_list)))
                    for idx, item in enumerate(media_list):
                        with grid_cols[idx % len(grid_cols)]:
                            st.image(item["annotated_pil"], caption=f"#{idx+1}: {item['filename']}", use_container_width=True)
            else:
                item = media_list[0] if media_list else {"original_pil": results["annotated_image"], "annotated_pil": results["annotated_image"], "filename": "site_brickwork_real.jpg"}
                c_orig, c_annot = st.columns(2)
                with c_orig:
                    st.markdown("##### 📷 Original Site Photo")
                    st.image(item["original_pil"], caption=f"Raw Site Photo ({item['filename']})", use_container_width=True)
                with c_annot:
                    st.markdown("##### 🔍 AI Engineering Callout Overlay")
                    st.image(item["annotated_pil"], caption="Professional Site Inspection Callouts", use_container_width=True)

            st.divider()
            st.markdown(f"### 4. Room-by-Room Construction Progress — {selected_area}")
            
            p_cols = st.columns(6)
            for i, (r_name, r_data) in enumerate(breakdown.items()):
                with p_cols[i % 6]:
                    status_bg = "#D1FAE5" if r_data["pct"] == 100.0 else ("#E0F2FE" if r_data["pct"] > 0 else "#F1F5F9")
                    status_fg = "#065F46" if r_data["pct"] == 100.0 else ("#0369A1" if r_data["pct"] > 0 else "#475569")
                    
                    room_html = textwrap.dedent(f"""
                    <div style="background-color: {status_bg}; border-radius: 8px; padding: 0.75rem; text-align: center; border: 1px solid #CBD5E1;">
                        <div style="font-weight: 700; font-size: 0.9rem; color: #0F172A;">{r_name}</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: {status_fg}; margin: 0.2rem 0;">{r_data['pct']:.0f}%</div>
                        <div style="font-size: 0.75rem; font-weight: 600; color: {status_fg};">{r_data['status']}</div>
                    </div>
                    """)
                    st.markdown(room_html, unsafe_allow_html=True)

            # Save batch monitoring logs for each image
            for p in saved_paths:
                log_payload = {
                    "project_id": curr_pid,
                    "log_date": date.today().strftime("%Y-%m-%d"),
                    "media_path": p,
                    "media_type": "batch_session",
                    "completed_work_pct": work_info["completion_pct"],
                    "missing_work_pct": 100.0 - work_info["completion_pct"],
                    "overall_progress_pct": results["overall_project_pct"],
                    "delay_pct": time_info["delay_pct"],
                    "quality_score": 96.0,
                    "status": "In Progress",
                    "ai_summary": f"Inspected {Path(p).name} for {selected_area} ({selected_zone}). Activity: {act_info['name']}",
                    "ai_recommendation": rep["ai_recommendation"]
                }
                save_monitoring_log(log_payload)
            st.toast(f"Saved {len(saved_paths)} image inspection(s) to database!", icon="💾")

        st.divider()
        st.subheader("5. Historical Site Inspection Logs")
        logs = get_monitoring_logs(curr_pid)
        if logs:
            st.dataframe(logs, use_container_width=True)
