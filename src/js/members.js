(function ($) {
    'use strict';
    $(document).ready(function() {

        var rowNumberCol = 0; // Which column of the table is for the fixed row counter;
        var rowNumberCb = function (e, table) {
            // Event handler to generate row numbers in the table
            $(e.target).find('tbody').children('tr').each(function (i, el) {
                $(el).children('td').get(rowNumberCol).innerHTML = i + 1;
            });
        }

        $.tablesorter.addParser({
            // Parser for the rank and league columns.
            //
            id: 'rank',
            is: function(s) {
                // return false so this parser is not auto detected
                return false;
            },
            format: function(s, table, cell, cellIndex) {
                // s is the text from the cell
                // table is the current table (as a DOM element; not jQuery object)
                // cell is the current table cell (DOM element)
                // cellIndex is the current cell's column index
                // format your data for normalization
                // (i.e. do something to get and/or modify your data, then return it)

                // For sorting ranks we add a "weight" value to league and add it to the rank,
                // so higher league players are sorted higher. Higher weight is worse, since higher rank is also worse.
                var weights = {
                    UNRANKED: 8,
                    BRONZE: 7,
                    SILVER: 6,
                    GOLD: 5,
                    PLATINUM: 4,
                    DIAMOND: 3,
                    MASTER: 2,
                    GRANDMASTER: 1,
                }
                var rank = cell.getAttribute('data-rank');
                var leagueWeight = weights[cell.getAttribute('data-league')];

                // And we convert to string to concat into a float, then parse it.
                // With a maximum of 100 ranks, we add leading zeros with a slice trick, so 3 digits,
                // or else a rank 1 GM will be the same as a rank 100 GM, because 1.1 === 1.100
                return parseFloat(leagueWeight + '.' + ("00" + rank).slice(-3), 10);
            },
            // flag for filter widget (true = ALWAYS search parsed values; false = search cell text)
            parsed: false,
            // set the type to either numeric or text (text uses a natural sort function
            // so it will work for everything, but numeric is faster for numbers
            type: 'numeric'
        });

        $.tablesorter.addParser({
            // Parser for the rank and league columns.
            //
            id: 'country',
            is: function(s) {
                // return false so this parser is not auto detected
                return false;
            },
            format: function(s, table, cell, cellIndex) {
                return cell.getAttribute('data-country'); // Use the data attribute of the cell as the sorting param.
            },
            parsed: true,
            type: 'text'
        });

        $.tablesorter.addParser({
            // Parser for the rank and league columns.
            //
            id: 'player-name',
            is: function(s) {
                // return false so this parser is not auto detected
                return false;
            },
            format: function(s, table, cell, cellIndex) {
                return cell.getAttribute('data-playername'); // Use the data attribute of the cell as the sorting param.
            },
            parsed: true,
            type: 'text'
        });

        $.tablesorter.addParser({
            // Parser for the rank and league columns.
            id: 'winrate',
            is: function(s) {
                // return false so this parser is not auto detected
                return false;
            },
            format: function(s, table, cell, cellIndex) {
                var wins = parseInt(cell.getAttribute('data-wins'), 10);
                var losses = parseInt(cell.getAttribute('data-losses'), 10);

                if (wins === undefined) {
                    console.info(wins, losses);
                }
                return 100 / (wins + losses) * wins // Return winrate
            },
            parsed: true,
            type: 'numeric'
        });

        $.tablesorter.addParser({
            // Parser for the rank and league columns.
            id: 'twitch',
            is: function(s) {
                // return false so this parser is not auto detected
                return false;
            },
            format: function(s, table, cell, cellIndex) {
                return cell.getAttribute('data-twitch');
            },
            parsed: true,
            type: 'text'
        });

        $("#members-table").tablesorter({
            sortList: [[1,0]], // Default sorting by Rank, descending
            headers: {
                0: {
                    sorter: false // Row number column - filled dynamically
                },
                1: {
                    sorter: 'rank'
                },
                2: {
                    sorter: 'country'
                },
                3: {
                    sorter: 'player-name'
                },
                4: {
                    sorter: false // Skype column
                },
                5: {
                    sorter: 'twitch' // Twitch link column
                },
                8: {
                    sorter: 'winrate' // Winrate column
                },
                13: {
                    sorter: false // Notes column
                },
                14: {
                    sorter: false // Admin column
                }
            }
        }).bind('sortEnd', rowNumberCb).bind('tablesorter-ready', rowNumberCb);

        // Winrate tooltips.
        $('#members-table tr[data-toggle="tooltip"]').tooltip({
            // Add a delay to minimise lag while scrolling the table.
            delay: 100,
            html: true, // We shouldn't be worried about XSS, since django escapes HTML.
            // Generate the title by using the data attributes
            title: function() {
                return '<p>Total games: ' + this.getAttribute('data-games-total') +
                '</p><p>Winrate: ' + this.getAttribute('data-winrate') + '%</p>';
            }
        });

        // Skype tooltips.
        $('#members-table [data-skype][data-toggle="tooltip"]').tooltip({
            // Add a delay to minimise lag while scrolling the table.
            trigger: 'click focus',
            html: true, // We shouldn't be worried about XSS, since django escapes HTML.
            // Generate the title by using the data attributes
            title: function() {
                //
                var skype = this.getAttribute('data-skype')
                return '<p><img class="skype-avatar loader" src="https://api.skype.com/users/' + skype + '/profile/avatar" alt="' + skype + '"></p>' +
                '<p><strong>' + skype + '</strong></p>' +
                '<p><a href="skype:' + skype + '?add">Add to contacts</a><br>' +
                '<a href="skype:' + skype + '?call">Call</a><br>' +
                '<a href="skype:' + skype + '?chat">Chat</a></p>';
            }
        });

        // Note popovers
        $('#members-table .notes[data-toggle="popover"]').popover({
            html: true // We shouldn't be worried about XSS, since Bleach escapes harmful HTML.
        });
    });
})(jQuery);