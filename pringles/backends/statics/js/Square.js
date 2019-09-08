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

/*global createjs, $, canvas */
/*exported Square*/
"use strict";

/**
 * @class Square
 * @author Laouen Mayal Louan Belloli
 *
 * @description Display a square with background color, border color and border radius.
 */

function Square(parameters) {
    /*jshint validthis:true */
    this.initialize(parameters);
}

/**
 * Initialize a new Square instance.
 *
 * @param {Object} parameters - all the requiered parameters to initialize the instance.
 * 
 */

Square.prototype = new createjs.Shape();
Square.prototype.ShapeInitialize = Square.prototype.initialize;
Square.prototype.ContainerTick = Square.prototype._tick;

Square.prototype.initialize = function(parameters) {
    
    this.ShapeInitialize();

    /*********** default values **************/
    this.strokeWidth = 1;
    this.radius = 0;
    this.strokeColor = "#000000";
    this.fillColor = "#FFFFFF";

    $.extend(true, this, parameters);

    this.check_min_values();
    this.draw_square();
};

Square.prototype.draw_square = function() {
    var i;

    this.graphics = new createjs.Graphics();
    this.graphics.setStrokeStyle(this.strokeWidth);
    this.graphics.beginStroke(this.strokeColor);
    this.graphics.beginFill(this.fillColor);
    this.graphics.drawRoundRect(0, 0, this.width, this.height, this.radius);

    this.canvas.stage.update();
};

Square.prototype.check_min_values = function() {
    this.width = Math.max(this.width, 1);
    this.height = Math.max(this.height, 1);
    this.radius = Math.max(this.radius, 0);
}