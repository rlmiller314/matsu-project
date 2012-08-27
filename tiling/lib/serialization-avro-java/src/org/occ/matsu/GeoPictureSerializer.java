package org.occ.matsu;

import org.occ.matsu.ByteOrder;
import org.occ.matsu.ZeroSuppressed;
import org.occ.matsu.GeoPictureWithMetadata;
import org.occ.matsu.InvalidGeoPictureException;

import org.apache.avro.Schema;
import org.apache.avro.io.DecoderFactory;
import org.apache.avro.io.ValidatingDecoder;
import org.apache.avro.io.DatumReader;
import org.apache.avro.specific.SpecificDatumReader;

import it.sauronsoftware.base64.Base64InputStream;
import it.sauronsoftware.base64.Base64;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;
import java.lang.Double;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;

import java.awt.Color;
import java.awt.image.BufferedImage;
import java.lang.Math;
import java.lang.StringBuilder;

import javax.script.ScriptEngineManager;
import javax.script.ScriptEngine;
import javax.script.ScriptException;

import javax.imageio.ImageIO;

class GeoPictureSerializer extends Object {

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

    String[] bands;
    int height;
    int width;
    int depth;
    double[][][] data;
    boolean valid = false;

    public GeoPictureSerializer() {}

    public String bandNames() throws InvalidGeoPictureException {
    	if (!valid) { throw new InvalidGeoPictureException(); }

	StringBuilder stringBuilder = new StringBuilder();
	stringBuilder.append("[");

	for (int k = 0;  k < depth;  k++) {
	    if (k != 0) { stringBuilder.append(","); }
	    stringBuilder.append(String.format("\"%s\"", bands[k]));
	}
	stringBuilder.append("]");

	return stringBuilder.toString();
    }

    public String dimensions() throws InvalidGeoPictureException {
    	if (!valid) { throw new InvalidGeoPictureException(); }
	return String.format("[%d,%d,%d]", width, height, depth);
    }

    public void loadSerialized(String serialized) throws IOException {
    	loadSerialized(new ByteArrayInputStream(serialized.getBytes()));
    }

    public void loadSerialized(InputStream serialized) throws IOException {
	InputStream inputStream = new Base64InputStream(serialized);

	DecoderFactory decoderFactory = new DecoderFactory();
	ValidatingDecoder d = decoderFactory.validatingDecoder(schema, decoderFactory.binaryDecoder(inputStream, null));

	DatumReader<GeoPictureWithMetadata> reader = new SpecificDatumReader<GeoPictureWithMetadata>(GeoPictureWithMetadata.class);
	GeoPictureWithMetadata p = reader.read(null, d);

	bands = new String[p.getBands().size()];
	int b = 0;
	for (java.lang.CharSequence band : p.getBands()) {
	    bands[b] = band.toString();
	    b++;
	}

	height = p.getHeight();
	width = p.getWidth();
	depth = p.getDepth();

	data = new double[height][width][depth];
	for (int i = 0;  i < height;  i++) {
	    for (int j = 0;  j < width;  j++) {
		for (int k = 0;  k < depth;  k++) {
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
		    i = (int)((index / height / width) % depth);
		    j = (int)((index / height) % width);
		    k = (int)(index % height);
		}
		else {
		    i = (int)((index / depth / width) % height);
		    j = (int)((index / depth) % width);
		    k = (int)(index % depth);
		}
		index++;

		data[i][j][k] = strip.getDouble();
	    }
	}

	valid = true;
    }

    public String spectrum(int x1, int y1, int x2, int y2, boolean log) throws IOException, InvalidGeoPictureException {
    	if (!valid) { throw new InvalidGeoPictureException(); }
	if (x1 < 0) { x1 = 0; }
	if (y1 < 0) { y1 = 0; }
	if (x2 >= width) { x2 = width - 1; }
	if (y2 >= height) { y2 = height - 1; }

    	double[] numer = new double[depth];
    	double[] denom = new double[depth];

	int numNonzero = 0;
    	for (int k = 0;  k < depth;  k++) {
    	    numer[k] = 0.;
    	    denom[k] = 0.;

    	    for (int i = 0;  i < x2 - x1;  i++) {
    		for (int j = 0;  j < y2 - y1;  j++) {
    		    double v = data[j + y1][i + x1][k];
		    if (v > 0.) {
			numer[k] += v;
			denom[k] += 1.;
		    }
		}
	    }

	    if (denom[k] > 0.) { numNonzero++; }
	}

	StringBuilder stringBuilder = new StringBuilder();
	stringBuilder.append("[");

	int i = 0;
	boolean first = true;
	for (int k = 0;  k < depth;  k++) {
	    if (denom[k] > 0.) {
		double output;

		if (log) {
		    output = Math.log(numer[k]) - Math.log(denom[k]);
		}
		else {
		    output = numer[k] / denom[k];
		}
		i++;

		if (!first) { stringBuilder.append(","); }
		first = false;

		stringBuilder.append(String.format("[\"%s\",%g]", bands[k], output));
	    }
	}
		
	stringBuilder.append("]");

	return stringBuilder.toString();
    }

