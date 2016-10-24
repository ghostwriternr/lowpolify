angular.module('uploadSuccessService', [])
    .service('UploadSuccess', function() {
        var uploadedFile = "";

        var setNewName = function(newName) {
            uploadedFile = newName;
        }

        var getNewName = function() {
            return uploadedFile;
        }

        return {
            uploadedFile: uploadedFile,
            setNewName: setNewName,
            getNewName: getNewName
        };
    });
