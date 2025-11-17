// Dashboard JavaScript
const API_BASE_URL = 'http://localhost:8000';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
});

// Load dashboard data
async function loadDashboardData() {
    // Mock data for now - replace with real API calls
    updateStats({
        totalCandidates: 0,
        messagesSent: 0,
        responseRate: '0%',
        activeRoles: 0
    });
    
    // Load pipeline (would call API)
    loadPipeline();
    
    // Load analytics (would call API)
    updateAnalytics();
}

// Update stats cards
function updateStats(data) {
    document.getElementById('total-candidates').textContent = data.totalCandidates || '-';
    document.getElementById('messages-sent').textContent = data.messagesSent || '-';
    document.getElementById('response-rate').textContent = data.responseRate || '-';
    document.getElementById('active-roles').textContent = data.activeRoles || '-';
}

// Load pipeline
async function loadPipeline() {
    const pipelineList = document.getElementById('pipeline-list');
    
    // TODO: Replace with actual API call
    // const response = await fetch(`${API_BASE_URL}/candidates`);
    // const candidates = await response.json();
    
    // For now, show empty state
    pipelineList.innerHTML = `
        <div class="empty-state">
            <p>No candidates in pipeline yet. Start by uploading CVs or connecting with candidates on LinkedIn.</p>
        </div>
    `;
}

// Filter pipeline
function filterPipeline() {
    const statusFilter = document.getElementById('status-filter').value;
    const searchFilter = document.getElementById('search-filter').value.toLowerCase();
    
    // TODO: Implement filtering logic
    console.log('Filtering by:', { statusFilter, searchFilter });
}

// Refresh pipeline
async function refreshPipeline() {
    await loadPipeline();
}

// Update analytics
async function updateAnalytics() {
    const timeRange = document.getElementById('time-range').value;
    
    // TODO: Replace with actual API call
    // const response = await fetch(`${API_BASE_URL}/analytics?range=${timeRange}`);
    // const analytics = await response.json();
    
    // Mock data
    document.getElementById('avg-response-time').textContent = '-';
    document.getElementById('conversion-rate').textContent = '-';
    document.getElementById('top-source').textContent = '-';
}

// Open tool modal
function openTool(toolName) {
    const modal = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    
    modal.classList.add('active');
    
    switch(toolName) {
        case 'cv-upload':
            modalTitle.textContent = 'Upload CV';
            modalBody.innerHTML = getCVUploadForm();
            break;
        case 'jd-normalize':
            modalTitle.textContent = 'Normalize Job Description';
            modalBody.innerHTML = getJDNormalizeForm();
            break;
        case 'endorsement':
            modalTitle.textContent = 'Generate Endorsement';
            modalBody.innerHTML = getEndorsementForm();
            break;
        case 'tone-settings':
            modalTitle.textContent = 'Tone Profile Settings';
            modalBody.innerHTML = getToneSettingsForm();
            loadToneProfile();
            break;
    }
}

// Close modal
function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
}

// CV Upload Form
function getCVUploadForm() {
    return `
        <form id="cv-upload-form" onsubmit="handleCVUpload(event)">
            <div class="form-group">
                <label>Upload CV File (PDF or DOCX)</label>
                <input type="file" id="cv-file" accept=".pdf,.docx" required>
            </div>
            <div class="form-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-primary">Upload & Parse</button>
            </div>
        </form>
    `;
}

// JD Normalize Form
function getJDNormalizeForm() {
    return `
        <form id="jd-normalize-form" onsubmit="handleJDNormalize(event)">
            <div class="form-group">
                <label>Job Description Text</label>
                <textarea id="jd-text" placeholder="Paste job description here..." required></textarea>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="use-llm"> Use LLM extraction (more accurate)
                </label>
            </div>
            <div class="form-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-primary">Normalize</button>
            </div>
        </form>
    `;
}

