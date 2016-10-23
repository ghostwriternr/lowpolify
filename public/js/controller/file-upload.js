angular.module('fileUpload', ['ngFileUpload'])
    .controller('uploadController', ['$scope', 'Upload', '$timeout', function($scope, Upload, $timeout) {
        $scope.$watch('file', function() {
            $scope.upload($scope.file);
        });

        $scope.upload = function(file, errFiles) {
            $scope.f = file;
            $scope.errFile = errFiles && errFiles[0];
            if (file) {
                Upload.upload({
                    url: '/api/upload',
                    method: 'POST',
                    arrayKey: '',
                    data: { file: file }
                }).then(function(response) {
                    if (response.data.error_code === 0) {
                        console.log(response);
                        console.log('Success! ' + response.config.data.file.name + ' uploaded. Response: ');
                    } else {
                        console.log(response.data.err_desc);
                    }
                }, function(response) {
                    console.log('Error status: ' + response.status);
                }, function(evt) {
                    file.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
                });
            }
        };
    }]);
