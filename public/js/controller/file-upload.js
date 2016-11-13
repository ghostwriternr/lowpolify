angular.module('fileUpload', ['ngFileUpload', 'rzModule'])
    .controller('uploadController', ['$scope', 'Upload', 'Lowpolify', 'UploadSuccess', '$timeout', function($scope, Upload, Lowpolify, UploadSuccess, $timeout) {
        var newName = '';

        $scope.$watch('file', function() {
            $scope.upload($scope.file);
        });

        $scope.slider = {
            value: 15,
            options: {
                floor: 0,
                ceil: 100,
                id: 'slider-id',
                showSelectionBar: true,
                disabled: false,
                getSelectionBarColor: function() {
                    return 'orange';
                },
                getPointerColor: function() {
                    return 'pink'
                },
                onStart: function(id) {
                    console.log('Slider start');
                },
                onChange: function(id) {
                    console.log('Slider change');
                },
                onEnd: function(id, value) {
                    console.log('Slider end');
                    console.log(value * 0.01);
                    Lowpolify.makeLowPoly(newName, value * 0.01)
                        .success(function(data) {
                            Lowpolify.getLowPoly(newName)
                                .success(function(data) {
                                    $scope.outputFilePath = data;
                                });
                        });
                }
            }
        };

        $scope.upload = function(file, errFiles) {
            $scope.f = file;
            $scope.errFile = errFiles && errFiles[0];
            if (file) {
                newName = file.name.substr(0, file.name.indexOf('.')) + '-' + Date.now() + '.' + file.name.split('.')[file.name.split('.').length - 1];
                Upload.rename(file, newName);
                Upload.upload({
                    url: '/api/upload',
                    method: 'POST',
                    arrayKey: '',
                    data: { file: file }
                }).then(function(response) {
                    if (response.data.error_code === 0) {
                        console.log('Success! ' + response.config.data.file.name + ' uploaded.');
                        UploadSuccess.uploadedFile = newName;
                        Lowpolify.makeLowPoly(newName, 0.15)
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
