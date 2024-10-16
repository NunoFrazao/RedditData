(function () {
    'use strict';

    function initFiltersToggle() {
        const filtersButton = document.getElementById('button-filters');
        if (filtersButton) {
            filtersButton.removeEventListener('click', toggleFilters); // Remove previous listener to avoid duplicates
            filtersButton.addEventListener('click', toggleFilters);
        }
    }

    function toggleFilters() {
        const filtersDiv = document.getElementById('div-main-filters');
        if (filtersDiv) {
            filtersDiv.style.display = filtersDiv.style.display === 'none' || !filtersDiv.style.display ? 'block' : 'none';
        }
    }

    // Initialize when the document is ready
    document.addEventListener('DOMContentLoaded', initFiltersToggle);

    // Expose the function globally so it can be called after login or route changes
    window.initFiltersToggle = initFiltersToggle;

})();
