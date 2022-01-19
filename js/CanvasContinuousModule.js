var CanvasContinuousModule = function(canvas_width, canvas_height) {
	// Create the element
	// ------------------

	// Create the tag with absolute positioning :
	var canvas_tag = `<canvas width="${canvas_width}" height="${canvas_height}" class="world-grid"/>`

	var parent_div_tag = '<div style="height:' + canvas_height + 'px;" class="world-grid-parent"></div>'

	// Append it to body:
	var canvas = $(canvas_tag)[0];
	var parent = $(parent_div_tag)[0];

	//$("body").append(canvas);
	$("#elements").append(parent);
	parent.append(canvas);

	// Create the context for the agents and interactions and the drawing controller:
	var context = canvas.getContext("2d");

	// Create an interaction handler using the
	var canvasDraw = new ContinuousVisualization(canvas_width, canvas_height, context);

	this.render = function(data) {
		canvasDraw.resetCanvas();
		for (var layer in data)
			canvasDraw.drawLayer(data[layer]);
	};

	this.reset = function() {
		canvasDraw.resetCanvas();
	};

};
