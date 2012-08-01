package org.occ.matsu;

import java.util.Map.Entry;

import org.apache.accumulo.core.client.Instance;
import org.apache.accumulo.core.client.ZooKeeperInstance;
import org.apache.accumulo.core.client.Connector;
import org.apache.accumulo.core.client.Scanner;
import org.apache.accumulo.core.Constants;
import org.apache.accumulo.core.data.Key;
import org.apache.accumulo.core.data.Range;
import org.apache.accumulo.core.data.Value;

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

    protected String configPath;

    protected static Instance zooKeeperInstance = null;
    protected static Connector connector = null;

    static {
	System.out.println("begin static");

	zooKeeperInstance = new ZooKeeperInstance(accumuloName, zooKeeperList);

	try {
	    connector = zooKeeperInstance.getConnector(userId, password.getBytes());
	}
	catch (AccumuloException exception) {
	    connector = null;
	}
	catch (AccumuloSecurityException exception) {
	    connector = null;
	}

	System.out.println("end static");
    }

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

    public void startup() throws ServletException {
	System.out.println("begin startup()");
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

	if (zooKeeperInstance == null  ||  connector == null) { return; }

	Scanner scanner;
	try {
	    scanner = connector.createScanner(tableName, Constants.NO_AUTHS);
	}
	catch (TableNotFoundException exception) {
	    return;
	}
	scanner.setRange(new Range("T10-01561-01485-RGB"));

	for (Entry<Key, Value> entry : scanner) {
	    String columnName = entry.getKey().getColumnQualifier().toString();
	    if (columnName.equals("l2png")) {
		byte[] l2png = entry.getValue().get();

		response.setContentType("image/png");
		response.setContentLength(l2png.length);

		ServletOutputStream servletOutputStream = response.getOutputStream();
		servletOutputStream.write(l2png);
		servletOutputStream.close();

		break;
	    }
	}

	System.out.println("end processRequest()");
    }

}
