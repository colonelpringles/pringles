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

/*global createjs, $, Square, manifest, options */
/*exported Port */
"use strict";

/**
 * @class Port
 * @author Laouen Mayal Louan Belloli
 *
 * @description Displays a model port with the port name and message type.
 */

function Port(parameters) {
	this.initialize(parameters);
}

Port.out = "out";
Port.in = "in";

Port.prototype = new createjs.Container();
Port.prototype.ContainerInitialize = Port.prototype.initialize;
Port.prototype.ContainerTick = Port.prototype._tick;

/**
 * Constructs a new Port instance.
 *
 * @param {Object} parameters - All the required parameters to the instance initialization.
 * @param {Canvas} parameters.canvas - The canvas where it belongs to update the stage.
 * @param {String} parameters.fillColor - The port background color in RGB format.
 * @param {Number} parameters.height - The port height in pixels.
 * @param {String} parameters.id - The port id.
 * @param {String} parameters.message_type - The name of the port message type.
 * @param {String} parameters.font_size - The font size of the port name and message type. 
 */

Port.prototype.initialize = function(parameters) {
    this.ContainerInitialize();

    this.text_color = manifest.port.text_color;
    this.font_size = manifest.font_size;
    
    $.extend(true,this,parameters);

    this.width = this.height * manifest.port.ratio;

    this.regX = this.width / 2;
    this.regY = this.height / 2;

    this.update_box();
    this.update_name();

    if (options.show_message_type) {
        this.draw_message_type();
    }

    this.canvas.stage.update();
};

Port.prototype.update_box = function() {
    if (this.port_box !== undefined) {
        this.removeChild(this.port_box);
    }    

    this.port_box = new Square({
        canvas: this.canvas,
        fillColor: manifest.port["background-color"],
        width: this.width,
        height: this.height
    });
    this.addChild(this.port_box);
    this.canvas.stage.update();
};

Port.prototype.update_colors = function() {
    this.update_box();
    this.update_name();
};

Port.prototype.update_name = function() {
    if (this.port_name !== undefined) {
        this.removeChild(this.port_name);
    }

    var text_style = this.font_size.toString() + "px Arial";
    this.port_name = new createjs.Text(this.id, text_style, manifest.port["color"]);
    this.port_name.textBaseline = "top";

    this.port_name.y = 2;
    this.port_name.x = this.width / 2;
    this.port_name.regX = this.port_name.getBounds().width / 2;
    
    this.addChild(this.port_name);
    
    if (!options.show_port_name) {
        this.port_name.visible = true;
    }

    this.canvas.stage.update();
};

Port.prototype.draw_message_type = function() {

    var text_style = this.font_size.toString() + "px Arial";
    this.port_message_type = new createjs.Text(this.message_type, text_style, this.text_color);
    this.port_message_type.textBaseline = "bottom";

    this.port_message_type.y = this.height - 2;
    this.port_message_type.x = this.width / 2;
    this.port_message_type.regX = this.port_message_type.getBounds().width / 2;


    this.addChild(this.port_message_type);
};

Port.prototype.toggle_name = function() {
    this.port_name.visible = !this.port_name.visible;
    this.canvas.stage.update();
};

Port.prototype.hide_name = function() {
    this.port_name.visible = false;
    this.canvas.stage.update();
};

Port.prototype.show_name = function() {
    this.port_name.visible = true;
    this.canvas.stage.update();
};