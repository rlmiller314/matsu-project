package org.occ.matsu.accumulo;

import java.util.Set;
import java.util.Iterator;
import java.util.Map.Entry;
import java.io.BufferedReader;
import java.io.InputStreamReader;

import org.apache.accumulo.core.client.Instance;
import org.apache.accumulo.core.client.ZooKeeperInstance;
import org.apache.accumulo.core.client.Connector;

import org.apache.hadoop.io.Text;
import org.apache.accumulo.core.security.ColumnVisibility;
import org.apache.accumulo.core.data.Value;
import org.apache.accumulo.core.data.Mutation;
import org.apache.accumulo.core.client.BatchWriter;
import org.apache.accumulo.core.client.MultiTableBatchWriter;

import org.apache.accumulo.core.client.Scanner;
import org.apache.accumulo.core.Constants;
import org.apache.accumulo.core.data.Key;
import org.apache.accumulo.core.data.Range;

import java.io.IOException;
import org.apache.accumulo.core.client.AccumuloException;
import org.apache.accumulo.core.client.AccumuloSecurityException;
import org.apache.accumulo.core.client.TableNotFoundException;
import org.apache.accumulo.core.client.MutationsRejectedException;
import org.apache.accumulo.core.client.TableExistsException;
import org.apache.accumulo.core.client.TableNotFoundException;

import org.json.simple.JSONValue;
import org.json.simple.JSONObject;
import org.json.simple.JSONArray;

public class AccumuloInterface {
    public static void read() throws AccumuloException, AccumuloSecurityException, TableNotFoundException {
	// Key start = null;
	// Key end = null;
	// scan.setRange(new Range(start, end));
	// Iterator<Entry<Key,Value>> iter = scan.iterator();

	// while (iter.hasNext()) {
	//     Entry<Key,Value> entry = iter.next();
	//     Text columnFamily = entry.getKey().getColumnFamily();
	//     Text columnQualifier = entry.getKey().getColumnQualifier();
	//     System.out.println("row: " + entry.getKey().getRow() + " columnFamily: " + columnFamily + " columnQualifier: " + columnQualifier + " value: " + entry.getValue().toString());
	// }
    }

    public static void main(String argv[]) throws AccumuloException, AccumuloSecurityException, TableNotFoundException, MutationsRejectedException, TableExistsException, IOException {
	if (argv.length != 2) {
	    throw new RuntimeException("Pass a command: 'read TABLENAME' or 'write TABLENAME'.");
	}

	if (argv[0].equals("read")) {
	    String tableName = argv[1];
	    System.out.println("AccumuloInterface reading from " + tableName);

	    Instance zookeeper = new ZooKeeperInstance("accumulo", "192.168.18.101:2181");
	    if (zookeeper == null) {
		System.err.println("ZooKeeper instance not found");
	    }

	    Connector connector = zookeeper.getConnector("root", "password".getBytes());
	
	    Scanner scan = connector.createScanner(tableName, Constants.NO_AUTHS);






	}
	else if (argv[0].equals("write")) {
	    String tableName = argv[1];
	    System.out.println("AccumuloInterface writing to " + tableName);

	    Instance zookeeper = new ZooKeeperInstance("accumulo", "192.168.18.101:2181");
	    if (zookeeper == null) {
		System.err.println("ZooKeeper instance not found");
	    }

	    Connector connector = zookeeper.getConnector("root", "password".getBytes());

	    if (!connector.tableOperations().exists(tableName)) {
		connector.tableOperations().create(tableName);
	    }
	
	    MultiTableBatchWriter multiTableBatchWriter = connector.createMultiTableBatchWriter(200000L, 300, 4);
	    BatchWriter batchWriter = multiTableBatchWriter.getBatchWriter(tableName);

	    Text columnFamily = new Text("f");

	    BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(System.in));
	    String line;
	    while ((line = bufferedReader.readLine()) != null) {
		JSONObject obj = (JSONObject)JSONValue.parse(line);
		if (obj == null) {
		    System.out.println("Received a malformated JSON object; skipping...");
		    continue;
		}

		String key = (String)obj.get("KEY");
		if (key == null) {
		    System.out.println("JSON object is missing its 'KEY'; skipping...");
		    continue;
		}

		Set columnNames = obj.keySet();
		columnNames.remove(new String("KEY"));

		Mutation mutation = new Mutation(new Text(key));
		for (Object columnName : columnNames) {
		    Object value = obj.get(columnName);

		    try {
			String stringValue = (String)value;
			stringValue = "\"" + JSONObject.escape(stringValue) + "\"";
			mutation.put(columnFamily, new Text((String)columnName), new Value(stringValue.getBytes()));
		    }
		    catch (ClassCastException e) {
			mutation.put(columnFamily, new Text((String)columnName), new Value(value.toString().getBytes()));
		    }
		}
		batchWriter.addMutation(mutation);

	    }

	    multiTableBatchWriter.close();
	}
	else {
	    throw new RuntimeException("Unrecognized command: must be 'read' or 'write'.");
	}
    }
}
