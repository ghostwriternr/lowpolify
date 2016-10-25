angular.module('clarifaiInteract', [])
    .controller('clarifaiController', ['$scope', '$http', 'Clarifai', 'UploadSuccess', function($scope, $http, Clarifai, UploadSuccess) {
        $scope.newName = UploadSuccess.uploadedFile;

        $scope.$watch(
            function() {
                return UploadSuccess.uploadedFile;
            },

            function(newVal) {
                $scope.newName = newVal;
                if ($scope.newName.length > 0)
                    $scope.getTags($scope.newName);
            }
        );

        $scope.getTags = function(file) {
            console.log("Calling getTags for " + file);
            Clarifai.getTags(file)
                .success(function(data) {
                    $scope.clarifaiResponse = data;
                    if (clarifaiResponse.status_code == "TOKEN_EXPIRED" || clarifaiResponse.status_code == "INVALID_TOKEN") {
                        Clarifai.authenticate()
                            .success(function(newToken) {
                                Clarifai.getTags(file)
                                    .success(function(data) {
                                        $scope.imageTags = data.slice(0, 10);
                                    })
                            })
                    } else
                        $scope.imageTags = data.slice(0, 10);
                });
        };
    }]);