    public String scatter(int x1, int y1, int x2, int y2, String horiz, String vert) throws InvalidGeoPictureException, ScriptException {
	if (!valid) { throw new InvalidGeoPictureException(); }
	if (x1 < 0) { x1 = 0; }
	if (y1 < 0) { y1 = 0; }
	if (x2 >= width) { x2 = width - 1; }
	if (y2 >= height) { y2 = height - 1; }

	int horizSimple = -1;
	int vertSimple = -1;
	for (int k = 0;  k < depth;  k++) {
	    if (bands[k].equals(horiz)) { horizSimple = k; }
	    if (bands[k].equals(vert)) { vertSimple = k; }
	}

	ScriptEngineManager scriptEngineManager = new ScriptEngineManager();
	ScriptEngine scriptEngine = scriptEngineManager.getEngineByName("JavaScript");

	boolean[] goodBands = new boolean[depth];
	for (int k = 0;  k < depth;  k++) {
	    goodBands[k] = false;
	    if (horiz.indexOf(bands[k]) != -1) { goodBands[k] = true; }
	    if (vert.indexOf(bands[k]) != -1) { goodBands[k] = true; }
	}

	double[][] horizs = new double[x2 - x1][y2 - y1];
	double[][] verts = new double[x2 - x1][y2 - y1];
	boolean[][] alphas = new boolean[x2 - x1][y2 - y1];

	for (int i = 0;  i < x2 - x1;  i++) {
	    for (int j = 0;  j < y2 - y1;  j++) {
		alphas[i][j] = true;

		if (horizSimple == -1  ||  vertSimple == -1) {
		    for (int k = 0;  k < depth;  k++) {
			if (goodBands[k]) {
			    scriptEngine.put(bands[k], data[j + y1][i + x1][k]);
			    if (data[j + y1][i + x1][k] == 0.) { alphas[i][j] = false; }
			}
		    }
		}

		if (horizSimple == -1) {
		    horizs[i][j] = (Double)scriptEngine.eval(horiz);
		}
		else {
		    horizs[i][j] = data[j + y1][i + x1][horizSimple];
		    if (horizs[i][j] == 0.) { alphas[i][j] = false; }
		}
		if (vertSimple == -1) {
		    verts[i][j] = (Double)scriptEngine.eval(vert);
		}
		else {
		    verts[i][j] = data[j + y1][i + x1][vertSimple];
		    if (verts[i][j] == 0.) { alphas[i][j] = false; }
		}

	    }
	}

	StringBuilder stringBuilder = new StringBuilder();
	stringBuilder.append("[");
	boolean first = true;
	for (int i = 0;  i < x2 - x1;  i++) {
	    for (int j = 0;  j < y2 - y1;  j++) {
		if (alphas[i][j]) {
		    if (!first) { stringBuilder.append(","); }
		    first = false;

		    stringBuilder.append(String.format("[%g,%g]", horizs[i][j], verts[i][j]));
		}
	    }
	}
	stringBuilder.append("]");

	return stringBuilder.toString();
    }

    public byte[] image(String red, String green, String blue, double min, double max, boolean base64) throws IOException, InvalidGeoPictureException, ScriptException {
	if (!valid) { throw new InvalidGeoPictureException(); }

	int redSimple = -1;
	int greenSimple = -1;
	int blueSimple = -1;
	for (int k = 0;  k < depth;  k++) {
	    if (bands[k].equals(red)) { redSimple = k; }
	    if (bands[k].equals(green)) { greenSimple = k; }
	    if (bands[k].equals(blue)) { blueSimple = k; }
	}

	if (redSimple == -1  ||  greenSimple == -1  ||  blueSimple == -1) {
	    throw new ScriptException("Javascript is only allowed for sub-images (it's slow!)");
	}

	return image(0, 0, width, height, red, green, blue, min, max, base64);
    }

