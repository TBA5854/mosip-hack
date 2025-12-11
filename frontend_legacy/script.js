// Global state
let uploadedFile = null;
let extractedData = {};
let fileId = null;

// DOM elements
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const extractBtn = document.getElementById('extract-btn');
const editBtn = document.getElementById('edit-btn');
const verifyBtn = document.getElementById('verify-btn');
const saveEditsBtn = document.getElementById('save-edits-btn');
const cancelEditBtn = document.getElementById('cancel-edit-btn');
const generateVcBtn = document.getElementById('generate-vc-btn');
const restartBtn = document.getElementById('restart-btn');
const loadingOverlay = document.getElementById('loading-overlay');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // Upload area
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // File input
    fileInput.addEventListener('change', handleFileSelect);
    
    // Buttons
    extractBtn.addEventListener('click', extractData);
    editBtn.addEventListener('click', showEditForm);
    verifyBtn.addEventListener('click', verifyData);
    saveEditsBtn.addEventListener('click', saveEditsAndVerify);
    cancelEditBtn.addEventListener('click', hideEditForm);
    generateVcBtn.addEventListener('click', generateVC);
    restartBtn.addEventListener('click', restart);
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // Validate file
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/tiff'];
    if (!validTypes.includes(file.type)) {
        alert('Please upload a PDF or image file (PNG, JPG, TIFF)');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
    }
    
    uploadedFile = file;
    uploadArea.querySelector('.upload-prompt').innerHTML = `
        <p>✓ ${file.name}</p>
        <p class="file-types">Click to change file</p>
    `;
    extractBtn.disabled = false;
}

