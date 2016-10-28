angular.module('clarifaiService', [])
    .factory('Clarifai', ['$http', function($http) {
        return {
            authenticate: function() {
                return $http.post('/api/clarifai/getAccessToken');
            },
            getTags: function(imageName) {
                return $http.post('/api/clarifai/getTags/' + imageName);
            },
            download: function(tagName, imageName) {
                return $http.get('/api/clarifai/tagDownload/' + tagName + "/" + imageName);
            }
        }
    }]);