// Endorsement Form
function getEndorsementForm() {
    return `
        <form id="endorsement-form" onsubmit="handleEndorsement(event)">
            <div class="form-group">
                <label>CV Data (JSON)</label>
                <textarea id="cv-data" placeholder="Paste normalized CV JSON..." required></textarea>
            </div>
            <div class="form-group">
                <label>Job Description Data (JSON)</label>
                <textarea id="jd-data" placeholder="Paste normalized JD JSON..." required></textarea>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="use-llm-endorsement"> Use LLM generation
                </label>
            </div>
            <div class="form-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-primary">Generate Endorsement</button>
            </div>
        </form>
    `;
}

// Tone Settings Form
function getToneSettingsForm() {
    return `
        <form id="tone-form" onsubmit="handleToneUpdate(event)">
            <div class="form-group">
                <label>Persona Name</label>
                <input type="text" id="persona-name" required>
            </div>
            <div class="form-group">
                <label>Company</label>
                <input type="text" id="company" required>
            </div>
            <div class="form-group">
                <label>Signoff</label>
                <textarea id="signoff" required></textarea>
            </div>
            <div class="form-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn-primary">Save Changes</button>
            </div>
        </form>
    `;
}

// Handle CV Upload
async function handleCVUpload(event) {
    event.preventDefault();
    const fileInput = document.getElementById('cv-file');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE_URL}/ingest/cv`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Upload failed');
        
        const data = await response.json();
        alert('CV uploaded and parsed successfully!');
        closeModal();
        refreshPipeline();
    } catch (error) {
        alert('Error uploading CV: ' + error.message);
    }
}

// Handle JD Normalize
async function handleJDNormalize(event) {
    event.preventDefault();
    const text = document.getElementById('jd-text').value;
    const useLLM = document.getElementById('use-llm').checked;
    
    try {
        const response = await fetch(`${API_BASE_URL}/normalize/jd?use_llm=${useLLM}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) throw new Error('Normalization failed');
        
        const data = await response.json();
        alert('JD normalized successfully!');
        console.log('Normalized JD:', data);
        closeModal();
    } catch (error) {
        alert('Error normalizing JD: ' + error.message);
    }
}

// Handle Endorsement
async function handleEndorsement(event) {
    event.preventDefault();
    const cvData = JSON.parse(document.getElementById('cv-data').value);
    const jdData = JSON.parse(document.getElementById('jd-data').value);
    const useLLM = document.getElementById('use-llm-endorsement').checked;
    
    try {
        const response = await fetch(`${API_BASE_URL}/endorsement/generate?use_llm=${useLLM}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cv: cvData,
                jd: jdData,
                interview: { transcript: '', notes: '' }
            })
        });
        
        if (!response.ok) throw new Error('Generation failed');
        
        const data = await response.json();
        alert('Endorsement generated!');
        console.log('Endorsement:', data);
        closeModal();
    } catch (error) {
        alert('Error generating endorsement: ' + error.message);
    }
}

// Load Tone Profile
async function loadToneProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/tone`);
        if (!response.ok) throw new Error('Failed to load tone profile');
        
        const data = await response.json();
        document.getElementById('persona-name').value = data.persona_name || '';
        document.getElementById('company').value = data.company || '';
        document.getElementById('signoff').value = data.signoff || '';
    } catch (error) {
        console.error('Error loading tone profile:', error);
    }
}

// Handle Tone Update
async function handleToneUpdate(event) {
    event.preventDefault();
    const personaName = document.getElementById('persona-name').value;
    const company = document.getElementById('company').value;
    const signoff = document.getElementById('signoff').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/tone`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                persona_name: personaName,
                company: company,
                signoff: signoff
            })
        });
        
        if (!response.ok) throw new Error('Update failed');
        
        alert('Tone profile updated successfully!');
        closeModal();
    } catch (error) {
        alert('Error updating tone profile: ' + error.message);
    }
}

