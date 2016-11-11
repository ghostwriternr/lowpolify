var fs = require('fs');
var path = require('path');
var mime = require('mime');
var request = require('request');
var jsonfile = require('jsonfile');
var secrets = "./app/secrets/secrets.json";
var baseUrl = "https://api.clarifai.com/v1/";
var clarifai = require(path.resolve(secrets));

module.exports = function(app) {
    app.post('/api/clarifai/getAccessToken', function(req, res) {
        console.log("Begin getAccessToken");
        request.post({
            url: baseUrl + "token/",
            form: {
                client_id: clarifai.clientId,
                client_secret: clarifai.clientSecret,
                grant_type: 'client_credentials'
            }
        }, function(error, response, body) {
            if (error) {
                console.log(error);
            } else {
                var obj = {};
                obj["clientId"] = clarifai.clientId;
                obj["clientSecret"] = clarifai.clientSecret;
                body = JSON.parse(body);
                obj["access"] = body;
                jsonfile.writeFileSync(secrets, obj);
                clarifai = obj;
                console.log(response.statusCode, body);
                console.log("getAccessToken successful");
                res.send(body.access_token);
            }
        });
    });


    app.post('/api/clarifai/getTags/:image', function(req, res) {
        console.log("Begin getTags");
        var img = path.resolve('image_dump/InputDump/' + req.params.image);
        fs.readFile(img, function(err, original_data) {
            if (err) {
                console.log(err);
            } else {
                var base64Image = original_data.toString('base64');
                request.post({
                    url: baseUrl + "tag/",
                    form: {
                        encoded_data: base64Image
                    },
                    headers: {
                        Authorization: "Bearer " + clarifai.access.access_token
                    }
                }, function(error, response, body) {
                    if (error) {
                        console.log(error);
                    } else {
                        body = JSON.parse(body);
                        console.log(body);
                        if (body.status_code == "TOKEN_EXPIRED")
                            res.json(body);
                        else {
                            console.log("getTags successful");
                            res.json(body);
                        }
                    }
                });
            }
        });
    });

    app.get('/api/clarifai/tagDownload/:tagName/:imageName', function(req, res) {
        console.log("Begin download");
        var img = path.resolve('image_dump/OutputDump/' + req.params.imageName);
        var mimetype = mime.lookup(img);

        res.setHeader('Content-disposition', 'attachment; filename=' + req.params.tagName + path.extname(img));
        res.setHeader('Content-type', mimetype);

        var filestream = fs.createReadStream(img);
        filestream.pipe(res);
        res.on('finish', function() {
            console.log("Download complete");
        });
    });
};
