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

/*global console, createjs, $, Square, Port, Link, relaxed_khan, selected_models,
         manifest, options, sort_ports, JSONModelGraphics, calculate_selected_color */
/*exported Model */

"use strict";
function Model(parameters) {
    /*jshint validthis:true */
    this.initialize(parameters);
}

/**
 * @class Model
 * @author Laouen Mayal Louan Belloli
 *
 * @description Represents and displays an entire model and its internal structure, EIC, IC, EOC,
 * ports, submodels (each submodel is a Model class). 
 */

Model.prototype = new createjs.Container();
Model.prototype.ContainerInitialize = Model.prototype.initialize;
Model.prototype.ContainerTick = Model.prototype._tick;


/**
 * Constructs a new Model instance 
 * @param {Object} parameters - All the required parameters to initialize the instance.
 * @param {Boolean} parameters.is_top - indicates whether the models is TOP or submodel.
 * @param {Canvas} parameters.canvas - The canvas where the model belongs to update the stage.
 * @param {JSON} parameters.structure - The model JSON structure.
 */
Model.prototype.initialize = function(parameters) {
    this.ContainerInitialize();


    /********* logical components **********/
    this.is_top = false;
    this.shows_port_names = options.show_port_name;
    this.structure = $.extend(true, {}, Model.empty_structure);

    /******* graphical default components **********/
    this.ports = {in: [], out: []};
    this.models = [];
    this.ic = [];
    this.eoc = [];
    this.eic = [];

    /************ status values *************/
    this.is_expanded = false;
    this.showing_links = true;
    this.dragged_child = false;
    this.selected = false;

    /********** Default values **************/
    this.textColor = "#000000";
    this.radius_percentage = 0.05;

    /********* custom values ****************/
    $.extend(true, this, parameters);
    this.id = this.structure.id;
    

    /********** logical model ***************/

    if (parameters.jsonGraphics !== undefined) {
        // this is to mantain the aliasing broken by the $.extend() method
        this.jsonGraphics = parameters.jsonGraphics;
    } else if (this.is_top) {
        // only top model can creates a new JSONModelGraphics if it isn't there.
        this.jsonGraphics = new JSONModelGraphics({ id: this.id });
    } else {
        console.error("[Model] initialize: model is not top and there is no specified JSONModelGraphics.");
    }

    /*********** graphical custom components ***********/
    if (this.is_top) {
        
        this.x = this.canvas.stageWidth / 2;
        this.y = this.canvas.stageHeight / 2;
        this.width = this.canvas.stageWidth * 0.85;
        this.height = this.canvas.stageHeight * 0.85;
        this.regX = this.width / 2;
        this.regY = this.height / 2;

    } else {
        
        this.x = this.jsonGraphics.json.model_box.x;
        this.y = this.jsonGraphics.json.model_box.y;
        this.width = this.jsonGraphics.json.model_box.width;
        this.height = this.jsonGraphics.json.model_box.height;
        this.regX = this.jsonGraphics.json.model_box.regX;
        this.regY = this.jsonGraphics.json.model_box.regY;
    }
    
    if (this.parent_dimentions !== undefined) {
        this.rescale_dimentions(this.parent_dimentions);
    }

    this.jsonGraphics.update_model_box({
        x: this.x, 
        y: this.y, 
        width: this.width,
        height: this.height,
        regX: this.regX,
        regY:this.regY,
        parent_dimentions: $.extend(true, {}, this.parent_dimentions) // for future rescaling reference
    });

    this.draw_coupled();

    if (this.is_top) this.toggle_models();

    this.addEventListener("click", this.toggle_selection.bind(this));
    this.addEventListener("mousedown", this.hold.bind(this));
    this.addEventListener("pressmove", this.move.bind(this));
    this.addEventListener("pressup", this.release.bind(this));
};

Model.type = {atomic: "atomic", coupled: "coupled"};

Model.empty_structure = {
    type: "atomic", // by default asumes it's an empty atomic model
    models: [],
    ic: [],
    ports: {in: [], out: []},
    eoc: [],
    eic: [],
};

Model.prototype.draw_coupled = function() {
    
    if (this.structure.type === "coupled") {
        this["background-color"] = manifest.coupled['background-color'];
    } else {
        this["background-color"] = manifest.atomic["background-color"];
    }

    this.update_box(this["background-color"]);
    this.update_name();
    this.update_ports();
    this.update_models();
    this.update_links();
    
    this.canvas.stage.update();
};

