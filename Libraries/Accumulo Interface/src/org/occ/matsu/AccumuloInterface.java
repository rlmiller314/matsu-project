package org.occ.matsu.accumulo;

import java.util.Iterator;
import java.util.Map.Entry;

import org.apache.accumulo.core.client.Instance;
import org.apache.accumulo.core.client.ZooKeeperInstance;
import org.apache.accumulo.core.client.Connector;

import org.apache.hadoop.io.Text;
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

public class AccumuloInterface {
    static Instance zooKeeperInstance = null;
    static Connector connector = null;

    static Scanner scanner = null;

    static Text columnFamily = new Text("f");
    static MultiTableBatchWriter multiTableBatchWriter = null;
    static BatchWriter batchWriter = null;

    public static void connectForReading(String accumuloName, String zooKeeperList, String userId, String password, String tableName) throws AccumuloException, AccumuloSecurityException, TableExistsException, TableNotFoundException {
	System.out.println("one");

	zooKeeperInstance = new ZooKeeperInstance(accumuloName, zooKeeperList);
	if (zooKeeperInstance == null) {
	    throw new AccumuloException("Could not connect to ZooKeeper " + accumuloName + " " + zooKeeperList);
	}

	System.out.println("two");

	connector = zooKeeperInstance.getConnector(userId, password.getBytes());

	System.out.println("three");

	scanner = connector.createScanner(tableName, Constants.NO_AUTHS);

	System.out.println("four");
    }

    public static byte[] readL2png(String key) {
	System.out.println("five");

	scanner.setRange(new Range(key));

	System.out.println("six");

	for (Entry<Key, Value> entry : scanner) {
	    System.out.println("seven");

	    String columnName = entry.getKey().getColumnQualifier().toString();

	    System.out.println("eight " + columnName);

	    if (columnName.equals("l2png")) {
		System.out.println("nine");

	    	return entry.getValue().get();
	    }

	    System.out.println("ten");
	}

	System.out.println("eleven");
	return new byte[0];
    }

    public static void connectForWriting(String accumuloName, String zooKeeperList, String userId, String password, String tableName) throws AccumuloException, AccumuloSecurityException, TableExistsException, TableNotFoundException {
	System.out.println("one");

	zooKeeperInstance = new ZooKeeperInstance(accumuloName, zooKeeperList);
	if (zooKeeperInstance == null) {
	    throw new AccumuloException("Could not connect to ZooKeeper " + accumuloName + " " + zooKeeperList);
	}

	System.out.println("two");

	connector = zooKeeperInstance.getConnector(userId, password.getBytes());
	if (!connector.tableOperations().exists(tableName)) {
	    connector.tableOperations().create(tableName);
	}

	System.out.println("three");

	multiTableBatchWriter = connector.createMultiTableBatchWriter(200000L, 300, 4);
	batchWriter = multiTableBatchWriter.getBatchWriter(tableName);

	System.out.println("four");
    }

    public static void write(String key, String metadata, byte[] l2png) throws MutationsRejectedException {
	System.out.println("five");

	Mutation mutation = new Mutation(new Text(key));

	System.out.println("six");

	mutation.put(columnFamily, new Text("metadata"), new Value(metadata.getBytes()));

	System.out.println("seven");

	mutation.put(columnFamily, new Text("l2png"), new Value(l2png));

	System.out.println("eight");

	batchWriter.addMutation(mutation);

	System.out.println("nine");
    }

    public static void finishedWriting() throws MutationsRejectedException {
	System.out.println("ten");

	multiTableBatchWriter.close();

	System.out.println("eleven");
    }

}
