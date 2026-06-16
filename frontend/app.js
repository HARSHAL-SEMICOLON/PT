// Resolve the API URL
function getApiUrl() {
  const savedUrl = localStorage.getItem('custom_backend_url');
  if (savedUrl) {
    return savedUrl.replace(/\/$/, ''); // Remove trailing slash
  }
  // Local development fallbacks
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.port === '3000') {
    return 'http://127.0.0.1:8000';
  }
  return window.location.origin;
}

let API_BASE_URL = getApiUrl();

// App State
let token = localStorage.getItem('token') || '';
let currentUser = null;

// DOM Selectors - Auth
const authSection = document.getElementById('auth-section');
const authCard = document.querySelector('.auth-card');
const authTitle = document.getElementById('auth-title');
const authSubtitle = document.getElementById('auth-subtitle');
const authForm = document.getElementById('auth-form');
const authEmail = document.getElementById('auth-email');
const authPassword = document.getElementById('auth-password');
const btnAuthSubmit = document.getElementById('btn-auth-submit');
const btnToggleAuth = document.getElementById('btn-toggle-auth');
const authToggleText = document.getElementById('auth-toggle-text');

// DOM Selectors - Registration fields
const registerOnlyElements = document.querySelectorAll('.register-only');
const regName = document.getElementById('reg-name');
const regRole = document.getElementById('reg-role');
const doctorFields = document.getElementById('doctor-fields');
const regSpecialization = document.getElementById('reg-specialization');
const patientFields = document.getElementById('patient-fields');
const regPhone = document.getElementById('reg-phone');

// DOM Selectors - Header/Nav
const userNav = document.getElementById('user-nav');
const userGreeting = document.getElementById('user-greeting');
const userRoleBadge = document.getElementById('user-role-badge');
const btnLogout = document.getElementById('btn-logout');

// DOM Selectors - Dashboard Views
const dashboardSection = document.getElementById('dashboard-section');
const doctorDashboard = document.getElementById('doctor-dashboard');
const patientDashboard = document.getElementById('patient-dashboard');

// Doctor Dashboard Elements
const doctorApptsList = document.getElementById('doctor-appts-list');
const doctorApptCount = document.getElementById('doctor-appt-count');
const recordPatientSelect = document.getElementById('record-patient-select');
const recordForm = document.getElementById('record-form');
const recordDiagnosis = document.getElementById('record-diagnosis');
const recordPrescription = document.getElementById('record-prescription');

// Patient Dashboard Elements
const bookDoctorSelect = document.getElementById('book-doctor-select');
const bookDate = document.getElementById('book-date');
const bookTime = document.getElementById('book-time');
const bookApptForm = document.getElementById('book-appt-form');
const patientApptsList = document.getElementById('patient-appts-list');
const patientApptCount = document.getElementById('patient-appt-count');
const patientRecordsList = document.getElementById('patient-records-list');

// Toast Element
const toast = document.getElementById('toast');

// DOM Selectors - API Configuration
const btnApiSettings = document.getElementById('btn-api-settings');
const apiModal = document.getElementById('api-modal');
const inputApiUrl = document.getElementById('input-api-url');
const btnApiSave = document.getElementById('btn-api-save');
const btnApiClose = document.getElementById('btn-api-close');

// Mode tracking
let isLoginMode = true;

// ── Auth Mode Toggling ────────────────────────────────────────────────────────

function toggleAuthMode() {
  isLoginMode = !isLoginMode;
  
  if (isLoginMode) {
    authTitle.textContent = 'Welcome Back';
    authSubtitle.textContent = 'Log in to manage your clinic appointments';
    btnAuthSubmit.textContent = 'Login';
    authToggleText.textContent = "Don't have an account?";
    btnToggleAuth.textContent = 'Register';
    
    // Hide register-only elements
    registerOnlyElements.forEach(el => el.classList.add('hidden'));
    doctorFields.classList.add('hidden');
    patientFields.classList.add('hidden');
  } else {
    authTitle.textContent = 'Create Account';
    authSubtitle.textContent = 'Register to book appointments & view medical history';
    btnAuthSubmit.textContent = 'Register';
    authToggleText.textContent = 'Already have an account?';
    btnToggleAuth.textContent = 'Login';
    
    // Show register-only elements
    registerOnlyElements.forEach(el => el.classList.remove('hidden'));
    updateRoleSpecificFields();
  }
}

