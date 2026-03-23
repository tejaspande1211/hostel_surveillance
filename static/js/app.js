
async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    localStorage.clear();
    window.location.href = '/login';
}

async function checkAuth() {
    try {
        const res = await fetch('/api/auth/me');
        if (!res.ok) { window.location.href = '/login'; return null; }
        const data = await res.json();
        document.getElementById('nav-role').textContent = data.role.toUpperCase();
        return data;
    } catch(e) { window.location.href = '/login'; return null; }
}

function isActive(path) { return window.location.pathname === path ? 'active' : ''; }

function buildSidebar(role) {
    const sidebar = document.getElementById('sidebar');
    const links = role === 'admin' ? `
        <div class="section-label">Admin</div>
        <a href="/dashboard" class="${isActive('/dashboard')}"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a>
        <a href="/students" class="${isActive('/students')}"><i class="fas fa-users me-2"></i>Students</a>
        <a href="/camera" class="${isActive('/camera')}"><i class="fas fa-video me-2"></i>Live Camera</a>
        <a href="/alerts" class="${isActive('/alerts')}"><i class="fas fa-bell me-2"></i>Alerts</a>
        <a href="/logs" class="${isActive('/logs')}"><i class="fas fa-list me-2"></i>Logs</a>` : `
        <div class="section-label">Main</div>
        <a href="/dashboard" class="${isActive('/dashboard')}"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a>
        <div class="section-label">Manage</div>
        <a href="/students" class="${isActive('/students')}"><i class="fas fa-users me-2"></i>Students</a>
        <a href="/attendance" class="${isActive('/attendance')}"><i class="fas fa-calendar-check me-2"></i>Attendance</a>
        <a href="/camera" class="${isActive('/camera')}"><i class="fas fa-video me-2"></i>Live Camera</a>
        <a href="/alerts" class="${isActive('/alerts')}"><i class="fas fa-bell me-2"></i>Alerts</a>`;
    sidebar.innerHTML = links;
}

async function api(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error('API error');
    return res.json();
}

async function loadDashboard() {
    const user = await checkAuth();
    if (!user) return;
    buildSidebar(user.role);
    document.getElementById('main-content').innerHTML = `
        <h5 class="mb-4 fw-bold">Dashboard</h5>
        <div class="row g-3 mb-4">
            <div class="col-md-3"><div class="card stat-card p-3"><div class="d-flex align-items-center gap-3">
                <div class="stat-icon bg-primary bg-opacity-10 text-primary">&#128101;</div>
                <div><div class="text-muted small">Total Students</div><div class="fs-4 fw-bold" id="stat-students">-</div></div>
            </div></div></div>
            <div class="col-md-3"><div class="card stat-card p-3"><div class="d-flex align-items-center gap-3">
                <div class="stat-icon bg-success bg-opacity-10 text-success">&#9989;</div>
                <div><div class="text-muted small">Present Today</div><div class="fs-4 fw-bold" id="stat-present">-</div></div>
            </div></div></div>
            <div class="col-md-3"><div class="card stat-card p-3"><div class="d-flex align-items-center gap-3">
                <div class="stat-icon bg-danger bg-opacity-10 text-danger">&#128680;</div>
                <div><div class="text-muted small">Unacked Alerts</div><div class="fs-4 fw-bold" id="stat-alerts">-</div></div>
            </div></div></div>
            <div class="col-md-3"><div class="card stat-card p-3"><div class="d-flex align-items-center gap-3">
                <div class="stat-icon bg-info bg-opacity-10 text-info">&#128203;</div>
                <div><div class="text-muted small">Total Logs</div><div class="fs-4 fw-bold" id="stat-logs">-</div></div>
            </div></div></div>
        </div>
        <div class="row g-3">
            <div class="col-md-8"><div class="card border-0 shadow-sm">
                <div class="card-header bg-white fw-bold">Recent Recognition Logs</div>
                <div class="card-body p-2" id="recent-logs" style="max-height:400px;overflow-y:auto;"></div>
            </div></div>
            <div class="col-md-4"><div class="card border-0 shadow-sm">
                <div class="card-header bg-white fw-bold">Today's Attendance</div>
                <div class="card-body p-2" id="today-attendance" style="max-height:400px;overflow-y:auto;"></div>
            </div></div>
        </div>`;
    await refreshDashboard();
    setInterval(refreshDashboard, 5000);
}

