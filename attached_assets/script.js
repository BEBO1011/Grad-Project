document.addEventListener("DOMContentLoaded", function () {
    const formTitle = document.getElementById("form-title");
    const fullNameInput = document.getElementById("full-name");
    const carBrandInput = document.getElementById("car-brand");
    const carModelInput = document.getElementById("car-model");
    const manufacturingYearInput = document.getElementById("manufacturing-year");
    const toggleText = document.getElementById("toggle-form");
    const form = document.getElementById("auth-form");

    toggleText.addEventListener("click", function (e) {
        e.preventDefault();
        if (fullNameInput.style.display === "none") {
            // تغيير إلى "Sign Up"
            fullNameInput.style.display = "block";
            carBrandInput.style.display = "block";
            carModelInput.style.display = "block";
            manufacturingYearInput.style.display = "block";
            formTitle.textContent = "Sign Up";
            toggleText.innerHTML = 'Already have an account? <a href="#">Sign In</a>';
        } else {
            // تغيير إلى "Sign In"
            fullNameInput.style.display = "none";
            carBrandInput.style.display = "none";
            carModelInput.style.display = "none";
            manufacturingYearInput.style.display = "none";
            formTitle.textContent = "Sign In";
            toggleText.innerHTML = 'Don\'t have an account? <a href="#">Sign Up</a>';
        }
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        window.location.href = "home.html"; // تحويل المستخدم للصفحة الرئيسية بعد التسجيل
    });
});

// إنشاء الخريطة وتحديد الموقع الافتراضي
var map = L.map('map').setView([30.0444, 31.2357], 10);

// إضافة خريطة من OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// إضافة ماركر افتراضي في وسط الخريطة
var marker = L.marker([30.0444, 31.2357], { draggable: true }).addTo(map);

// تحديث القيم عند تحريك الماركر
marker.on('dragend', function (e) {
    var latlng = marker.getLatLng();
    document.getElementById('latitude').value = latlng.lat.toFixed(6);
    document.getElementById('longitude').value = latlng.lng.toFixed(6);
});


// بيانات مراكز الصيانة
const maintenanceCenters = [
    { name: "AutoFix Garage", location: "Cairo, Egypt", rating: "⭐ 4.5" },
    { name: "Speedy Repairs", location: "Giza, Egypt", rating: "⭐ 4.2" },
    { name: "Elite Motors", location: "Alexandria, Egypt", rating: "⭐ 4.8" },
    { name: "Turbo Tune", location: "Mansoura, Egypt", rating: "⭐ 4.6" }
];

// إضافة المراكز إلى قسم "All"
const allCentersContainer = document.getElementById('all-centers');
maintenanceCenters.forEach(center => {
    const card = document.createElement('div');
    card.classList.add('card');
    card.innerHTML = <><h4>${center.name}</h4><p>${center.location}</p><p>${center.rating}</p></>;
    allCentersContainer.appendChild(card);
});

// إضافة بعض المراكز إلى قسم "Recently Viewed"
const recentlyViewedContainer = document.getElementById('recently-viewed');
const recentlyViewed = maintenanceCenters.slice(0, 2); // آخر مركزين تم زيارتهما
recentlyViewed.forEach(center => {
    const card = document.createElement('div');
    card.classList.add('card');
    card.innerHTML = <><h4>${center.name}</h4><p>${center.location}</p><p>${center.rating}</p></>;
    recentlyViewedContainer.appendChild(card);
});