package org.occ.matsu;

import org.occ.matsu.ByteOrder;
import org.occ.matsu.ZeroSuppressed;
import org.occ.matsu.GeoPictureWithMetadata;

class GeoPictureSerializer {
    public static void main(String[] argv) {
	System.out.println("begin");

	ByteOrder byteOrder1 = ByteOrder.LittleEndian;
	ByteOrder byteOrder2 = ByteOrder.BigEndian;
	ByteOrder byteOrder3 = ByteOrder.NativeEndian;
	ByteOrder byteOrder4 = ByteOrder.IgnoreEndian;

	java.nio.ByteBuffer bb;

	ZeroSuppressed zeroSuppressed = new ZeroSuppressed();
	zeroSuppressed.setIndex(1234567890L);
	// zeroSuppressed.setStrip(bb);



	System.out.println("end");
    }
}
