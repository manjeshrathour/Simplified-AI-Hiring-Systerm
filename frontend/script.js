// AI Recruiting System - Frontend Script

// const API_BASE = 'http://localhost:8000';

// const API_BASE = "https://432c-106-192-229-160.ngrok-free.app";
// const WS_BASE = "wss://432c-106-192-229-160.ngrok-free.app";

const API_BASE = "https://mac-interlunar-nonancestrally.ngrok-free.dev";
const WS_BASE = "wss://mac-interlunar-nonancestrally.ngrok-free.dev";

// State Management
let currentTab = 'dashboard';
let allInterviews = [];
let showCompletedInterviews = false;

// DOM Element References
const loadingEl = document.getElementById('loading');
const notificationEl = document.getElementById('notification');
const fileUploadEl = document.getElementById('file-upload');
const postJobBtn = document.getElementById('post-job-btn');
const postJobModal = document.getElementById('post-job-modal');
const closeModalBtn = document.getElementById('close-modal-btn');
const postJobForm = document.getElementById('post-job-form');
const showCompletedToggle = document.getElementById('show-completed-interviews-toggle');

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupDynamicEventListeners();
    loadData();
});

// Event Listener Setup
function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // File upload
    fileUploadEl.addEventListener('change', handleFileUpload);

    // Modal controls
    postJobBtn.addEventListener('click', () => postJobModal.classList.remove('hidden'));
    closeModalBtn.addEventListener('click', () => postJobModal.classList.add('hidden'));
    postJobModal.addEventListener('click', (e) => {
        if (e.target === postJobModal) postJobModal.classList.add('hidden');
    });
    postJobForm.addEventListener('submit', handlePostJobSubmit);

    // Interview filter toggle - Show completed interviews
    showCompletedToggle.addEventListener('change', () => {
        showCompletedInterviews = showCompletedToggle.checked;
        renderInterviews();
    });
}

function setupDynamicEventListeners() {
    const mainContent = document.querySelector('.main-content');

    mainContent.addEventListener('click', (event) => {
        // Handle job deletion
        const deleteJobButton = event.target.closest('.delete-job-btn');
        if (deleteJobButton) {
            const jobId = deleteJobButton.dataset.jobId;
            if (jobId) {
                handleDeleteJob(jobId);
            }
            return;
        }

        // Handle interview deletion
        const deleteInterviewButton = event.target.closest('.delete-interview-btn');
        if (deleteInterviewButton) {
            const interviewId = deleteInterviewButton.dataset.interviewId;
            if (interviewId) {
                handleDeleteInterview(interviewId);
            }
            return;
        }

        // NEW: Handle candidate deletion
        const deleteCandidateButton = event.target.closest('.delete-candidate-btn');
        if (deleteCandidateButton) {
            const email = deleteCandidateButton.dataset.email;
            if (email) {
                handleDeleteCandidate(email);
            }
            return;
        }
    });
}
// ... (existing code) ...

// Candidate Deletion Handler
async function handleDeleteCandidate(email) {
    if (!confirm(`Are you sure you want to delete candidate ${email}? This action cannot be undone.`)) {
        return;
    }

    showNotification(`Deleting candidate...`, 'success');
    loadingEl.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE}/candidates/${email}`, {
            method: 'DELETE'
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Failed to delete candidate.');
        }

        showNotification(result.message || 'Candidate deleted successfully!', 'success');
        await loadData();
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        loadingEl.classList.add('hidden');
    }
}


// Tab Switching Logic
function switchTab(tabName) {
    if (currentTab === tabName) return;

    currentTab = tabName;

    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });

    loadData();
}

// Data Loading Logic
async function loadData() {
    loadingEl.classList.remove('hidden');

    try {
        let data;
        switch (currentTab) {
            case 'dashboard':
                data = await fetchData('/stats');
                renderDashboard(data.stats || data);
                break;
            case 'jobs':
                data = await fetchData('/jobs/');
                renderJobs(data.jobs || []);
                break;
            case 'candidates':
                data = await fetchData('/candidates/');
                renderCandidates(data.candidates || []);
                break;
            case 'interviews':
                data = await fetchData('/interviews/');
                allInterviews = data.interviews || [];
                renderInterviews();
                break;
        }
    } catch (error) {
        showNotification(`Error loading data: ${error.message}`, 'error');
    } finally {
        loadingEl.classList.add('hidden');
    }
}

// File Upload Handler
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    showNotification('Uploading and processing resume...', 'success');
    loadingEl.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload-resume/`, {
            method: 'POST',
            body: formData,
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Upload failed.');
        }

        showNotification(result.message || 'Resume processed!', 'success');
        switchTab('candidates');
    } catch (error) {
        showNotification(`Upload failed: ${error.message}`, 'error');
    } finally {
        fileUploadEl.value = '';
        loadingEl.classList.add('hidden');
    }
}

