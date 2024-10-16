(function () {
    'use strict'

    function initProfileDropdown() {
        const profileButton = document.getElementById('button-profile')
        if (profileButton) {
            profileButton.removeEventListener('click', toggleDropdown) // Remove previous listener to avoid duplicates
            profileButton.addEventListener('click', toggleDropdown)
        }

        const dropdownLinks = document.querySelectorAll('.dropdown-links')
        dropdownLinks.forEach(link => {
            link.removeEventListener('click', toggleDropdown) // Remove previous listener to avoid duplicates
            link.addEventListener('click', toggleDropdown)
        })
    }

    function toggleDropdown() {
        const dropdown = document.getElementById('dropdown-profile')
        if (dropdown) {
            dropdown.style.display = dropdown.style.display === 'none' || !dropdown.style.display ? 'block' : 'none'
        }
    }

    // Initialize when the document is ready
    document.addEventListener('DOMContentLoaded', initProfileDropdown)

    // Expose the function globally so it can be called after login or route changes
    window.initProfileDropdown = initProfileDropdown

})()
