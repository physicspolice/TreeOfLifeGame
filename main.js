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
			for(var i in $scope.nodes)
			{
				$scope.nodes[i].nameIndex  = 0;
				$scope.nodes[i].imageIndex = 0;
				if($scope.nodes[i].names.length > 1)
				{
					// TODO animate.
				}
				if($scope.nodes[i].images.length > 1)
				{
					// TODO animate.
				}
			}
			$scope.gameStatus = 'ready';
		});
	};

	$scope.submitGame = function(choice)
	{
		$scope.gameStatus = 'posting';
		ids = [];
		for(var i in $scope.nodes)
			ids.push($scope.nodes[i].tid)
		$http.post('game.php', { 'ids': ids, 'choice': choice }).success(function(response)
		{
			var nodes = [];
			for(i in response.order)
				nodes.push($scope.nodes[response.order[i]]);
			for(i in response.ancestors)
			{
				response.ancestors[i].nameIndex  = 0;
				response.ancestors[i].imageIndex = 0;
				nodes.push(response.ancestors[i]);
			}
			$scope.nodes = nodes; // TODO animate.
			$scope.gameStatus = response.correct ? 'won' : 'lost';
		});
	};

	$scope.newGame();
});
