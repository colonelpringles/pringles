/**
 * BSD 2-Clause License
 *
 * Copyright (c) 2017, Laouen Mayal Louan Belloli
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * * Redistributions of source code must retain the above copyright notice, this
 *   list of conditions and the following disclaimer.
 * 
 * * Redistributions in binary form must reproduce the above copyright notice,
 *   this list of conditions and the following disclaimer in the documentation
 *   and/or other materials provided with the distribution.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 */

/*global options */
/*exported relaxed_khan, sort_ports */
"use strict";

/**
 * Sorts a graph in topologically, if this is not posible due to cycles, the 
 * sort is made minimizing the amount of egdes violating the topological rule.
 * 
 * @param  {model: string, neigghbors: [string]} graph - A graph represented as adjacency lists where model is the node.
 * @return {[model]} A list of the models (nodes) sorted
 */
function relaxed_khan(graph) {
	var L, n;

	graph = copy(graph); // in order to not modify the original grap
	L = [];
	while (graph.length > 0) {
		graph.sort(degree_comparator.bind(degree_comparator, copy(graph)));
		n = graph.splice(0,1)[0];
		L.push(n);
	}

	L = separate_in_columns(L);
	if (options.compress_in_left) L = compress_columns_in_left(L);

	return extract_models_by_column(L);
}

function degree_comparator(graph, a, b) {
	return in_degree(graph, a) - in_degree(graph, b); 
}

function copy(graph) {
	var copied = [];
	for (var i = 0; i < graph.length; i++) { copied.push(graph[i]); }
	return copied; 
}

function in_degree(graph, node) {
	var degree, i, j, neighbors;

	degree = 0;
	for (i = 0; i < graph.length; i++) {
		neighbors = graph[i].neighbors;
		for (j = 0; j < neighbors.length; j++) {
			if (neighbors[j] === node.model) {
				degree++;
			}
		}
	}
	return degree;
}

function separate_in_columns(sorted_graph) {
	var i, res, neighbors, node;

	res = [[sorted_graph[0]]];
	neighbors = sorted_graph[0].neighbors;

	for(i = 1; i < sorted_graph.length; i++) {
		
		node = sorted_graph[i];
		if(neighbors.indexOf(node.model) === -1) { // if is no neighbor it can be placed in the same column
			neighbors = neighbors.concat(node.neighbors);
			res[res.length - 1].push(node);
		} else { // if is a neighbor, a new column must start
			res.push([node]);
			neighbors = node.neighbors;
		}
	}

	return res;
}

function compress_columns_in_left(nodesByColumns) {
	var i, n, node, column, new_location, neighbors;
	for(i = 1; i < nodesByColumns.length; i++) {
		column = nodesByColumns[i];

		for(n = 0; n < column.length; n++) {
			node = column[n];
			new_location = i;
			neighbors = get_neighbors(nodesByColumns[new_location - 1]);
			while (new_location > 0 && neighbors.indexOf(node.model) === -1) {
				new_location--;
				if (new_location > 0) {
					neighbors = get_neighbors(nodesByColumns[new_location - 1]);
				}
			}

			if (new_location < i) {
				nodesByColumns[i].splice(n, 1);
				nodesByColumns[new_location].push(node);
			}
		}
	}
	return nodesByColumns;
}

function get_neighbors(column) {
	return column.reduce(function(neighbors, node) {
	  return neighbors.concat(node.neighbors);
	}, []);
}

function extract_models_by_column(L) {
	return L.map(function(column) { 
		return column.map(function(node) { 
			return node.model;
		});
	});
}

function sort_ports(ports) {
	
	if (options.sort_ports_by_name) {
		return ports.sort(function(a, b) { 
			if (a.name < b.name) return -1;
			if (a.name > b.name) return 1;
			return 0;
		});
	}

	else return ports;
}