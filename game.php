<?php

function lca($na, $nb)
{
	$l = array();
	while(true)
	{
		$a = array_pop($na['parents']);
		$b = array_pop($nb['parents']);
		if($a == $b)
			$l[] = $a;
		else
			break;
	}
	return $l;
}

function order($game)
{
	$ancestors = array(
		lca($game[0], $game[1]),
		lca($game[1], $game[2]),
		lca($game[0], $game[2]),
	);
	if($ancestors[0] == $ancestors[1]) return array(array(0, 2, 1), array($ancestors[0], $ancestors[1]));
	if($ancestors[1] == $ancestors[2]) return array(array(0, 1, 2), array($ancestors[1], $ancestors[2]));
	if($ancestors[0] == $ancestors[2]) return array(array(1, 2, 0), array($ancestors[0], $ancestors[2]));
	var_dump(array('game' => $game, 'ancestors' => $ancestors));
	die('Failed to determine order!');
}

function newGame()
{
	$species = json_decode(file_read_contents('species.json'));
	$game = array();
	while(count($game) < 3)
	{
		$tid = $species[rand(0, count($species))];
		$game[] = json_decode(file_read_contents('nodes/$tid.json'));
	}
	return $game;
}

if($choice = (int) $_POST)
{
	if(!is_array($_POST['ids']))  die('Missing ids array.');
	if(count($_POST['ids']) != 3) die('Wrong number of ids.');
	$game = array();
	for($_POST['ids'] as $id)
	{
		$file = 'nodes/' . intVal($id) . '.json';
		if(!file_exists($file)) die('Node not found: ' . intVal($id));
		$game[] = json_decode(file_read_contents($file));
	}
	list($order, $ancestors) = order($game);
	die(json_encode(array(
		'ancestors' => $ancestors,
		'order'     => $order,
		'correct'   => ($order[2] == $choice),
	));
}
else
{
	do
	{
		$game = newGame();
		$retry = false;
		if($game[0]['tid'] == $game[1]['tid']) $retry = true;
		if($game[1]['tid'] == $game[2]['tid']) $retry = true;
		if($game[0]['tid'] == $game[2]['tid']) $retry = true;
		if(lca($game[0], $game[1]) == lca($game[1], $game[2])) $retry = true;
	}
	while($retry);
	die(json_encode($game));
}