async function refreshDashboard() {
    try {
        const today = new Date().toISOString().split('T')[0];
        const [stats, logs, att] = await Promise.all([
            api('/api/dashboard/stats'),
            api('/api/logs?limit=20'),
            api('/api/attendance?date=' + today)
        ]);
        document.getElementById('stat-students').textContent = stats.total_students;
        document.getElementById('stat-present').textContent = stats.present_today;
        document.getElementById('stat-alerts').textContent = stats.unacked_alerts;
        document.getElementById('stat-logs').textContent = stats.total_logs;
        document.getElementById('recent-logs').innerHTML = logs.map(l =>
            `<div class="log-item badge-${l.person_type}">
                <strong>${l.person_type}</strong>${l.person_id ? ' &middot; ID ' + l.person_id : ''}
                &middot; ${(l.confidence*100).toFixed(1)}%
                <span class="float-end text-muted">${l.timestamp.split(' ')[1]}</span>
            </div>`).join('');
        document.getElementById('today-attendance').innerHTML = att.length
            ? att.map(a => `<div class="log-item badge-student mb-1">
                <strong>${a.name}</strong> (${a.roll_number})<br>
                <small>In: ${a.time_in ? a.time_in.split(' ')[1].split('.')[0] : '-'}</small>
              </div>`).join('')
            : '<p class="text-muted text-center py-3">No attendance yet today</p>';
    } catch(e) { console.error(e); }
}

