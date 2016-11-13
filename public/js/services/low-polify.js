angular.module('lowPolifyService', [])
    .factory('Lowpolify', ['$http', function($http) {
        return {
            makeLowPoly: function(inImage, cFraction) {
                return $http.post('/api/makeLowPoly/' + inImage + '/' + cFraction);
            },
            getLowPoly: function(inImage) {
                return $http.get('/api/getLowPoly/' + inImage);
            }
        }
    }])
