var fs = require('fs');
var path = require('path');
var multer = require('multer');
var PythonShell = require('python-shell');

var storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, path.resolve('image_dump/InputDump/'))
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname)
    }
});
var upload = multer({
    storage: storage
}).single('file');

module.exports = function (app, io) {

    io.on('connection', function (socket) {
        console.log('A user connected');
        socket.on('hello', function () {
            console.log('Hello server! from ' + socket.id);
        });

        socket.on('disconnect', function () {
            console.log('A user disconnected');
        });
    });

    function findSocketByCookie(cookie) {
        for (var i in io.sockets.connected) {
            var socket = io.sockets.connected[i];
            if (socket.id === cookie) {
                return socket;
            }
        }
    }

    app.post('/api/upload', function (req, res) {
        console.log("Begin upload");
        upload(req, res, function (err) {
            if (err) {
                res.json({
                    error_code: 1,
                    err_desc: err
                });
                return;
            }
            console.log("Upload Success");
            res.json({
                error_code: 0,
                err_desc: null
            });
        })
    });

    app.post('/api/makeLowPoly/:name/:cFraction', function (req, res) {
        console.log("Begin makeLowPoly with cFraction" + req.params.cFraction);
        var options = {
            mode: 'text',
            scriptPath: 'scripts/',
            args: [path.resolve('image_dump/InputDump/' + req.params.name), path.resolve('image_dump/OutputDump/' + req.params.name), req.params.cFraction]
        };
        var pyshell = new PythonShell('lowpolify.py', options);
        pyshell.on('message', function (message) {
            if (message === 'Done') {
                console.log("makeLowPoly successful");
                res.send(message);
            }
            var socket = findSocketByCookie(req.cookies.io);
            socket.emit('scriptRun', {'message': message});
        });

        pyshell.end(function (err) {
            if (err) throw err;
            console.log('finished');
        });
    });

    app.get('/api/getLowPoly/:name', function (req, res) {
        console.log("Begin getLowPoly");
        var img = path.resolve('image_dump/OutputDump/' + req.params.name);
        fs.readFile(img, function (err, data) {
            if (err) throw err;
            console.log("getLowPoly successful");
            res.writeHead(200, {
                'Content-Type': 'text/html'
            });
            res.end(new Buffer(data).toString('base64'));
        });
    });
};