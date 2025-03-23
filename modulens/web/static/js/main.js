// ModuLens Web Interface JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Add loading indicator to form submission
    const promptForm = document.getElementById('promptForm');
    if (promptForm) {
        promptForm.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            submitBtn.disabled = true;
        });
    }

    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Copy response to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-response');
    if (copyButtons.length > 0) {
        copyButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                const responseId = this.getAttribute('data-response-id');
                const responseText = document.getElementById(responseId).textContent;
                
                navigator.clipboard.writeText(responseText).then(function() {
                    // Update button text temporarily
                    const originalText = button.innerHTML;
                    button.innerHTML = 'Copied!';
                    
                    setTimeout(function() {
                        button.innerHTML = originalText;
                    }, 2000);
                });
            });
        });
    }
}); 