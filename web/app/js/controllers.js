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
        otherwise({
            redirectTo: '/sensorinos'
        });
}]);



sensorinoApp.controller('MainCtrl', function($scope, Restangular) {
		Restangular.setBaseUrl("http://127.0.0.1:5000")
		var Rsensorinos =  Restangular.all('sensorinos');
		var Rsensorino =   Restangular.all('sensorino');

		Rsensorinos.getList().then(function(sensorinos){
			$scope.sensorinos=sensorinos;
		});
	

		$scope.deleteSensorino = function(sid){
			console.log("delete sid");
			console.log(sid);
		}

		$scope.createSensorino = function(mySensorino){
			console.log("create one");
			Rsensorinos.post(mySensorino);
		}	

		$scope.reset = function(){ 
			console.log("clear stuff");
		}

	});

sensorinoApp.controller('SensorinoDetailsCtrl', function($scope, $routeParams, Restangular) {
        Restangular.setBaseUrl("http://127.0.0.1:5000/sensorino")
        var Rsensorino =   Restangular.all('');
        Rsensorino.get($routeParams.sId).then( function(sensorino){
            $scope.sensorino=sensorino;
        });
    });


