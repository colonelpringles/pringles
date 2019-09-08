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

/*global $, Link */
/*exported JSONModelGraphics */
"use strict";

function JSONModelGraphics(parameters) {
    this.initialize(parameters);
}

/**
 * Constructs a new instance of JSONModelGraphics.
 * @param {Object} parameters - All the necessary parameters to initialize the instance.
 * @param {JSON} parameters.structure - All the structure information related with the formalism, models, EIC, EOC, IC, etc.
 * @param {JSON} parmeters.json - All the custom graphic values needed to display the instance as exported.
 */
JSONModelGraphics.prototype.initialize = function(parameters) {

    this.json = $.extend(true, {}, JSONModelGraphics.emptyJSONGraphics);
    $.extend(true, this, parameters);
    this.json.id = this.id;
};

JSONModelGraphics.emptyJSONGraphics = {
    id: "",
    models: [],
    ic: [],
    eoc: [],
    eic: []
};

JSONModelGraphics.emptyJSONLink = {
    nodes: [],
    information: {}
};

JSONModelGraphics.prototype.update_model_box = function(model_box) {
    this.json.model_box = {};
    $.extend(true, this.json.model_box, model_box);
};

JSONModelGraphics.prototype.update_model_position = function(x, y) {
    if (this.json.model_box === undefined) {
        this.json.model_box = {};
    }

    this.json.model_box.x = x;
    this.json.model_box.y = y;
};

JSONModelGraphics.prototype.get_ic = function(ic) {
    var i, new_ic;
    
    for(i = 0; i < this.json.ic.length; i++) {
        if (this.same_ic(this.json.ic[i], ic)) {
            return $.extend(true, 
                this.clone_json(JSONModelGraphics.emptyJSONLink),
                this.clone_json(this.json.ic[i]));
        }
    }

    new_ic = $.extend(true, this.clone_json(JSONModelGraphics.emptyJSONLink), ic);
    this.json.ic.push(new_ic);
    return this.clone_json(new_ic);
};

JSONModelGraphics.prototype.get_eic = function(eic) {
    var i, new_eic;

    for(i = 0; i < this.json.eic.length; i++) {
        if (this.same_ic(this.json.eic[i], eic)) {
            return $.extend(true, 
                this.clone_json(JSONModelGraphics.emptyJSONLink),
                this.clone_json(this.json.eic[i]));
        }
    }

    new_eic = $.extend(true, this.clone_json(JSONModelGraphics.emptyJSONLink), eic);
    this.json.ic.push(new_eic);
    return this.clone_json(new_eic);
};

JSONModelGraphics.prototype.get_eoc = function(eoc) {
    var i, new_eoc;
    
    for(i = 0; i < this.json.eoc.length; i++) {
        if (this.same_ic(this.json.eoc[i], eoc)) {
            return $.extend(true, 
                this.clone_json(JSONModelGraphics.emptyJSONLink),
                this.clone_json(this.json.eoc[i]));
        }
    }

    new_eoc = $.extend(true, this.clone_json(JSONModelGraphics.emptyJSONLink), eoc);
    this.json.ic.push(new_eoc);
    return this.clone_json(new_eoc);
};

JSONModelGraphics.prototype.save_ic = function(ic) {
    var i, link_to_save;

    link_to_save = this.clone_json(ic);

    for(i = 0; i < this.json.ic.length; i++) {
        if (this.same_ic(this.json.ic[i], ic)) {
            this.json.ic[i] = link_to_save;
            return;
        }
    }

    this.json.ic.push(link_to_save);
};

JSONModelGraphics.prototype.save_eic = function(eic) {
    var i, link_to_save;

    link_to_save = this.clone_json(eic);

    for(i = 0; i < this.json.eic.length; i++) {
        if (this.same_eic(this.json.eic[i], eic)) {
            this.json.eic[i] = link_to_save;
            return;
        }
    }

    this.json.eic.push(link_to_save);
};

JSONModelGraphics.prototype.save_eoc = function(eoc) {
    var i, link_to_save;

    link_to_save = this.clone_json(eoc);

    for(i = 0; i < this.json.eoc.length; i++) {
        if (this.same_eoc(this.json.eoc[i], eoc)) {
            this.json.eoc[i] = link_to_save;
            return;
        }
    }

    this.json.eoc.push(link_to_save);
};

JSONModelGraphics.prototype.get_ic_nodes = function(ic) {
    var i;
    for(i = 0; i < this.json.ic.length; i++) {
        if (this.same_ic(this.json.ic[i], ic)) {
            return this.clone_json(this.json.ic[i].nodes);
        }
    }
};

