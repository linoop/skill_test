// COBOL to Java Converter JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const convertForm = document.getElementById('convertForm');
    const progressOverlay = document.getElementById('progressOverlay');
    const convertBtn = document.getElementById('convertBtn');

    convertForm.addEventListener('submit', function(e) {
        // Check if a file is selected
        const fileInput = document.querySelector('input[type="file"]');
        if (!fileInput.files.length) {
            alert('Please select a COBOL file first.');
            e.preventDefault();
            return;
        }
    
        progressOverlay.style.display = 'block';
        convertBtn.disabled = true;
        convertBtn.textContent = 'Converting...';
    });
    
    window.addEventListener('load', function() {
        progressOverlay.style.display = 'none';
        convertBtn.disabled = false;
        convertBtn.textContent = 'Convert';
    });
});
