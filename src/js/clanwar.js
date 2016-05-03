/*
* Member table events and functions
*/

/* global jQuery, userIsAdmin */

(function ($) {
    'use strict';
    $(document).ready(function() {
        var $clanwarTable = $('#clanwar-table');
 
        // Note popovers
        $clanwarTable.find('.notes[data-toggle="popover"]').popover({
            html: true
        });

        // Time zone tooltips
        $(function () {
            $('[data-toggle="tooltip"]').tooltip({
                html: true
            });
        });
    });
})(jQuery);