JSONModelGraphics.prototype.get_eic_nodes = function(eic) {
    var i;
    for(i = 0; i < this.json.eic.length; i++) {
        if (this.same_eic(this.json.eic[i], eic)) {
            return this.clone_json(this.json.eic[i].nodes);
        }
    }
};

JSONModelGraphics.prototype.get_eoc_nodes = function(eoc) {
    var i;
    for(i = 0; i < this.json.eoc.length; i++) {
        if (this.same_eoc(this.json.eoc[i], eoc)) {
            return this.clone_json(this.json.eoc[i].nodes);
        }
    }
};

JSONModelGraphics.prototype.save_ic_nodes = function(ic, nodes) {
    var i, nodes_to_save;

    nodes_to_save = this.clone_json(nodes);

    for(i = 0; i < this.json.ic.length; i++) {
        if (this.same_ic(this.json.ic[i], ic)) {
            this.json.ic[i].nodes = nodes_to_save;
            return;
        }
    }

    this.json.ic.push($.extend(true, {nodes: nodes_to_save}, ic));
};

JSONModelGraphics.prototype.save_eic_nodes = function(eic, nodes) {
    var i, nodes_to_save;

    nodes_to_save = this.clone_json(nodes);

    for(i = 0; i < this.json.eic.length; i++) {
        if (this.same_eic(this.json.eic[i], eic)) {
            this.json.eic[i].nodes = nodes_to_save;
            return;
        }
    }

    this.json.eic.push($.extend(true, {nodes: nodes_to_save}, eic));
};

JSONModelGraphics.prototype.save_eoc_nodes = function(eoc, nodes) {
    var i, nodes_to_save;

    nodes_to_save = this.clone_json(nodes);

    for(i = 0; i < this.json.eoc.length; i++) {
        if (this.same_eoc(this.json.eoc[i], eoc)) {
            this.json.eoc[i].nodes = nodes_to_save;
            return;
        }
    }

    this.json.eoc.push($.extend(true, {nodes: nodes_to_save}, eoc));
};

JSONModelGraphics.prototype.same_ic = function(ic_a, ic_b) {
    return  ic_a.from_model == ic_b.from_model &&
            ic_a.from_port == ic_b.from_port &&
            ic_a.to_model == ic_b.to_model &&
            ic_a.to_port == ic_b.to_port;
};

JSONModelGraphics.prototype.same_eic = function(eic_a, eic_b) {
    return  eic_a.from_port == eic_b.from_port &&
            eic_a.to_model == eic_b.to_model &&
            eic_a.to_port == eic_b.to_port;
};

JSONModelGraphics.prototype.same_eoc = function(eoc_a, eoc_b) {
    return  eoc_a.from_model == eoc_b.from_model &&
            eoc_a.from_port == eoc_b.from_port &&
            eoc_a.to_port == eoc_b.to_port;
};

JSONModelGraphics.prototype.clone_json = function(nodes) {
    
    return JSON.parse(JSON.stringify(nodes));
};

JSONModelGraphics.prototype.add_node_to_link = function(kind, information, node, index) {
    var nodes;

    if (kind === Link.Kind.IC) {
        
        nodes = this.get_ic_nodes(information);
        nodes.splice(index, 0, this.clone_json(node));
        this.save_ic_nodes(information, nodes);
    
    } else if (kind === Link.Kind.EIC) {
    
        nodes = this.get_eic_nodes(information);
        nodes.splice(index, 0, this.clone_json(node));
        this.save_eic_nodes(information, nodes);
    
    } else if (kind === Link.Kind.EOC) {

        nodes = this.get_eoc_nodes(information);
        nodes.splice(index, 0, this.clone_json(node));
        this.save_eoc_nodes(information, nodes);

    }
};

JSONModelGraphics.prototype.update_link_nodes = function(kind, information, nodes) {
    
    if (kind === Link.Kind.IC) {
        this.save_ic_nodes(information, nodes);
    } else if (kind === Link.Kind.EIC) {
        this.save_eic_nodes(information, nodes);
    } else if (kind === Link.Kind.EOC) {
        this.save_eoc_nodes(information, nodes);
    }
};

JSONModelGraphics.prototype.get_submodel = function(model_id) {
    var i, jsonGraphics;

    for (i = 0; i < this.json.models.length; i++) {
        if (this.json.models[i].id === model_id) {
            jsonGraphics = new JSONModelGraphics({ id: model_id });
            // generate aliasing to modify the same logical structure
            jsonGraphics.json = this.json.models[i];
            return jsonGraphics; 
        }
    }

    // if there is no sub model, it creates a new empty
    
    jsonGraphics = new JSONModelGraphics({ id: model_id });
    this.json.models.push(jsonGraphics.json);
    return jsonGraphics;
};