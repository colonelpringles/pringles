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

/*global $, createjs, Model, JSONModelGraphics, manifest, Square */
/*export Canvas */
"use strict";

var canvas_id = 0;

/**
 * @class Canvas
 * @author Laouen Mayal Louan Belloli
 *
 * @description Represent a canvas where a Model is displayed.
 * It creates the DOM canvas, append it to the html body and initialize a new createjs.Stage
 * and subStage container.
 */

function Canvas(parameters) {
	this.initialize(parameters);
}

Canvas.prototype.initialize = function(parameters) {
    var graphics, structure, jsonGraphics;

    this.id = "stage_canvas_" + canvas_id.toString();
    this.canvas_id++;
    
    // 'Width':'90%','Height':'800'
    this.dom_canvas = $('<canvas/>',{'id': this.id });
    $('#' + parameters.diagrammer_id + ' #models-wrapper').append(this.dom_canvas);
    this.dom_canvas.attr('width', this.dom_canvas.width());
    this.dom_canvas.attr('height', this.dom_canvas.height());

    this.stage = new createjs.Stage(this.dom_canvas.get(0));
    this.subStage = new createjs.Container();
    this.stage.addChild(this.subStage);

    this.stageWidth  = this.dom_canvas.width();
    this.stageHeight = this.dom_canvas.height();

    this.background = new Square({
        strokeWidth: 0,
        radius: 0,
        width: this.stageWidth,
        height: this.stageHeight,
        strokeColor: manifest.subStage.strokeColor,
        fillColor: manifest.subStage.fillColor,
        canvas: this
    });

    if (parameters.json_input !== undefined && parameters.json_input !== null) {
        structure = parameters.json_input;
        graphics = structure.graphics || {};
        delete structure.graphics;
        jsonGraphics = new JSONModelGraphics({
            id: structure.id,
            json: graphics
        });
    } else {
        structure = parameters.structure;
        jsonGraphics = parameters.jsonGraphics;
    }
    
    this.top_model = new Model({
        is_top: true,
        canvas: this,
        structure: structure,
        jsonGraphics: jsonGraphics
    });

    this.subStage.addChild(this.background);
    this.subStage.addChild(this.top_model);

    this.selectiveFTPStageUpdate(manifest.canvas.fps);

    // responsive canvas resize.
    var wr = window.onresize;
    var us = this.updateScales.bind(this);
    window.onresize = function () { 
        if (typeof wr === "function") wr(); 
        us();
    };
    window.onresize();

    this.stage.update();
};

/******************* selective stage update methods *******************************/

/**
 * If there are some stage graphic changes declared, update the stage graphics.
 * 
 */
Canvas.prototype.updateStage = function () {

  if (this.stageHasChanged) {
    this.stage.updateStage();
    this.stageHasChanged = false;
    //console.log("update stage");
  }
};

/**
 * Declare a new stage graphic change.
 *
 */
Canvas.prototype.declareNewStageChange = function () {
  
  this.stageHasChanged = true;
  //console.log("new change");
};

/**
 * Set the Ticker to check in each interval if there are graphic changes. If there are graphical chages, the stage is updated, if not no.
 * This solution is between updating the screen in each interval of time and in each stage change. While no chages are made, the stage is not updated
 * when change arrives, the stage is updated until a maximum of one chage per interval, if to changes are triggered in the same interval, their modifications
 * will be visible at the same time at the end of the interval.
 *
 * @param {Number} fps - Defines the interval in Frame Per Seconds.
 */
Canvas.prototype.selectiveFTPStageUpdate = function (fps) {

  if (!this.selectiveFTPEnabled) { 
    this.stage.updateStage = this.stage.update.bind(this.stage);
    this.stage.update = this.declareNewStageChange.bind(this);

    this.stageHasChanged = false;
    createjs.Ticker.setFPS(fps);
    createjs.Ticker.addEventListener("tick", this.updateStage.bind(this));
    this.selectiveFTPEnabled = true;
  } else {
    createjs.Ticker.setFPS(fps);
  }
};

Canvas.prototype.updateScales = function() {

    this.dom_canvas.attr('width', this.dom_canvas.width());
    this.dom_canvas.attr('height', this.dom_canvas.height());
    this.stageWidth  = this.dom_canvas.width();
    this.stageHeight = this.dom_canvas.height();

    this.top_model.update_scale();

    this.stage.update();
};