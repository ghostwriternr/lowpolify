var path = require('path');
var multer = require('multer')

var storage = multer.diskStorage({
    destination: function(req, file, cb) {
        cb(null, path.resolve('image_dump/InputDump/'))
    },
    filename: function(req, file, cb) {
        var datetimestamp = Date.now();
        cb(null, file.fieldname + '-' + datetimestamp + '.' + file.originalname.split('.')[file.originalname.split('.').length - 1])
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

    app.get('*', function(req, res) {
        res.sendFile(path.resolve('public/index.html'));
    });

};
