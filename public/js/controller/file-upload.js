angular.module('fileUpload', ['ngFileUpload'])
    .controller('uploadController', ['$scope', 'Upload', 'Lowpolify', '$timeout', function($scope, Upload, Lowpolify, $timeout) {
        $scope.$watch('file', function() {
            $scope.upload($scope.file);
        });

        $scope.upload = function(file, errFiles) {
            $scope.f = file;
            $scope.errFile = errFiles && errFiles[0];
            if (file) {
                var newName = file.name.substr(0, file.name.indexOf('.')) + '-' + Date.now() + '.' + file.name.split('.')[file.name.split('.').length - 1];
                Upload.rename(file, newName);
                Upload.upload({
                    url: '/api/upload',
                    method: 'POST',
                    arrayKey: '',
                    data: { file: file }
                }).then(function(response) {
                    if (response.data.error_code === 0) {
                        console.log('Success! ' + response.config.data.file.name + ' uploaded.');
                        Lowpolify.makeLowPoly(newName)
                            .success(function(data) {
                                Lowpolify.getLowPoly(newName)
                                    .success(function(data) {
                                        $scope.outputFilePath = data;
                                    });
                            });
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