Model.prototype.update_name = function() {
    if (this.name !== undefined) {
        this.removeChild(this.name);
    }

    var color;
    if (this.structure.type == Model.type.atomic) color = manifest.atomic.color;
    else color = manifest.coupled.color;
    
    var text_style = "24px Arial";
    this.name = new createjs.Text(this.id, text_style, color);
    this.name.textBaseline = "top";
    this.name.y = 2;
    this.name.x = this.width / 2;
    
    var bounds = this.name.getBounds();
    this.name.regX = bounds.width / 2;

    this.name.scaleX = (this.width * 0.7) / bounds.width;
    this.name.scaleY = (this.height * 0.1) / bounds.height;

    this.name.scaleX = this.name.scaleY = Math.min(this.name.scaleX, this.name.scaleY);

    this.addChild(this.name);

    this.canvas.stage.update();
};

Model.prototype.update_ports = function() {
    
    this.clean(this.ports.in);
    this.clean(this.ports.out);

    this.add_ports(this.structure.ports.in, this.ports.in, 0, Port.in);
    this.add_ports(this.structure.ports.out, this.ports.out, this.width, Port.out);

    this.canvas.stage.update();
};

Model.prototype.add_ports = function(structure_ports, graphical_ports, x, kind) {
    var i, height, port, margin, sorted_structure_ports;

    this.clean(graphical_ports);

    sorted_structure_ports = sort_ports(structure_ports);

    height = (this.height * 0.9 / sorted_structure_ports.length) - 1;
    height = Math.min(height, Math.floor(this.height * 0.06));

    margin = (this.height * 0.9 / sorted_structure_ports.length) - height;

    for(i = 0; i < sorted_structure_ports.length; ++i) {
        port = new Port({
            canvas: this.canvas,
            height: height,
            kind: kind,
            id: sorted_structure_ports[i].name,
            message_type: sorted_structure_ports[i].message_type,
            font_size: height * 0.4
        });

        port.x = x;
        port.y = this.height * 0.05 + (margin / 2) + i * (height + margin);
        graphical_ports.push(port);
        this.addChild(port);
    }
};

Model.prototype.calculate_submodel_positions = function() {
    var graph, models, ic, i, j, node;

    graph = [];
    models = this.structure.models;
    ic = this.structure.ic;
    for(i = 0; i < models.length; i++) {
        node = {model: models[i].id, neighbors: []};
        for(j = 0; j < ic.length; j++) {
            if (ic[j].from_model === node.model) {
                node.neighbors.push(ic[j].to_model);
            }
        }
        graph.push(node);
    }

    return relaxed_khan(graph);
};

Model.prototype.clean = function(models) {
    while (models.length > 0) {
        this.removeChild(models[0]);
        models.splice(0,1);
    }
};

Model.prototype.update_models = function() {

    if (this.structure.type === "atomic" || this.structure.models.length === 0 ) { return; }

    var modelsByColumns, highestColum, modelsWidth, modelsHeight, i, j, x;
    var model, columnMoldes, modelStructure, jsonGraphics;

    this.clean(this.models);

    modelsByColumns = this.calculate_submodel_positions();

    highestColum = modelsByColumns[0].length;
    for(i = 1; i < modelsByColumns.length; i++) {
        if (modelsByColumns[i].length > highestColum) {
            highestColum = modelsByColumns[i].length;
        }
    }

    // Model witdh as the models margin -> columns * 2
    modelsWidth = Math.floor(this.width * 0.85 / (modelsByColumns.length * 2));
    modelsHeight = Math.floor(this.height * 0.85 / (highestColum * 2));

    if (options.squared_models) {
        modelsWidth = Math.min(modelsWidth, modelsHeight);
        modelsHeight = Math.min(modelsWidth, modelsHeight);
    }

    var modelVerticalSpace = (this.height / highestColum);
    var modelHorizontalSpace = (this.width / modelsByColumns.length);

    for (j = 0; j < modelsByColumns.length; j++) {

        columnMoldes = modelsByColumns[j];
        x = modelHorizontalSpace / 2 + j * modelHorizontalSpace;
        for (i = 0; i < columnMoldes.length; i++) {

            modelStructure = this.get_model(columnMoldes[i]);
            jsonGraphics = this.jsonGraphics.get_submodel(columnMoldes[i]);

            if (jsonGraphics.json.model_box === undefined) {
                jsonGraphics.update_model_box({
                    x: x, 
                    y: modelVerticalSpace / 2 + i * modelVerticalSpace, 
                    width: modelsWidth,
                    height: modelsHeight,
                    regX: modelsWidth / 2,
                    regY: modelsHeight / 2
                });
            }

            model = new Model({
                visible: false,
                canvas: this.canvas,
                jsonGraphics: jsonGraphics,
                structure: $.extend(true, {}, modelStructure),
                parent_dimentions: {width: this.width, height: this.height}
            });
            this.addChild(model);
            this.models.push(model);
        }
    }

    this.canvas.stage.update();
};

