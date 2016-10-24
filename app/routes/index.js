var path = require('path');

module.exports = function(app) {

	require('./lowpolify-routes.js')(app);
    require('./clarifai-routes.js')(app);

    app.get('*', function(req, res) {
        res.sendFile(path.resolve('public/index.html'));
    });
};
