function copyResults() {
    // Target the main content area string, removing excess newlines
    const resultContainer = document.getElementById('ai-results-container');
    if (!resultContainer) return;

    // Retrieve raw inner text and clean up arbitrary spacing
    let textToCopy = resultContainer.innerText;
    textToCopy = textToCopy.replace(/\n{3,}/g, '\n\n').trim();

    navigator.clipboard.writeText(textToCopy).then(() => {
        const btn = document.getElementById('copyBtn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.style.backgroundColor = '#057642'; // LinkedIn Success Green
        btn.style.color = '#fff';

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.backgroundColor = '';
            btn.style.color = '';
        }, 2000);
    }).catch((err) => {
        console.error('[LinkedInAnalyzer] Failed to copy text:', err);
        alert('Failed to copy results to clipboard');
    });
}

// Ensure first tab triggers active state bootstrap logic
document.addEventListener("DOMContentLoaded", function () {
    const triggerTabList = [].slice.call(document.querySelectorAll('#msgTabs button'));
    if (triggerTabList.length > 0) {
        const firstTab = new bootstrap.Tab(triggerTabList[0]);
        firstTab.show();
    }
});

function copySingleMessage(btn) {
    // Prevent multiple clicks breaking the timeout rollback
    if (btn.dataset.copying === 'true') return;

    // Find the closest parent relative container and grab the message box
    const container = btn.closest('.position-relative');
    if (!container) return;

    const messageBox = container.querySelector('.message-box');
    if (!messageBox) return;

    const textToCopy = messageBox.innerText.trim();

    btn.dataset.copying = 'true';
    navigator.clipboard.writeText(textToCopy).then(() => {
        // Temporarily change button to Green Check
        btn.innerHTML = '<i class="fas fa-check"></i> Copied';
        btn.classList.remove('btn-outline-secondary');
        btn.classList.add('btn-success');
        btn.style.color = '#fff';

        setTimeout(() => {
            btn.innerHTML = '<i class="fas fa-copy"></i>';
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-secondary');
            btn.style.color = '';

            // Allow clicking again
            delete btn.dataset.copying;
        }, 2000);
    }).catch((err) => {
        console.error('[LinkedInAnalyzer] Failed to copy single message:', err);
        alert('Failed to copy this message to clipboard');
        delete btn.dataset.copying;
    });
}