// set up ======================================================================
var express = require('express');
var app = express(); // create our app w/ express
var port = process.env.PORT || 8080; // set the port
var morgan = require('morgan');
var bodyParser = require('body-parser');
var methodOverride = require('method-override');
var cookieParser = require('cookie-parser');

var server = require('http').Server(app);
var io = require('socket.io')(server);

// configuration ===============================================================

app.use(express.static('./public')); // set the static files location /public/img will be /img for users
app.use(morgan('dev')); // log every request to the console
app.use(bodyParser.urlencoded({ 'extended': 'true' })); // parse application/x-www-form-urlencoded
app.use(bodyParser.json()); // parse application/json
app.use(bodyParser.json({ type: 'application/vnd.api+json' })); // parse application/vnd.api+json as json
app.use(methodOverride('X-HTTP-Method-Override')); // override with the X-HTTP-Method-Override header in the request

app.use(cookieParser());

// redirections
app.use('/scripts', express.static(__dirname + '/scripts/'));
app.use('/imge_dump', express.static(__dirname + '/image_dump/'));
app.use('/secrets', express.static(__dirname + '/app/secrets/'));
app.use('/upload_module', express.static(__dirname + '/node_modules/ng-file-upload/dist/'));
app.use('/slider_module', express.static(__dirname + '/node_modules/angularjs-slider/dist/'));

// routes ======================================================================
require('./app/routes')(app, io);

// listen (start app with node server.js) ======================================
server.listen(port);
console.log("The magic begins on port " + port);
