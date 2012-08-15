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

    public static void main(String[] argv) throws IOException {
	System.out.println("begin");

	InputStream inputStream = new Base64InputStream(new FileInputStream(new File("/home/pivarski/matsu-project/Libraries/Serialization with Avro/tests/test.serialized")));
	// InputStream inputStream = new FileInputStream(new File("/home/pivarski/matsu-project/Libraries/Serialization with Avro/tests/test.binary"));

	DecoderFactory decoderFactory = new DecoderFactory();
	ValidatingDecoder decoder = decoderFactory.validatingDecoder(schema, decoderFactory.binaryDecoder(inputStream, null));

	// GeoPictureWithMetadata p = new GeoPictureWithMetadata();
	// SpecificDatumReader<GeoPictureWithMetadata> reader = new SpecificDatumReader<GeoPictureWithMetadata>(schema);
	// SpecificData<GeoPictureWithMetadata> p = reader.read(null, d);

	// DatumReader reader = new SpecificDatumReader(GeoPictureWithMetadata.class);
	// GeoPictureWithMetadata result = new GeoPictureWithMetadata();
	// reader.read(result, decoder);

	DatumReader<GeoPictureWithMetadata> reader = new SpecificDatumReader<GeoPictureWithMetadata>(GeoPictureWithMetadata.class);
	GeoPictureWithMetadata result = reader.read(null, decoder);

	// DatumReader<GeoPictureWithMetadata> reader = SpecificData.createDatumReader(schema);

	


	System.out.println(result.getBands());
	System.out.println(result.getMetadata());
	System.out.println(result.getHeight());
	System.out.println(result.getWidth());
	System.out.println(result.getDepth());
	System.out.println(result.getDtype());
	System.out.println(result.getByteorder());
	System.out.println(result.getItemsize());
	System.out.println(result.getNbytes());
	System.out.println(result.getFortran());
	System.out.println(result.getData());



	System.out.println("end");
    }
}
