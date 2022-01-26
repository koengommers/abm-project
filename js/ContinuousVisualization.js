var ContinuousVisualization = function(height, width, context) {
	var height = height;
	var width = width;
	var context = context;

	this.drawLayer = function(layer) {
		for (var i in layer) {
			var p = layer[i];
			if (p.Shape == "rect")
				this.drawRectange(p.x, p.y, p.w, p.h, p.Color, p.Filled);
      else if (p.Shape == "circle")
				this.drawCircle(p.x, p.y, p.r, p.Color, p.Filled);
      else if (p.Shape == "circleWithTrail")
        this.drawCircleWithTrail(p.x, p.y, p.fromx, p.fromy, p.Color, p.r, p.s)
		};

	};

	this.drawCircle = function(x, y, radius, color, fill) {
		var cx = x * width;
		var cy = y * height;
		var r = radius;

		context.beginPath();
		context.arc(cx, cy, r, 0, Math.PI * 2, false);
		context.closePath();

		context.strokeStyle = color;
		context.stroke();

		if (fill) {
			context.fillStyle = color;
			context.fill();
		}

	};

  this.drawCircleWithTrail = function(x, y, fromx, fromy, color, radius, stroke) {
    var cx = x * width;
    var cy = y * height;
    var cfromx = fromx * width;
    var cfromy = fromy * height;

    context.beginPath();
    context.arc(cx, cy, radius, 0, Math.PI * 2, false);
    context.closePath();

    context.fillStyle = color;
    context.fill();

    var dx = Math.abs(cx - cfromx) 
    var dy = Math.abs(cy - cfromy) 
    if (!(dx > 100 || dy > 100)) {
      context.lineWidth = stroke;
      context.moveTo(cfromx, cfromy);
      context.lineTo(cx, cy);
      context.strokeStyle = color;
      context.stroke()
    }
  }

	this.drawRectange = function(x, y, w, h, color, fill) {
		context.beginPath();
		var dx = w * width;
		var dy = h * height;

		// Keep the drawing centered:
		var x0 = (x*width) - 0.5*dx;
		var y0 = (y*height) - 0.5*dy;

		context.strokeStyle = color;
		context.fillStyle = color;
		if (fill)
			context.fillRect(x0, y0, dx, dy);
		else
			context.strokeRect(x0, y0, dx, dy);
	};

	this.resetCanvas = function() {
		context.clearRect(0, 0, height, width);
		context.beginPath();
	};
};
