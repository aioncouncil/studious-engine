# Zone Geographic Patterns Debugging

This document outlines common issues and solutions related to the Zone Geographic Patterns, particularly focusing on map functionality within the Atlantis Go platform.

## Issue: Map fails to load or initialize properly

### Symptoms
- Blank map area with no tiles displayed
- JavaScript console errors: "Leaflet not defined" or "L is not defined"
- Spinner continues indefinitely without loading map content
- User location pointer doesn't appear

### Affected Components
- `MapView` in `studious_engine/core/views/core.py`
- `map.html` template in `studious_engine/templates/core/map.html`
- Leaflet.js library integration

### Root Cause
The most common cause is that the Leaflet.js library fails to load properly, or the map initialization occurs before the library is fully loaded. Another potential cause is that the user's location cannot be determined, preventing the map from centering properly.

### Solution
Implement a robust map initialization with fallback mechanisms:

```javascript
function initMap() {
  // Check if Leaflet is available
  if (typeof L === 'undefined') {
    console.error('Leaflet library not loaded');
    document.getElementById('map-error').textContent = 'Map failed to load. Please refresh the page.';
    return;
  }
  
  // Create map with fallback coordinates if user location not available
  const defaultLat = 37.7749; // Fallback latitude
  const defaultLng = -122.4194; // Fallback longitude
  
  const mapOptions = {
    center: [
      parseFloat(document.getElementById('user-lat').value) || defaultLat,
      parseFloat(document.getElementById('user-lng').value) || defaultLng
    ],
    zoom: 15,
    zoomControl: true
  };
  
  // Initialize the map
  const map = L.map('map-container', mapOptions);
  
  // Add tile layer with error handling
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map);
  
  return map;
}
```

### Prevention
- Add proper error handling to all map-related functionality
- Include loading indicators and clear error messages
- Implement a health check mechanism for the map
- Test map functionality on various devices and network conditions

## Issue: User's location not updating on the map

### Symptoms
- User's position marker stays fixed in one location despite movement
- GPS icon shows active but location doesn't update
- Zones don't appear or disappear as user moves

### Affected Components
- `MapView.get_context_data` in `studious_engine/core/views/core.py`
- Browser geolocation API integration
- `loadUserLocation` function in map JavaScript

### Root Cause
The issue may stem from browser permissions being denied, geolocation API failures, or the client-side code not properly updating the user marker position when new coordinates are received.

### Solution
Implement a robust geolocation tracking system:

```javascript
function trackUserLocation(map) {
  let userMarker = null;
  
  // Function to update marker position
  function updatePosition(position) {
    const { latitude, longitude } = position.coords;
    const latlng = [latitude, longitude];
    
    // Create or update user marker
    if (!userMarker) {
      userMarker = L.marker(latlng).addTo(map);
      map.setView(latlng);
    } else {
      userMarker.setLatLng(latlng);
    }
    
    // Update backend with new location
    fetch('/api/update-location/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: JSON.stringify({ latitude, longitude })
    });
  }
  
  // Start watching position with high accuracy
  navigator.geolocation.watchPosition(
    updatePosition,
    error => console.error('Geolocation error:', error),
    { enableHighAccuracy: true }
  );
}
```

### Prevention
- Implement clear permission requests with explanations
- Add fallback mechanisms for when location services are unavailable
- Include visual feedback about location tracking status
- Test location functionality on various devices and browsers

## Issue: Zone boundaries not displaying or loading incorrectly on map

### Symptoms
- Zone polygons are missing on the map
- Zone boundaries appear in wrong locations
- Console errors related to GeoJSON parsing
- Zones flash or flicker when navigating the map

### Affected Components
- `map_elements_api` in core API views
- Zone GeoJSON generation
- Leaflet polygon rendering
- Client-side zone data handling

### Root Cause
Issues typically stem from invalid GeoJSON data, coordinate transformation problems, or errors in how zone data is fetched and processed on the client side.

### Solution
Implement proper zone loading with error handling:

