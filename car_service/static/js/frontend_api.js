const API_BASE_URL = "http://127.0.0.1:8082"; // Empty string for same-domain relative paths


// Get all WhatsApp buttons with the class "whatsapp-btn"
document.querySelectorAll(".whatsapp-btn").forEach(function(button) {
    button.addEventListener("click", function() {
        // Hardcoded phone number for testing
        var phoneNumber = "201112218026"; // Replace with your test number
        var whatsappUrl = `https://wa.me/${phoneNumber}?text=Hello`; // Correct usage of backticks
        window.open(whatsappUrl, "_blank"); // Open WhatsApp chat in a new tab
    });
});

// Get all "Call Now" buttons with the class "call-btn"
document.querySelectorAll(".call-btn").forEach(function(button) {
    button.addEventListener("click", function() {
        // Hardcoded phone number for testing
        var phoneNumber = "201112218026"; // Replace with the actual phone number for each center if needed
        var callUrl = `tel:${phoneNumber}`; // Use the "tel:" protocol to initiate a phone call
        window.location.href = callUrl; // This will open the dialer on mobile devices
    });
});

// Getting location
function getUserLocation(callback) {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const userLat = position.coords.latitude;
                const userLon = position.coords.longitude;
                console.log("User Location:", userLat, userLon);
                callback(userLat, userLon);
            },
            error => {
                console.error("Error getting location:", error);
                alert("Error getting your location. Default location will be used.");
                
                // Default location in case of error (e.g., Cairo, Egypt)
                const defaultLat = 30.0444;
                const defaultLon = 31.2357;
                callback(defaultLat, defaultLon);
            }
        );
    } else {
        console.error("Geolocation is not supported by this browser.");
        alert("Geolocation is not supported. Using default location.");

        // Provide a default location if geolocation is not supported
        const defaultLat = 30.0444;
        const defaultLon = 31.2357;
        callback(defaultLat, defaultLon);
    }
}

getUserLocation(function(latitude, longitude) {
    // Use the latitude and longitude here
    console.log("Received Location:", latitude, longitude);

    // Send the data to the backend
    sendLocationToBackend(latitude, longitude);
});

// add fake data 
document.addEventListener("DOMContentLoaded", async function () {
    const allCentersContainer = document.getElementById("all-centers");
    const recentlyViewedContainer = document.getElementById("recently-viewed");

    console.log("all-centers found?", allCentersContainer);
    console.log("recently-viewed found?", recentlyViewedContainer);

    if (!allCentersContainer || !recentlyViewedContainer) {
        console.error("⚠️ ERROR: One or both containers are missing in the HTML. Check your HTML structure.");
        return;
    }

    try {
        const response = await fetch("/api/maintenance-centers");
        const centers = await response.json();
        console.log("Loaded maintenance centers:", centers);

        centers.forEach((center, index) => {
            const card = document.createElement("div");
            card.className = "card";
            card.innerHTML = `
                <i class="fas fa-tools"></i> ${center.name} 
                <br>📍 Location: ${center.latitude}, ${center.longitude}
            `;

            allCentersContainer.appendChild(card);

            if (index < 3) {
                recentlyViewedContainer.appendChild(card.cloneNode(true));
            }
        });

    } catch (error) {
        console.error("❌ ERROR: Could not load maintenance centers:", error);
    }
});

// Sign Up Function DONE    
async function signup(email, name, password, carBrand, carModel, year) {
    const response = await fetch(`${API_BASE_URL}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name, password, car_brand: carBrand, car_model: carModel, manufacturing_year: year })
    });
    return response.json();
}

// Sign In Function DONE
async function signin(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/signin`, { 
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            throw new Error("HTTP error! Status: " + response.status);
        }

        const data = await response.json(); // ✅ Convert response to JSON

        console.log("Signin response:", data); // ✅ Debugging

        if (data.message === "Login successful") {  // ✅ Check message from API
            // Store user data in localStorage
            localStorage.setItem('userId', data.user_id);
            localStorage.setItem('userName', data.name);
            localStorage.setItem('userEmail', data.email);
            
            alert(`Welcome, ${data.name}!`);
            window.location.href = "/home"; // Redirect user to homepage
        } else {
            alert("Sign in failed. Check your credentials.");
        }
    } catch (error) {
        console.error("Error during signin:", error);
        alert("An error occurred. Please try again.");
    }
}


