/*
 * OCCRequest
 *
 * A class to store the relevant parts of the HttpServletRequest.
 *
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

import java.awt.Color;
import java.util.List;

import javax.servlet.http.HttpServletRequest;


public class OCCRequest {

    protected String requestType;
    protected String reqString;
    protected HttpServletRequest httpReq;

    protected String version;
    protected String reqType;


    protected String[] layers;
    protected String[] styles;

    protected String crs;

    protected String projection;

    protected String bounds;
    protected int width = 512;
    protected int height = 256;

    protected String format;

    protected boolean trans;
    protected int bgcolor;


    /**
     * Fills the properties of the OCCRequest by
     * parsing the request string.
     * <p/>
     * @see #parseRequestString
     */
    public OCCRequest(HttpServletRequest req){
        httpReq = req;
        reqString = req.getQueryString();
        parseRequestString();
    } // end constructor

//    public OCCRequest(String req){
//        reqString = req;
//
//        parseRequestString(reqString);
//    } // end constructor


    /**
     * Parses the request string, setting internal
     * variables.
     * <p/>
     * The parsed request parameters are: "VERSION", "LAYERS",
     * "STYLES", "CRS", "BBOX", "WIDTH", "HEIGHT", "TRANSPARENT"
     */
    private void parseRequestString(){

        requestType = httpReq.getParameter("REQUEST");
        if(requestType.equalsIgnoreCase("GetCapabilities")){
            return;
        }

        version = httpReq.getParameter("VERSION");
        //reqType = httpReq.getParameter("REQUEST");

        String layer = httpReq.getParameter("LAYERS");
        layers = layer.split(",");
        String style = httpReq.getParameter("STYLES");
        styles = style.split(",");

        crs = httpReq.getParameter("CRS");

        //bounds = this.parseBoundingBox(httpReq.getParameter("BBOX"));
        bounds = httpReq.getParameter("BBOX").replace(",", "_");

        width = Integer.parseInt(httpReq.getParameter("WIDTH"));
        height = Integer.parseInt(httpReq.getParameter("HEIGHT"));

        trans = Boolean.parseBoolean(httpReq.getParameter("TRANSPARENT"));

    } // end parseRequestString

    public int getWidth(){
        return width;
    }
    public int getHeight(){
        return height;
    }
    public String toString(){
        return reqString;
    }

}
