/*
 * OCCAccumuloCache
 *
 * A class to pull images from Accumulo given a WMS request.
 *
 * @version %I%, %G%
 *
 * Copyright (C) 2008-2012  Open Cloud Consortium.
 *
 * This file is part of Matsu.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.occ.matsu.wms.cache;

import java.awt.image.BufferedImage;
import java.util.Hashtable;
import java.io.IOException;

import org.occ.matsu.coords.GeoSpatialUtilities;
import org.occ.matsu.accumulo.ImageGetter;
import org.occ.matsu.wms.servlet.OCCRequest;
import org.occ.matsu.wms.servlet.OCCWMSEntry;

/**
 * OCCCache is an interface for caches
 *
 * @author alevine@texeltek.com
 *
 */
public class OCCAccumuloCache implements OCCCache {

    private Hashtable<String, String[]> layerStyle = null;
    private boolean connected = false;
    protected OCCWMSEntry occ_entry = null;
    protected String layer = null;
    protected String style = null;

    private ImageGetter investigator = null;


	public OCCAccumuloCache(OCCWMSEntry ent) {
		occ_entry = ent;
		try{
			this.initialize(ent);
		} catch(IOException ioe){
			ioe.printStackTrace();
		}
	}

    @Override
    public void initialize(OCCWMSEntry conf) throws IOException {
        layerStyle = new Hashtable<String, String[]>();
        layer = conf.getLayerName();
        style = conf.getStyleName();
        String zookeepers = conf.getProperty("zookeepers");

        investigator = new ImageGetter(zookeepers);

        if( ! investigator.isConnected()) {
            connected = false;
            return;
        }
    }

    /**
     * Return false if the connection to the zookeeper/cache failed.
     */
    public boolean isConnected() {
        return connected;
    }
	

    /**
     * Return the protected configuration used during
     * initialization.
     */
    public OCCWMSEntry getConfiguration() {
        return occ_entry;
    }

    /**
     * Implements the OCCCache 'getImage' function using its
     * internal seting for layer and style.
     *
     * @param   w   image width in pixels
     * @param   h   image height in pixels
     * @param   bb  the bounding box describing image boundaries
     *
     * @return  a BufferedImage that matches the request,
     *          using this OCCCache's internal setting for
     *          layer and style, else null if the layer and
     *          style are not set.
     */
    public BufferedImage getImage(int w, int h, String bbox)
            throws IOException {
        if ( (layer != null) && (style != null) ) {
            return getImage(layer, style, null, w, h, bbox);
        } else {
            return null;
        }
    }

    /**
     * Implements the OCCCache 'getImage' function using its
     * internal seting for layer and style.
     *
     * @param   argLayer      the layer name, like 'haiti'
     * @param   argStyle      the style name
     * @param   projection  currently discarded and set to null
     * @param   w           image width in pixels
     * @param   h           image height in pixels
     * @param   bb          the bounding box describing image boundaries
     *
     * @return  a BufferedImage that matches the request.
     */
    public BufferedImage getImage(
            String _layer, String _style, String projection,
            int w, int h, String bbox)
                throws IOException {

        return investigator.getImage(bbox, _layer, _style, projection, w, h);
    }

    /**
     * Returns true if the stated layer contains images of the
     * stated style.
     */
    public boolean hasLayerStyle(String _layer, String _style) {
//        String[] styles = layerStyle.get(_layer);
//        if (styles != null) {
//            for(String stl : styles){
//                if(stl.equalsIgnoreCase(_style)){
//                    return true;
//                }
//            }
//        }
//        return false;
        return (layer.equals(_layer) && style.equals(_style));
    }

    /**
     * Returns the overall bounds of this image set.
     */
    public String getBounds() {
		return occ_entry.getBounds();
    }

    /**
     * Returns the protected layer name.
     */
    public String getLayerName() {
        return layer;
    }

    /**
     * Returns the protected style value.
     */
    public String getStyleName() {
        return style;
    }
}
