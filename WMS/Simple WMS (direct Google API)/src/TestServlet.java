import java.io.PrintWriter;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.accumulo.core.client.Instance;
import org.apache.accumulo.core.client.ZooKeeperInstance;
import org.apache.accumulo.core.client.Connector;
import org.apache.accumulo.core.client.Scanner;
import org.apache.accumulo.core.Constants;

import javax.servlet.ServletException;
import javax.servlet.UnavailableException;
import java.io.IOException;
import org.apache.accumulo.core.client.AccumuloException;
import org.apache.accumulo.core.client.AccumuloSecurityException;
import org.apache.accumulo.core.client.TableNotFoundException;

public class TestServlet extends HttpServlet {
    String tableName = "MatsuLevel2Tiles";
    String accumuloName = "accumulo";
    String zookeeperIPPort = "192.168.18.101:2181";
    String userid = "root";
    String password = "password";

    static Instance zookeeperInstance = null;
    static Connector connector = null;
    static Scanner scanner = null;

    public void initError() throws ServletException {
	throw new UnavailableException("Couldn't connect to Accumulo table " + tableName + " in " + accumuloName + "@" + zookeeperIPPort);
    }

    public void init() throws ServletException {
	System.out.println("begin init()");

	zookeeperInstance = null;
	connector = null;
	scanner = null;

	try {
	    zookeeperInstance = new ZooKeeperInstance(accumuloName, zookeeperIPPort);
	    if (zookeeperInstance == null) {
		throw new AccumuloException("Could not find Zookeeper");
	    }
	    connector = zookeeperInstance.getConnector(userid, password.getBytes());
	    scanner = connector.createScanner(tableName, Constants.NO_AUTHS);
	}
	catch (AccumuloException exception) { initError(); }
	catch (AccumuloSecurityException exception) { initError(); }
	catch (TableNotFoundException exception) { initError(); }

	System.out.println("end init()");
    }
    
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
	System.out.println("begin doGet()");

	PrintWriter printWriter = response.getWriter();

	if (zookeeperInstance == null) { throw new UnavailableException("Zookeeper has not been initialized."); }
	if (connector == null) { throw new UnavailableException("Connector has not been initialized."); }
	if (scanner == null) { throw new UnavailableException("Scanner has not been initialized."); }

	printWriter.println("uno dos tres");
	printWriter.close();

	System.out.println("end doGet()");
    }

}
