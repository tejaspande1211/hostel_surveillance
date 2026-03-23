-- ADMINS TABLE
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- WARDENS TABLE
CREATE TABLE IF NOT EXISTS wardens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    hostel_block TEXT,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- STUDENTS TABLE
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    room_number TEXT,
    hostel_block TEXT,
    course TEXT,
    year INTEGER,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- STAFF TABLE
CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT,
    email TEXT,
    phone TEXT,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- BLACKLISTED PERSONS TABLE
CREATE TABLE IF NOT EXISTS blacklisted_persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    reason TEXT NOT NULL,
    added_by INTEGER NOT NULL,
    image_path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (added_by) REFERENCES wardens(id)
);

-- FACE EMBEDDINGS TABLE
CREATE TABLE IF NOT EXISTS face_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_type TEXT NOT NULL,
    person_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    embedding BLOB NOT NULL,
    model_used TEXT DEFAULT 'ArcFace',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ATTENDANCE RECORDS TABLE
CREATE TABLE IF NOT EXISTS attendance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date DATE NOT NULL,
    time_in DATETIME,
    time_out DATETIME,
    status TEXT DEFAULT 'present',
    FOREIGN KEY (student_id) REFERENCES students(id),
    UNIQUE(student_id, date)
);

-- RECOGNITION LOGS TABLE
CREATE TABLE IF NOT EXISTS recognition_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    person_type TEXT,
    person_id INTEGER,
    confidence REAL,
    frame_path TEXT,
    camera_id INTEGER DEFAULT 0
);

-- ALERTS TABLE
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL,
    person_id INTEGER,
    person_type TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    image_path TEXT,
    email_sent INTEGER DEFAULT 0,
    sms_sent INTEGER DEFAULT 0,
    acknowledged INTEGER DEFAULT 0
);