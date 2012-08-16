package org.occ.matsu;

import java.io.PrintWriter;

import javax.servlet.ServletOutputStream;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import java.io.IOException;
// import javax.servlet.ServletException;

public class GeoPictureServlet extends HttpServlet {

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
	processRequest(request, response);
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
    	processRequest(request, response);
    }

    protected void processRequest(HttpServletRequest request, HttpServletResponse response) throws IOException {

    	// ServletOutputStream servletOutputStream = response.getOutputStream();
    	// servletOutputStream.write("it works\n");
    	// servletOutputStream.close();

    	PrintWriter printWriter = response.getWriter();
    	printWriter.println("sure does");
    	printWriter.close();

    }
}
