package org.occ.matsu;

import java.io.PrintWriter;

import org.apache.accumulo.core.client.Instance;
import org.apache.accumulo.core.client.ZooKeeperInstance;
import org.apache.accumulo.core.client.Connector;
import org.apache.accumulo.core.client.Scanner;
import org.apache.accumulo.core.Constants;
import org.apache.accumulo.core.data.Key;
import org.apache.accumulo.core.data.Range;

import javax.servlet.ServletConfig;
import javax.servlet.ServletContext;
import javax.servlet.ServletOutputStream;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import java.io.IOException;
import javax.servlet.ServletException;
import org.apache.accumulo.core.client.AccumuloException;
import org.apache.accumulo.core.client.AccumuloSecurityException;
import org.apache.accumulo.core.client.TableNotFoundException;

public class MatsuServlet extends HttpServlet {
    protected static String accumuloName = "accumulo";
    protected static String zooKeeperList = "192.168.18.101:2181";
    protected static String userId = "root";
    protected static String password = "password";
    protected static String tableName = "MatsuLevel2Tiles";

    protected static String configPath;

    protected static Instance zooKeeperInstance = null;
    protected static Connector connector = null;
    protected static Scanner scanner = null;

    @Override public void init(ServletConfig servletConfig) throws ServletException {
	System.out.println("begin init()");

	super.init(servletConfig);

	System.out.println("really begin init()");

	ServletContext servletContext = servletConfig.getServletContext();
	configPath = servletContext.getRealPath(servletConfig.getInitParameter("config.path"));

	System.out.println("go do startup()");
	startup();

	System.out.println("end init()");
    }

    public synchronized static void startup() throws ServletException {
	System.out.println("begin startup()");

        zooKeeperInstance = new ZooKeeperInstance(accumuloName, zooKeeperList);
        if (zooKeeperInstance == null) {
	    System.out.println("zooKeeperInstance is null, throwing exception");

            throw new ServletException("Could not connect to ZooKeeper " + accumuloName + " " + zooKeeperList);
        }

	try {
	    connector = zooKeeperInstance.getConnector(userId, password.getBytes());
	}
	catch (AccumuloException exception) {
	    throw new ServletException("Could not create connector from ZooKeeper instance (AccumuloException)");
	}
	catch (AccumuloSecurityException exception) {
	    throw new ServletException("Could not create connector from ZooKeeper instance (AccumuloSecurityException)");
	}

	try {
	    scanner = connector.createScanner(tableName, Constants.NO_AUTHS);
	}
	catch (TableNotFoundException exception) {
	    throw new ServletException("Could not create scanner from connector (TableNotFoundException)");
	}

	System.out.println("end startup()");
    }

    @Override protected void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
	processRequest(request, response);
    }

    @Override protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
	processRequest(request, response);
    }

    protected void processRequest(HttpServletRequest request, HttpServletResponse response) throws IOException {
	System.out.println("begin processRequest()");

	PrintWriter printWriter = response.getWriter();
	printWriter.write("hello");
	printWriter.close();

	System.out.println("end processRequest()");
    }

}
