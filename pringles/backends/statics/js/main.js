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

/*global $, Canvas, console, JSONModelGraphics, manifest */
/*exported main, new_input_model, update_options, update_color, menu_init, 
    import_colors, export_colors */
"use strict";

var canvases = [];

var selected_models = [];

var options = {
	squared_models : false,
	show_message_type : false,
	show_port_name : true,
	compress_in_left : false,
	sort_ports_by_name : true,
};

var evt = {
	stopImmediatePropagation: function() {}
};

function remove_selected_top_models() {
	var i;

	while (selected_models.length > 0) {
		if (selected_models[0].is_top) {
            for (i = 0; i < canvases.length; i++) {
                if (canvases[i].top_model.id === selected_models[0].id) {
                    canvases.splice(i, 1);
                }
            }
			selected_models[0].canvas.dom_canvas.remove();
		}
		selected_models[0].toggle_selection(evt);		
	}
}

function expand_in_new_canvas_selected() {
	
	while (selected_models.length > 0) {
		new_model(selected_models[0].structure, selected_models[0].jsonGraphics.json);
		selected_models[0].toggle_selection(evt);
	}
}

function toggle_links_selected() {
	
	while (selected_models.length > 0) {
		selected_models[0].toggle_links();
		selected_models[0].toggle_selection(evt);
	}
}

function show_submodel_links_selected() {

    while (selected_models.length > 0) {
        if (!selected_models[0].is_top) {
            selected_models[0].parent.show_submodel_links(selected_models[0]);
        }
        selected_models[0].toggle_selection(evt);
    }
}

function export_model_json_selected() {

    while (selected_models.length > 0) {
        if (selected_models[0].is_top) {
            export_model_json(selected_models[0]);
        }
        selected_models[0].toggle_selection(evt);
    }
}

function export_model_image_selected(imgType) {
    var export_img;
	var models_to_export = [];
    var delay = 1000 / manifest.canvas.fps + manifest.canvas.fps;

	while (selected_models.length > 0) {	
        if (selected_models[0].is_top) {
            models_to_export.push(selected_models[0]);
        }
		selected_models[0].toggle_selection(evt);
	}

    for (var i = 0; i < models_to_export.length; i++) {
        models_to_export[i].canvas.stage.update();
        export_img = export_model_image.bind(export_model_image, models_to_export[i], imgType);
        setTimeout(export_img, delay);
    }
}

function toggle_models_selected() {
	while (selected_models.length > 0) {
		selected_models[0].toggle_models();
		selected_models[0].toggle_selection(evt);
	}
}

function toggle_port_name_selected() {
	while (selected_models.length > 0) {
		selected_models[0].toggle_port_names();
		selected_models[0].toggle_selection(evt);
	}
}

function new_model(structure, jsonGraphics) {
	canvases.push(new Canvas({
		structure: structure,
		jsonGraphics: new JSONModelGraphics({
			id: jsonGraphics.id,
			json: $.extend(true, {}, jsonGraphics)
		})
	}));
}

function new_input_model(evt) {
    var reader, structure;

    reader = new FileReader();
    reader.onload = function() {
        evt.target.value = "";
        structure = JSON.parse(reader.result);
        canvases.push(new Canvas({ json_input: structure }));
    };
    reader.readAsText(evt.target.files[0]);
}

$(window).keydown(function (e) {
    switch(e.keyCode) {
        case 13: expand_in_new_canvas_selected(); break;  
        case 46: remove_selected_top_models(); break;
        case 49: toggle_models_selected(); break;
        case 50: toggle_links_selected(); break;
        case 51: show_submodel_links_selected(); break;
        case 52: toggle_port_name_selected(); break;
        case 53: export_model_json_selected(); break;
        case 54: export_model_image_selected('png'); break;
        case 55: export_model_image_selected('jpeg'); break;
    }
});

function set_option(name, value) {
    options[name] = value;
}

function update_options() {

	console.log("udate options");
	options.squared_models = $('input[name="squared_models"]:checked').length > 0;
	options.show_message_type = $('input[name="show_message_type"]:checked').length > 0;
	options.show_port_name = $('input[name="show_port_name"]:checked').length > 0;
	options.compress_in_left = $('input[name="compress_in_left"]:checked').length > 0;
	options.sort_ports_by_name = $('input[name="sort_ports_by_name"]:checked').length > 0;
}

function export_model_json(model) {

	var exportedJson = $.extend(true, {}, model.structure);
	exportedJson.graphics = $.extend(true, {}, model.jsonGraphics.json);

	var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportedJson, undefined, 4));
	var downloadLink = document.getElementById('download');
	downloadLink.setAttribute("href", dataStr);
	downloadLink.setAttribute("download", model.id + ".json");
	downloadLink.click();
}

function export_model_image(model, imgType) {
	
    var img = model.canvas.dom_canvas.get(0).toDataURL("image/" + imgType, 1.0);
	var downloadLink = document.getElementById('download');
    downloadLink.setAttribute("href", img);
	downloadLink.setAttribute("download", model.id + "." + imgType);
	downloadLink.click();
}

function update_color(evt) {
    var i;
    var attributes = evt.target.attributes;
    var model = attributes.model.value;
    var element = attributes.element.value;
    var value = evt.target.value;

    manifest[model][element] = value;
    $('label[model="' + model + '"]').css(element, value);

    for (i = 0; i < canvases.length; i++) {
        canvases[i].top_model.update_colors();
    }
}

function menu_init() {
    var model, models, element, elements, i, j;

    models = ["coupled", "atomic", "port"];
    elements = ["background-color", "color"];

    for (i = 0; i < models.length; i++) {
        model = models[i];
        for (j = 0; j < elements.length; j++) {
            element = elements[j];
            $('label[model="' + model + '"]').css(element, manifest[model][element]);
        }
    }
}

function import_colors(evt) {
    var reader, configurations, models, model, elements, element, i, j;

    reader = new FileReader();
    reader.onload = function() {
        evt.target.value = "";
        configurations = JSON.parse(reader.result);

        models = ["coupled", "atomic", "port"];
        elements = ["background-color", "color"];

        for (i = 0; i < models.length; i++) {
            model = models[i];
            for (j = 0; j < elements.length; j++) {
                element = elements[j];
                if (typeof configurations[model][element] === "string") {
                    manifest[model][element] = configurations[model][element];
                    $('label[model="' + model + '"]').css(element, manifest[model][element]);
                }
            }
        }

        for (i = 0; i < canvases.length; i++) {
            canvases[i].top_model.update_colors();
        }
    };
    reader.readAsText(evt.target.files[0]);
}

function export_colors() {
    var exportedJson, models, elements, model, element, i, j;
    exportedJson = {};

    models = ["coupled", "atomic", "port"];
    elements = ["background-color", "color"];

    for (i = 0; i < models.length; i++) {
        model = models[i];
        exportedJson[model] = {};
        for (j = 0; j < elements.length; j++) {
            element = elements[j];
            exportedJson[model][element] = manifest[model][element];
        }
    }

    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportedJson, undefined, 4));
    var downloadLink = document.getElementById('download');
    downloadLink.setAttribute("href", dataStr);
    downloadLink.setAttribute("download", "DEVSDiagrammer_colors.json");
    downloadLink.click();
}

function parse_query_params(modelAsJson) {
    var structure = JSON.parse(modelAsJson);
    canvases.push(new Canvas({ json_input: structure }));
}