function updateRoleSpecificFields() {
  if (isLoginMode) return;
  
  const role = regRole.value;
  if (role === 'doctor') {
    doctorFields.classList.remove('hidden');
    patientFields.classList.add('hidden');
  } else if (role === 'patient') {
    doctorFields.classList.add('hidden');
    patientFields.classList.remove('hidden');
  }
}

// ── Event Listeners ──────────────────────────────────────────────────────────

btnToggleAuth.addEventListener('click', (e) => {
  e.preventDefault();
  toggleAuthMode();
});

regRole.addEventListener('change', updateRoleSpecificFields);

btnLogout.addEventListener('click', logout);

authForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const email = authEmail.value;
  const password = authPassword.value;
  
  if (isLoginMode) {
    await handleLogin(email, password);
  } else {
    const name = regName.value;
    const role = regRole.value;
    const specialization = regSpecialization.value;
    const phone = regPhone.value;
    
    await handleRegister(name, email, password, role, specialization, phone);
  }
});

bookApptForm.addEventListener('submit', handleBookAppointment);
recordForm.addEventListener('submit', handleAddMedicalRecord);

// API Settings Modal Event Listeners
btnApiSettings.addEventListener('click', (e) => {
  e.preventDefault();
  inputApiUrl.value = localStorage.getItem('custom_backend_url') || '';
  apiModal.classList.remove('hidden');
});

btnApiClose.addEventListener('click', (e) => {
  e.preventDefault();
  apiModal.classList.add('hidden');
});

btnApiSave.addEventListener('click', (e) => {
  e.preventDefault();
  const newUrl = inputApiUrl.value.trim();
  if (newUrl) {
    localStorage.setItem('custom_backend_url', newUrl);
  } else {
    localStorage.removeItem('custom_backend_url');
  }
  API_BASE_URL = getApiUrl();
  apiModal.classList.add('hidden');
  showToast('API Backend URL updated!');
  
  if (token) {
    initApp();
  }
});

// ── Toast Utility ────────────────────────────────────────────────────────────

function showToast(message, type = 'success') {
  toast.textContent = message;
  toast.style.borderColor = type === 'success' ? 'var(--success-color)' : 'var(--danger-color)';
  toast.classList.remove('hidden');
  
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 4000);
}

// ── API Operations ───────────────────────────────────────────────────────────

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Attach Auth Headers if token exists
  if (token) {
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    };
  }
  
  try {
    const response = await fetch(url, options);
    
    if (response.status === 401) {
      logout();
      throw new Error('Session expired. Please log in again.');
    }
    
    if (response.status === 204) {
      return null;
    }
    
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Something went wrong');
    }
    
    return data;
  } catch (error) {
    showToast(error.message, 'error');
    throw error;
  }
}

// ── Auth Logic ───────────────────────────────────────────────────────────────

async function handleRegister(name, email, password, role, specialization, phone) {
  try {
    const payload = { name, email, password, role };
    if (role === 'doctor') payload.specialization = specialization;
    if (role === 'patient') payload.phone = phone;
    
    await apiRequest('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    showToast('Registration successful! Logging you in...');
    // Auto login
    await handleLogin(email, password);
  } catch (err) {
    // Error toast handled by apiRequest
  }
}

async function handleLogin(email, password) {
  try {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    });
    
    token = data.access_token;
    localStorage.setItem('token', token);
    
    await initApp();
    showToast('Login successful!');
  } catch (err) {
    // Error toast handled by apiRequest
  }
}

function logout() {
  token = '';
  currentUser = null;
  localStorage.removeItem('token');
  
  // Reset navigation & view state
  userNav.classList.add('hidden');
  dashboardSection.classList.add('hidden');
  authSection.classList.remove('hidden');
  authForm.reset();
  
  // Return to login mode default
  isLoginMode = false;
  toggleAuthMode();
}

