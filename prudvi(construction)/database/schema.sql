-- BuildVerse AI Database Schema

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    owner_name TEXT NOT NULL,
    location TEXT NOT NULL,
    plot_area REAL NOT NULL,
    plot_unit TEXT NOT NULL,
    budget REAL NOT NULL,
    num_floors INTEGER NOT NULL,
    start_date TEXT,
    completion_date TEXT,
    workers_available INTEGER DEFAULT 10,
    working_hours_per_day REAL DEFAULT 8.0,
    material_preference TEXT DEFAULT 'Standard',
    weather_region TEXT DEFAULT 'Moderate',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS floors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    floor_name TEXT NOT NULL,
    floor_level INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    floor_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    room_type TEXT NOT NULL,
    length REAL NOT NULL,
    width REAL NOT NULL,
    area REAL NOT NULL,
    position TEXT DEFAULT 'Center',
    windows INTEGER DEFAULT 1,
    doors INTEGER DEFAULT 1,
    FOREIGN KEY (floor_id) REFERENCES floors(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    phase_name TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    progress_pct REAL DEFAULT 0.0,
    cost REAL DEFAULT 0.0,
    labor INTEGER DEFAULT 5,
    materials TEXT,
    dependencies TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS monitoring_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    media_path TEXT,
    media_type TEXT,
    completed_work_pct REAL,
    missing_work_pct REAL,
    overall_progress_pct REAL,
    delay_pct REAL,
    quality_score REAL,
    status TEXT,
    ai_summary TEXT,
    ai_recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS digital_twin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    element_id TEXT NOT NULL,
    element_name TEXT NOT NULL,
    phase_name TEXT NOT NULL,
    status TEXT NOT NULL, -- 'Completed', 'In-Progress', 'Pending'
    mesh_data TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
