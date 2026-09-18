"""
Database Handler for BuildVerse AI
Manages SQLite / PostgreSQL connections, table creation, and CRUD operations.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import DB_PATH, DATABASE_DIR

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    schema_file = DATABASE_DIR / "schema.sql"
    if schema_file.exists():
        with open(schema_file, "r") as f:
            schema = f.read()
        conn = get_connection()
        conn.executescript(schema)
        conn.commit()
        conn.close()

def save_project(project_data: Dict[str, Any]) -> int:
    """Saves or updates a project and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if project_data.get("id"):
        cursor.execute("""
            UPDATE projects SET
                name=?, owner_name=?, location=?, plot_area=?, plot_unit=?,
                budget=?, num_floors=?, start_date=?, completion_date=?,
                workers_available=?, working_hours_per_day=?, material_preference=?, weather_region=?
            WHERE id=?
        """, (
            project_data["name"], project_data["owner_name"], project_data["location"],
            project_data["plot_area"], project_data.get("plot_unit", "sq.ft"), project_data["budget"],
            project_data["num_floors"], project_data.get("start_date"), project_data.get("completion_date"),
            project_data.get("workers_available", 10), project_data.get("working_hours_per_day", 8.0),
            project_data.get("material_preference", "Standard"), project_data.get("weather_region", "Moderate"),
            project_data["id"]
        ))
        project_id = project_data["id"]
    else:
        cursor.execute("""
            INSERT INTO projects (
                name, owner_name, location, plot_area, plot_unit, budget, num_floors,
                start_date, completion_date, workers_available, working_hours_per_day,
                material_preference, weather_region
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_data["name"], project_data["owner_name"], project_data["location"],
            project_data["plot_area"], project_data.get("plot_unit", "sq.ft"), project_data["budget"],
            project_data["num_floors"], project_data.get("start_date"), project_data.get("completion_date"),
            project_data.get("workers_available", 10), project_data.get("working_hours_per_day", 8.0),
            project_data.get("material_preference", "Standard"), project_data.get("weather_region", "Moderate")
        ))
        project_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return project_id

def save_floors_and_rooms(project_id: int, floors_data: List[Dict[str, Any]]):
    """Saves floor and room details for a project."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Delete existing rooms and floors for clean refresh
    cursor.execute("DELETE FROM rooms WHERE project_id=?", (project_id,))
    cursor.execute("DELETE FROM floors WHERE project_id=?", (project_id,))
    
    for floor in floors_data:
        cursor.execute(
            "INSERT INTO floors (project_id, floor_name, floor_level) VALUES (?, ?, ?)",
            (project_id, floor["floor_name"], floor["floor_level"])
        )
        floor_id = cursor.lastrowid
        
        for room in floor.get("rooms", []):
            cursor.execute("""
                INSERT INTO rooms (
                    floor_id, project_id, room_type, length, width, area, position, windows, doors
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                floor_id, project_id, room["room_type"], room["length"], room["width"],
                room["length"] * room["width"], room.get("position", "Center"),
                room.get("windows", 1), room.get("doors", 1)
            ))
            
    conn.commit()
    conn.close()

def save_schedules(project_id: int, schedules_data: List[Dict[str, Any]]):
    """Saves construction phase schedules."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedules WHERE project_id=?", (project_id,))
    
    for s in schedules_data:
        cursor.execute("""
            INSERT INTO schedules (
                project_id, phase_name, start_date, end_date, duration_days,
                progress_pct, cost, labor, materials, dependencies, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, s["phase_name"], s["start_date"], s["end_date"],
            s["duration_days"], s.get("progress_pct", 0.0), s.get("cost", 0.0),
            s.get("labor", 5), json.dumps(s.get("materials", [])),
            json.dumps(s.get("dependencies", [])), s.get("status", "Pending")
        ))
        
    conn.commit()
    conn.close()

def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves full project information including floors, rooms, and schedules."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM projects WHERE id=?", (project_id,))
    p_row = cursor.fetchone()
    if not p_row:
        conn.close()
        return None
        
    project = dict(p_row)
    
    # Fetch floors and rooms
    cursor.execute("SELECT * FROM floors WHERE project_id=? ORDER BY floor_level", (project_id,))
    floors = [dict(f) for f in cursor.fetchall()]
    
    for f in floors:
        cursor.execute("SELECT * FROM rooms WHERE floor_id=?", (f["id"],))
        f["rooms"] = [dict(r) for r in cursor.fetchall()]
        
    project["floors"] = floors
    
    # Fetch schedules
    cursor.execute("SELECT * FROM schedules WHERE project_id=? ORDER BY id", (project_id,))
    schedules = []
    for s in cursor.fetchall():
        s_dict = dict(s)
        try:
            s_dict["materials"] = json.loads(s_dict["materials"]) if s_dict["materials"] else []
            s_dict["dependencies"] = json.loads(s_dict["dependencies"]) if s_dict["dependencies"] else []
        except Exception:
            pass
        schedules.append(s_dict)
        
    project["schedules"] = schedules
    conn.close()
    return project

def get_all_projects() -> List[Dict[str, Any]]:
    """Lists all saved projects."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY id DESC")
    projects = [dict(p) for p in cursor.fetchall()]
    conn.close()
    return projects

def save_monitoring_log(log_data: Dict[str, Any]) -> int:
    """Saves daily progress monitoring log."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO monitoring_logs (
            project_id, log_date, media_path, media_type, completed_work_pct,
            missing_work_pct, overall_progress_pct, delay_pct, quality_score,
            status, ai_summary, ai_recommendation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        log_data["project_id"], log_data["log_date"], log_data.get("media_path"),
        log_data.get("media_type", "image"), log_data["completed_work_pct"],
        log_data["missing_work_pct"], log_data["overall_progress_pct"],
        log_data["delay_pct"], log_data["quality_score"], log_data["status"],
        log_data["ai_summary"], log_data["ai_recommendation"]
    ))
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

def get_monitoring_logs(project_id: int) -> List[Dict[str, Any]]:
    """Retrieves all monitoring logs for a project."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monitoring_logs WHERE project_id=? ORDER BY id DESC", (project_id,))
    logs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return logs

# Ensure DB is initialized on module import
init_db()
