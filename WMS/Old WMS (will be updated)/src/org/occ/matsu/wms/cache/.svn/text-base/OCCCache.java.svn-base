package org.occ.matsu.wms.cache;

import java.awt.image.BufferedImage;
import java.io.IOException;

import org.occ.matsu.wms.servlet.OCCRequest;
import org.occ.matsu.wms.servlet.OCCWMSEntry;

/**
 * OCCCache is an interface for caches
 * 
 * @author alevine@texeltek.com
 *
 */
public interface OCCCache {

	public void initialize(OCCWMSEntry conf) throws IOException;
	
	public OCCWMSEntry getConfiguration();
	
	public BufferedImage getImage(int w, int h, String bbox) throws IOException;
	public BufferedImage getImage(String layer, String style, String projection,
            int w, int h, String bbox) throws IOException;
	
	public boolean hasLayerStyle(String layer, String style);
	
	public String getBounds();
	public String getLayerName();
	public String getStyleName();
	
}