// Job Deletion Handler
async function handleDeleteJob(jobId) {
    if (!confirm(`Are you sure you want to delete job posting ${jobId}? This action cannot be undone.`)) {
        return;
    }

    showNotification(`Deleting job ${jobId}...`, 'success');
    loadingEl.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
            method: 'DELETE'
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Failed to delete job.');
        }

        showNotification(result.message || 'Job deleted successfully!', 'success');
        await loadData();
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        loadingEl.classList.add('hidden');
    }
}

// Interview Deletion Handler
async function handleDeleteInterview(interviewId) {
    if (!confirm(`Are you sure you want to delete this interview? This action cannot be undone.`)) {
        return;
    }

    showNotification(`Deleting interview...`, 'success');
    loadingEl.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE}/interviews/${interviewId}`, {
            method: 'DELETE'
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Failed to delete interview.');
        }

        showNotification(result.message || 'Interview deleted successfully!', 'success');
        await loadData();
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        loadingEl.classList.add('hidden');
    }
}


// Post Job Form Handler
async function handlePostJobSubmit(event) {
    event.preventDefault();
    loadingEl.classList.remove('hidden');

    // Generate unique job ID automatically
    const timestamp = Date.now();
    const randomNum = Math.floor(Math.random() * 1000);
    const autoJobId = `JOB-${timestamp}-${randomNum}`;

    const jobData = {
        job_id: autoJobId,
        title: document.getElementById('job-title').value.trim(),
        location: document.getElementById('job-location').value.trim(),
        employment_type: document.getElementById('employment-type').value.trim(),
        description: document.getElementById('job-description').value.trim(),
        required_skills: document.getElementById('required-skills').value
            .split(',')
            .map(skill => skill.trim())
            .filter(skill => skill.length > 0),
    };

    try {
        const response = await fetch(`${API_BASE}/jobs/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jobData)
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Failed to post job.');
        }

        showNotification(result.message || 'Job posted successfully!', 'success');
        postJobModal.classList.add('hidden');
        postJobForm.reset();
        loadData();
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        loadingEl.classList.add('hidden');
    }
}

// API Helper Function
// async function fetchData(endpoint) {
//     const response = await fetch(`${API_BASE}${endpoint}`);

//     if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail || `Server returned status ${response.status}`);
//     }

//     return response.json();
// }


async function fetchData(endpoint) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "69420" // ✅ Add this line
        }
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Server returned status ${response.status}`);
    }

    return response.json();
}


// Rendering Functions

function renderDashboard(statsData) {
    if (!statsData) return;

    document.getElementById('stat-candidates').textContent = statsData.total_candidates ?? '0';
    document.getElementById('stat-jobs').textContent = statsData.active_jobs ?? '0';
    document.getElementById('stat-interviews').textContent = statsData.interviews_scheduled ?? '0';

    // NEW: Render Vector Count in mini-stat
    const vectorMini = document.getElementById('stat-vectors-mini');
    if (vectorMini) vectorMini.textContent = (statsData.vector_count ?? '0') + ' Embeddings';

    // NEW: Render Average Score
    const analytics = statsData.analytics || {};
    const avgScore = analytics.average_score || 0;
    document.getElementById('stat-avg-score').textContent = avgScore.toFixed(1) + '%';

    // NEW: Render Chart
    const ctx = document.getElementById('performanceChart');
    if (ctx) {
        // Destroy existing chart if any
        if (window.myPerformanceChart) {
            window.myPerformanceChart.destroy();
        }

        const breakdown = analytics.interviews_breakdown || { scheduled: 0, completed: 0 };

        window.myPerformanceChart = new Chart(ctx, {
            type: 'bar', // or 'doughnut'
            data: {
                labels: ['Candidates', 'Active Jobs', 'Scheduled Interviews', 'Completed Interviews'],
                datasets: [{
                    label: 'Count',
                    data: [
                        statsData.total_candidates || 0,
                        statsData.active_jobs || 0,
                        breakdown.scheduled || 0,
                        breakdown.completed || 0
                    ],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.7)', // Blue
                        'rgba(139, 92, 246, 0.7)', // Purple
                        'rgba(16, 185, 129, 0.7)', // Green
                        'rgba(245, 158, 11, 0.7)'  // Orange
                    ],
                    borderColor: [
                        'rgba(59, 130, 246, 1)',
                        'rgba(139, 92, 246, 1)',
                        'rgba(16, 185, 129, 1)',
                        'rgba(245, 158, 11, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}

function renderJobs(jobs) {
    const container = document.getElementById('jobs-container');
    document.getElementById('jobs-count').textContent = `${jobs.length} total`;

    if (jobs.length === 0) {
        container.innerHTML = createEmptyState(
            'No job postings found.',
            'Click "Post New Job" to get started.'
        );
        return;
    }

    container.innerHTML = jobs.map(job => `
        <div class="card">
            <div class="card-header">
                <div>
                    <h3 class="card-title">${escapeHtml(job.title || 'No Title')}</h3>
                    <p class="card-subtitle">${escapeHtml(job.location || 'N/A')} | ${escapeHtml(job.employment_type || 'N/A')}</p>
                </div>
                <div class="card-actions">
                    <span class="badge badge-green">Active</span>
                    <button class="delete-job-btn" data-job-id="${escapeHtml(job.job_id)}" title="Delete Job Posting">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                            <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                        </svg>
                    </button>
                </div>
            </div>
            <p class="card-description">${escapeHtml(job.description || 'No description available.')}</p>
            <div class="skills-tags">
                ${(job.required_skills || []).map(skill =>
        `<span class="skill-tag">${escapeHtml(skill)}</span>`
    ).join('')}
            </div>
        </div>
    `).join('');
}

// Candidate Deletion Handler
async function handleDeleteCandidate(email) {
    if (!confirm(`Are you sure you want to delete candidate ${email}? This action cannot be undone.`)) {
        return;
    }

    showNotification(`Deleting candidate...`, 'success');
    loadingEl.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE}/candidates/${email}`, {
            method: 'DELETE'
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Failed to delete candidate.');
        }

        showNotification(result.message || 'Candidate deleted successfully!', 'success');
        await loadData();
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        loadingEl.classList.add('hidden');
    }
}