async function extractData() {
    if (!uploadedFile) return;
    
    showLoading();
    
    const formData = new FormData();
    formData.append('file', uploadedFile);
    formData.append('include_quality_score', 'true');
    
    try {
        const response = await fetch('/api/extract', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Extraction failed');
        
        const data = await response.json();
        extractedData = data.extracted_fields;
        fileId = data.file_id;
        
        // Display results
        displayQualityScores(data.quality_scores);
        displayExtractedData(data.extracted_fields);
        
        // Show extraction section
        document.getElementById('extraction-section').classList.remove('hidden');
        document.getElementById('upload-section').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('Error during extraction: ' + error.message);
    } finally {
        hideLoading();
    }
}

function displayQualityScores(scores) {
    if (!scores || scores.length === 0) return;
    
    const container = document.getElementById('quality-scores');
    const score = scores[0]; // Display first page score
    
    container.innerHTML = `
        <h3>Image Quality Analysis</h3>
        <div class="quality-item">
            <span class="quality-label">Overall Quality</span>
            <div class="quality-value">
                <span class="status-badge status-${score.overall_quality.toLowerCase()}">
                    ${score.overall_quality}
                </span>
            </div>
        </div>
        <div class="quality-item">
            <span class="quality-label">Blur Detection</span>
            <div class="quality-value">
                <span>${score.blur_score.toFixed(2)}</span>
                <span class="status-badge status-${score.blur_status === 'Good' ? 'good' : 'poor'}">
                    ${score.blur_status}
                </span>
            </div>
        </div>
        <div class="quality-item">
            <span class="quality-label">Brightness</span>
            <div class="quality-value">
                <span>${score.brightness_score.toFixed(2)}</span>
                <span class="status-badge status-${score.brightness_status === 'Good' ? 'good' : 'fair'}">
                    ${score.brightness_status}
                </span>
            </div>
        </div>
        ${score.recommendations.length > 0 ? `
            <div class="quality-item">
                <span class="quality-label">Recommendations</span>
                <div class="quality-value">
                    <ul>
                        ${score.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        ` : ''}
    `;
}

function displayExtractedData(fields) {
    const container = document.getElementById('extracted-data');
    container.innerHTML = '';
    
    const fieldLabels = {
        name: 'Name',
        dob: 'Date of Birth',
        age: 'Age',
        gender: 'Gender',
        email: 'Email',
        phone: 'Phone',
        address: 'Address'
    };
    
    Object.entries(fields).forEach(([key, value]) => {
        const fieldDiv = document.createElement('div');
        fieldDiv.className = 'field-item';
        fieldDiv.innerHTML = `
            <div class="field-label">${fieldLabels[key] || key}</div>
            <div class="field-value">${value || 'Not found'}</div>
        `;
        container.appendChild(fieldDiv);
    });
}

function showEditForm() {
    // Populate form with extracted data
    document.getElementById('edit-name').value = extractedData.name || '';
    document.getElementById('edit-dob').value = extractedData.dob || '';
    document.getElementById('edit-age').value = extractedData.age || '';
    document.getElementById('edit-gender').value = extractedData.gender || '';
    document.getElementById('edit-email').value = extractedData.email || '';
    document.getElementById('edit-phone').value = extractedData.phone || '';
    document.getElementById('edit-address').value = extractedData.address || '';
    
    document.getElementById('edit-section').classList.remove('hidden');
    document.getElementById('extraction-section').classList.add('hidden');
}

function hideEditForm() {
    document.getElementById('edit-section').classList.add('hidden');
    document.getElementById('extraction-section').classList.remove('hidden');
}

function saveEditsAndVerify() {
    // Update extracted data with edits
    extractedData = {
        name: document.getElementById('edit-name').value,
        dob: document.getElementById('edit-dob').value,
        age: parseInt(document.getElementById('edit-age').value) || undefined,
        gender: document.getElementById('edit-gender').value,
        email: document.getElementById('edit-email').value,
        phone: document.getElementById('edit-phone').value,
        address: document.getElementById('edit-address').value
    };
    
    // Update display
    displayExtractedData(extractedData);
    
    hideEditForm();
    verifyData();
}

async function verifyData() {
    if (!uploadedFile || !extractedData) return;
    
    showLoading();
    
    const formData = new FormData();
    formData.append('file', uploadedFile);
    formData.append('submitted_data', JSON.stringify(extractedData));
    
    try {
        const response = await fetch('/api/verify', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Verification failed');
        
        const data = await response.json();
        
        // Display results
        displayVerificationResults(data);
        
        // Show verification section
        document.getElementById('verification-section').classList.remove('hidden');
        document.getElementById('verification-section').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('Error during verification: ' + error.message);
    } finally {
        hideLoading();
    }
}

function displayVerificationResults(data) {
    // Overall score
    const overallContainer = document.getElementById('overall-score');
    const scoreClass = data.overall_score >= 0.85 ? 'score-high' :
                       data.overall_score >= 0.70 ? 'score-medium' : 'score-low';
    
    overallContainer.innerHTML = `
        <div class="score-circle ${scoreClass}">
            ${(data.overall_score * 100).toFixed(0)}%
        </div>
        <h3>${data.overall_match ? '✓ Verification Passed' : '✗ Verification Failed'}</h3>
        <p>Overall match confidence: ${(data.overall_score * 100).toFixed(1)}%</p>
    `;
    
    // Field-by-field results
    const resultsContainer = document.getElementById('verification-results');
    resultsContainer.innerHTML = '';
    
    Object.entries(data.verification_result).forEach(([field, result]) => {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'result-item';
        resultDiv.innerHTML = `
            <div class="result-field">${field.toUpperCase()}</div>
            <div class="result-value">
                <strong>OCR:</strong> ${result.ocr_value || 'N/A'}
            </div>
            <div class="result-value">
                <strong>Form:</strong> ${result.form_value || 'N/A'}
            </div>
            <div class="result-match ${result.match ? 'match-yes' : 'match-no'}">
                ${result.match ? '✓ Match' : '✗ Mismatch'}
                <br>
                <small>${(result.confidence * 100).toFixed(0)}%</small>
            </div>
        `;
        resultsContainer.appendChild(resultDiv);
    });
}

async function generateVC() {
    if (!fileId) return;
    
    showLoading();
    
    const formData = new FormData();
    formData.append('file_id', fileId);
    formData.append('verified_data', JSON.stringify(extractedData));
    
    try {
        const response = await fetch('/api/generate-vc', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('VC generation failed');
        
        const data = await response.json();
        
        // Display VC
        displayVC(data);
        
        // Show VC section
        document.getElementById('vc-section').classList.remove('hidden');
        document.getElementById('vc-section').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('Error generating VC: ' + error.message);
    } finally {
        hideLoading();
    }
}

function displayVC(data) {
    // Display VC JSON
    const vcContainer = document.getElementById('vc-display');
    vcContainer.innerHTML = `<pre>${JSON.stringify(data.vc, null, 2)}</pre>`;
    
    // Set download links
    document.getElementById('download-vc-btn').href = data.vc_download_url;
    document.getElementById('download-qr-btn').href = data.qr_download_url;
    
    // Display QR code
    const qrContainer = document.getElementById('qr-display');
    qrContainer.innerHTML = `<img src="${data.qr_download_url}" alt="VC QR Code">`;
}

function restart() {
    uploadedFile = null;
    extractedData = {};
    fileId = null;
    
    // Reset UI
    document.querySelectorAll('.card').forEach(card => {
        if (card.id !== 'upload-section') {
            card.classList.add('hidden');
        }
    });
    
    uploadArea.querySelector('.upload-prompt').innerHTML = `
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
        <p>Click to upload or drag and drop</p>
        <p class="file-types">PDF, PNG, JPG (Max 10MB)</p>
    `;
    
    extractBtn.disabled = true;
    fileInput.value = '';
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