// ── Initializing App ─────────────────────────────────────────────────────────

async function initApp() {
  if (!token) return;
  
  try {
    currentUser = await apiRequest('/auth/me');
    
    // Update header nav
    userGreeting.textContent = `Welcome, ${currentUser.name}`;
    userRoleBadge.textContent = currentUser.role;
    userRoleBadge.className = `badge ${currentUser.role}`;
    userNav.classList.remove('hidden');
    
    // Toggle dashboards
    authSection.classList.add('hidden');
    dashboardSection.classList.remove('hidden');
    
    loadDashboard();
  } catch (err) {
    logout();
  }
}

// ── Dashboard Loading ────────────────────────────────────────────────────────

function loadDashboard() {
  // Hide both dashboards first
  doctorDashboard.classList.add('hidden');
  patientDashboard.classList.add('hidden');
  
  if (currentUser.role === 'doctor') {
    doctorDashboard.classList.remove('hidden');
    initDoctorDashboard();
  } else if (currentUser.role === 'patient') {
    patientDashboard.classList.remove('hidden');
    initPatientDashboard();
  }
}

// ── Doctor Dashboard Logic ───────────────────────────────────────────────────

async function initDoctorDashboard() {
  loadDoctorAppointments();
  loadDoctorPatients();
}

async function loadDoctorAppointments() {
  try {
    const appointments = await apiRequest('/appointments');
    doctorApptCount.textContent = appointments.length;
    
    doctorApptsList.innerHTML = appointments.length === 0 
      ? '<tr><td colspan="5" class="text-center" style="text-align: center; color: var(--text-muted)">No appointments booked yet.</td></tr>'
      : appointments.map(appt => `
          <tr>
            <td style="font-weight: 500">${appt.patient?.user?.name || 'Unknown Patient'}</td>
            <td>${appt.appointment_date}</td>
            <td>${appt.appointment_time}</td>
            <td><span class="status-badge ${appt.status}">${appt.status}</span></td>
            <td>
              ${appt.status === 'scheduled' 
                ? `<button class="btn btn-danger btn-sm" onclick="cancelAppointment('${appt.id}')">Cancel</button>
                   <button class="btn btn-secondary btn-sm" onclick="completeAppointment('${appt.id}')">Complete</button>` 
                : '-'}
            </td>
          </tr>
        `).join('');
  } catch (err) {}
}

async function loadDoctorPatients() {
  try {
    const patients = await apiRequest('/patients');
    
    // Fill patients select dropdown in medical record form
    recordPatientSelect.innerHTML = '<option value="">Choose a patient...</option>' + 
      patients.map(p => `<option value="${p.id}">${p.user?.name || 'Unknown'} (${p.phone || 'No phone'})</option>`).join('');
  } catch (err) {}
}

async function handleAddMedicalRecord(e) {
  e.preventDefault();
  
  const patientId = recordPatientSelect.value;
  const diagnosis = recordDiagnosis.value;
  const prescription = recordPrescription.value;
  
  try {
    await apiRequest('/medical-records', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient_id: patientId, diagnosis, prescription })
    });
    
    showToast('Medical record successfully created!');
    recordForm.reset();
  } catch (err) {}
}

// ── Patient Dashboard Logic ──────────────────────────────────────────────────

async function initPatientDashboard() {
  loadPatientDoctors();
  loadPatientAppointments();
  loadPatientMedicalRecords();
}

async function loadPatientDoctors() {
  try {
    const doctors = await apiRequest('/doctors');
    bookDoctorSelect.innerHTML = '<option value="">Select a specialist...</option>' +
      doctors.map(d => `<option value="${d.id}">${d.user?.name || 'Unknown'} (${d.specialization || 'General'})</option>`).join('');
  } catch (err) {}
}

