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
	zooKeeperInstance = new ZooKeeperInstance(accumuloName, zooKeeperList);
	if (zooKeeperInstance == null) {
	    throw new AccumuloException("Could not connect to ZooKeeper " + accumuloName + " " + zooKeeperList);
	}

	connector = zooKeeperInstance.getConnector(userId, password.getBytes());
	scanner = connector.createScanner(tableName, Constants.NO_AUTHS);
    }

    public static byte[] readL2png(String key) throws IOException {
	scanner.setRange(new Range(key));

	for (Entry<Key, Value> entry : scanner) {
	    String columnName = entry.getKey().getColumnQualifier().toString();
	    if (columnName.equals("l2png")) {
	    	return entry.getValue().get();
	    }
	}

	throw new IOException("key \"" + key + "\" column \"l2png\" not found");
    }

    public static String readMetadata(String key) throws IOException {
	scanner.setRange(new Range(key));

	for (Entry<Key, Value> entry : scanner) {
	    String columnName = entry.getKey().getColumnQualifier().toString();
	    if (columnName.equals("metadata")) {
	    	return entry.getValue().toString();
	    }
	}

	throw new IOException("key \"" + key + "\" column \"l2png\" not found");
    }

    public static void connectForWriting(String accumuloName, String zooKeeperList, String userId, String password, String tableName) throws AccumuloException, AccumuloSecurityException, TableExistsException, TableNotFoundException {
	zooKeeperInstance = new ZooKeeperInstance(accumuloName, zooKeeperList);
	if (zooKeeperInstance == null) {
	    throw new AccumuloException("Could not connect to ZooKeeper " + accumuloName + " " + zooKeeperList);
	}

	connector = zooKeeperInstance.getConnector(userId, password.getBytes());
	if (!connector.tableOperations().exists(tableName)) {
	    connector.tableOperations().create(tableName);
	}

	multiTableBatchWriter = connector.createMultiTableBatchWriter(200000L, 300, 4);
	batchWriter = multiTableBatchWriter.getBatchWriter(tableName);
    }

    public static void write(String key, String metadata, byte[] l2png) throws MutationsRejectedException {
	Mutation mutation = new Mutation(new Text(key));
	mutation.put(columnFamily, new Text("metadata"), new Value(metadata.getBytes()));
	mutation.put(columnFamily, new Text("l2png"), new Value(l2png));
	batchWriter.addMutation(mutation);
    }

    public static void finishedWriting() throws MutationsRejectedException {
	multiTableBatchWriter.close();
    }

}
