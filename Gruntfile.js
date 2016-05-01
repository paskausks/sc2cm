/* global module */
module.exports = function(grunt) {
    'use strict';
    var bootstrapDir = 'node_modules/bootstrap/';
    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        less: {
            // Compiles LESS to CSS
            // Common options
            options: {
                // Specify dirs for @import directives
                paths: [
                    'static-src/less',
                    'node_modules/bootstrap/less',
                    'node_modules/font-awesome/less'
                ],
                strictUnits: true
            },
            dev: {
                options: {
                    compress: false,
                    // Generate source maps
                    sourceMap: true,
                    sourceMapFilename: 'sc2clanman/static/css/main.dev.map', // where file is generated and located
                    sourceMapBasepath: 'src', // This part is omitted from the referenced file URLS ...
                    sourceMapRootpath: '/tg/', // .. and this is added instead
                    sourceMapURL: 'sc2clanman/static/css/main.dev.map', // the complete url and filename put in the compiled css file
                },
                files: {
                    'sc2clanman/static/css/main.dev.css': 'src/less/main.less'
                }
            },
            admin: {
                // Task for transpiling and minifying LESS for the Django admin panel
                options: {
                    compress: true
                },
                files: {
                    'sc2clanman/static/css/admin/main.min.css': 'src/less/admin/main.less'
                }
            }
        },
        uglify: {
            // Minifies and mangles javascript
            options: {
                mangle: {
                    /*
                       Don't touch the variable names, which have
                       external dependencies, which aren't compressed into the main file.
                       Which in this case are jQuery and the Django javascript translation catalog functions
                       */
                    except: [
                        'jQuery',
                        'gettext',
                        'ngettext',
                        'interpolate',
                    ]
                },
                // All scripts will be wrapped inside closure and wrap value can be used
                // as a object where public variables can be put
                // We leave source maps disabled until we need debugging of minified javascript
                sourceMap: false,
                sourceMapIncludeSources: false,
                screwIE8: true,
                compress: {
                    // Remove console.log etc. statements.
                    drop_console: true
                }
            },
            production: {
                files: {
                    // Destination file
                    'sc2clanman/static/js/main.min.js': ['sc2clanman/static/js/main.dev.js'],
                }
            }
        },
        concat: {
            // Concatinates javascript files
            options: {
                separator: grunt.util.linefeed,
            },
            dev: {
                // We define all source files explicitly in order, just to be safe
                src: [
                'node_modules/tablesorter/dist/js/jquery.tablesorter.js',
                'node_modules/bootstrap/js/tooltip.js',
                'node_modules/bootstrap/js/popover.js',
                'src/js/members.js',
                'src/js/clanwar.js',
                ],
                // And define our destination
                dest: 'sc2clanman/static/js/main.dev.js',
            },
        },
        purifycss: {
            // Removes unused rules from CSS
            options: {
                minify: true,
            },
            target: {
                src: [
                    'sc2clanman/templates/sc2clanman/*.html',
                    'sc2clanman/static/js/main.dev.js'
                ],
                css: ['sc2clanman/static/css/main.dev.css'],
                dest: 'sc2clanman/static/css/main.purified.css'
            },
        },
        cssmin: {
            // Takes the purified CSS and minifies it for production
            options: {
                benchmark: true
            },
            target: {
                files: {
                    'sc2clanman/static/css/main.min.css': ['sc2clanman/static/css/main.purified.css']
                }
            }
        },
        watch: {
            options: {livereload: true},
            less: {
                files: ['src/less/*.less'],
                tasks: ['less:dev']
            },
            lessadmin: {
                files: ['src/less/admin/*.less'],
                tasks: ['less:admin']
            },
            concat: {
                files: ['src/js/*.js'],
                tasks: ['concat']
            },
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-purifycss');
    // Default task(s).
    grunt.registerTask('default', 'Development tasks for watching style and script files', ['less:dev', 'concat']);
    grunt.registerTask('build', 'Build task to create minified production files', ['purifycss', 'cssmin', 'uglify:production']);

};
