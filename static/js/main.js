// Resume Matcher - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // File upload validation
    const resumeInput = document.getElementById('resume');
    const jobDescInput = document.getElementById('job_description');
    
    if (resumeInput) {
        resumeInput.addEventListener('change', function(e) {
            validateFileType(e.target, 'pdf', 'Resume must be a PDF file');
        });
    }
    
    if (jobDescInput && jobDescInput.tagName === 'TEXTAREA') {
        jobDescInput.addEventListener('input', function(e) {
            validateJobDescriptionText(e.target);
        });
    }

    // Progress animation for match scores
    animateProgressBars();
    
    // Keyword highlighting
    highlightKeywords();
    
    // Auto-hide alerts
    autoHideAlerts();
});

function validateFileType(input, expectedType, errorMessage) {
    const file = input.files[0];
    if (file) {
        const fileExtension = file.name.split('.').pop().toLowerCase();
        const maxSize = 16 * 1024 * 1024; // 16MB
        
        if (fileExtension !== expectedType) {
            showAlert(errorMessage, 'danger');
            input.value = '';
            return false;
        }
        
        if (file.size > maxSize) {
            showAlert('File size must be less than 16MB', 'danger');
            input.value = '';
            return false;
        }
        
        // Show file info
        const fileInfo = document.createElement('small');
        fileInfo.className = 'form-text text-success';
        fileInfo.innerHTML = `<i class="fas fa-check-circle me-1"></i>File selected: ${file.name} (${formatFileSize(file.size)})`;
        
        // Remove existing file info
        const existingInfo = input.parentNode.querySelector('.form-text.text-success');
        if (existingInfo) {
            existingInfo.remove();
        }
        
        input.parentNode.appendChild(fileInfo);
    }
    return true;
}

function validateJobDescriptionText(textarea) {
    const text = textarea.value.trim();
    const minLength = 50; // Minimum characters for a meaningful job description
    
    // Remove existing validation messages
    const existingInfo = textarea.parentNode.querySelector('.form-text.text-success, .form-text.text-warning');
    if (existingInfo) {
        existingInfo.remove();
    }
    
    if (text.length === 0) {
        return false;
    }
    
    if (text.length < minLength) {
        const warningInfo = document.createElement('small');
        warningInfo.className = 'form-text text-warning';
        warningInfo.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i>Job description seems too short. Please provide more details for better analysis.`;
        textarea.parentNode.appendChild(warningInfo);
        return false;
    }
    
    // Show success message
    const successInfo = document.createElement('small');
    successInfo.className = 'form-text text-success';
    successInfo.innerHTML = `<i class="fas fa-check-circle me-1"></i>Job description looks good! (${text.length} characters)`;
    textarea.parentNode.appendChild(successInfo);
    
    return true;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (alertDiv && alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1.5s ease-in-out';
            bar.style.width = width;
        }, 100);
    });
}

function highlightKeywords() {
    // Add click handlers to keyword badges for additional information
    const keywordBadges = document.querySelectorAll('.keyword-cloud .badge');
    
    keywordBadges.forEach(badge => {
        badge.addEventListener('click', function() {
            const keyword = this.textContent.trim().replace(/[✓!]/g, '');
            const isMatched = this.classList.contains('bg-success');
            const isMissing = this.classList.contains('bg-warning');
            
            let message = `Keyword: "${keyword}"`;
            if (isMatched) {
                message += ' - Found in both resume and job description ✓';
            } else if (isMissing) {
                message += ' - Missing from resume. Consider adding this skill!';
            } else {
                message += ' - Present in resume but not required for this job';
            }
            
            showTooltip(this, message);
        });
    });
}

function showTooltip(element, message) {
    // Create temporary tooltip
    const tooltip = new bootstrap.Tooltip(element, {
        title: message,
        trigger: 'manual',
        placement: 'top'
    });
    
    tooltip.show();
    
    setTimeout(() => {
        tooltip.hide();
        tooltip.dispose();
    }, 3000);
}

function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) return;
        
        setTimeout(() => {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

// Upload form enhancements
function enhanceUploadForm() {
    const uploadForm = document.getElementById('uploadForm');
    if (!uploadForm) return;
    
    uploadForm.addEventListener('submit', function(e) {
        const resumeFile = document.getElementById('resume').files[0];
        const jobDescText = document.getElementById('job_description').value.trim();
        
        if (!resumeFile || !jobDescText) {
            e.preventDefault();
            showAlert('Please select a resume file and provide job description text', 'warning');
            return false;
        }
        
        if (jobDescText.length < 50) {
            e.preventDefault();
            showAlert('Job description is too short. Please provide more details for accurate analysis.', 'warning');
            return false;
        }
        
        // Show processing indicator
        showProcessingIndicator();
    });
}

function showProcessingIndicator() {
    const submitBtn = document.getElementById('submitBtn');
    const progressContainer = document.getElementById('progressContainer');
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    }
    
    if (progressContainer) {
        progressContainer.style.display = 'block';
        
        // Animate progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) {
                clearInterval(interval);
                progress = 90; // Don't complete until actual completion
            }
            
            const progressBar = progressContainer.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = progress + '%';
            }
        }, 500);
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N for new analysis
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        const uploadLink = document.querySelector('a[href*="upload"]');
        if (uploadLink) {
            window.location.href = uploadLink.href;
        }
    }
    
    // Escape to close modals/alerts
    if (e.key === 'Escape') {
        const alerts = document.querySelectorAll('.alert .btn-close');
        alerts.forEach(closeBtn => closeBtn.click());
    }
});

// Results page enhancements
function enhanceResultsPage() {
    // Add click-to-copy functionality for keywords
    const keywords = document.querySelectorAll('.keyword-cloud .badge');
    
    keywords.forEach(keyword => {
        keyword.style.cursor = 'pointer';
        keyword.title = 'Click to copy';
        
        keyword.addEventListener('click', function() {
            const text = this.textContent.trim().replace(/[✓!]/g, '');
            copyToClipboard(text);
            
            // Visual feedback
            const originalContent = this.innerHTML;
            this.innerHTML = '<i class="fas fa-check"></i> Copied!';
            
            setTimeout(() => {
                this.innerHTML = originalContent;
            }, 1000);
        });
    });
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    }
}

// Initialize page-specific features
if (document.getElementById('uploadForm')) {
    enhanceUploadForm();
}

if (document.querySelector('.keyword-cloud')) {
    enhanceResultsPage();
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Performance monitoring
window.addEventListener('load', function() {
    // Log page load time for debugging
    const loadTime = performance.now();
    console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
});
