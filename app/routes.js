var path = require('path');

module.exports = function(app) {

    app.get('*', function(req, res) {
        res.sendFile(path.resolve('public/index.html'));
    });

};