async function loadStudents() {
    const user = await checkAuth();
    if (!user) return;
    buildSidebar(user.role);
    document.getElementById('main-content').innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="fw-bold mb-0">Students</h5>
            <button class="btn btn-primary btn-sm" onclick="showAddStudent()"><i class="fas fa-plus me-1"></i>Add Student</button>
        </div>
        <div id="add-form" class="card border-0 shadow-sm mb-4 d-none">
            <div class="card-header bg-white fw-bold">Add New Student</div>
            <div class="card-body">
                <div class="row g-2">
                    <div class="col-md-3"><input class="form-control" id="f-roll" placeholder="Roll Number*"></div>
                    <div class="col-md-3"><input class="form-control" id="f-name" placeholder="Full Name*"></div>
                    <div class="col-md-3"><input class="form-control" id="f-email" placeholder="Email"></div>
                    <div class="col-md-3"><input class="form-control" id="f-phone" placeholder="Phone"></div>
                    <div class="col-md-3"><input class="form-control" id="f-room" placeholder="Room Number"></div>
                    <div class="col-md-3"><input class="form-control" id="f-block" placeholder="Hostel Block"></div>
                    <div class="col-md-3"><input class="form-control" id="f-course" placeholder="Course"></div>
                    <div class="col-md-3"><input class="form-control" id="f-year" placeholder="Year" type="number"></div>
                </div>
                <div class="mt-3">
                    <button class="btn btn-success btn-sm" onclick="submitStudent()">Save Student</button>
                    <button class="btn btn-secondary btn-sm ms-2" onclick="document.getElementById('add-form').classList.add('d-none')">Cancel</button>
                </div>
            </div>
        </div>
        <div class="card border-0 shadow-sm">
            <div class="card-body p-0">
                <table class="table table-hover mb-0">
                    <thead class="table-light"><tr><th>Roll No</th><th>Name</th><th>Room</th><th>Block</th><th>Course</th><th>Actions</th></tr></thead>
                    <tbody id="students-table"></tbody>
                </table>
            </div>
        </div>`;
    await refreshStudents();
}

function showAddStudent() { document.getElementById('add-form').classList.remove('d-none'); }

async function submitStudent() {
    const data = {
        roll_number: document.getElementById('f-roll').value,
        name: document.getElementById('f-name').value,
        email: document.getElementById('f-email').value,
        phone: document.getElementById('f-phone').value,
        room_number: document.getElementById('f-room').value,
        hostel_block: document.getElementById('f-block').value,
        course: document.getElementById('f-course').value,
        year: document.getElementById('f-year').value
    };
    if (!data.roll_number || !data.name) { alert('Roll number and name required'); return; }
    const res = await fetch('/api/students', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
    if (res.ok) { document.getElementById('add-form').classList.add('d-none'); await refreshStudents(); }
    else { const err = await res.json(); alert(err.error || 'Failed'); }
}

async function refreshStudents() {
    const students = await api('/api/students');
    document.getElementById('students-table').innerHTML = students.map(s => `
        <tr>
            <td><span class="badge bg-secondary">${s.roll_number}</span></td>
            <td>${s.name}</td><td>${s.room_number||'-'}</td><td>${s.hostel_block||'-'}</td><td>${s.course||'-'}</td>
            <td>
                <label class="btn btn-outline-primary btn-sm" title="Upload face">
                    <i class="fas fa-camera"></i>
                    <input type="file" accept="image/*" style="display:none" onchange="uploadFace(${s.id},this)">
                </label>
                <button class="btn btn-outline-danger btn-sm" onclick="deleteStudent(${s.id})"><i class="fas fa-trash"></i></button>
            </td>
        </tr>`).join('');
}

async function uploadFace(sid, input) {
    const file = input.files[0];
    if (!file) return;
    const form = new FormData();
    form.append('image', file);
    const res = await fetch('/api/students/' + sid + '/face', { method:'POST', body:form });
    const data = await res.json();
    alert(res.ok ? 'Face registered!' : data.error);
}

async function deleteStudent(sid) {
    if (!confirm('Remove this student?')) return;
    await fetch('/api/students/' + sid, { method:'DELETE' });
    await refreshStudents();
}

async function loadCamera() {
    const user = await checkAuth();
    if (!user) return;
    buildSidebar(user.role);
    document.getElementById('main-content').innerHTML = `
        <h5 class="fw-bold mb-4">Live Camera Feed</h5>
        <div class="row g-3">
            <div class="col-md-8"><div class="camera-feed">
                <img src="/api/camera/stream" alt="Live Feed">
            </div></div>
            <div class="col-md-4"><div class="card border-0 shadow-sm h-100">
                <div class="card-header bg-white fw-bold">Live Detections</div>
                <div class="card-body p-2" id="live-logs" style="max-height:500px;overflow-y:auto;"></div>
            </div></div>
        </div>`;
    setInterval(async () => {
        try {
            const logs = await api('/api/logs?limit=15');
            document.getElementById('live-logs').innerHTML = logs.map(l =>
                `<div class="log-item badge-${l.person_type} mb-1">
                    <strong>${l.person_type}</strong>${l.person_id ? ' &middot; ID '+l.person_id : ''}
                    &middot; ${(l.confidence*100).toFixed(1)}%
                    <div style="font-size:0.75rem" class="text-muted">${l.timestamp}</div>
                </div>`).join('');
        } catch(e) {}
    }, 2000);
}

async function loadAlerts() {
    const user = await checkAuth();
    if (!user) return;
    buildSidebar(user.role);
    document.getElementById('main-content').innerHTML = `
        <h5 class="fw-bold mb-4">Security Alerts</h5>
        <div class="card border-0 shadow-sm">
            <div class="card-body p-0">
                <table class="table table-hover mb-0">
                    <thead class="table-light"><tr><th>Time</th><th>Type</th><th>Person</th><th>Status</th><th>Action</th></tr></thead>
                    <tbody id="alerts-table"></tbody>
                </table>
            </div>
        </div>`;
    const alerts = await api('/api/alerts');
    document.getElementById('alerts-table').innerHTML = alerts.length
        ? alerts.map(a => `<tr>
            <td><small>${a.timestamp}</small></td>
            <td><span class="badge ${a.alert_type==='blacklist'?'bg-danger':'bg-warning text-dark'}">${a.alert_type}</span></td>
            <td>${a.person_id||'Unknown'}</td>
            <td>${a.acknowledged?'<span class="badge bg-success">Acknowledged</span>':'<span class="badge bg-secondary">Pending</span>'}</td>
            <td>${!a.acknowledged?'<button class="btn btn-sm btn-outline-success" onclick="ackAlert('+a.id+')">Acknowledge</button>':''}</td>
          </tr>`).join('')
        : '<tr><td colspan="5" class="text-center text-muted py-4">No alerts</td></tr>';
}

async function ackAlert(id) {
    await fetch('/api/alerts/'+id+'/ack', { method:'POST' });
    await loadAlerts();
}

async function loadAttendance() {
    const user = await checkAuth();
    if (!user) return;
    buildSidebar(user.role);
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('main-content').innerHTML = `
        <h5 class="fw-bold mb-4">Attendance Records</h5>
        <div class="d-flex gap-2 mb-3">
            <input type="date" id="att-date" class="form-control w-auto" value="${today}">
            <button class="btn btn-primary btn-sm" onclick="refreshAttendance()">Filter</button>
        </div>
        <div class="card border-0 shadow-sm">
            <div class="card-body p-0">
                <table class="table table-hover mb-0">
                    <thead class="table-light"><tr><th>Roll No</th><th>Name</th><th>Date</th><th>Time In</th><th>Time Out</th><th>Status</th></tr></thead>
                    <tbody id="att-table"></tbody>
                </table>
            </div>
        </div>`;
    await refreshAttendance();
}

async function refreshAttendance() {
    const date = document.getElementById('att-date').value;
    const records = await api('/api/attendance' + (date ? '?date='+date : ''));
    document.getElementById('att-table').innerHTML = records.length
        ? records.map(r => `<tr>
            <td><span class="badge bg-secondary">${r.roll_number}</span></td>
            <td>${r.name}</td><td>${r.date}</td>
            <td>${r.time_in?r.time_in.split(' ')[1].split('.')[0]:'-'}</td>
            <td>${r.time_out?r.time_out.split(' ')[1].split('.')[0]:'-'}</td>
            <td><span class="badge bg-success">${r.status}</span></td>
          </tr>`).join('')
        : '<tr><td colspan="6" class="text-center text-muted py-4">No records found</td></tr>';
}

async function loadLogs() {
    const user = await checkAuth();
    if (!user) return;
    buildSidebar(user.role);
    document.getElementById('main-content').innerHTML = `
        <h5 class="fw-bold mb-4">Recognition Logs</h5>
        <div class="card border-0 shadow-sm">
            <div class="card-body p-0">
                <table class="table table-hover mb-0">
                    <thead class="table-light"><tr><th>Timestamp</th><th>Type</th><th>Person ID</th><th>Confidence</th></tr></thead>
                    <tbody id="logs-table"></tbody>
                </table>
            </div>
        </div>`;
    const logs = await api('/api/logs?limit=100');
    document.getElementById('logs-table').innerHTML = logs.map(l => `<tr>
        <td><small>${l.timestamp}</small></td>
        <td><span class="badge badge-${l.person_type} px-2 py-1">${l.person_type}</span></td>
        <td>${l.person_id||'-'}</td>
        <td>
            <div class="progress d-inline-flex" style="height:6px;width:80px;vertical-align:middle">
                <div class="progress-bar ${l.confidence>0.7?'bg-success':'bg-warning'}" style="width:${(l.confidence*100).toFixed(0)}%"></div>
            </div>
            <small class="ms-1">${(l.confidence*100).toFixed(1)}%</small>
        </td>
    </tr>`).join('');
}