Model.prototype.update_links = function() {
    this.remove_links();

    this.draw_ic(this.structure.ic);
    this.draw_eic(this.structure.eic);
    this.draw_eoc(this.structure.eoc);
};

Model.prototype.draw_ic = function(ics) {
    var icGraphics, to_port, from_port, link, ic, i;

    for (i = 0; i < ics.length; i++) {
        ic = ics[i];

        from_port = this.getPort(ic.from_model, ic.from_port, Port.out);
        to_port = this.getPort(ic.to_model, ic.to_port, Port.in);
        
        icGraphics = this.jsonGraphics.get_ic(ic);
        link = this.connect(from_port, to_port, ic, Link.Kind.IC, icGraphics);
        icGraphics.nodes = link.nodes;
        this.jsonGraphics.save_ic(icGraphics);
        this.ic.push(link);
    }

    this.canvas.stage.update();
};

Model.prototype.draw_eic = function(eics) {
    var to_port, from_port, link, eicGraphics, eic, i;

    for (i = 0; i < eics.length; i++) {
        eic = eics[i];

        from_port = this.getPort(this.id, eic.from_port, Port.in);
        to_port = this.getPort(eic.to_model, eic.to_port, Port.in);

        eicGraphics = this.jsonGraphics.get_eic(eic);
        link = this.connect(from_port, to_port, eic, Link.Kind.EIC, eicGraphics);
        eicGraphics.nodes = link.nodes;
        this.jsonGraphics.save_eic(eicGraphics);
        this.eic.push(link);
    }

    this.canvas.stage.update();
};

Model.prototype.draw_eoc = function(eocs) {
    var to_port, from_port, link, eocGraphics, eoc, i;

    for (i = 0; i < eocs.length; i++) {
        eoc = eocs[i];

        from_port = this.getPort(eoc.from_model, eoc.from_port, Port.out);
        to_port = this.getPort(this.id, eoc.to_port, Port.out);
        
        eocGraphics = this.jsonGraphics.get_eoc(eoc);
        link = this.connect(from_port, to_port, eoc, Link.Kind.EOC, eocGraphics);
        eocGraphics.nodes = link.nodes;
        this.jsonGraphics.save_eoc(eocGraphics);
        this.eoc.push(link);
    }

    this.canvas.stage.update();
};

Model.prototype.connect = function(from_port, to_port, information, kind, linkGraphics) {
    var link;

    link = new Link({
        visible: this.is_expanded && this.showing_links,
        kind: kind,
        information: information,
        from_port: from_port,
        to_port: to_port,
        nodes: linkGraphics.nodes || [],
        color: manifest.link.color,
        width: 2,
        canvas: this.canvas,
        parent: this,
    });

    this.addChild(link);
    return link;
};

Model.prototype.getPort = function(model_id, port_id, kind) {
    var model, ports, i;

    model = this.getModel(model_id);

    if (kind == Port.in) {
        ports = model.ports.in;
    } else {
        ports = model.ports.out;
    }

    for (i = 0; i < ports.length; i++) {
        if (ports[i].id === port_id) {
            return ports[i];
        }
    }
};

Model.prototype.getModel = function(model_id) {
    var i;

    if (model_id === this.id) {
        return this;
    }

    for (i = 0; i < this.models.length; i++) {
        if (this.models[i].id === model_id) {
            return this.models[i];
        }
    }  
};

Model.prototype.get_model = function(id) {
    for (var i = 0; i < this.structure.models.length; i++) {
        if (this.structure.models[i].id == id) {
            return this.structure.models[i];
        }
    }
};

Model.prototype.clean_internal_graphics = function() {
    
    this.remove_links();
    this.clean(this.models);
    this.canvas.stage.update();

    this.is_expanded = false;
};

Model.prototype.remove_links = function() {
    
    this.clean(this.eic);
    this.clean(this.eoc);
    this.clean(this.ic);

    this.canvas.stage.update();
};

