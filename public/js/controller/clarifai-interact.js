angular.module('clarifaiInteract', [])
    .controller('clarifaiController', ['$scope', '$http', '$window', 'Clarifai', 'UploadSuccess', function($scope, $http, $window, Clarifai, UploadSuccess) {
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
                    if ($scope.clarifaiResponse.status_code == "TOKEN_EXPIRED" || $scope.clarifaiResponse.status_code == "INVALID_TOKEN") {
                        Clarifai.authenticate()
                            .success(function(newToken) {
                                Clarifai.getTags(file)
                                    .success(function(newData) {
                                        $scope.imageTags = newData.results[0].result.tag.classes.slice(0, 10);
                                    });
                            });
                    } else
                        $scope.imageTags = $scope.clarifaiResponse.results[0].result.tag.classes.slice(0, 10);
                });
        };

        $scope.download = function(tagName) {
            tagName = tagName.replace(/\W+/g, '-');
            path = "/api/clarifai/tagDownload/" + tagName + "/" + UploadSuccess.uploadedFile;
            $window.location.href = path;
        }
    }]);
