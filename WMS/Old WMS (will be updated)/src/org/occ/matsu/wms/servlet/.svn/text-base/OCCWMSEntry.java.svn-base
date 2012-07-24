/*
 * OCCWMSEntry
 *
 * This class stores four strings: a layer name,
 * style name, directory, and bounding box, identifying
 * an available set of images for the WMS.
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

import java.util.Properties;


public class OCCWMSEntry {

    protected String layerName;
    protected String styleName;
    protected String directory;
//    protected String projection;
    protected String bounds;

    protected Properties wmsProps;

    public OCCWMSEntry(){
        layerName = null;
        styleName = null;
        directory = null;
        bounds = null;

    } // end constructor

    public OCCWMSEntry(String l, String s, String d, String b){
        layerName = l;
        styleName = s;
        directory = d;
        if (b != null) {
            bounds = b.replace(",", "_");
        }
    }

    public OCCWMSEntry(Properties props){
        wmsProps = props;
    }
    public String getProperty(String p){
        return (String)wmsProps.get(p);
    }

    public void setLayerName(String l){
        layerName = l;
    }
    public void setStyleName(String s){
        styleName = s;
    }
    public void setDirectory(String d){
        directory = d;
    }

    public void setProperties(Properties props){
        wmsProps = props;
    }

    public String getLayerName(){
        return layerName;
    }
    public String getStyleName(){
        return styleName;
    }
    public String getDirectory(){
        return directory;
    }
    public String getBounds(){
        return bounds;
    }

    public String toString(){
        StringBuffer sb = new StringBuffer();
        sb.append("Layer Name: " + layerName + "\n");
        sb.append("Style Name: " + styleName + "\n");
        sb.append("Directory:  " + directory + "\n");
        sb.append("Bounds:     " + bounds + "\n");
        return sb.toString();
    }

}