// Search Car Problems DONE
async function searchCarProblem(query, brand, model, lang) {
    const response = await fetch(`${API_BASE_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, brand, model, lang })
    });
    return response.json();
}

// Nearest car owner
async function getNearestOwner(lat, lon) {
    const response = await fetch(`${API_BASE_URL}/nearest-owner?lat=${lat}&lon=${lon}`);
    return response.json();
}

// searching for location 
async function handleNearestOwner(lat, lon) {
    try {
        const response = await getNearestOwner(lat, lon);
        document.getElementById("nearest-owner-response").innerText = JSON.stringify(response, null, 2);
    } catch (error) {
        console.error("Error finding nearest car owner:", error);
    }
}

// Get Nearest Car Owner
async function handleNearestCenter(lat, lon) {
    console.log("🚀 Received lat:", lat, "lon:", lon);  // ✅ Check values before sending

    if (isNaN(lat) || isNaN(lon)) {
        alert("❌ Please enter a valid latitude and longitude.");
        return;
    }

    try {
        const response = await fetch(`/nearest-maintenance-center?lat=${lat}&lon=${lon}`);
        console.log("🟢 Response status:", response.status);  // ✅ Check response status

        const data = await response.json();
        console.log("✅ Maintenance Center Response:", data);  // ✅ Check response

        document.getElementById("nearest-center-response").innerText = JSON.stringify(data, null, 2);
    } catch (error) {
        console.error("❌ Error finding nearest maintenance center:", error);
    }
}

function manualLocation() {
    const lat = parseFloat(document.getElementById("manual-lat").value);
    const lon = parseFloat(document.getElementById("manual-lon").value);

    if (!isNaN(lat) && !isNaN(lon)) {
        console.log("Using manually entered location:", lat, lon);
        handleNearestOwner(lat, lon);  // Calls function with manual coordinates
    } else {
        alert("Please enter a valid latitude and longitude.");
    }
}

// Get Nearest Maintenance Centers
async function getNearestCenters(lat, lon, brand) {
    const response = await fetch(`${API_BASE_URL}/nearest-center?lat=${lat}&lon=${lon}&brand=${brand}`);
    return response.json();
}

// Get Directions
async function getDirections(startLat, startLon, endLat, endLon, lang="en") {
    const response = await fetch(`${API_BASE_URL}/get-directions?start=${startLon},${startLat}&end=${endLon},${endLat}&lang=${lang}`);
    return response.json();
}

// Save User Location
async function saveUserLocation(userId, lat, lon) {
    const response = await fetch(`${API_BASE_URL}/save-location`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, latitude: lat, longitude: lon })
    });
    return response.json();
}
// Function to send location to the backend
async function sendLocationToBackend(lat, lon) {
    try {
        // Only send if we have a logged-in user
        const userId = localStorage.getItem("userId");
        if (userId) {
            console.log("Sending location to backend for user:", userId);
            await saveUserLocation(userId, lat, lon);
            console.log("Location saved successfully");
        } else {
            console.log("User not logged in, location not saved");
        }
    } catch (error) {
        console.error("Error saving location:", error);
    }
}

// Book Appointment
async function bookAppointment(userId, vehicleId, centerId, serviceId, appointmentDate, notes) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/book-appointment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                vehicle_id: vehicleId,
                center_id: centerId,
                service_id: serviceId,
                appointment_date: appointmentDate,
                notes: notes
            })
        });

        if (!response.ok) {
            if (response.status === 401) {
                handleAuthError({ status: 401 });
                return;
            }
            throw new Error('Failed to book appointment');
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error booking appointment:', error);
        throw error;
    }
}

// Add this function at the top level
function handleAuthError(error) {
    if (error.status === 401) {
        // Clear any existing user data
        localStorage.removeItem('userId');
        localStorage.removeItem('userName');
        localStorage.removeItem('userEmail');
        
        // Show error popup
        const errorMessage = error.message || "Please sign in to access this feature";
        window.location.href = `/login?error=${encodeURIComponent(errorMessage)}`;
    }
}

// Update the fetch calls in loadUserVehicles
async function loadUserVehicles() {
    try {
        const userId = localStorage.getItem('userId');
        if (!userId) {
            throw new Error('User not logged in');
        }

        const response = await fetch(`${API_BASE_URL}/api/user/vehicles?user_id=${userId}`);
        if (!response.ok) {
            if (response.status === 401) {
                handleAuthError({ status: 401 });
                return;
            }
            throw new Error('Failed to load vehicles');
        }
        const vehicles = await response.json();
        const vehicleSelect = document.getElementById('vehicleSelect');
        vehicleSelect.innerHTML = '<option value="">Select a vehicle</option>';
        vehicles.forEach(vehicle => {
            vehicleSelect.innerHTML += `<option value="${vehicle.id}">${vehicle.make} ${vehicle.model} (${vehicle.year})</option>`;
        });
    } catch (error) {
        console.error('Error loading vehicles:', error);
        alert('Failed to load vehicles. Please try again.');
    }
}

// Update the fetch calls in loadCenterServices
async function loadCenterServices(centerId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/maintenance-center/${centerId}`);
        if (!response.ok) {
            if (response.status === 401) {
                handleAuthError({ status: 401 });
                return;
            }
            throw new Error('Failed to load services');
        }
        const center = await response.json();
        const serviceSelect = document.getElementById('serviceSelect');
        serviceSelect.innerHTML = '<option value="">Select a service</option>';
        center.services.forEach(service => {
            serviceSelect.innerHTML += `<option value="${service.id}">${service.name} - $${service.price}</option>`;
        });
    } catch (error) {
        console.error('Error loading services:', error);
        alert('Failed to load services. Please try again.');
    }
}
