// Utility: update the location button UI state
function updateLocationButton(state, message) {
    const btn = document.getElementById('locationBtn');
    const status = document.getElementById('locationStatus');
    const btnText = btn.querySelector('.btn-text');
    const btnIcon = btn.querySelector('.btn-icon');

    switch(state) {
        case 'loading':
            btn.disabled = true;
            btn.classList.add('loading');
            btnIcon.textContent = '🔄';
            btnText.textContent = 'Getting Location...';
            status.textContent = '';
            break;
        case 'success':
            btn.disabled = false;
            btn.classList.remove('loading');
            btnIcon.textContent = '✅';
            btnText.textContent = 'Location Updated';
            status.textContent = message || 'Location updated successfully';
            status.className = 'location-status success';
            setTimeout(() => {
                btnIcon.textContent = '📍';
                btnText.textContent = 'Use My Location';
            }, 2000);
            break;
        case 'error':
            btn.disabled = false;
            btn.classList.remove('loading');
            btnIcon.textContent = '❌';
            btnText.textContent = 'Location Failed';
            status.textContent = message || 'Unable to get location';
            status.className = 'location-status error';
            setTimeout(() => {
                btnIcon.textContent = '📍';
                btnText.textContent = 'Try Again';
            }, 3000);
            break;
    }
}

// Geolocation fetch and send location to server
function getLocationAndSend() {
    if (!navigator.geolocation) {
        updateLocationButton('error', 'Geolocation not supported by this browser');
        return;
    }

    updateLocationButton('loading');

    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            fetch('/set_location', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat: lat, lon: lon })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateLocationButton('success', 'Refreshing weather data...');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    updateLocationButton('error', data.message || 'Server error');
                }
            })
            .catch(error => {
                console.error('Network error:', error);
                updateLocationButton('error', 'Network error occurred');
            });
        },
        function(error) {
            let message = 'Location access denied';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    message = 'Location access denied by user';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message = 'Location information unavailable';
                    break;
                case error.TIMEOUT:
                    message = 'Location request timed out';
                    break;
            }
            updateLocationButton('error', message);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
    );
}

// Intercept form submit to split lat/lon values
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form[action="/user_location"]');
    if (form) {
        form.addEventListener('submit', function(e) {
            const select = document.getElementById('location-select');
            const val = select.value;
            if (!val) {
                e.preventDefault();
                alert('Please select a location');
                return false;
            }
            const [lat, lon] = val.split(',');

            // Remove existing hidden inputs if any
            ['lat', 'lon'].forEach(name => {
                const existing = form.querySelector(`input[name="${name}"]`);
                if (existing) existing.remove();
            });
            // Add new hidden inputs
            const latInput = document.createElement('input');
            latInput.type = 'hidden';
            latInput.name = 'lat';
            latInput.value = lat;
            form.appendChild(latInput);
            const lonInput = document.createElement('input');
            lonInput.type = 'hidden';
            lonInput.name = 'lon';
            lonInput.value = lon;
            form.appendChild(lonInput);

            select.disabled = true;
        });
    }

   const locationName = window.locationName || "";

   const hasLocation = locationName !== "" && locationName !== "Unknown Location";


    if (!hasLocation && !localStorage.getItem('locationRequested')) {
        localStorage.setItem('locationRequested', 'true');
    }
});
