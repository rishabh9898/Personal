// API Base URL
const API_BASE = '/api';

// Current results storage
let currentResults = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadUploadedFiles();
});

// Setup all event listeners
function setupEventListeners() {
    // Search form
    document.getElementById('search-form').addEventListener('submit', handleSearch);

    // Upload form
    document.getElementById('upload-form').addEventListener('submit', handleUpload);

    // File input change
    document.getElementById('resume-files').addEventListener('change', displaySelectedFiles);
}

// Tab switching
function switchTab(tabName, element) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Add active class to clicked button
    if (element) {
        element.classList.add('active');
    }

    // Load data for specific tabs
    if (tabName === 'status') {
        loadAgentStatus();
    }
}

// Toggle collapsible sections
function toggleSection(element) {
    const content = element.nextElementSibling;
    const isExpanded = content.classList.contains('expanded');

    if (isExpanded) {
        content.classList.remove('expanded');
        element.textContent = element.textContent.replace('⮟', '⮞');
    } else {
        content.classList.add('expanded');
        element.textContent = element.textContent.replace('⮞', '⮟');
    }
}

// Handle candidate search
async function handleSearch(e) {
    e.preventDefault();

    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.loading-spinner');

    // Get form data
    const jobTitle = document.getElementById('job-title').value;
    const location = document.getElementById('location').value;
    const keywords = document.getElementById('keywords').value
        .split(',')
        .map(k => k.trim())
        .filter(k => k);

    const jobDescription = document.getElementById('job-description').value;
    const requiredSkills = document.getElementById('required-skills').value
        .split(',')
        .map(s => s.trim())
        .filter(s => s);
    const minExperience = parseInt(document.getElementById('min-experience').value) || 0;

    const searchLinkedIn = document.getElementById('search-linkedin').checked;
    const searchIndeed = document.getElementById('search-indeed').checked;

    const linkedinEmail = document.getElementById('linkedin-email').value;
    const linkedinPassword = document.getElementById('linkedin-password').value;

    // Prepare request
    const request = {
        mode: 'full_search',
        job_title: jobTitle,
        location: location,
        keywords: keywords,
        search_linkedin: searchLinkedIn,
        search_indeed: searchIndeed,
        rank_candidates: jobDescription ? true : false,
        shortlist_size: 10
    };

    // Add job requirements if provided
    if (jobDescription) {
        request.job_requirements = {
            title: jobTitle,
            description: jobDescription,
            required_skills: requiredSkills,
            min_years_experience: minExperience,
            location: location
        };
    }

    // Add LinkedIn credentials if provided
    if (linkedinEmail && linkedinPassword) {
        request.linkedin_email = linkedinEmail;
        request.linkedin_password = linkedinPassword;
    }

    try {
        // Show loading state
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        spinner.style.display = 'inline';

        // Make API call
        const response = await fetch(`${API_BASE}/orchestrate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentResults = data;

        // Show results
        displayResults(data);

        // Switch to results tab
        switchTab('results');

        showToast('Search completed successfully!', 'success');

    } catch (error) {
        console.error('Search error:', error);
        showToast(`Search failed: ${error.message}`, 'error');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// Handle resume upload
async function handleUpload(e) {
    e.preventDefault();

    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.loading-spinner');

    const fileInput = document.getElementById('resume-files');
    const files = fileInput.files;

    if (files.length === 0) {
        showToast('Please select at least one file', 'warning');
        return;
    }

    try {
        // Show loading state
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        spinner.style.display = 'inline';

        // Upload files
        const formData = new FormData();
        for (let file of files) {
            formData.append('files', file);
        }

        const uploadResponse = await fetch(`${API_BASE}/upload-resumes`, {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            throw new Error(`Upload failed! status: ${uploadResponse.status}`);
        }

        const uploadData = await uploadResponse.json();
        const filePaths = uploadData.file_paths;

        // Parse resumes
        const parseResponse = await fetch(`${API_BASE}/parse-resumes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(filePaths)
        });

        if (!parseResponse.ok) {
            throw new Error(`Parsing failed! status: ${parseResponse.status}`);
        }

        const parseData = await parseResponse.json();

        // Store and display results
        currentResults = {
            mode: 'parse_only',
            total_candidates_found: parseData.candidates.length,
            candidates: parseData.candidates,
            sources: { uploaded_resumes: parseData.candidates.length }
        };

        displayResults(currentResults);

        // Switch to results tab
        switchTab('results');

        // Refresh uploaded files list
        loadUploadedFiles();

        // Clear file input
        fileInput.value = '';
        document.getElementById('file-list').innerHTML = '';

        showToast(`Successfully parsed ${parseData.candidates.length} resumes!`, 'success');

    } catch (error) {
        console.error('Upload error:', error);
        showToast(`Upload failed: ${error.message}`, 'error');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// Display selected files
function displaySelectedFiles(e) {
    const files = e.target.files;
    const fileList = document.getElementById('file-list');

    fileList.innerHTML = '';

    for (let file of files) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span>📄 ${file.name} (${formatFileSize(file.size)})</span>
        `;
        fileList.appendChild(fileItem);
    }
}

// Load uploaded files list
async function loadUploadedFiles() {
    try {
        const response = await fetch(`${API_BASE}/resumes`);
        const data = await response.json();

        const container = document.getElementById('uploaded-files-list');

        if (data.files.length === 0) {
            container.innerHTML = '<p class="help-text">No files uploaded yet</p>';
            return;
        }

        container.innerHTML = data.files.map(file => `
            <div class="file-item">
                <span>📄 ${file}</span>
                <button onclick="deleteResume('${file}')" class="btn btn-danger" style="padding: 6px 12px; font-size: 0.9rem;">
                    Delete
                </button>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading files:', error);
    }
}

