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

/*global createjs, $, manifest, console */
/*exported Link*/
"use strict";

/**
 * @class Link
 * @author Laouen Mayal Louan Belloli
 * 
 * @description Displays a graphical vectorized links represented by a list of nodes in its local 
 * reference space. Each node can be dragged to a new position, and new nodes can be created by 
 * dragging a point witin the link. The new node is placed in between the two adjacents nodes of the
 * link containing the selected point.
 */

function Link(parameters) {
    /*jshint validthis:true */
    this.initialize(parameters);
}

Link.prototype = new createjs.Shape();
Link.prototype.ShapeInitialize = Link.prototype.initialize;
Link.prototype.ContainerTick = Link.prototype._tick;

Link.Kind = { IC: "IC", EIC: "EIC", EOC: "EOC" };

/**
 * Construct a new Link instance
 * @param  {Object} parameters - all the required parameters to construct a new instance.
 * @param {Port} paramters.to_port - The port connected to the link end.
 * @param {Port} paramters.from_port - The port connected to the link start.
 * @param {[Object]} parameters.nodes - the sorted list of nodes, a node is an object with attributes x and y.
 * @param {Canvas} parameters.canvas - The canvas where the link belongs to update the stage.
 * @param {Model} parameters.parent - The parent model where the link belongs.
 * @param {String} parameters.color - The link colo in RGB format.
 * @param {Number} parameters.width - The link width in pixels.
 */
Link.prototype.initialize = function(parameters) {
    
    this.ShapeInitialize();
    $.extend(true, this, parameters);

    this.scale_node_positions();

    this.holded = false;
    this.node_epsilon = manifest.link.node_epsilon;
    this.epsilon = manifest.link.epsilon;
    this.margin = manifest.link.margin;

    this.check_min_values();
    this.update();

    this.addEventListener("mousedown", this.hold.bind(this));
    this.addEventListener("pressmove", this.move.bind(this));
    this.addEventListener("pressup", this.release.bind(this));
};

Link.prototype.update = function() {

    this.graphics = new createjs.Graphics();
    this.draw_link(this.graphics, this.width);
    this.hitArea = new createjs.Shape();
    this.hitArea.graphics = new createjs.Graphics();
    this.draw_link(this.hitArea.graphics, this.width + this.margin);
    this.canvas.stage.update();
};

Link.prototype.draw_link = function(graphic, width) {
    var i;

    graphic.setStrokeStyle(width);
    graphic.beginStroke(this.color);

    graphic.moveTo(this.nodes[0].x, this.nodes[0].y);
    for (i = 1; i < this.nodes.length; ++i) {
        graphic.lineTo(this.nodes[i].x, this.nodes[i].y);
    }
};

Link.prototype.check_min_values = function() {
    this.width = Math.max(this.width, 1);
};

/**
 * Warning: it does not return the first and last nodes because they can't  be dragged.
 * @param  {Object} evt - The mouse event.
 * @return {Object}     The node under the mouse.
 */
Link.prototype.get_node = function(evt) {
    var i;

    for(i = 1; i < this.nodes.length - 1; ++i) {
        
        if (this.is_over_node(this.nodes[i], evt)) {
            return this.nodes[i];
        }
    }

    return null;
};

Link.prototype.distance = function(a, b) {
    return Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2));
};

Link.prototype.is_over_node = function (node, evt) {
    return this.distance(evt, node) < this.margin + this.node_epsilon;
};

Link.prototype.is_between = function(a, b, c) {
    var distanceByC = this.distance(a, c) + this.distance(c, b);
    return Math.abs(distanceByC - this.distance(a, b)) < this.margin + this.epsilon;
};

Link.prototype.get_new_node_index = function(node) {
    var i;

    for (i = 1; i < this.nodes.length; i++) {
        if (this.is_between(this.nodes[i - 1], this.nodes[i], node)) {
            return i;
        }
    }
};

