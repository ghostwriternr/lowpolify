var fs = require('fs');
var path = require('path');
var schedule = require('node-schedule');

var cleaner = schedule.scheduleJob('0 * * * * *', function() {
    fs.readdir('image_dump/OutputDump/', function(err, files) {
        if (err) throw err;
        files.forEach(function(file) {
            var filename = file;
            filename = filename.substr(0, filename.indexOf('.'));
            if (filename.length > 0) {
                var timestamp = filename.substr(filename.lastIndexOf('-') + 1);
                if (Date.now() - timestamp >= 900000) {
                    fs.unlink('image_dump/OutputDump/' + file);
                }
            }
        });
    });
    fs.readdir('image_dump/InputDump/', function(err, files) {
        if (err) throw err;
        files.forEach(function(file) {
            var filename = file;
            filename = filename.substr(0, filename.indexOf('.'));
            if (filename.length > 0) {
                var timestamp = filename.substr(filename.lastIndexOf('-') + 1);
                if (Date.now() - timestamp >= 900000) {
                    fs.unlink('image_dump/InputDump/' + file);
                }
            }
        });
    });
});

module.exports = function(app) {

    require('./lowpolify-routes.js')(app);
    require('./clarifai-routes.js')(app);

    app.get('*', function(req, res) {
        res.sendFile(path.resolve('public/index.html'));
    });
};