Model.prototype.show_submodel_links = function(submodel) {
    var i, ic, eic, eoc;

    ic = this.ic.filter(function(link) {
        return link.information.from_model === submodel.id || link.information.to_model === submodel.id;
    });

    eic = this.eic.filter(function(link) {
        return link.information.to_model === submodel.id;
    });

    eoc = this.eoc.filter(function(link) {
        return link.information.from_model === submodel.id;
    });

    for (i = 0; i < ic.length; i++) {
        ic[i].visible = !ic[i].visible;
    }

    for (i = 0; i < eic.length; i++) {
        eic[i].visible = !eic[i].visible;
    }

    for (i = 0; i < eoc.length; i++) {
        eoc[i].visible = !eoc[i].visible;
    }

    this.canvas.stage.update();
};

Model.prototype.update_submodel_link = function(submodel) {
    var i, submodel_ports_in, submodel_ports_out;

    submodel_ports_in = submodel.ports.in.map(function(p) { return p.id; });
    submodel_ports_out = submodel.ports.out.map(function(p) { return p.id; });
    

    for (i = 0; i < this.eic.length; i++) {
        if (submodel_ports_in.indexOf(this.eic[i].to_port)) {
            this.eic[i].update_end_points();
        }
    }

    for (i = 0; i < this.eoc.length; i++) {
        if (submodel_ports_out.indexOf(this.eoc[i].from_port)) {    
            this.eoc[i].update_end_points();
        }
    }

    for (i = 0; i < this.ic.length; i++) {
        if (submodel_ports_in.indexOf(this.ic[i].to_port) || submodel_ports_out.indexOf(this.ic[i].from_port)) {
            this.ic[i].update_end_points();
        }
    }

    this.canvas.stage.update();
};

Model.prototype.update_colors = function() {
    var i;

    if (this.structure.type === Model.type.atomic) {
        this.update_box(manifest.atomic['background-color']);
        this["background-color"] = manifest.atomic['background-color'];
    } else {
        this.update_box(manifest.coupled['background-color']);
        this["background-color"] = manifest.coupled['background-color'];
        for (i = 0; i < this.models.length; i++) {
            this.models[i].update_colors();
        }
    }
    
    this.update_name();

    for(i = 0; i < this.ports.in.length; i++) {
        this.ports.in[i].update_colors();
    }

    for(i = 0; i < this.ports.out.length; i++) {
        this.ports.out[i].update_colors();
    }
};

Model.prototype.update_box = function(color) {
    this.removeChild(this.model_box);

    this.model_box = new Square({
        canvas: this.canvas,
        width: this.width,
        height: this.height,
        radius: 2,
        fillColor: color
    });

    this.addChildAt(this.model_box, 0);
    this.canvas.stage.update();
};

Model.prototype.change_models_visibility = function(visible) {
    var i;

    for(i = 0; i < this.models.length; i++) {
        this.models[i].visible = visible;
    }

    this.canvas.stage.update();
};

Model.prototype.change_links_visibility = function(visible) {
    var i, linkGraphics;

    for(i = 0; i < this.ic.length; i++) {
        linkGraphics = this.jsonGraphics.get_ic(this.ic[i].information);
        this.ic[i].visible = visible;
    }

    for(i = 0; i < this.eic.length; i++) {
        linkGraphics = this.jsonGraphics.get_eic(this.eic[i].information);
        this.eic[i].visible = visible;
    }

    for(i = 0; i < this.eoc.length; i++) {
        linkGraphics = this.jsonGraphics.get_eoc(this.eoc[i].information);
        this.eoc[i].visible = visible;
    }
    
    this.canvas.stage.update();
};

Model.prototype.toggle_models = function() {

    this.is_expanded = !this.is_expanded;
    this.showing_links = true;
    this.change_models_visibility(this.is_expanded);
    this.change_links_visibility(this.is_expanded && this.showing_links);
};

Model.prototype.toggle_port_names = function() {
    
    if (this.shows_port_names) {
        this.hide_port_names();
    } else {
        this.show_port_names();
    }
};

Model.prototype.toggle_links = function() {

    this.showing_links = !this.showing_links;
    this.change_links_visibility(this.is_expanded && this.showing_links);
};

Model.prototype.show_port_names = function() {
    var i;

    for(i = 0; i < this.ports.in.length; i++) {
        this.ports.in[i].show_name();
    }

    for(i = 0; i < this.ports.out.length; i++) {
        this.ports.out[i].show_name();
    }

    for(i = 0; i < this.models.length; i++) {
        this.models[i].show_port_names();
    }

    this.shows_port_names = true;
};

