package org.occ.matsu;

import java.util.Map.Entry;
import java.util.Set;
import java.util.HashSet;
import java.lang.Integer;
import java.lang.Long;
import java.io.PrintWriter;
import java.nio.ByteBuffer;

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
import java.lang.NumberFormatException;
import javax.servlet.ServletException;
import org.apache.accumulo.core.client.AccumuloException;
import org.apache.accumulo.core.client.AccumuloSecurityException;
import org.apache.accumulo.core.client.TableNotFoundException;

public class MatsuServlet extends HttpServlet {
    protected static String accumuloName = @ACCUMULO_DB_NAME@;
    protected static String zooKeeperList = @ACCUMULO_ZOOKEEPER_LIST@;
    protected static String userId = @ACCUMULO_USER_NAME@;
    protected static String password = @ACCUMULO_PASSWORD@;
    protected static String imageTableName = @ACCUMULO_TABLE_NAME@;
    protected static String pointsTableName = @ACCUMULO_POINTS_TABLE_NAME@;

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
	String command = request.getParameter("command");
	if (command == null) {
	    getImage(request, response);
	}
	else if (command.equals("image")) {
	    getImage(request, response);
	}
	else if (command.equals("points")) {
	    getPoints(request, response);
	}
    }

    protected void getImage(HttpServletRequest request, HttpServletResponse response) throws IOException {
    	if (zooKeeperInstance == null  ||  connector == null) { return; }

    	Scanner scanner;
    	try {
    	    scanner = connector.createScanner(imageTableName, Constants.NO_AUTHS);
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

    protected boolean getPoints_writeOne(PrintWriter output, String lastrow, double longitude, double latitude, String metadata, String comma, long timemin, long timemax, int groupdepth, Set<String> seen) {
	String tileName = lastrow.substring(0, 15);
	String timeStamp_ = lastrow.substring(16, 26);
	String identifier = lastrow.substring(27, 43);

	boolean useThis = true;
	if (timemin != 0L  ||  timemax != 9999999999L) {
	    try {
		long timeStamp = Long.parseLong(timeStamp_);
		if (timeStamp < timemin  ||  timeStamp > timemax) { useThis = false; }
	    }
	    catch (NumberFormatException exception) { }
	}

	if (useThis  &&  groupdepth < 10) {
	    String depth_ = tileName.substring(1, 3);
	    String longIndex_ = tileName.substring(4, 9);
	    String latIndex_ = tileName.substring(10, 15);

	    try {
		int depth = Integer.parseInt(depth_);
		int longIndex = Integer.parseInt(longIndex_);
		int latIndex = Integer.parseInt(latIndex_);
	    
		int factor = (int)Math.pow(2, 10 - groupdepth);

		longIndex = longIndex / factor;
		latIndex = latIndex / factor;

		tileName = String.format("T%02d-%05d-%05d", groupdepth, longIndex, latIndex);
		if (seen.contains(tileName)) {
		    useThis = false;
		}
		else {
		    seen.add(tileName);
		}
	    }
	    catch (NumberFormatException exception) {
		useThis = false;
	    }
	}

	if (useThis) {
	    output.print(String.format("%s\n    {\"tile\": \"%s\", \"time\": \"%s\", \"identifier\": \"%s\", \"longitude\": %g, \"latitude\": %g, \"metadata\": %s}", comma, tileName, timeStamp_, identifier, longitude, latitude, metadata));
	}

	return useThis;
    }

    protected void getPoints(HttpServletRequest request, HttpServletResponse response) throws IOException {
    	if (zooKeeperInstance == null  ||  connector == null) { return; }

    	Scanner scanner;
    	try {
    	    scanner = connector.createScanner(pointsTableName, Constants.NO_AUTHS);
    	}
    	catch (TableNotFoundException exception) {
    	    return;
    	}

    	String longmin_ = request.getParameter("longmin");
    	String longmax_ = request.getParameter("longmax");
    	String latmin_ = request.getParameter("latmin");
    	String latmax_ = request.getParameter("latmax");
	String timemin_ = request.getParameter("timemin");
	String timemax_ = request.getParameter("timemax");
	String groupdepth_ = request.getParameter("groupdepth");

    	if (longmin_ == null   ||  longmax_ == null  ||  latmin_ == null  ||  latmax_ == null) { return; }

	int longmin, longmax, latmin, latmax;
	try {
	    longmin = Integer.parseInt(longmin_);
	    longmax = Integer.parseInt(longmax_);
	    latmin = Integer.parseInt(latmin_);
	    latmax = Integer.parseInt(latmax_);
	}
	catch (NumberFormatException exception) { return; }

	long timemin = 0L;
	if (timemin_ != null) {
	    try {
		timemin = Long.parseLong(timemin_);
	    }
	    catch (NumberFormatException exception) { }
	}

	long timemax = 9999999999L;
	if (timemax_ != null) {
	    try {
		timemax = Long.parseLong(timemax_);
	    }
	    catch (NumberFormatException exception) { }
	}

	int groupdepth = 10;
	if (groupdepth_ != null) {
	    try {
		groupdepth = Integer.parseInt(groupdepth_);
	    }
	    catch (NumberFormatException exception) { }
	}
	
	response.setContentType("text/plain");
	PrintWriter output = response.getWriter();
	output.print("{\"data\": [");
	String comma = "";

	Set<String> seen = new HashSet<String>();

	for (int longIndex = longmin;  longIndex <= longmax;  longIndex++) {
	    scanner.setRange(new Range(String.format("T10-%05d-%05d-0000000000", longIndex, latmin),
				       String.format("T10-%05d-%05d-9999999999", longIndex, latmax)));
	    
	    Entry<Key, Value> last = null;
	    String lastrow = "";
	    double longitude = -1000.0;
	    double latitude = -1000.0;
	    String metadata = "{}";

	    for (Entry<Key, Value> entry : scanner) {
		String entryrow = entry.getKey().getRow().toString();

		if (last != null  &&  !lastrow.equals(entryrow)) {
		    if (getPoints_writeOne(output, lastrow, longitude, latitude, metadata, comma, timemin, timemax, groupdepth, seen)) {
			comma = ",";
		    }
		    longitude = -1000.0;
		    latitude = -1000.0;
		    metadata = "{}";
		}

		String columnName = entry.getKey().getColumnQualifier().toString();
		if (columnName.equals("longitude")) {
		    longitude = ByteBuffer.wrap(entry.getValue().get()).getDouble();
		}
		else if (columnName.equals("latitude")) {
		    latitude = ByteBuffer.wrap(entry.getValue().get()).getDouble();
		}
		else if (columnName.equals("metadata")) {
		    metadata = entry.getValue().toString();
		}

		last = entry;
		lastrow = entryrow;
	    }

	    if (last != null) {
		getPoints_writeOne(output, lastrow, longitude, latitude, metadata, comma, timemin, timemax, groupdepth, seen);
	    }
	}

	output.println("\n    ]}");
    }

}
