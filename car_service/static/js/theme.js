/**
 * Theme management for CarLux Service app
 * Handles dark/light theme persistence and switching
 */
document.addEventListener("DOMContentLoaded", function() {
    // Apply saved theme on page load
    function applyTheme() {
        const savedSettings = localStorage.getItem("userSettings");
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            if (settings.theme === 'dark') {
                document.documentElement.setAttribute('data-theme', 'dark');
            } else {
                document.documentElement.removeAttribute('data-theme');
            }
        }
    }
    
    // Initialize theme
    applyTheme();
    
    // Add theme toggle to header if toggle element exists
    const userIconsContainer = document.querySelector('.user-icons');
    if (userIconsContainer) {
        // Check if theme toggle button already exists
        if (!document.getElementById('theme-toggle-btn')) {
            const themeToggle = document.createElement('span');
            themeToggle.id = 'theme-toggle-btn';
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            themeToggle.title = 'Toggle Dark Mode';
            themeToggle.style.cursor = 'pointer';
            
            // Update icon based on current theme
            const isDarkTheme = document.documentElement.getAttribute('data-theme') === 'dark';
            themeToggle.innerHTML = isDarkTheme ? 
                '<i class="fas fa-sun"></i>' : 
                '<i class="fas fa-moon"></i>';
                
            themeToggle.addEventListener('click', function() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                let newTheme = 'light';
                
                if (currentTheme !== 'dark') {
                    document.documentElement.setAttribute('data-theme', 'dark');
                    themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
                    newTheme = 'dark';
                } else {
                    document.documentElement.removeAttribute('data-theme');
                    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
                }
                
                // Save theme preference
                const savedSettings = localStorage.getItem("userSettings");
                if (savedSettings) {
                    const settings = JSON.parse(savedSettings);
                    settings.theme = newTheme;
                    localStorage.setItem("userSettings", JSON.stringify(settings));
                } else {
                    // Create new settings object if none exists
                    const settings = {
                        language: 'en',
                        timezone: 'UTC',
                        timeFormat: '24h',
                        theme: newTheme
                    };
                    localStorage.setItem("userSettings", JSON.stringify(settings));
                }
                
                // Show quick feedback
                const notification = document.createElement('div');
                notification.className = 'notification success';
                notification.innerHTML = `<i class="fas fa-check-circle"></i> ${newTheme.charAt(0).toUpperCase() + newTheme.slice(1)} mode enabled`;
                document.body.appendChild(notification);
                
                setTimeout(() => {
                    notification.style.opacity = '0';
                    setTimeout(() => {
                        notification.remove();
                    }, 500);
                }, 2000);
            });
            
            userIconsContainer.prepend(themeToggle);
        }
    }
});