```javascript
function loadZoneElements(map) {
  // Clear existing zone layers
  if (window.zoneLayers) {
    window.zoneLayers.forEach(layer => map.removeLayer(layer));
  }
  window.zoneLayers = [];
  
  // Get map center coordinates
  const center = map.getCenter();
  
  // Fetch zones from the API
  fetch(`/api/map-elements/?lat=${center.lat}&lng=${center.lng}&radius=5000`)
    .then(response => response.json())
    .then(data => {
      if (!data.zones || data.zones.length === 0) {
        console.log('No zones found in this area');
        return;
      }
      
      // Add each zone to the map
      data.zones.forEach(zone => {
        try {
          if (!zone.geometry) return;
          
          const zoneLayer = L.geoJSON(zone.geometry, {
            style: {
              color: '#3388ff',
              weight: 2,
              opacity: 0.7,
              fillOpacity: 0.2
            }
          }).addTo(map);
          
          zoneLayer.bindPopup(`<h3>${zone.name}</h3><p>${zone.description}</p>`);
          window.zoneLayers.push(zoneLayer);
        } catch (error) {
          console.error('Error adding zone:', error);
        }
      });
    })
    .catch(error => {
      console.error('Error loading zones:', error);
    });
}
```

### Prevention
- Validate GeoJSON data before sending it to the client
- Implement proper error handling at all levels
- Add logging for geometric operations
- Test with different zone geometries and edge cases

## Issue: Map performance degradation with large number of zones

### Symptoms
- Map becomes slow or unresponsive when many zones are loaded
- Browser memory usage increases significantly
- Zooming and panning become laggy
- Mobile devices experience crashes or freezes

### Affected Components
- Client-side map rendering
- Zone data loading and processing
- Leaflet polygon rendering performance

### Root Cause
Loading and rendering too many zone polygons simultaneously, especially complex polygons with many vertices, can overwhelm browser rendering capabilities and memory.

### Solution
Implement zoom-level based detail management:

```javascript
function loadOptimizedZones(map) {
  const zoom = map.getZoom();
  const bounds = map.getBounds();
  const ne = bounds.getNorthEast();
  const sw = bounds.getSouthWest();
  
  // Choose detail level based on zoom
  const detail = zoom >= 15 ? 'high' : zoom >= 12 ? 'medium' : 'low';
  
  fetch(`/api/zones/?ne_lat=${ne.lat}&ne_lng=${ne.lng}&sw_lat=${sw.lat}&sw_lng=${sw.lng}&detail=${detail}`)
    .then(response => response.json())
    .then(data => {
      // Clear existing zones
      if (window.zoneLayers) {
        window.zoneLayers.forEach(layer => map.removeLayer(layer));
      }
      window.zoneLayers = [];
      
      // Use different approaches based on zoom level
      if (zoom < 10) {
        // Just add markers at zone centers for low zoom levels
        data.zones.forEach(zone => {
          if (zone.center) {
            L.marker([zone.center.lat, zone.center.lng]).addTo(map);
          }
        });
      } else {
        // Add zone polygons for higher zoom levels
        data.zones.forEach(zone => {
          if (zone.geometry) {
            const layer = L.geoJSON(zone.geometry, {
              style: {
                weight: zoom >= 14 ? 2 : 1,
                opacity: zoom >= 14 ? 0.8 : 0.6,
                fillOpacity: zoom >= 14 ? 0.2 : 0.1
              }
            }).addTo(map);
            window.zoneLayers.push(layer);
          }
        });
      }
    });
  
  // Update when map is moved
  map.on('moveend', function() {
    loadOptimizedZones(map);
  });
}
```

### Prevention
- Implement proper level-of-detail management for different zoom levels
- Use markers instead of polygons at low zoom levels
- Simplify polygon geometries based on zoom level
- Limit the number of zones loaded at once
- Test map performance with large numbers of zones

## Tags
#map #performance #geolocation #zones #leaflet #rendering #user-experience #mobile-compatibility