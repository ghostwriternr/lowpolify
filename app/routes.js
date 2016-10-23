var fs = require('fs');
var path = require('path');
var multer = require('multer');
var PythonShell = require('python-shell');
var Clarifai = require('clarifai');
var secrets = require('./secrets/secrets.json');
var app = new Clarifai.App(
    secrets.clientId,
    secrets.clientSecret
);

var storage = multer.diskStorage({
    destination: function(req, file, cb) {
        cb(null, path.resolve('image_dump/InputDump/'))
    },
    filename: function(req, file, cb) {
        var datetimestamp = Date.now();
        cb(null, file.originalname)
    }
});
var upload = multer({
    storage: storage
}).single('file');

module.exports = function(app) {

    app.post('/api/upload', function(req, res) {
        console.log("Begin multer");
        upload(req, res, function(err) {
            if (err) {
                res.json({ error_code: 1, err_desc: err });
                return;
            }
            res.json({ error_code: 0, err_desc: null });
        })
    });

    app.post('/api/makeLowPoly/:name', function(req, res) {
        var options = {
            mode: 'text',
            scriptPath: 'scripts/',
            args: [path.resolve('image_dump/InputDump/' + req.params.name), path.resolve('image_dump/OutputDump/' + req.params.name)]
        };
        var pyshell = new PythonShell('lowpolify.py', options);
        pyshell.on('message', function(message) {
            res.send(message);
        });

        pyshell.end(function(err) {
            if (err) throw err;
            console.log('finished');
        });
    });

    app.get('/api/getLowPoly/:name', function(req, res) {
        var img = path.resolve('image_dump/OutputDump/' + req.params.name);
        fs.readFile(img, function(err, data) {
            if (err) throw err;
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(new Buffer(data).toString('base64'));
        });
    });

    app.get('*', function(req, res) {
        res.sendFile(path.resolve('public/index.html'));
    });

};
