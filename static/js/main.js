let selectedFile = null;
let selectedAmsSlot = null;
let statusInterval = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    startStatusPolling();
});

function initializeEventListeners() {
    // File selection
    document.querySelectorAll('.file-card').forEach(card => {
        card.addEventListener('click', function() {
            selectFile(this);
        });
    });

    // AMS slot selection
    document.querySelectorAll('.ams-slot').forEach(slot => {
        slot.addEventListener('click', function() {
            selectAmsSlot(this);
        });
    });

    // Light toggle
    document.getElementById('light-toggle').addEventListener('click', toggleLight);

    // Print button
    document.getElementById('print-btn').addEventListener('click', startPrint);

    // Cancel selection button
    document.getElementById('cancel-selection-btn').addEventListener('click', cancelSelection);

    // Cancel print button
    document.getElementById('cancel-print-btn').addEventListener('click', cancelPrint);
}

function selectFile(card) {
    // Remove previous selection
    document.querySelectorAll('.file-card').forEach(c => c.classList.remove('selected'));
    
    // Select new file
    card.classList.add('selected');
    selectedFile = card.dataset.filename;
    
    // Show AMS selection
    document.getElementById('ams-section').style.display = 'block';
    
    // Scroll to AMS section
    document.getElementById('ams-section').scrollIntoView({ behavior: 'smooth' });
}

function selectAmsSlot(slot) {
    // Remove previous selection
    document.querySelectorAll('.ams-slot').forEach(s => s.classList.remove('selected'));
    
    // Select new slot
    slot.classList.add('selected');
    selectedAmsSlot = slot.dataset.slot;
    
    // Show action buttons
    document.getElementById('actions-section').style.display = 'block';
    
    // Scroll to actions
    document.getElementById('actions-section').scrollIntoView({ behavior: 'smooth' });
}

function cancelSelection() {
    selectedFile = null;
    selectedAmsSlot = null;
    
    document.querySelectorAll('.file-card').forEach(c => c.classList.remove('selected'));
    document.querySelectorAll('.ams-slot').forEach(s => s.classList.remove('selected'));
    
    document.getElementById('ams-section').style.display = 'none';
    document.getElementById('actions-section').style.display = 'none';
}

async function startPrint() {
    if (!selectedFile || !selectedAmsSlot) {
        alert('Please select a file and AMS slot');
        return;
    }

    try {
        const response = await fetch('/api/print', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: selectedFile,
                ams_slot: selectedAmsSlot
            })
        });

        const data = await response.json();

        if (data.success) {
            // Show active print section
            document.getElementById('current-file').textContent = selectedFile;
            document.getElementById('current-slot').textContent = `Slot ${selectedAmsSlot}`;
            document.getElementById('active-print-section').style.display = 'block';
            
            // Hide selection sections
            document.getElementById('ams-section').style.display = 'none';
            document.getElementById('actions-section').style.display = 'none';
            
            cancelSelection();
            
            showNotification('Print started successfully!', 'success');
        } else {
            showNotification('Error: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error starting print:', error);
        showNotification('Failed to start print', 'error');
    }
}

async function cancelPrint() {
    if (!confirm('Are you sure you want to cancel the current print?')) {
        return;
    }

    try {
        const response = await fetch('/api/cancel', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('active-print-section').style.display = 'none';
            showNotification('Print cancelled', 'success');
        } else {
            showNotification('Error: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error cancelling print:', error);
        showNotification('Failed to cancel print', 'error');
    }
}

async function toggleLight() {
    const currentState = document.getElementById('light-toggle').dataset.state || 'off';
    const newState = currentState === 'on' ? 'off' : 'on';

    try {
        const response = await fetch(`/api/light/${newState}`);
        const data = await response.json();

        if (data.success) {
            document.getElementById('light-toggle').dataset.state = newState;
            document.getElementById('light-toggle').textContent = 
                newState === 'on' ? '💡 Light On' : '💡 Light Off';
        }
    } catch (error) {
        console.error('Error toggling light:', error);
    }
}

function startStatusPolling() {
    updateStatus();
    statusInterval = setInterval(updateStatus, 3000); // Update every 3 seconds
}

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.success) {
            document.getElementById('printer-status').textContent = 'Connected';
            
            // Update status fields based on API response
            if (data.status) {
                document.getElementById('state').textContent = 
                    data.status.print_state || 'Unknown';
                document.getElementById('temperature').textContent = 
                    data.status.nozzle_temp ? `${data.status.nozzle_temp}°C` : '-';
            }
        } else {
            document.getElementById('printer-status').textContent = 'Error';
        }
    } catch (error) {
        console.error('Error fetching status:', error);
        document.getElementById('printer-status').textContent = 'Disconnected';
    }
}

function showNotification(message, type) {
    // Simple notification - you can enhance this with a library
    alert(message);
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (statusInterval) {
        clearInterval(statusInterval);
    }
});