/**
 * Mobile menu functionality for CarLux Service app
 * Handles sidebar toggle on mobile devices
 */
document.addEventListener("DOMContentLoaded", function() {
    // Check if we're on a mobile device or small screen
    function isMobileView() {
        return window.innerWidth < 992; // Bootstrap's lg breakpoint
    }
    
    // Add mobile menu toggle if it doesn't exist
    function addMobileMenuToggle() {
        if (!document.querySelector('.mobile-menu') && document.querySelector('.sidebar')) {
            const mobileToggle = document.createElement('div');
            mobileToggle.className = 'mobile-menu';
            mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
            document.body.appendChild(mobileToggle);
            
            // Toggle sidebar visibility
            mobileToggle.addEventListener('click', function() {
                const sidebar = document.querySelector('.sidebar');
                sidebar.classList.toggle('sidebar-open');
                
                // Toggle icon
                if (sidebar.classList.contains('sidebar-open')) {
                    mobileToggle.innerHTML = '<i class="fas fa-times"></i>';
                } else {
                    mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
                }
            });
            
            // Close sidebar when clicking outside
            document.addEventListener('click', function(event) {
                const sidebar = document.querySelector('.sidebar');
                const mobileToggle = document.querySelector('.mobile-menu');
                
                if (sidebar && sidebar.classList.contains('sidebar-open') && 
                    !sidebar.contains(event.target) && 
                    !mobileToggle.contains(event.target)) {
                    sidebar.classList.remove('sidebar-open');
                    mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
                }
            });
        }
    }
    
    // Adjust sidebar for mobile view
    function adjustForMobile() {
        const sidebar = document.querySelector('.sidebar');
        const content = document.querySelector('.content');
        
        if (sidebar && content) {
            if (isMobileView()) {
                // Mobile view adjustments
                sidebar.classList.add('mobile-sidebar');
                content.style.marginLeft = '0';
                addMobileMenuToggle();
            } else {
                // Desktop view adjustments
                sidebar.classList.remove('mobile-sidebar', 'sidebar-open');
                content.style.marginLeft = '220px';
            }
        }
    }
    
    // Initial adjustment
    adjustForMobile();
    
    // Re-adjust on window resize
    window.addEventListener('resize', adjustForMobile);
});