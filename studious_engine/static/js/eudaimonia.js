// EudaimoniaGo Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    try {
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

        // Initialize performance optimizations
        optimizeScrollingEvents();
        
        // Initialize lazy loading
        initLazyLoading();
    } catch (error) {
        reportError(error, 'initialization');
    }
});

// Initialize Bootstrap tooltips
function initTooltips() {
    try {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    } catch (error) {
        console.error('Error initializing tooltips:', error);
    }
}

// Campus Map Initialization
function initCampusMap() {
    console.log('Initializing campus map');
    
    try {
        // Mock map initialization - would be replaced with actual map API implementation
        const mapElement = document.getElementById('campus-map');
        
        if (!mapElement) {
            throw new Error('Map element not found');
        }
        
        // Mock map display with placeholder
        mapElement.innerHTML = '<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;background-color:#e9ecef;"><p>Campus Map Placeholder<br>Real map would be initialized here with location API</p></div>';
        
        // Setup locate me button functionality
        const locateBtn = document.getElementById('locate-me-btn');
        if (locateBtn) {
            locateBtn.addEventListener('click', function() {
                getUserLocation();
            });
        }
    } catch (error) {
        console.error('Error initializing campus map:', error);
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

// Add performance optimization for scrolling events
function optimizeScrollingEvents() {
    let ticking = false;
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                // Handle scroll events here
                
                ticking = false;
            });
            
            ticking = true;
        }
    });
}

// Debounce utility function to limit function calls
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Implement error reporting
function reportError(error, context) {
    console.error(`Error in ${context || 'unknown context'}:`, error);
    
    // In production, we could send this to a server
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        // Mock error reporting service
        // In a real app, this would send to a service like Sentry
        const errorData = {
            message: error.message,
            stack: error.stack,
            context: context,
            url: window.location.href,
            timestamp: new Date().toISOString()
        };
        
        // Log instead of actually sending in this example
        console.log('Would report to error service:', errorData);
        
        // Actual implementation would be:
        // fetch('/api/error-reporting', {
        //    method: 'POST',
        //    headers: { 'Content-Type': 'application/json' },
        //    body: JSON.stringify(errorData)
        // });
    }
}

// Add lazy loading for images
function initLazyLoading() {
    if ('loading' in HTMLImageElement.prototype) {
        // Browser supports native lazy loading
        const images = document.querySelectorAll('img[data-src]');
        images.forEach(img => {
            img.src = img.dataset.src;
            img.setAttribute('loading', 'lazy');
            img.removeAttribute('data-src');
        });
    } else {
        // Fallback for browsers that don't support native lazy loading
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const lazyImage = entry.target;
                        lazyImage.src = lazyImage.dataset.src;
                        lazyImage.removeAttribute('data-src');
                        imageObserver.unobserve(lazyImage);
                    }
                });
            });
            
            lazyImages.forEach(image => {
                imageObserver.observe(image);
            });
        } else {
            // Fallback for older browsers without IntersectionObserver
            let active = false;
            
            const lazyLoad = debounce(() => {
                if (active === false) {
                    active = true;
                    
                    setTimeout(() => {
                        lazyImages.forEach(lazyImage => {
                            if ((lazyImage.getBoundingClientRect().top <= window.innerHeight 
                                && lazyImage.getBoundingClientRect().bottom >= 0) 
                                && getComputedStyle(lazyImage).display !== 'none') {
                                
                                lazyImage.src = lazyImage.dataset.src;
                                lazyImage.removeAttribute('data-src');
                                
                                lazyImages = lazyImages.filter(image => image !== lazyImage);
                                
                                if (lazyImages.length === 0) {
                                    document.removeEventListener('scroll', lazyLoad);
                                    window.removeEventListener('resize', lazyLoad);
                                    window.removeEventListener('orientationchange', lazyLoad);
                                }
                            }
                        });
                        
                        active = false;
                    }, 200);
                }
            }, 100);
            
            document.addEventListener('scroll', lazyLoad);
            window.addEventListener('resize', lazyLoad);
            window.addEventListener('orientationchange', lazyLoad);
            lazyLoad();
        }
    }
}