angular.module('lowpolify', ['ngRoute', 'fileUpload', 'lowPolifyService', 'clarifaiInteract', 'clarifaiService', 'uploadSuccessService'])
    .config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider) {
        $locationProvider.html5Mode(true);
    }]);
