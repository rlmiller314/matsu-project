package org.occ.matsu.accumulo;

import org.apache.accumulo.core.client.Instance;
import org.apache.accumulo.core.client.ZooKeeperInstance;
import org.apache.accumulo.core.client.Connector;

import org.apache.hadoop.io.Text;
import org.apache.accumulo.core.security.ColumnVisibility;
import org.apache.accumulo.core.data.Value;
import org.apache.accumulo.core.data.Mutation;
import org.apache.accumulo.core.client.BatchWriter;
import org.apache.accumulo.core.client.MultiTableBatchWriter;

import java.util.Iterator;
import java.util.Map.Entry;

import org.apache.accumulo.core.client.Scanner;
import org.apache.accumulo.core.Constants;
import org.apache.accumulo.core.data.Key;
import org.apache.accumulo.core.data.Range;

import org.apache.accumulo.core.client.AccumuloException;
import org.apache.accumulo.core.client.AccumuloSecurityException;
import org.apache.accumulo.core.client.TableNotFoundException;
import org.apache.accumulo.core.client.MutationsRejectedException;
import org.apache.accumulo.core.client.TableExistsException;
import org.apache.accumulo.core.client.TableNotFoundException;

public class WriteToAccumulo {

    static String tableName = "quicktest8";

    public static void write() throws AccumuloException, AccumuloSecurityException, TableNotFoundException, MutationsRejectedException, TableExistsException {
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

	for (int i = 0; i < 100; i++) {
	    Mutation mutation = new Mutation(new Text(String.format("row_%d", i)));

	    mutation.put(columnFamily, new Text("A"), new Value((String.format("%d", i)).getBytes()));
	    mutation.put(columnFamily, new Text("B"), new Value((String.format("%d", -i)).getBytes()));
	    mutation.put(columnFamily, new Text("C"), new Value((String.format("%d", i*10)).getBytes()));

	    batchWriter.addMutation(mutation);
	}

	multiTableBatchWriter.close();
    }

    public static void read() throws AccumuloException, AccumuloSecurityException, TableNotFoundException {
	Instance zookeeper = new ZooKeeperInstance("accumulo", "192.168.18.101:2181");
	if (zookeeper == null) {
	    System.err.println("ZooKeeper instance not found");
	}

	Connector connector = zookeeper.getConnector("root", "password".getBytes());
	
	Scanner scan = connector.createScanner(tableName, Constants.NO_AUTHS);
	Key start = null;
	Key end = null;
	scan.setRange(new Range(start, end));
	Iterator<Entry<Key,Value>> iter = scan.iterator();

	while (iter.hasNext()) {
	    Entry<Key,Value> entry = iter.next();
	    Text columnFamily = entry.getKey().getColumnFamily();
	    Text columnQualifier = entry.getKey().getColumnQualifier();
	    System.out.println("row: " + entry.getKey().getRow() + " columnFamily: " + columnFamily + " columnQualifier: " + columnQualifier + " value: " + entry.getValue().toString());
	}
    }

    public static void main(String argv[]) throws AccumuloException, AccumuloSecurityException, TableNotFoundException, MutationsRejectedException, TableExistsException {
	write();
	read();
    }
}
