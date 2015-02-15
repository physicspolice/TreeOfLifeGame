var gameApp = angular.module('gameApp', []);

gameApp.controller('gameController', function($scope, $http)
{
	$scope.nodes = [];
	$scope.newGame = function()
	{
		$scope.gameStatus = 'loading';
		$http.get('game.php').success(function(response)
		{
			$scope.nodes = response;
			$scope.gameStatus = 'ready';
			console.log($scope.gameStatus, $scope.nodes);
		});
	};

	$scope.submitGame = function(coice)
	{
		$scope.gameStatus = 'posting';
		ids = [];
		for(var i in $scope.nodes)
			ids.push($scope.nodes[i].tid)
		$http.post('game.php', { 'ids': ids, 'choice': choice }).success(function(response)
		{
			var nodes = [];
			for(i in response.order)
				nodes.append($scope.nodes[response.order[i]]);
			for(i in response.ancestors)
				nodes.append(response.ancestors[i]);
			$scope.nodes = nodes; // TODO animate.
			$scope.gameStatus = response.correct ? 'won' : 'lost';
		});
	};

	$scope.newGame();
});
