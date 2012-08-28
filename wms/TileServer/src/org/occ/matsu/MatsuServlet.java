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
    protected static String accumuloName = @ACCUMULO_DB_NAME@;
    protected static String zooKeeperList = @ACCUMULO_ZOOKEEPER_LIST@;
    protected static String userId = @ACCUMULO_USER_NAME@;
    protected static String password = @ACCUMULO_PASSWORD@;
    protected static String tableName = @ACCUMULO_TABLE_NAME@;

    protected String configPath;

    protected static Instance zooKeeperInstance = null;
    protected static Connector connector = null;

    static {
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
    }

    @Override public void init(ServletConfig servletConfig) throws ServletException {
    	super.init(servletConfig);

    	ServletContext servletContext = servletConfig.getServletContext();
    	configPath = servletContext.getRealPath(servletConfig.getInitParameter("config.path"));
    }

    @Override protected void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
    	processRequest(request, response);
    }

    @Override protected void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
    	processRequest(request, response);
    }

    protected void processRequest(HttpServletRequest request, HttpServletResponse response) throws IOException {
    	if (zooKeeperInstance == null  ||  connector == null) { return; }

    	Scanner scanner;
    	try {
    	    scanner = connector.createScanner(tableName, Constants.NO_AUTHS);
    	}
    	catch (TableNotFoundException exception) {
    	    return;
    	}

    	String key = request.getParameter("key");
    	if (key == null) { return; }

    	scanner.setRange(new Range(key));

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
    }

}
