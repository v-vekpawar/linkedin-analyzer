function clearForm() {
    document.getElementById('analyzeForm').reset();
    document.getElementById('user_linkedin_url_container').style.display = 'none';
}
// Toggle visibility of "Your LinkedIn URL" input based on analysis mode
document.getElementById('analysis_mode').addEventListener('change', function() {
    const yourUrlContainer = document.getElementById('user_linkedin_url_container');
    const yourUrlInput = document.getElementById('user_url');

    if (this.value === 'compatibility_score') {
        yourUrlContainer.style.display = 'block';
        if (!useSampleCheckbox.checked) {
            yourUrlInput.setAttribute('required', 'required');
        }
        
        // FIX: If sample is checked, auto-fill user_url too
        if (useSampleCheckbox.checked) {
            yourUrlInput.value = 'https://www.linkedin.com/in/sample-user';
            yourUrlInput.removeAttribute('required');
        }
    } else {
        yourUrlContainer.style.display = 'none';
        yourUrlInput.removeAttribute('required');
        yourUrlInput.value = '';
    }
});

// Autofill and toggle required for profile_url when using sample data
document.getElementById('use_sample').addEventListener('change', function() {
    const urlInput = document.getElementById('profile_url');
    const yourUrlInput = document.getElementById('user_url');
    const analysisMode = document.getElementById('analysis_mode').value;
    
    if (this.checked) {
        urlInput.value = 'https://www.linkedin.com/in/sampleuser';
        urlInput.removeAttribute('required');
        
        // FIX: Also fill user_url if compatibility mode is selected
        if (analysisMode === 'compatibility_score') {
            yourUrlInput.value = 'https://www.linkedin.com/in/sample-user';
            yourUrlInput.removeAttribute('required');
        }
    } else {
        urlInput.value = '';
        urlInput.setAttribute('required', 'required');
        yourUrlInput.value = '';
        
        if (analysisMode === 'compatibility_score') {
            yourUrlInput.setAttribute('required', 'required');
        }
    }
});

document.getElementById('analyzeForm').addEventListener('submit', function(e) {
    const useSample = document.getElementById('use_sample').checked;
    const urlInput = document.getElementById('profile_url');
    const analysisMode = document.getElementById('analysis_mode').value;
    const yourUrlInput = document.getElementById('user_url');
    
    if (useSample) {
        urlInput.value = 'https://www.linkedin.com/in/sampleuser';
        urlInput.removeAttribute('required');
        
        // FIX: Also set user_url if compatibility mode
        if (analysisMode === 'compatibility_score') {
            yourUrlInput.value = 'https://www.linkedin.com/in/sample-user';
            yourUrlInput.removeAttribute('required');
        }
    } else {
        urlInput.setAttribute('required', 'required');
        if (!urlInput.value) {
            urlInput.focus();
            e.preventDefault();
            return false;
        }
    }
    
    // Validate "Your LinkedIn URL" if compatibility_score is selected
    if (analysisMode === 'compatibility_score' && !useSample) {
        if (!yourUrlInput.value) {
            yourUrlInput.focus();
            e.preventDefault();
            alert('Please enter your LinkedIn URL for compatibility score analysis');
            return false;
        }
    }
    
    const submitBtn = document.getElementById('submitBtn');
    const loading = document.getElementById('loading');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    loading.style.display = 'block';
    loading.scrollIntoView({ behavior: 'smooth' });
});

setTimeout(function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000);