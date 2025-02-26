// EudaimoniaGo Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('EudaimoniaGo initialized');
    
    // Initialize all tooltips
    initTooltips();
    
    // Initialize map if element exists
    if (document.getElementById('campus-map')) {
        initCampusMap();
    }
    
    // Initialize filter functionality if on zones page
    if (document.getElementById('zone-type-filter')) {
        initZoneFilters();
    }
    
    // Initialize filter functionality if on innovations page
    if (document.getElementById('innovation-stage-filter')) {
        initInnovationFilters();
    }
    
    // Add pulse animation to new elements
    highlightNewElements();
});

// Initialize Bootstrap tooltips
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Campus Map Initialization
function initCampusMap() {
    console.log('Initializing campus map');
    
    // Mock map initialization - would be replaced with actual map API implementation
    const mapElement = document.getElementById('campus-map');
    
    // Mock map display with placeholder
    mapElement.innerHTML = '<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;background-color:#e9ecef;"><p>Campus Map Placeholder<br>Real map would be initialized here with location API</p></div>';
    
    // Setup locate me button functionality
    const locateBtn = document.getElementById('locate-me-btn');
    if (locateBtn) {
        locateBtn.addEventListener('click', function() {
            getUserLocation();
        });
    }
}

// Geolocation function
function getUserLocation() {
    console.log('Getting user location');
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                // Success callback
                console.log("Location obtained: ", position.coords.latitude, position.coords.longitude);
                
                // Show success message
                showNotification('Location found! You are now on the map.', 'success');
                
                // Here we would center the map on user location and highlight nearby zones
                // This is just a placeholder for the real implementation
                updateNearbyZones(position);
            },
            function(error) {
                // Error callback
                console.error("Error getting location: ", error);
                showNotification('Could not get your location. Please check permissions.', 'danger');
            }
        );
    } else {
        console.error("Geolocation not supported by this browser");
        showNotification('Geolocation is not supported by your browser.', 'warning');
    }
}

// Update nearby zones based on user location
function updateNearbyZones(position) {
    // This is a mock function that would normally fetch zones near the user
    // For demonstration, we'll just show a static list
    
    const nearbyZonesElement = document.getElementById('nearby-zones');
    if (nearbyZonesElement) {
        // In a real application, this would be dynamically populated based on proximity
        nearbyZonesElement.innerHTML = `
            <div class="list-group">
                <a href="#" class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1">Library (Zone 12)</h5>
                        <small>50m away</small>
                    </div>
                    <p class="mb-1">Academic zone with 3 active experiences</p>
                </a>
                <a href="#" class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1">Student Center (Zone 5)</h5>
                        <small>120m away</small>
                    </div>
                    <p class="mb-1">Social zone with 2 active experiences</p>
                </a>
            </div>
        `;
    }
}

// Zone filter functionality
function initZoneFilters() {
    const filterSelect = document.getElementById('zone-type-filter');
    
    filterSelect.addEventListener('change', function() {
        const selectedType = this.value;
        const zoneCards = document.querySelectorAll('.zone-card');
        
        zoneCards.forEach(function(card) {
            if (selectedType === 'all' || card.dataset.zoneType === selectedType) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

// Innovation filter functionality
function initInnovationFilters() {
    const filterSelect = document.getElementById('innovation-stage-filter');
    
    filterSelect.addEventListener('change', function() {
        const selectedStage = this.value;
        const innovationCards = document.querySelectorAll('.innovation-card');
        
        innovationCards.forEach(function(card) {
            if (selectedStage === 'all' || card.dataset.stage === selectedStage) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

// Notification display
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Position it
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    // Auto remove after 5 seconds
    setTimeout(function() {
        notification.classList.remove('show');
        setTimeout(function() {
            notification.remove();
        }, 500);
    }, 5000);
}

// Animation for new elements
function highlightNewElements() {
    const newElements = document.querySelectorAll('.new-element');
    
    newElements.forEach(function(element) {
        element.classList.add('pulse-animation');
        
        // Remove animation after it plays once
        element.addEventListener('animationend', function() {
            element.classList.remove('pulse-animation');
        });
    });
}

// Progress tracking animation
function animateProgress() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(function(bar) {
        const targetWidth = bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        
        setTimeout(function() {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = targetWidth;
        }, 100);
    });
}

// Level up animation
function levelUpAnimation(element) {
    element.classList.add('level-up-animation');
    
    // Play sound effect
    // const levelUpSound = new Audio('/static/sounds/level-up.mp3');
    // levelUpSound.play();
    
    setTimeout(function() {
        element.classList.remove('level-up-animation');
    }, 3000);
}