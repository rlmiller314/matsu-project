package org.occ.matsu;

import org.occ.matsu.GeoPictureSerializer;
import org.occ.matsu.InvalidGeoPictureException;

import java.io.PrintWriter;
import java.io.FileInputStream;

import javax.servlet.ServletOutputStream;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import java.io.IOException;

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

	if (command != null  &&  command.equals("loadSerialized")) {
	    String fileName = "/home/export/tanya/pictures-L1G-serialized/GobiDesert01.serialized";

	    FileInputStream fileInputStream = new FileInputStream(fileName);
	    geoPictureSerializer.loadSerialized(fileInputStream);
	    PrintWriter printWriter = response.getWriter();
	    printWriter.println("loaded " + fileName);
	    printWriter.close();
	}

	if (command != null  &&  command.equals("bandNames")) {
	    PrintWriter printWriter = response.getWriter();
	    printWriter.println(geoPictureSerializer.bandNames());
	    printWriter.close();
	}

    	// ServletOutputStream servletOutputStream = response.getOutputStream();
    	// servletOutputStream.write("it works\n");
    	// servletOutputStream.close();

    }
}