async function loadPatientAppointments() {
  try {
    const appointments = await apiRequest('/appointments');
    patientApptCount.textContent = appointments.length;
    
    patientApptsList.innerHTML = appointments.length === 0
      ? '<tr><td colspan="6" class="text-center" style="text-align: center; color: var(--text-muted)">You have no booked appointments.</td></tr>'
      : appointments.map(appt => `
          <tr>
            <td style="font-weight: 500">${appt.doctor?.user?.name || 'Unknown Doctor'}</td>
            <td><span class="badge doctor">${appt.doctor?.specialization || 'General'}</span></td>
            <td>${appt.appointment_date}</td>
            <td>${appt.appointment_time}</td>
            <td><span class="status-badge ${appt.status}">${appt.status}</span></td>
            <td>
              ${appt.status === 'scheduled' 
                ? `<button class="btn btn-danger btn-sm" onclick="cancelAppointment('${appt.id}')">Cancel</button>
                   <button class="btn btn-secondary btn-sm" onclick="promptReschedule('${appt.id}', '${appt.appointment_date}', '${appt.appointment_time}')">Reschedule</button>` 
                : '-'}
            </td>
          </tr>
        `).join('');
  } catch (err) {}
}

async function loadPatientMedicalRecords() {
  try {
    const records = await apiRequest('/medical-records');
    
    patientRecordsList.innerHTML = records.length === 0
      ? '<p style="grid-column: span 3; text-align: center; color: var(--text-muted); padding: 30px 0;">No medical history records found.</p>'
      : records.map(rec => `
          <div class="glass-panel record-card">
            <div class="record-card-header">
              <h3>Diagnosis & Treatment</h3>
              <span class="record-date">${new Date(rec.created_at).toLocaleDateString()}</span>
            </div>
            <div class="record-field">
              <span>Doctor</span>
              <p style="font-weight: 500">${rec.doctor?.user?.name || 'Unknown Doctor'} (${rec.doctor?.specialization || 'General'})</p>
            </div>
            <div class="record-field">
              <span>Diagnosis</span>
              <p>${rec.diagnosis || 'None'}</p>
            </div>
            <div class="record-field">
              <span>Prescription</span>
              <p style="color: #38bdf8; font-weight: 500">${rec.prescription || 'None'}</p>
            </div>
          </div>
        `).join('');
  } catch (err) {}
}

async function handleBookAppointment(e) {
  e.preventDefault();
  
  const doctorId = bookDoctorSelect.value;
  const dateVal = bookDate.value;
  const timeVal = bookTime.value;
  
  // Format time value to include seconds (HH:MM:SS) if missing
  const formattedTime = timeVal.length === 5 ? `${timeVal}:00` : timeVal;
  
  try {
    await apiRequest('/appointments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doctor_id: doctorId,
        appointment_date: dateVal,
        appointment_time: formattedTime
      })
    });
    
    showToast('Appointment booked successfully!');
    bookApptForm.reset();
    initPatientDashboard();
  } catch (err) {}
}

// ── Global Reschedule/Cancel/Complete Action Helpers ──────────────────────────

window.cancelAppointment = async function(id) {
  if (!confirm('Are you sure you want to cancel this appointment?')) return;
  
  try {
    await apiRequest(`/appointments/${id}`, { method: 'DELETE' });
    showToast('Appointment cancelled successfully.');
    
    if (currentUser.role === 'patient') {
      loadPatientAppointments();
    } else {
      loadDoctorAppointments();
    }
  } catch (err) {}
};

window.completeAppointment = async function(id) {
  try {
    await apiRequest(`/appointments/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'completed' })
    });
    showToast('Appointment marked as completed.');
    loadDoctorAppointments();
  } catch (err) {}
};

window.promptReschedule = async function(id, currentDate, currentTime) {
  const newDate = prompt('Enter new date (YYYY-MM-DD):', currentDate);
  if (!newDate) return;
  
  let newTime = prompt('Enter new time (HH:MM):', currentTime.substring(0, 5));
  if (!newTime) return;
  
  if (newTime.length === 5) newTime = `${newTime}:00`;
  
  try {
    await apiRequest(`/appointments/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        appointment_date: newDate,
        appointment_time: newTime
      })
    });
    
    showToast('Appointment rescheduled successfully.');
    loadPatientAppointments();
  } catch (err) {}
};

// ── App Startup ──────────────────────────────────────────────────────────────

initApp();
