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
                    console.log($scope.clarifaiResponse);
                    // This if block shouldn't be needed for Clarifai API v2.
                    // TODO: Verify the above statement with corner cases.
                    if ($scope.clarifaiResponse.status.code == "TOKEN_EXPIRED" || $scope.clarifaiResponse.status.code == "TOKEN_INVALID" || $scope.clarifaiResponse.status_code == "TOKEN_APP_INVALID") {
                        Clarifai.authenticate()
                            .success(function(newToken) {
                                Clarifai.getTags(file)
                                    .success(function(newData) {
                                        $scope.imageTags = newData.outputs[0].data.concepts.slice(0, 10);
                                    });
                            });
                    } else
                        $scope.imageTags = $scope.clarifaiResponse.outputs[0].data.concepts.slice(0, 10);
                });
        };

        $scope.download = function(tagName) {
            tagName = tagName.replace(/\W+/g, '-');
            path = "/api/clarifai/tagDownload/" + tagName + "/" + UploadSuccess.uploadedFile;
            $window.location.href = path;
        }
    }]);