// Render Candidates Function
function renderCandidates(candidates) {
    const container = document.getElementById('candidates-container');
    document.getElementById('candidates-count').textContent = `${candidates.length} total`;

    if (candidates.length === 0) {
        container.innerHTML = createEmptyState(
            'No candidates found.',
            'Upload a resume to get started.'
        );
        return;
    }

    container.innerHTML = candidates.map((candidate, index) => {
        const github = candidate.github_analysis || {};
        const hasGitHub = github && github.total_repos > 0;
        const bestFitRepo = github.best_fit_repo || {};
        const enrichedProfile = candidate.enriched_profile || '';
        const publicPresence = candidate.public_presence || '';

        // Collapsible card ID
        const collapseId = `candidate-details-${index}`;

        return `
        <div class="card candidate-card-collapsible">
            <div class="card-header" style="cursor: pointer;" onclick="if (!event.target.closest('.delete-candidate-btn')) document.getElementById('${collapseId}').classList.toggle('hidden')">
                <div>
                    <h3 class="card-title">
                        ${escapeHtml(candidate.name || 'Unnamed Candidate')}
                        ${hasGitHub ? `<span style="font-size: 0.75rem; color: #8b5cf6;">⭐ ${github.total_repos} repos</span>` : ''}
                    </h3>
                    <p class="card-subtitle">
                        ${escapeHtml(candidate.email || 'N/A')} | 
                        Matched: ${escapeHtml((candidate.matched_jobs || []).join(', ') || 'N/A')}
                    </p>
                </div>
                <div class="card-actions">
                    <div class="score-display">
                        <p class="score-value ${candidate.score > 75 ? 'score-green' : 'score-red'}">${candidate.score || 0}%</p>
                        <p class="score-label">Match Score</p>
                    </div>
                    <button class="delete-candidate-btn" data-email="${escapeHtml(candidate.email)}" title="Delete Candidate">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                            <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                        </svg>
                    </button>
                </div>
            </div>
            
            <!-- Collapsible Details Section -->
            <div id="${collapseId}" class="hidden" style="padding: 1rem; background-color: #f8fafc; border-top: 1px solid #e2e8f0;">
                
                ${hasGitHub ? `
                <!-- GitHub Analytics Section -->
                <div style="margin-bottom: 1.5rem; padding: 1rem; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <h4 style="font-size: 0.875rem; font-weight: 600; color: #64748b; margin-bottom: 0.75rem; display: flex; align-items: center;">
                        <svg style="width: 16px; height: 16px; margin-right: 0.5rem;" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                        </svg>
                        GitHub Profile Analytics
                    </h4>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.75rem; margin-bottom: 1rem;">
                        <div style="padding: 0.75rem; background: #f1f5f9; border-radius: 6px;">
                            <p style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.25rem;">Total Repositories</p>
                            <p style="font-size: 1.25rem; font-weight: 600; color: #1e293b;">${github.total_repos || 0}</p>
                        </div>
                        <div style="padding: 0.75rem; background: #fef3c7; border-radius: 6px;">
                            <p style="font-size: 0.75rem; color: #92400e; margin-bottom: 0.25rem;">Total Stars</p>
                            <p style="font-size: 1.25rem; font-weight: 600; color: #78350f;">${github.total_stars || 0} ⭐</p>
                        </div>
                        <div style="padding: 0.75rem; background: #dbeafe; border-radius: 6px;">
                            <p style="font-size: 0.75rem; color: #1e40af; margin-bottom: 0.25rem;">Portfolio Quality</p>
                            <p style="font-size: 1.25rem; font-weight: 600; color: #1e3a8a; text-transform: capitalize;">${github.portfolio_quality || 'N/A'}</p>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <p style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 500;">Primary Languages:</p>
                        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                            ${(github.primary_languages || []).map(lang =>
            `<span style="background: #8b5cf6; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem;">${escapeHtml(lang)}</span>`
        ).join('')}
                        </div>
                    </div>
                    
                    ${bestFitRepo.url ? `
                    <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 6px; padding: 0.75rem;">
                        <p style="font-size: 0.75rem; color: #166534; font-weight: 600; margin-bottom: 0.5rem;">🏆 Best Fit Repository</p>
                        <p style="font-size: 0.875rem; font-weight: 500; color: #15803d; margin-bottom: 0.25rem;">${escapeHtml(bestFitRepo.name || 'N/A')}</p>
                        <p style="font-size: 0.75rem; color: #16a34a; margin-bottom: 0.5rem;">${escapeHtml(bestFitRepo.reason || '')}</p>
                        <a href="${escapeHtml(bestFitRepo.url)}" target="_blank" style="color: #2563eb; text-decoration: underline; font-size: 0.75rem; font-weight: 500;">
                            View Repository →
                        </a>
                    </div>
                    ` : ''}
                    
                    ${github.professional_summary ? `
                    <div style="margin-top: 0.75rem; padding: 0.75rem; background: #fef9c3; border-radius: 6px;">
                        <p style="font-size: 0.75rem; color: #713f12; line-height: 1.5;">${escapeHtml(github.professional_summary)}</p>
                    </div>
                    ` : ''}
                </div>
                ` : `
                <div style="margin-bottom: 1.5rem; padding: 1rem; background: #fef2f2; border-radius: 8px; border: 1px solid #fecaca;">
                    <p style="font-size: 0.875rem; color: #991b1b;">No GitHub profile found in resume</p>
                </div>
                `}
                
                ${enrichedProfile ? `
                <!-- Enriched Profile Summary -->
                <div style="margin-bottom: 1.5rem; padding: 1rem; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <h4 style="font-size: 0.875rem; font-weight: 600; color: #64748b; margin-bottom: 0.75rem;">📝 Enriched Profile Summary</h4>
                    <p style="font-size: 0.875rem; color: #475569; line-height: 1.6;">${escapeHtml(enrichedProfile)}</p>
                </div>
                ` : ''}
                
                ${publicPresence && !publicPresence.includes('No significant') ? `
                <!-- Public Presence -->
                <div style="padding: 1rem; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <h4 style="font-size: 0.875rem; font-weight: 600; color: #64748b; margin-bottom: 0.75rem;">🌐 Public Contributions</h4>
                    <p style="font-size: 0.875rem; color: #475569; line-height: 1.6;">${escapeHtml(publicPresence)}</p>
                </div>
                ` : ''}
                
                <!-- Skills Tags -->
                <div style="margin-top: 1rem;">
                    <h4 style="font-size: 0.875rem; font-weight: 600; color: #64748b; margin-bottom: 0.5rem;">Skills</h4>
                    <div class="skills-tags">
                        ${(candidate.skills || []).map(skill =>
            `<span class="skill-tag-purple">${escapeHtml(skill)}</span>`
        ).join('')}
                    </div>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

function renderInterviews() {
    const container = document.getElementById('interviews-container');

    // Filter interviews based on the toggle state
    const interviewsToRender = showCompletedInterviews
        ? allInterviews.filter(interview =>
            interview.status.toLowerCase().includes('completed')
        )
        : allInterviews.filter(interview =>
            !interview.status.toLowerCase().includes('completed')
        );

    document.getElementById('interviews-count').textContent = `${interviewsToRender.length} ${showCompletedInterviews ? 'completed' : 'active'}`;

    if (interviewsToRender.length === 0) {
        const message = showCompletedInterviews
            ? 'No completed interviews found.'
            : 'No active interviews found. Toggle "Show Completed" to see past interviews.';
        container.innerHTML = createEmptyState(message, '');
        return;
    }

    container.innerHTML = interviewsToRender.map(interview => {
        const isAiInterview = interview.status.includes('ai_interview');
        const isCompleted = interview.status.toLowerCase().includes('completed');
        let cardContent = '';

        if (isAiInterview) {
            let statusBadge = isCompleted
                ? '<span class="badge badge-gray">AI Completed</span>'
                : '<span class="badge badge-purple">AI Interview</span>';

            const footerText = `Status: ${interview.status.replace(/_/g, ' ')}`;
            let meetingBox = '';

            if (interview.status === 'pending_ai_interview') {
                meetingBox = `
                    <div class="meeting-box">
                        <div class="meeting-info">
                            <p class="meeting-title">AI Interview Room</p>
                            <p class="meeting-subtitle">Candidate has been invited.</p>
                        </div>
                        <a href="${escapeHtml(interview.meeting_link)}" target="_blank" class="join-btn" style="background-color: #7c3aed;">Go to Room</a>
                    </div>
                `;
            } else if (interview.status === 'completed_ai_interview') {
                meetingBox = `
                    <div class="alert alert-success">
                        <strong>Interview Complete!</strong> Final Score: <strong>${interview.interview_score ?? 'N/A'}</strong>
                    </div>
                `;
            }

            const candidateName = interview.candidate_id.split('@')[0];
            // ✅ Fix: Use real ID first, fallback only if missing
            const interviewId = interview.id || interview._id || interview.interview_id || `${interview.candidate_id}_${interview.job_id}`;

            cardContent = `
                <div class="card-header">
                    <div>
                        <h3 class="card-title">Candidate: ${escapeHtml(candidateName)}</h3>
                        <p class="card-subtitle">For Job: ${escapeHtml(interview.job_id)}</p>
                    </div>
                    <div class="card-actions">
                        ${statusBadge}
                        <button class="delete-interview-btn" data-interview-id="${escapeHtml(interviewId)}" title="Delete Interview">
                            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                                <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                                <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="card-footer">
                    <span>${escapeHtml(footerText)}</span>
                </div>
                ${meetingBox}
            `;
        } else {
            const candidateName = interview.candidate_id.split('@')[0];
            const scheduledTime = new Date(interview.scheduled_time).toLocaleString();
            // ✅ Fix: Use real ID first, fallback only if missing
            const interviewId = interview.id || interview._id || interview.interview_id || `${interview.candidate_id}_${interview.job_id}`;

            let statusBadge = isCompleted
                ? '<span class="badge badge-gray">Completed</span>'
                : '<span class="badge badge-blue">Scheduled</span>';

            cardContent = `
                <div class="card-header">
                    <div>
                        <h3 class="card-title">Candidate: ${escapeHtml(candidateName)}</h3>
                        <p class="card-subtitle">For Job: ${escapeHtml(interview.job_id)}</p>
                    </div>
                    <div class="card-actions">
                        ${statusBadge}
                        <button class="delete-interview-btn" data-interview-id="${escapeHtml(interviewId)}" title="Delete Interview">
                            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                                <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                                <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="card-footer">
                    <span>Scheduled for: ${escapeHtml(scheduledTime)}</span>
                </div>
                ${!isCompleted ? `
                <div class="meeting-box">
                    <div class="meeting-info">
                        <p class="meeting-title">Virtual Interview Room</p>
                        <p class="meeting-subtitle">Ready to join the call</p>
                    </div>
                    <a href="${escapeHtml(interview.meeting_link)}" target="_blank" class="join-btn">Join Now</a>
                </div>` : ''}
            `;
        }

        return `<div class="card">${cardContent}</div>`;
    }).join('');
}

// UI Helper Functions

function showNotification(message, type = 'success') {
    notificationEl.textContent = message;
    notificationEl.className = 'notification';
    notificationEl.classList.add(type);
    notificationEl.classList.remove('hidden');

    setTimeout(() => {
        notificationEl.classList.add('hidden');
    }, 5000);
}

function createEmptyState(title, subtitle) {
    return `
        <div class="empty-state">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width: 64px; height: 64px; color: #cbd5e1; margin: 0 auto 1rem;">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
            </svg>
            <p style="color: #64748b; margin-bottom: 0.5rem;">${escapeHtml(title)}</p>
            <p style="font-size: 0.875rem; color: #94a3b8;">${escapeHtml(subtitle)}</p>
        </div>
    `;
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}