// Delete resume file
async function deleteResume(filename) {
    if (!confirm(`Delete ${filename}?`)) return;

    try {
        const response = await fetch(`${API_BASE}/resumes/${filename}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('File deleted successfully', 'success');
            loadUploadedFiles();
        } else {
            throw new Error('Delete failed');
        }
    } catch (error) {
        showToast(`Failed to delete file: ${error.message}`, 'error');
    }
}

// Display results
function displayResults(data) {
    const container = document.getElementById('results-container');

    if (!data || data.total_candidates_found === 0) {
        container.innerHTML = '<p class="empty-state">No candidates found</p>';
        return;
    }

    let html = '';

    // Summary section
    html += `
        <div class="results-summary">
            <h3>📊 Search Results Summary</h3>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">${data.total_candidates_found}</div>
                    <div class="stat-label">Total Candidates</div>
                </div>
                ${data.sources.linkedin ? `
                    <div class="stat-card">
                        <div class="stat-value">${data.sources.linkedin}</div>
                        <div class="stat-label">From LinkedIn</div>
                    </div>
                ` : ''}
                ${data.sources.indeed ? `
                    <div class="stat-card">
                        <div class="stat-value">${data.sources.indeed}</div>
                        <div class="stat-label">From Indeed</div>
                    </div>
                ` : ''}
                ${data.sources.uploaded_resumes ? `
                    <div class="stat-card">
                        <div class="stat-value">${data.sources.uploaded_resumes}</div>
                        <div class="stat-label">From Uploads</div>
                    </div>
                ` : ''}
            </div>
        </div>
    `;

    // Ranked candidates or raw candidates
    const candidates = data.ranked_results?.ranked_candidates || data.candidates;

    candidates.forEach(candidate => {
        html += renderCandidateCard(candidate);
    });

    container.innerHTML = html;
}

// Render individual candidate card
function renderCandidateCard(candidate) {
    const score = candidate.overall_score;
    let scoreClass = '';
    let matchQuality = '';

    if (score) {
        if (score >= 80) {
            scoreClass = 'score-excellent';
            matchQuality = 'Excellent Match';
        } else if (score >= 65) {
            scoreClass = 'score-good';
            matchQuality = 'Good Match';
        } else if (score >= 50) {
            scoreClass = 'score-fair';
            matchQuality = 'Fair Match';
        } else {
            scoreClass = 'score-poor';
            matchQuality = 'Poor Match';
        }
    }

    return `
        <div class="candidate-card">
            <div class="candidate-header">
                <div>
                    <div class="candidate-name">${candidate.name || candidate.title || 'Unknown'}</div>
                    ${candidate.headline ? `<p style="color: var(--text-secondary); margin-top: 5px;">${candidate.headline}</p>` : ''}
                </div>
                ${score ? `
                    <div class="candidate-score ${scoreClass}">
                        ${score.toFixed(0)}/100
                        <div style="font-size: 0.75rem; font-weight: normal;">${matchQuality}</div>
                    </div>
                ` : ''}
            </div>

            <div class="candidate-info">
                ${candidate.email ? `<div class="info-item"><span class="info-label">Email:</span> ${candidate.email}</div>` : ''}
                ${candidate.phone ? `<div class="info-item"><span class="info-label">Phone:</span> ${candidate.phone}</div>` : ''}
                ${candidate.location ? `<div class="info-item"><span class="info-label">Location:</span> ${candidate.location}</div>` : ''}
                ${candidate.years_of_experience ? `<div class="info-item"><span class="info-label">Experience:</span> ${candidate.years_of_experience} years</div>` : ''}
                ${candidate.source ? `<div class="info-item"><span class="info-label">Source:</span> ${candidate.source}</div>` : ''}
                ${candidate.profile_url ? `<div class="info-item"><a href="${candidate.profile_url}" target="_blank" style="color: var(--primary-color);">View Profile →</a></div>` : ''}
            </div>

            ${candidate.summary || candidate.snippet ? `
                <div style="margin-top: 15px;">
                    <strong>Summary:</strong>
                    <p style="color: var(--text-secondary); margin-top: 5px;">${candidate.summary || candidate.snippet}</p>
                </div>
            ` : ''}

            ${candidate.skills && candidate.skills.length > 0 ? `
                <div class="skills-list">
                    ${candidate.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                </div>
            ` : ''}

            ${candidate.scoring ? renderScoring(candidate.scoring) : ''}
        </div>
    `;
}

// Render scoring details
function renderScoring(scoring) {
    return `
        <div style="margin-top: 20px; padding-top: 20px; border-top: 2px solid var(--border-color);">
            <h4 style="margin-bottom: 10px;">AI Analysis</h4>

            ${scoring.strengths && scoring.strengths.length > 0 ? `
                <div style="margin-bottom: 10px;">
                    <strong style="color: var(--success-color);">✓ Strengths:</strong>
                    <ul style="margin-top: 5px; padding-left: 20px;">
                        ${scoring.strengths.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            ${scoring.weaknesses && scoring.weaknesses.length > 0 ? `
                <div style="margin-bottom: 10px;">
                    <strong style="color: var(--warning-color);">⚠ Areas of Concern:</strong>
                    <ul style="margin-top: 5px; padding-left: 20px;">
                        ${scoring.weaknesses.map(w => `<li>${w}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            ${scoring.recommendation ? `
                <div style="margin-top: 10px; padding: 10px; background: #f0f9ff; border-radius: 6px;">
                    <strong>Recommendation:</strong>
                    <p style="margin-top: 5px;">${scoring.recommendation}</p>
                </div>
            ` : ''}
        </div>
    `;
}

// Load agent status
async function loadAgentStatus() {
    const container = document.getElementById('agent-status-container');

    try {
        const response = await fetch(`${API_BASE}/agents/status`);
        const data = await response.json();

        let html = '<div class="agent-grid">';

        for (const [key, agent] of Object.entries(data)) {
            html += `
                <div class="agent-card">
                    <h4>${agent.agent_type}</h4>
                    <div style="margin: 10px 0;">
                        <span class="status-badge status-${agent.status}">${agent.status.toUpperCase()}</span>
                    </div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary);">
                        <p><strong>Agent ID:</strong> ${agent.agent_id}</p>
                        <p><strong>Created:</strong> ${new Date(agent.created_at).toLocaleString()}</p>
                        ${agent.last_run ? `<p><strong>Last Run:</strong> ${new Date(agent.last_run).toLocaleString()}</p>` : ''}
                        <p><strong>Results:</strong> ${agent.results_count}</p>
                        <p><strong>Errors:</strong> ${agent.errors_count}</p>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        container.innerHTML = html;

    } catch (error) {
        console.error('Error loading agent status:', error);
        container.innerHTML = '<p class="empty-state">Failed to load agent status</p>';
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;

    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    // Hide toast after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// Utility: Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
