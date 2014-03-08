'use strict';

/* Controllers */


var sensorinoApp = angular.module('sensorinoApp', ['restangular', 'ngRoute' ]);
//var sensorinoApp = angular.module('sensorinoApp', []);

sensorinoApp.config(['$httpProvider', function($httpProvider) {
        $httpProvider.defaults.useXDomain = true;
        delete $httpProvider.defaults.headers.common['X-Requested-With'];
    }
]);

sensorinoApp.config(['$routeProvider', function($routeProvider) {
        $routeProvider.
        when('/sensorinos', {
            templateUrl: 'partials/listSensorinos.html',
            controller: 'MainCtrl'
        }).
        when('/graphs', {
            templateUrl: 'partials/graphs.html',
            controller: 'GraphsCtrl'
        }).
        when('/sensorino/:sId', {
            templateUrl: 'partials/sensorinoDetails.html',
            controller: 'SensorinoDetailsCtrl'
        }).
        when('/sensorino/:sId/dataServices/:serviceId', {
            templateUrl: 'partials/serviceDataLog.html',
            controller: 'ServiceDataLogCtrl'
        }).
        otherwise({
            redirectTo: '/sensorinos'
        });
}]);



sensorinoApp.controller('MainCtrl', function($scope, Restangular) {
		Restangular.setBaseUrl("http://127.0.0.1:5001")
		var Rsensorinos =  Restangular.all('sensorinos');

        $scope.showForm=false;
        $scope.activateForm = function(){
            $scope.showForm=true;
        }

        $scope.loadSensorinos=function(){
            Rsensorinos.getList().then(function(sensorinos){
			    $scope.sensorinos=sensorinos;
            });
		}

        $scope.loadSensorinos();			

		$scope.deleteSensorino = function(sid){
			console.log("delete sid");
			console.log(sid);
            Restangular.one('sensorinos', sid).remove().then(function(){
                 $scope.loadSensorinos();
            });
		}

		$scope.createSensorino = function(mySensorino){
			console.log("create one then clean");
			Rsensorinos.post(mySensorino).then(function(){
                $scope.reset();
                $scope.loadSensorinos();
            });
		}


		$scope.reset = function(){ 
			console.log("clear stuff");
            $scope.showForm=false;
		}

});

sensorinoApp.controller('SensorinoDetailsCtrl', function($scope, $location, $routeParams, Restangular) {

        $scope.showForm=false;
        $scope.activateForm = function(){
            $scope.showForm=true;
        }

        Restangular.setBaseUrl("http://127.0.0.1:5001")
        var Rsensorino =   Restangular.all('sensorinos');
        Rsensorino.get($routeParams.sId).then( function(sensorino){
            $scope.sensorino=sensorino;
        });

        var RServices=Restangular.all("sensorinos/"+$routeParams.sId+"/dataServices");
        $scope.loadServices=function(){
            RServices.getList().then(function(services){
                $scope.services=services;
            });
        }

        $scope.createService = function(newService){
            console.log("createService:");
            console.log(newService);
            RServices.post(newService).then($scope.loadServices());
        }

        $scope.deleteService = function(serviceId){
            console.log("delete service :");
            console.log(serviceId);
            var RService=Restangular.one("sensorinos/"+$routeParams.sId+"/dataServices/"+serviceId);
            RService.remove().then($scope.loadServices());
        }

        $scope.move=function(newPath){
            console.log("move to "+newPath)
            $location.path(newPath);
        }

        $scope.loadServices();

});


sensorinoApp.controller('ServiceDataLogCtrl',  function($scope, $routeParams, Restangular) {

    Restangular.setBaseUrl("http://127.0.0.1:5001")
    var RServicesData=Restangular.all("sensorinos/"+$routeParams.sId+"/dataServices/"+$routeParams.serviceId+"/data");
    $scope.loadData=function(){
        RServicesData.getList().then(function(logs){
            $scope.logs=logs;
        });
    }
    $scope.loadData()
  
 
    var RService=Restangular.one("sensorinos/"+$routeParams.sId+"/dataServices/"+$routeParams.serviceId);
    $scope.loadService=function(){
        RService.get().then(function(service){
            $scope.service=service;
        });
    }
    $scope.loadService();

});


