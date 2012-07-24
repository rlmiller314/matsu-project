/*
 * OCCWMSConfiguration
 *
 * This class stores the list of layers available via
 * the web mapping service.
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
package org.occ.matsu.wms.servlet;

import java.util.ArrayList;
import java.io.File;
import java.io.IOException;
import java.lang.Math;
import java.util.Properties;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.apache.log4j.Logger;
import org.occ.matsu.wms.logging.OCCStartupException;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;


/**
 * This class stores the list of layers available to the
 * WMS and provides methods to see which layers are available.
 * <p/>
 * Each layer is an OCCWMSEntry, which stores the following
 * properties: "layername", "stylename", "bbox",
 *     and possibly "datald" (if data are in a local directory),
 *     or "zookeepers" (if data are in Accumulo)
 */
public class OCCWMSConfiguration {

    protected ArrayList<OCCWMSEntry> layers;
    protected String sourceFile;
    protected static Logger logger = Logger.getLogger(OCCWMSConfiguration.class);

    /**
     * The empty constructor just initializes the list of layers
     * as an empty list.
     */
    public OCCWMSConfiguration(){
        layers = new ArrayList<OCCWMSEntry>();
    }

    /**
     * Initializes the list of layers and adds the entry
     * in the argument.
     * 
     * @param the entry to add to the layer
     */
    public OCCWMSConfiguration(OCCWMSEntry e){
        layers = new ArrayList<OCCWMSEntry>();
        layers.add(e);
    }

    /**
     * Initializes the list of layers and adds the contents
     * of the list in the argument.
     */
    public OCCWMSConfiguration(ArrayList<OCCWMSEntry> l){
        layers = new ArrayList<OCCWMSEntry>();
        layers.addAll(l);
    }

    /**
     * Initializes the list of layers add adds the contents
     * of the list as described in the file.
     */
    public OCCWMSConfiguration(String file){
        layers = new ArrayList<OCCWMSEntry>();
        //System.out.println("Working from file: " + file);
        sourceFile = file;
        try{
            parseConfig(file);
        } catch(OCCStartupException se){
            logger.error(se);
        }
    }

    /**
     * Returns true if the argument is the name of a
     * layer stored in the configuration's internal list,
     * else false.
     *
     * @param   l   the string name of the desired layer
     *
     * @return  true if a layer of that name exists, else false
     */
    public boolean containsLayer(String l){
        boolean retBoolean = false;
        for(int x = 0; x < layers.size(); x++){
            OCCWMSEntry e = layers.get(x);
            if(e == null){
                continue;
            }
            if(e.getLayerName().equals(l)){
                return true;
            }
        }
        return retBoolean;
    }

    /**
     * If the requested layer exists, return it, else return null.
     *
     * @param   l   the string name of the desired layer
     *
     * @return  the layer, as an OCCWMSEntry, if it exists, else null
     */
    public OCCWMSEntry getLayer(String l){
        for(int x = 0; x < layers.size(); x++){
            OCCWMSEntry e = layers.get(x);
            if(e == null){
                continue;
            }
            if(e.getLayerName().equals(l)){
                return e;
            }
        }
        return null;
    }

    /**
     * Returns a list of available layers.
     */
    public ArrayList<OCCWMSEntry> getLayers(){
        return layers;
    }

    /**
     * Parses the configuration file, adding all layers to
     * an internal list.
     *
     * @throws  OCCStartupException, if the named configuration
     *          file does not exist.
     */
    private void parseConfig(String confFile) throws OCCStartupException{
        File file = new File(confFile);
        if(! file.isFile()){
            throw new OCCStartupException(this.getClass().getName() + " parseConfig",
                    "Startup Config file does not exist",
                    "Make sure the config file exists.");
        }

        try{
            DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
            DocumentBuilder db = dbf.newDocumentBuilder();
            Document doc = db.parse(file);
            Element e = doc.getDocumentElement();
            getEntries(e);
        }  catch(ParserConfigurationException pce){
            logger.error(pce);
            return;
        } catch (SAXException e) {
            // TODO Auto-generated catch block
            logger.error(e);
            return;
        } catch (IOException e) {
            // TODO Auto-generated catch block
            logger.error(e);
            return;
        }

    } // end parseConfig


