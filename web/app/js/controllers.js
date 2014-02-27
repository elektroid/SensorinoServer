'use strict';

/* Controllers */


var sensorinoApp = angular.module('sensorinoApp', ['restangular']);
//var sensorinoApp = angular.module('sensorinoApp', []);

sensorinoApp.config(['$httpProvider', function($httpProvider) {
        $httpProvider.defaults.useXDomain = true;
        delete $httpProvider.defaults.headers.common['X-Requested-With'];
    }
]);

sensorinoApp.controller('MainCtrl', function($scope, Restangular) {
		Restangular.setBaseUrl("http://127.0.0.1:5000")
		var sensorinos =  Restangular.all('sensorinos');
		var sensorino =   Restangular.all('sensorino');

		sensorinos.getList().then(function(sensorinos){
			$scope.sensorinos=sensorinos;
		});
	

		$scope.deleteSensorino = function(sid){
			console.log("delete sid");
			console.log(sid);
		}

		$scope.createSensorino = function(sname, description, loc){
			console.log("create one");
			var mySensorino = {
				name: sname,
				location: loc,
				description: description
			};
			sensorino.post(mySensorino);
		}	

		$scope.reset = function(){ 
			console.log("clear stuff");
		}


	});




