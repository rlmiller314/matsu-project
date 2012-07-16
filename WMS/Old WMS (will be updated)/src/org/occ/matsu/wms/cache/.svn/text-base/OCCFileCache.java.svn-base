package org.occ.matsu.wms.cache;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

import javax.imageio.ImageIO;

import org.occ.matsu.wms.servlet.OCCRequest;
import org.occ.matsu.wms.servlet.OCCWMSEntry;


public class OCCFileCache implements OCCCache{

	protected OCCWMSEntry occ_entry = null;
	private String occ_dirName = null;
	private File occ_tld = null;
	
	
	public OCCFileCache(OCCWMSEntry ent){
		occ_entry = ent;
		try{
			this.initialize(ent);
		} catch(IOException ioe){
			ioe.printStackTrace();
		}
	}
	
	@Override
	public String getBounds() {
		return occ_entry.getBounds();
	}

	@Override
	public OCCWMSEntry getConfiguration() {
		return occ_entry;
	}

	@Override
	public BufferedImage getImage(int w, int h, String bbox) throws IOException {
        return null;
//		double minX = bb.getMinX();
//		
//		String fileName = OCCWMSEntry.boxToString(bb);
//		
//		fileName = occ_dirName + minX + File.separator + fileName + "_" + w + "x" + h + ".png";
//
//		System.out.println("Opening file: " + fileName);
//		
//		File f2open = new File(fileName);
//		BufferedImage retImage = ImageIO.read(f2open);
//		
//		return retImage;
	}

	@Override
	public BufferedImage getImage(
                String layer, String style, String projection,
                int w, int h, String bbox)
            throws IOException{
		return this.getImage(w, h, bbox);
	}
	
	@Override
	public boolean hasLayerStyle(String layer, String style){
		if(occ_entry.getLayerName().equalsIgnoreCase(layer) &&
				occ_entry.getStyleName().equalsIgnoreCase(style)){
			return true;
		}
		return false;
		
	} // end hasLayerStyle
	
	@Override
	public String getLayerName() {
		return occ_entry.getLayerName();
	}

	@Override
	public String getStyleName() {
		return occ_entry.getStyleName();
	}

	@Override
	public void initialize(OCCWMSEntry conf) throws IOException {

		occ_dirName = conf.getDirectory();
		
		occ_tld = new File(occ_dirName);
		if(! occ_tld.exists()){
			throw new IOException(occ_dirName + " does not exists.");
		}
		if(occ_tld.isFile()){
			throw new IOException(occ_dirName + " is not a directory.");
		}
		if(! occ_dirName.endsWith(File.separator)){
			occ_dirName = occ_dirName + File.separator;
		}
		
		String[] listDir = occ_tld.list();
		if(listDir == null || listDir.length == 0){
			throw new IOException(occ_dirName + " contains no sub directories.");
		}
	}

}