Link.prototype.scale_node_positions = function() {
    var start_point, end_point, new_x_distance, current_x_distance;
    var new_y_distance, current_y_distance, scaleX, scaleY, i;
    var from_port, to_port;

    from_port = this.from_port;
    to_port = this.to_port;

    start_point = from_port.parent.localToLocal(from_port.x + from_port.width - from_port.regX,
                                                from_port.y - from_port.regY + from_port.height / 2,
                                                this.parent);
    end_point = to_port.parent.localToLocal(to_port.x - to_port.regX,
                                            to_port.y - to_port.regY + to_port.height / 2,
                                            this.parent);

    if (this.nodes.length > 2) {

        // If there is more nodes that just the end point, they must be scaled according to the new end points.

        current_x_distance  = Math.abs(this.nodes[0].x - this.nodes[this.nodes.length - 1].x);
        new_x_distance      = Math.abs(start_point.x - end_point.x);
        current_y_distance  = Math.abs(this.nodes[0].y - this.nodes[this.nodes.length - 1].y);
        new_y_distance      = Math.abs(start_point.y - end_point.y);
        
        scaleX = new_x_distance / current_x_distance;
        scaleY = new_y_distance / current_y_distance;

        for(i = 1; i < this.nodes.length - 1; i++) {
            this.nodes[i].x = this.nodes[i].x * scaleX;
            this.nodes[i].y = this.nodes[i].y * scaleY;
        }
    }
    
    // replace first and last nodes
    this.nodes.splice(0, 1, start_point);
    this.nodes.splice(Math.max(1, this.nodes.length - 1), 1, end_point);
};


Link.prototype.update_end_points = function() {
    var start_point, end_point, from_port, to_port;

    from_port = this.from_port;
    to_port = this.to_port;

    start_point = from_port.parent.localToLocal(from_port.x + from_port.width - from_port.regX,
                                                from_port.y - from_port.regY + from_port.height / 2,
                                                this.parent);
    end_point = to_port.parent.localToLocal(to_port.x - to_port.regX,
                                            to_port.y - to_port.regY + to_port.height / 2,
                                            this.parent);
    // replace first and last nodes
    this.nodes.splice(0, 1, start_point);
    this.nodes.splice(Math.max(1, this.nodes.length - 1), 1, end_point);
    
    this.update();
};

/********* Drag & drop ******************/

Link.prototype.hold = function(evt) {
    var local_position, node;
    evt.stopImmediatePropagation();

    if (!this.holded) {
        this.parent.dragged_child = true;
        this.holded = true;

        local_position = this.globalToLocal(evt.stageX, evt.stageY);
        node = this.get_node(local_position);
        
        if (node !== null) {
            this.holded_node = node;
        } else {
            this.create_node(local_position);
        }
    }
};

Link.prototype.move = function(evt) {
    evt.stopImmediatePropagation();
    evt.stopPropagation();

    if (this.holded) {
        this.update_position(evt);
    }
};

Link.prototype.release = function(evt) {
    evt.stopImmediatePropagation();
    evt.stopPropagation();

    console.log("Object: link - release");
    if(this.holded) {
        this.parent.dragged_child = false;
        this.holded = false;
        this.merge_nodes();
        this.update_position(evt);
        this.parent.jsonGraphics.update_link_nodes(this.kind, this.information, this.nodes);
    }
};

Link.prototype.update_position = function(evt) {
    var local_position = this.globalToLocal(evt.stageX, evt.stageY);
    this.holded_node.x = local_position.x;
    this.holded_node.y = local_position.y;
    this.update();
};

Link.prototype.merge_nodes = function() {
    var i = 1;
    while (i < this.nodes.length) {
        if (this.distance(this.nodes[i - 1], this.nodes[i]) < this.node_epsilon + this.margin) {
            this.nodes.splice(i, 1);
        } else {
            i++;
        }
    }
};

Link.prototype.create_node = function(local_position) {
    var index;

    this.holded_node = local_position;
    index = this.get_new_node_index(this.holded_node);
    this.nodes.splice(index, 0, this.holded_node);

    this.parent.jsonGraphics.add_node_to_link(this.kind, this.information, this.holded_node, index);
};