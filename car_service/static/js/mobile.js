/**
 * Mobile menu functionality for CarLux Service app
 * Handles sidebar toggle on mobile devices with enhanced UX
 */
document.addEventListener("DOMContentLoaded", function() {
    // Check if we're on a mobile device or small screen
    function isMobileView() {
        return window.innerWidth < 992; // Bootstrap's lg breakpoint
    }
    
    // Create backdrop element for mobile sidebar
    function createBackdrop() {
        if (!document.querySelector('.sidebar-backdrop')) {
            const backdrop = document.createElement('div');
            backdrop.className = 'sidebar-backdrop';
            document.body.appendChild(backdrop);
            
            // Close sidebar when clicking on backdrop
            backdrop.addEventListener('click', function() {
                closeSidebar();
            });
        }
    }
    
    // Function to toggle sidebar open
    function openSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const mobileToggle = document.querySelector('.mobile-menu');
        const backdrop = document.querySelector('.sidebar-backdrop');
        
        if (sidebar) {
            sidebar.classList.add('sidebar-open');
            if (mobileToggle) {
                mobileToggle.innerHTML = '<i class="fas fa-times"></i>';
                mobileToggle.setAttribute('aria-expanded', 'true');
            }
            if (backdrop) {
                backdrop.classList.add('active');
            }
            // Prevent body scrolling when sidebar is open
            document.body.style.overflow = 'hidden';
        }
    }
    
    // Function to close sidebar
    function closeSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const mobileToggle = document.querySelector('.mobile-menu');
        const backdrop = document.querySelector('.sidebar-backdrop');
        
        if (sidebar) {
            sidebar.classList.remove('sidebar-open');
            if (mobileToggle) {
                mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
                mobileToggle.setAttribute('aria-expanded', 'false');
            }
            if (backdrop) {
                backdrop.classList.remove('active');
            }
            // Restore body scrolling
            document.body.style.overflow = '';
        }
    }
    
    // Add mobile menu toggle if it doesn't exist
    function addMobileMenuToggle() {
        if (!document.querySelector('.mobile-menu') && document.querySelector('.sidebar')) {
            const mobileToggle = document.createElement('div');
            mobileToggle.className = 'mobile-menu';
            mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
            mobileToggle.setAttribute('aria-label', 'Toggle navigation menu');
            mobileToggle.setAttribute('role', 'button');
            mobileToggle.setAttribute('tabindex', '0');
            mobileToggle.setAttribute('aria-expanded', 'false');
            document.body.appendChild(mobileToggle);
            
            // Create backdrop for mobile sidebar
            createBackdrop();
            
            // Toggle sidebar visibility with enhanced accessibility
            mobileToggle.addEventListener('click', function() {
                const sidebar = document.querySelector('.sidebar');
                
                if (sidebar && !sidebar.classList.contains('sidebar-open')) {
                    openSidebar();
                } else {
                    closeSidebar();
                }
            });
            
            // Enable keyboard accessibility
            mobileToggle.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    mobileToggle.click();
                }
            });
            
            // Close sidebar when clicking outside
            document.addEventListener('click', function(event) {
                const sidebar = document.querySelector('.sidebar');
                const mobileToggle = document.querySelector('.mobile-menu');
                
                if (sidebar && sidebar.classList.contains('sidebar-open') && 
                    !sidebar.contains(event.target) && 
                    !mobileToggle.contains(event.target)) {
                    closeSidebar();
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
                
                // Remove backdrop if exists and visible
                const backdrop = document.querySelector('.sidebar-backdrop');
                if (backdrop) {
                    backdrop.classList.remove('active');
                }
                
                // Remove any overflow restrictions on body
                document.body.style.overflow = '';
            }
        }
    }
    
    // Add touch swipe support for sidebar
    function addSwipeSupport() {
        let touchStartX = 0;
        let touchEndX = 0;
        
        // Detect touch start position
        document.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, false);
        
        // Detect touch end position and handle swipe
        document.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, false);
        
        // Process swipe direction
        function handleSwipe() {
            const sidebar = document.querySelector('.sidebar');
            if (!sidebar) return;
            
            // Minimum swipe distance (in pixels)
            const swipeThreshold = 70;
            
            // Right to left swipe (close sidebar)
            if (touchStartX - touchEndX > swipeThreshold && sidebar.classList.contains('sidebar-open')) {
                closeSidebar();
            }
            
            // Left to right swipe (open sidebar) - only near the left edge
            if (touchEndX - touchStartX > swipeThreshold && touchStartX < 50 && !sidebar.classList.contains('sidebar-open')) {
                openSidebar();
            }
        }
    }
    
    // Initial adjustment
    adjustForMobile();
    
    // Add swipe support for mobile
    addSwipeSupport();
    
    // Re-adjust on window resize
    window.addEventListener('resize', adjustForMobile);
});