Model.prototype.hide_port_names = function() {
    var i;

    for(i = 0; i < this.ports.in.length; i++) {
        this.ports.in[i].hide_name();
    }

    for(i = 0; i < this.ports.out.length; i++) {
        this.ports.out[i].hide_name();
    }

    for(i = 0; i < this.models.length; i++) {
        this.models[i].hide_port_names();
    }
    this.shows_port_names = false;
};

Model.prototype.distance = function(a, b) {
    return Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2));
};

Model.prototype.rescale_dimentions = function(parent_dimentions) {
    var scaleX, scaleY;

    if (this.jsonGraphics.json.model_box.parent_dimentions !== undefined) {
        scaleX = parent_dimentions.width / this.jsonGraphics.json.model_box.parent_dimentions.width;
        scaleY = parent_dimentions.height / this.jsonGraphics.json.model_box.parent_dimentions.height;

        this.width = this.width * scaleX;
        this.x = this.x * scaleX;
        
        this.height = this.height * scaleY;
        this.y = this.y * scaleY;

        this.regX = this.width / 2;
        this.regY = this.height / 2;
    }
};

Model.prototype.update_scale = function(parent_dimentions) {

    if (this.is_top) {

        this.x = this.canvas.stageWidth / 2;
        this.y = this.canvas.stageHeight / 2;
        this.width = this.canvas.stageWidth * 0.85;
        this.height = this.canvas.stageHeight * 0.85;
        this.regX = this.width / 2;
        this.regY = this.height / 2;

    } else {
        this.rescale_dimentions(parent_dimentions);
    }

    this.jsonGraphics.update_model_box({
        x: this.x, 
        y: this.y, 
        width: this.width,
        height: this.height,
        regX: this.regX,
        regY:this.regY,
        parent_dimentions: $.extend(true, {}, parent_dimentions) // for future rescaling reference
    });

    this.update_box(this['background-color']);
    this.update_name();
    this.update_ports();
    
    for(var i = 0; i < this.models.length; i++) {
        this.models[i].update_scale({
            width: this.width,
            height: this.height
        });
    }

    this.update_links();
    this.canvas.stage.update();
};

/*********** Drag & Drop *****************/

Model.prototype.toggle_selection = function(evt) {
    evt.stopImmediatePropagation();

    if (this.dragged || this.dragged_child) { return; }
    console.log("ID:", this.id, "Select");

    this.is_selected = !this.is_selected;
    this.parent.dragged_child = false;

    if (this.is_selected) {
        selected_models.push(this);
        this.update_box(calculate_selected_color(this["background-color"]));

    } else {
        var i = 0;
        while (i < selected_models.length) {
            if (selected_models[i].id === this.id) {
                selected_models.splice(i,1);
            } else {
                i++;
            }
        }

        this.update_box(this["background-color"]);
    }
};

Model.prototype.hold = function(evt) {
    evt.stopImmediatePropagation();
    
    if (!this.holding && !this.is_top && !this.dragged_child) {

        console.log("ID:", this.id, "hold");
        this.parent.dragged_child = true;
        this.holding = true;
        
        this.mouse_offset = this.parent.globalToLocal(evt.stageX, evt.stageY);
        this.mouse_offset.x -= this.x;
        this.mouse_offset.y -= this.y;
        this.original_position = {x: this.x, y: this.y};
        this.dragged = false;
        console.log(this.mouse_offset);
    }
};

Model.prototype.move = function(evt) {
    evt.stopImmediatePropagation();
    
    if (this.holding) {
        console.log("ID:", this.id, "move");
        this.update_position(evt);
    }
};

Model.prototype.release = function(evt) {
    evt.stopImmediatePropagation();
    
    if (this.holding) {
        console.log("ID: ", this.id, "release");
        this.parent.dragged_child = false;
        this.holding = false;
        
        this.update_position(evt);
    }
};

Model.prototype.update_position = function (evt) {

    var mose_local_position = this.parent.globalToLocal(evt.stageX, evt.stageY);
    this.x = mose_local_position.x - this.mouse_offset.x;
    this.y = mose_local_position.y - this.mouse_offset.y;

    this.jsonGraphics.update_model_position(this.x, this.y);

    if (!this.dragged && this.distance(this, this.original_position) > 1) {
        this.dragged = true;
    }

    this.parent.update_submodel_link(this);
    this.canvas.stage.update();
};