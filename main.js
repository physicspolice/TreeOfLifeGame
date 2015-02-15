var gameApp = angular.module('gameApp', []);

gameApp.controller('gameCtrl', function($scope, $http) {
	$http.get('species.json').success(function(response) {
		$scope.species = response;
	});
	$scope.newGame = function() {
		$scope.game = [0, 0, 0];
		for(var i in $scope.game) {
			var tid = Math.floor((Math.random() * $scope.species) + 1);
			$http.get('nodes/' + tid + '.json').success(function(response) {
				$scope.game[i] = response;
				$scope.game[i].tid = tid;
			});
		}
		// TODO find both common ancestors
		var tryAgain = false;
		if($scope.game[0].tid == $scope.game[1].tid) tryAgain = true;
		if($scope.game[1].tid == $scope.game[2].tid) tryAgain = true;
		if($scope.game[0].tid == $scope.game[2].tid) tryAgain = true;
		if($scope.game[3].tid == $scope.game[4].tid) tryAgain = true;
		if(tryAgain) $scope.newGame();
	};
	$scope.submitGame = function() {
		// TODO
	};
	$scope.newGame();
}

function submitGame() {
	
}
