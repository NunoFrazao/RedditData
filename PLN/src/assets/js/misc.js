(function ($) {
    'use strict'
    $(function () {
        var body = $('body')

        // Toggle sidebar
        $('[data-toggle="minimize"]').on("click", () => {
            if ((body.hasClass('sidebar-toggle-display')) || (body.hasClass('sidebar-absolute'))) {
                body.toggleClass('sidebar-hidden')
            } else {
                body.toggleClass('sidebar-icon-only')
            }
        })
    })
})(jQuery)