    /**
     * Parses the passed element, adding the layer to an
     * internal list.
     */
    private void getEntries(Element e){
        if(e == null){
            return;
        }
        NodeList nl = e.getChildNodes();
        for(int x = 0; x < nl.getLength(); x++){
            if(nl.item(x).getNodeType() == Node.ELEMENT_NODE){
                //System.out.println(nl.item(x).getNodeName());
                if(nl.item(x).getNodeName().equals("wmsentry")){
                    OCCWMSEntry ent = parseWMSEntry((Element)nl.item(x));
                    //System.out.println(ent);
                    layers.add(ent);
                }
            }
        }
    } // end getEntries


    /**
     * Parses the argument for the layer properties
     * and returns a new OCCWMSEntry with the properties
     * set.
     * <p/>
     * Properties not named in the argument will just have
     * the value 'null'.
     */
    private OCCWMSEntry parseWMSEntry(Element e){
        String layerName = null;
        String styleName = null;
        String tld = null;
        String bounds = null;
        if(e == null){
            return null;
        }
        NodeList nl = e.getChildNodes();
        Properties props = new Properties();
        for(int x = 0; x < nl.getLength(); x++){
            if(nl.item(x).getNodeType() == Node.ELEMENT_NODE){
                String key = nl.item(x).getNodeName().trim();
                String val = null;
                //System.out.println(nl.item(x).getNodeName());
                NodeList nl2 = nl.item(x).getChildNodes();
                if(nl2 != null && nl2.getLength() > 0){
                    val = nl2.item(0).getNodeValue().trim();
                }
                if(key.equals("layername")){
                    layerName = val;
                } else if(key.equals("stylename")){
                    styleName = val;
                } else if(key.equals("datatld")){
                    tld = val;
                } else if(key.equals("bounds")){
                    bounds = val;
                }
                props.put(key, val);

            }
        }
        OCCWMSEntry retVal = new OCCWMSEntry(layerName, styleName, tld, bounds);
        retVal.setProperties(props);
        return retVal;
    } // end parseWMSEntry


    /**
     * Returns a string, formatted in XML, that identifies the
     * available layers and their properties.
     *
     * @return  the formatted string listing available layers
     *          that identify the available layers, their
     *          projection, the range of available
     *          bounding boxes, and style.
     */
    public String getCapabilities(String offset){
        StringBuffer sb = new StringBuffer();
        sb.append("<Layer>\n");
        for(int x = 0; x < layers.size(); x++){
            sb.append(offset + "<Layer>\n");
            sb.append(offset + offset + "<Name>" + layers.get(x).layerName + "</Name>\n");

            sb.append(offset + offset + "<Title>" + layers.get(x).layerName + "</Title>\n");
            sb.append(offset + offset + "<CRS>" + "EPSG:4326" + "</CRS>\n");

            String[] vals = layers.get(x).getBounds().split("_");
            double v0 = Double.parseDouble(vals[0]);
            double v1 = Double.parseDouble(vals[1]);
            double v2 = Double.parseDouble(vals[2]);
            double v3 = Double.parseDouble(vals[3]);
    
            double minX = Math.min(v0, v2);
            double minY = Math.min(v1, v3);
            double maxX = Math.max(v0, v2);
            double maxY = Math.max(v1, v3);
            sb.append(offset + offset + "<BoundingBox CRS=\"EPSG:4326\" minx=\"" +
                    minX +
                    "\" miny=\"" + minY +
                    "\" maxx=\"" + maxX +
                    "\" maxy=\"" + maxY +
                    "\" />\n");


            sb.append(offset + offset + "<Style>\n");

            sb.append(offset + offset + offset + "<Name>" + layers.get(x).styleName + "</Name>\n");
            sb.append(offset + offset + offset + "<Title>" + layers.get(x).styleName + "</Title>\n");
// put in bounds
            sb.append(offset + offset + "</Style>\n");

            sb.append(offset + "</Layer>\n");
        }
        sb.append("</Layer>\n");

        return sb.toString();
    } // end getCapabilities


    /**
     * Converts the internal list of layers to a newline-separated
     * string containing all of the layer names.
     *
     * @return  the list of layer names, separated by newlines
     */
    public String toString(){
        StringBuffer sb = new StringBuffer();
        for(int x = 0; x < layers.size(); x++){
            sb.append(layers.get(x) + "\n");
        }
        return sb.toString();
    } // end toString

} // end OCCWMSConfiguration
