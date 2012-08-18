package org.occ.matsu;

import org.occ.matsu.GeoPictureSerializer;
import org.occ.matsu.InvalidGeoPictureException;

import java.io.PrintWriter;
import java.io.FileInputStream;
import java.lang.Integer;
import java.lang.Double;

import javax.servlet.ServletOutputStream;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.lang.NumberFormatException;
import java.lang.NullPointerException;
import javax.script.ScriptException;

public class GeoPictureServlet extends HttpServlet {
    GeoPictureSerializer geoPictureSerializer = new GeoPictureSerializer();

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
	try {
	    processRequest(request, response);
	}
	catch (InvalidGeoPictureException exception) {
	    PrintWriter printWriter = response.getWriter();
	    printWriter.println("InvalidGeoPictureException: do a loadSerialized first");
	    printWriter.close();
	}
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
	try {
	    processRequest(request, response);
	}
	catch (InvalidGeoPictureException exception) {
	    PrintWriter printWriter = response.getWriter();
	    printWriter.println("InvalidGeoPictureException: do a loadSerialized first");
	    printWriter.close();
	}
    }

    protected void processRequest(HttpServletRequest request, HttpServletResponse response) throws IOException, InvalidGeoPictureException {
	String command = request.getParameter("command");

	if (command != null) {
	    if (command.equals("loadSerialized")) {
		String fileName = "/home/export/tanya/pictures-L1G-serialized/GobiDesert01-small.serialized";

		String which = request.getParameter("which");
		if (which != null) {
		    fileName = String.format("/home/export/tanya/pictures-L1G-serialized/%s.serialized", which);
		}
		FileInputStream fileInputStream = new FileInputStream(fileName);

		double before = System.nanoTime() / 1e9 / 60.;
		geoPictureSerializer.loadSerialized(fileInputStream);
		double after = System.nanoTime() / 1e9 / 60.;

		response.setContentType("text/plain");
		PrintWriter printWriter = response.getWriter();
		printWriter.println(String.format("Loaded %s in %g minutes.", fileName, after - before));
		printWriter.close();
	    }

	    else if (command.equals("bandNames")) {
		response.setContentType("text/plain");
		PrintWriter printWriter = response.getWriter();
		printWriter.println(geoPictureSerializer.bandNames());
		printWriter.close();
	    }

	    else if (command.equals("dimensions")) {
		response.setContentType("text/plain");
		PrintWriter printWriter = response.getWriter();
		printWriter.println(geoPictureSerializer.dimensions());
		printWriter.close();
	    }

	    else if (command.equals("spectrum")) {
		response.setContentType("text/plain");
		PrintWriter printWriter = response.getWriter();

		try {
		    int x1 = Integer.parseInt(request.getParameter("x1"));
		    int y1 = Integer.parseInt(request.getParameter("y1"));
		    int x2 = Integer.parseInt(request.getParameter("x2"));
		    int y2 = Integer.parseInt(request.getParameter("y2"));

		    boolean log = false;
		    if (request.getParameter("log") != null) {
			log = true;
		    }

		    printWriter.println(geoPictureSerializer.spectrum(x1, y1, x2, y2, log));
		}
		catch (NumberFormatException exception) {
		    printWriter.println("Invalid x1, y1, x2, y2.");
		}
		catch (NullPointerException exception) {
		    printWriter.println("Missing x1, y1, x2, y2.");
		}

		printWriter.close();
	    }

	    else if (command.equals("scatter")) {
		response.setContentType("text/plain");
		PrintWriter printWriter = response.getWriter();

		try {
		    int x1 = Integer.parseInt(request.getParameter("x1"));
		    int y1 = Integer.parseInt(request.getParameter("y1"));
		    int x2 = Integer.parseInt(request.getParameter("x2"));
		    int y2 = Integer.parseInt(request.getParameter("y2"));
		    String horiz = request.getParameter("horiz");
		    String vert = request.getParameter("vert");

		    if (horiz == null  ||  vert == null) {
			printWriter.println("Missing horiz or vert.");
		    }
		    else {
			try {
			    printWriter.println(geoPictureSerializer.scatter(x1, y1, x2, y2, horiz, vert));
			}
			catch (ScriptException exception) {
			    printWriter.println(String.format("Javascript error in horiz or vert: %s.", exception.getMessage()));
			}
		    }
		}
		catch (NumberFormatException exception) {
		    printWriter.println("Invalid x1, y1, x2, y2.");
		}
		catch (NullPointerException exception) {
		    printWriter.println("Missing x1, y1, x2, y2.");
		}

		printWriter.close();
	    }

	    else if (command.equals("image")) {
		boolean subImage = true;
		int x1 = 0;
		int y1 = 0;
		int x2 = 0;
		int y2 = 0;

		try {
		    x1 = Integer.parseInt(request.getParameter("x1"));
		    y1 = Integer.parseInt(request.getParameter("y1"));
		    x2 = Integer.parseInt(request.getParameter("x2"));
		    y2 = Integer.parseInt(request.getParameter("y2"));
		}
		catch (NumberFormatException exception) {
		    subImage = false;
		}
		catch (NullPointerException exception) {
		    subImage = false;
		}

		double min = 0.;
		try {
		    min = Double.parseDouble(request.getParameter("min"));
		}
		catch (NumberFormatException exception) { }
		catch (NullPointerException exception) { }

		double max = 0.;
		try {
		    max = Double.parseDouble(request.getParameter("max"));
		}
		catch (NumberFormatException exception) { }
		catch (NullPointerException exception) { }

		String red = request.getParameter("red");
		String green = request.getParameter("green");
		String blue = request.getParameter("blue");

		boolean base64 = false;
		if (request.getParameter("base64") != null) {
		    base64 = true;
		}

		if (red == null  ||  green == null  ||  blue == null) {
		    response.setContentType("text/plain");
		    PrintWriter printWriter = response.getWriter();
		    printWriter.println("Missing red, green, or blue.");
		    printWriter.close();
		}
		else {
		    try {
			byte[] picture;
			if (subImage) {
			    picture = geoPictureSerializer.image(x1, y1, x2, y2, red, green, blue, min, max, base64);
			}
			else {
			    picture = geoPictureSerializer.image(red, green, blue, min, max, base64);
			}

			if (base64) {
			    response.setContentType("text/plain");
			    PrintWriter printWriter = response.getWriter();
			    printWriter.println(new String(picture));
			    printWriter.close();
			}
			else {
			    response.setContentType("image/png");
			    ServletOutputStream servletOutputStream = response.getOutputStream();
			    servletOutputStream.write(picture);
			    servletOutputStream.close();
			}
		    }
		    catch (ScriptException exception) {
			response.setContentType("text/plain");
			PrintWriter printWriter = response.getWriter();
			printWriter.println(String.format("Javascript error in red, green, or blue: %s.", exception.getMessage()));
			printWriter.close();
		    }
		}
	    }

	    else {
		response.setContentType("text/plain");
		PrintWriter printWriter = response.getWriter();
		printWriter.println(String.format("Unrecognized command \"%s\".", command));
		printWriter.close();
	    }

	}
	else {
	    response.setContentType("text/plain");
	    PrintWriter printWriter = response.getWriter();
	    printWriter.println("Missing command.");
	    printWriter.close();
	}
    }
}
