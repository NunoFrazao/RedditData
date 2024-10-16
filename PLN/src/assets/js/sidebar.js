(function () {
    'use strict'

    function initSidebarToggle() {
        const sidebarButton = document.getElementById('button-open-sidebar')
        if (sidebarButton) {
            sidebarButton.removeEventListener('click', toggleSidebar) // Remove previous listener to avoid duplicates
            sidebarButton.addEventListener('click', toggleSidebar)
        }
    }

    function toggleSidebar() {
        const pageWrapper = document.querySelector('.page-body-wrapper')
        if (pageWrapper) {
            pageWrapper.classList.toggle('page-body-wrapper-open')
        }
    }

    // Initialize when the document is ready
    document.addEventListener('DOMContentLoaded', initSidebarToggle)

    // Expose the function globally so it can be called after login or route changes
    window.initSidebarToggle = initSidebarToggle

})()
