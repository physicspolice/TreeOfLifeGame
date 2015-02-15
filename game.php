<?php

function lca($na, $nb)
{
	$l = array();
	while(true)
	{
		$a = array_pop($na['parents']);
		$b = array_pop($nb['parents']);
		if($a && $b && ($a == $b))
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
	if($ancestors[0] == $ancestors[1]) return array(array(0, 2, 1), array(end($ancestors[0]), end($ancestors[2])));
	if($ancestors[1] == $ancestors[2]) return array(array(0, 1, 2), array(end($ancestors[1]), end($ancestors[0])));
	if($ancestors[0] == $ancestors[2]) return array(array(1, 2, 0), array(end($ancestors[0]), end($ancestors[1])));
	var_dump(array('game' => $game, 'ancestors' => $ancestors));
	die('Failed to determine order!');
}

function newGame()
{
	$species = json_decode(file_get_contents('species.json'), true);
	$nodes = array();
	while(count($nodes) < 3)
	{
		$tid = $species[rand(0, count($species))];
		$node = json_decode(file_get_contents("nodes/$tid.json"), true);
		$nodes[] = $node;
	}
	return $nodes;
}

if($_SERVER['REQUEST_METHOD'] == 'POST')
{
	$post = json_decode(file_get_contents('php://input'), true);
	$choice = (int) $post['choice'];
	if(!is_array($post['ids']))  die('Missing ids array.');
	if(count($post['ids']) != 3) die('Wrong number of ids.');
	$game = array();
	foreach($post['ids'] as $id)
	{
		$file = 'nodes/' . intVal($id) . '.json';
		if(!file_exists($file)) die('Node not found: ' . intVal($id));
		$game[] = json_decode(file_get_contents($file), true);
	}
	list($order, $ids) = order($game);
	$ancestors = array();
	foreach($ids as $id)
	{
		$node = json_decode(file_get_contents("nodes/$id.json"), true);
		unset($node['leaf'], $node['parents']);
		$ancestors[] = $node;
	}
	die(json_encode(array(
		'ancestors' => $ancestors,
		'order'     => $order,
		'correct'   => ($order[2] == $choice),
	)));
}
else
{
	do
	{
		$nodes = newGame();
		$retry = false;
		if($nodes[0]['tid'] == $nodes[1]['tid']) $retry = true;
		if($nodes[1]['tid'] == $nodes[2]['tid']) $retry = true;
		if($nodes[0]['tid'] == $nodes[2]['tid']) $retry = true;
		if(lca($nodes[0], $nodes[1]) == lca($nodes[1], $nodes[2])) $retry = true;
	}
	while($retry);
	foreach($nodes as &$node)
		unset($node['leaf'], $node['parents']);
	die(json_encode($nodes));
}
