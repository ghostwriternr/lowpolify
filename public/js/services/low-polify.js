angular.module('lowPolifyService', [])
	.factory('Lowpolify', ['$http', function($http){
		return {
			makeLowPoly: function(inImage){
				return $http.post('/api/makeLowPoly/' + inImage);
			},
			getLowPoly: function(inImage){
				return $http.get('/api/getLowPoly/' + inImage);
			}
		}
	}])