    public byte[] image(int x1, int y1, int x2, int y2, String red, String green, String blue, double min, double max, boolean base64) throws IOException, InvalidGeoPictureException, ScriptException {
	if (!valid) { throw new InvalidGeoPictureException(); }
	if (x1 < 0) { x1 = 0; }
	if (y1 < 0) { y1 = 0; }
	if (x2 >= width) { x2 = width - 1; }
	if (y2 >= height) { y2 = height - 1; }

	int redSimple = -1;
	int greenSimple = -1;
	int blueSimple = -1;
	for (int k = 0;  k < depth;  k++) {
	    if (bands[k].equals(red)) { redSimple = k; }
	    if (bands[k].equals(green)) { greenSimple = k; }
	    if (bands[k].equals(blue)) { blueSimple = k; }
	}
	
	ScriptEngineManager scriptEngineManager = new ScriptEngineManager();
	ScriptEngine scriptEngine = scriptEngineManager.getEngineByName("JavaScript");

	boolean[] goodBands = new boolean[depth];
	for (int k = 0;  k < depth;  k++) {
	    goodBands[k] = false;
	    if (red.indexOf(bands[k]) != -1) { goodBands[k] = true; }
	    if (green.indexOf(bands[k]) != -1) { goodBands[k] = true; }
	    if (blue.indexOf(bands[k]) != -1) { goodBands[k] = true; }
	}

	double[][] reds = new double[x2 - x1][y2 - y1];
	double[][] greens = new double[x2 - x1][y2 - y1];
	double[][] blues = new double[x2 - x1][y2 - y1];
	boolean[][] alphas = new boolean[x2 - x1][y2 - y1];
	
	List<Double> redrad = new ArrayList<Double>();
	List<Double> greenrad = new ArrayList<Double>();
	List<Double> bluerad = new ArrayList<Double>();
	
	for (int i = 0;  i < x2 - x1;  i++) {
	    for (int j = 0;  j < y2 - y1;  j++) {
		alphas[i][j] = true;

		if (redSimple == -1  ||  greenSimple == -1  ||  blueSimple == -1) {
		    for (int k = 0;  k < depth;  k++) {
			if (goodBands[k]) {
			    scriptEngine.put(bands[k], data[j + y1][i + x1][k]);
			    if (data[j + y1][i + x1][k] == 0.) { alphas[i][j] = false; }
			}
		    }
		}

		if (redSimple == -1) {
		    reds[i][j] = (Double)scriptEngine.eval(red);
		}
		else {
		    reds[i][j] = data[j + y1][i + x1][redSimple];
		    if (reds[i][j] == 0.) { alphas[i][j] = false; }
		}

		if (greenSimple == -1) {
		    greens[i][j] = (Double)scriptEngine.eval(green);
		}
		else {
		    greens[i][j] = data[j + y1][i + x1][greenSimple];
		    if (greens[i][j] == 0.) { alphas[i][j] = false; }
		}

		if (blueSimple == -1) {
		    blues[i][j] = (Double)scriptEngine.eval(blue);
		}
		else {
		    blues[i][j] = data[j + y1][i + x1][blueSimple];
		    if (blues[i][j] == 0.) { alphas[i][j] = false; }
		}

		if (min == max  &&  alphas[i][j]) {
		    redrad.add(reds[i][j]);
		    greenrad.add(greens[i][j]);
		    bluerad.add(blues[i][j]);
		}
	    }
	}

	if (min == max) {
	    if (redrad.size() == 0) {
		throw new ScriptException("No non-empty pixels were found");
	    }

	    Collections.sort(redrad);
	    Collections.sort(greenrad);
	    Collections.sort(bluerad);
	
	    int redIndex5 = Math.max((int)Math.floor(redrad.size() * 0.05), 0);
	    int redIndex95 = Math.min((int)Math.ceil(redrad.size() * 0.95), redrad.size() - 1);

	    int greenIndex5 = Math.max((int)Math.floor(greenrad.size() * 0.05), 0);
	    int greenIndex95 = Math.min((int)Math.ceil(greenrad.size() * 0.95), greenrad.size() - 1);

	    int blueIndex5 = Math.max((int)Math.floor(bluerad.size() * 0.05), 0);
	    int blueIndex95 = Math.min((int)Math.ceil(bluerad.size() * 0.95), bluerad.size() - 1);

	    min = Math.min(redrad.get(redIndex5), Math.min(greenrad.get(greenIndex5), bluerad.get(blueIndex5)));
	    max = Math.max(redrad.get(redIndex95), Math.max(greenrad.get(greenIndex95), bluerad.get(blueIndex95)));
	}

	BufferedImage bufferedImage = new BufferedImage(x2 - x1, y2 - y1, BufferedImage.TYPE_4BYTE_ABGR);
	for (int i = 0;  i < x2 - x1;  i++) {
	    for (int j = 0;  j < y2 - y1;  j++) {
		int r = Math.min(Math.max((int)Math.floor((reds[i][j] - min) / (max - min) * 256), 0), 255);
		int g = Math.min(Math.max((int)Math.floor((greens[i][j] - min) / (max - min) * 256), 0), 255);
		int b = Math.min(Math.max((int)Math.floor((blues[i][j] - min) / (max - min) * 256), 0), 255);

		int abgr = new Color(r, g, b).getRGB();
		if (!alphas[i][j]) {
		    abgr &= 0x00ffffff;
		}
		bufferedImage.setRGB(i, j, abgr);
	    }
	}

	ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
	ImageIO.write(bufferedImage, "PNG", byteArrayOutputStream);

	if (base64) {
	    return Base64.encode(byteArrayOutputStream.toByteArray());
	}
	else {
	    return byteArrayOutputStream.toByteArray();
	}
    }

}
