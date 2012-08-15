package org.occ.matsu;

import org.occ.matsu.ByteOrder;
import org.occ.matsu.ZeroSuppressed;
import org.occ.matsu.GeoPictureWithMetadata;

import org.apache.avro.Schema;
import org.apache.avro.io.DecoderFactory;
import org.apache.avro.io.ValidatingDecoder;
import org.apache.avro.io.DatumReader;
import org.apache.avro.specific.SpecificDatumReader;
import org.apache.avro.specific.SpecificData;

import it.sauronsoftware.base64.Base64InputStream;

import java.io.IOException;
import java.io.InputStream;
import java.io.File;
import java.io.FileInputStream;
import java.nio.ByteBuffer;

class GeoPictureSerializer {
    public static final Schema schema = new Schema.Parser().parse(
        "{\"type\": \"record\", \"name\": \"GeoPictureWithMetadata\", \"fields\":\n" +
	"    [{\"name\": \"metadata\", \"type\": {\"type\": \"map\", \"values\": \"string\"}},\n" +
	"     {\"name\": \"bands\", \"type\": {\"type\": \"array\", \"items\": \"string\"}},\n" +
	"     {\"name\": \"height\", \"type\": \"int\"},\n" +
	"     {\"name\": \"width\", \"type\": \"int\"},\n" +
	"     {\"name\": \"depth\", \"type\": \"int\"},\n" +
	"     {\"name\": \"dtype\", \"type\": \"int\"},\n" +
	"     {\"name\": \"itemsize\", \"type\": \"int\"},\n" +
	"     {\"name\": \"nbytes\", \"type\": \"long\"},\n" +
	"     {\"name\": \"fortran\", \"type\": \"boolean\"},\n" +
	"     {\"name\": \"byteorder\", \"type\": {\"type\": \"enum\", \"name\": \"ByteOrder\", \"symbols\": [\"LittleEndian\", \"BigEndian\", \"NativeEndian\", \"IgnoreEndian\"]}},\n" +
	"     {\"name\": \"data\", \"type\":\n" +
	"        {\"type\": \"array\", \"items\":\n" +
	"            {\"type\": \"record\", \"name\": \"ZeroSuppressed\", \"fields\":\n" +
	"                [{\"name\": \"index\", \"type\": \"long\"}, {\"name\": \"strip\", \"type\": \"bytes\"}]}}}\n" +
	"     ]}");

    public static double[][][] data;

    public static void main(String[] argv) throws IOException {
	System.out.println("begin");

	InputStream inputStream = new Base64InputStream(new FileInputStream(new File("/home/pivarski/matsu-project/Libraries/Serialization with Avro/tests/test.serialized")));

	DecoderFactory decoderFactory = new DecoderFactory();
	ValidatingDecoder d = decoderFactory.validatingDecoder(schema, decoderFactory.binaryDecoder(inputStream, null));

	DatumReader<GeoPictureWithMetadata> reader = new SpecificDatumReader<GeoPictureWithMetadata>(GeoPictureWithMetadata.class);
	GeoPictureWithMetadata p = reader.read(null, d);

	System.out.println(p.getBands());
	System.out.println(p.getMetadata());
	System.out.println(p.getHeight());
	System.out.println(p.getWidth());
	System.out.println(p.getDepth());
	System.out.println(p.getDtype());
	System.out.println(p.getByteorder());
	System.out.println(p.getItemsize());
	System.out.println(p.getNbytes());
	System.out.println(p.getFortran());
	System.out.println(p.getData());

	data = new double[p.getHeight()][p.getWidth()][p.getDepth()];
	for (int i = 0;  i < p.getHeight();  i++) {
	    for (int j = 0;  j < p.getWidth();  j++) {
		for (int k = 0;  k < p.getDepth();  k++) {
		    data[i][j][k] = 0.;
		}
	    }
	}

	for (ZeroSuppressed zs : p.getData()) {
	    long index = zs.getIndex();

	    ByteBuffer strip = zs.getStrip();
	    if (! p.getByteorder().equals(ByteOrder.BigEndian)) {
		strip.order(java.nio.ByteOrder.LITTLE_ENDIAN);
	    }

	    while (strip.hasRemaining()) {
		int i, j, k;
		if (p.getFortran()) {
		    i = (int)((index / p.getHeight() / p.getWidth()) % p.getDepth());
		    j = (int)((index / p.getHeight()) % p.getWidth());
		    k = (int)(index % p.getHeight());
		}
		else {
		    i = (int)((index / p.getDepth() / p.getWidth()) % p.getHeight());
		    j = (int)((index / p.getDepth()) % p.getWidth());
		    k = (int)(index % p.getDepth());
		}
		index++;

		data[i][j][k] = strip.getDouble();

		System.out.println(String.format("%d %g", index, data[i][j][k]));

	    }
	}

	p.setData(null);

	for (int i = 0;  i < p.getHeight();  i++) {
	    for (int j = 0;  j < p.getWidth();  j++) {
		System.out.print("[");
		for (int k = 0;  k < p.getDepth();  k++) {
		    System.out.print(data[i][j][k]);
		    System.out.print(" ");
		}
		System.out.println("]");
	    }
	    System.out.println();
	}

	System.out.println("end");
    }
}
