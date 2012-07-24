/*
 * MatsuWMS
 *
 * This is the main class that will respond to the Web Mapping
 * Service query.
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

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.io.PrintWriter;

import javax.imageio.ImageIO;
import javax.servlet.ServletConfig;
import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.ServletOutputStream;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;

import org.occ.matsu.wms.cache.CacheManager;
import org.occ.matsu.coords.GeoSpatialUtilities;
import org.occ.matsu.wms.logging.OCCStartupException;



/**
 * Responds to the WMS query, with limitations set on that
 * query.
 * <p/>
 * The image type is image/png, there is a maximum of
 * 16 layers, and the image has a maximum size of
 * 512 x 256.
 */
public class MatsuWMS extends HttpServlet{

    protected static Logger logger;
    protected static String configPath;
    protected static OCCWMSConfiguration config;
    protected static OCCRequestHandler reqHandler;

    protected static CacheManager cacheManager;

    protected static boolean showDebug = false;

    // read in the config data
    @Override
    public void init (ServletConfig conf) throws ServletException{
        super.init (conf);

        // set up the logger
        logger = Logger.getLogger(this.getClass());

        // get the user XML configuration path
        ServletContext sc = conf.getServletContext();
        configPath = conf.getInitParameter("config.path");
        configPath = sc.getRealPath(configPath);
        logger.info("The path is: " + configPath); // TTS

        try{
            startup();
        } catch(OCCStartupException sue){
            logger.error(sue);
        }

    } // end init

    public synchronized static void startup() throws OCCStartupException{
        // read in the config file
        config = new OCCWMSConfiguration(configPath);
        cacheManager = new CacheManager(config);

    } // end startup



    @Override
    protected void doGet (HttpServletRequest request,
                          HttpServletResponse response)
            throws ServletException, IOException {
        doPost (request, response);
    }

    @Override
    protected void doPost (HttpServletRequest request,
                           HttpServletResponse response)
            throws ServletException, IOException {
        try {
            processRequest (request, response);
        }
        catch (Exception e) {
            e.printStackTrace();
        }
    } // end doPost


    protected void processRequest(HttpServletRequest request,
                                  HttpServletResponse response)
            throws IOException{
        // first steps - send the config as output
//        response.setContentType("text/html");
//        PrintWriter pw = response.getWriter();
//        pw.write("Hello World!");
//        ArrayList<OCCWMSEntry> layers = config.getLayers();
//        for(int x = 0; x < layers.size(); x++){
//            pw.write(layers.get(x).toString());
//        }
//
//        pw.flush();
//        pw.close();
        logger.info(request.getQueryString());

        OCCRequest occReq = new OCCRequest(request);
        String requestType = request.getParameter("REQUEST");

        PrintWriter pr;
        // getcapabilities
        if(requestType.equalsIgnoreCase("GetCapabilities")){
            //response.setContentType("application/vnd.ogc.se_xml");
            response.setContentType("text/xml");
            pr = response.getWriter();
            pr.write(this.getCapabilitiesXML());
            pr.flush();
            pr.close();

        } else if(requestType.equalsIgnoreCase("GetMap")){
            // get an image
            int w = occReq.getWidth();
            int h = occReq.getHeight();

            BufferedImage retImage =
                    new BufferedImage(w, h, BufferedImage.TYPE_4BYTE_ABGR);
            Graphics gr = retImage.getGraphics();
            String[] layers = occReq.layers;
            String[] styles = occReq.styles;
            for(int x = 0; x < layers.length; x++){
                BufferedImage curImage = cacheManager.getImage(
                        layers[x], styles[x], null, w, h, occReq.bounds);
                // this is a simple fix for now
                if(occReq.trans){
                    for(int i = 0; i < w; i++){
                        for(int j = 0; j < h; j++){
                            int curRGB = curImage.getRGB(i, j);

                            curRGB = 0x88ffffff & curRGB;
                            curImage.setRGB(i, j, curRGB);
                        }
                    }
                }

                gr.drawImage(curImage, 0, 0, w, h, 0, 0, w, h, null);

            }

            if(showDebug){
                // add debug information to image
                GeoSpatialUtilities.addDebugInfo(occReq.bounds, retImage);
            }


//            response.setContentType("text/html");
//            pr = response.getWriter();
//            pr.write(occReq.toString());
//            pr.flush();
//            pr.close();

            ServletOutputStream os = response.getOutputStream();
            response.setContentType("image/png");
            ImageIO.write(retImage, "png", os);
            os.close();

        } else {
            // send an xml error
        }// end processing request

        // getmap

    } // end processRequest


    private String getCapabilitiesXML(){
        StringBuffer sb = new StringBuffer();
        sb.append("<?xml version='1.0' encoding=\"UTF-8\"?>\n");
        sb.append("<WMS_Capabilities version=\"1.3.0\" xmlns=\"http://www.opengis.net/wms\"\n");
        sb.append("xmlns:xlink=\"http://www.w3.org/1999/xlink\"\n");
        sb.append("xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n");
        sb.append("xsi:schemaLocation=\"http://www.opengis.net/wms\n" +
                "http://schemas.opengis.net/wms/1.3.0/capabilities_1_2_0.xsd\">\n");
        sb.append("<!-- Service Metadata -->\n");
        sb.append("<Service>\n");
        sb.append("  <!-- The WMT-defined name for this type of service -->\n");
        sb.append("  <Name>WMS</Name>\n");
        sb.append("  <!-- Human-readable title for pick lists -->\n");
        sb.append("  <Title>Acme Corp. Map Server</Title>\n");
        sb.append("  <!-- Narrative description providing additional information -->\n");
        sb.append("  <Abstract>Map Server maintained by Acme Corporation.  Contact: webmaster@wmt.acme.com.  High-quality maps showing roadrunner nests and possible ambush locations.</Abstract>\n");
        sb.append("  <KeywordList>\n");
        sb.append("    <Keyword>TileSet</Keyword>\n");
        sb.append("    <Keyword>Delta</Keyword>\n");
        sb.append("  </KeywordList>\n");
        sb.append("  <!-- Top-level web address of service or service provider.  See also OnlineResource elements under <DCPType>. -->\n");
        sb.append("  <OnlineResource xmlns:xlink=\"http://www.w3.org/1999/xlink\" xlink:type=\"simple\" xlink:href=\"http://hostname/\" />\n");
        sb.append("  <!-- Contact information -->\n");
        sb.append("  <ContactInformation>\n");
        sb.append("    <ContactPersonPrimary>\n");
        sb.append("      <ContactPerson>Bob Grossman</ContactPerson>\n");
        sb.append("      <ContactOrganization>OCC</ContactOrganization>\n");
        sb.append("    </ContactPersonPrimary>\n");
        sb.append("    <ContactPosition>Computer Scientist</ContactPosition>\n");
        sb.append("    <ContactAddress>\n");
        sb.append("      <AddressType>postal</AddressType>\n");
        sb.append("      <Address>NASA Goddard Space Flight Center</Address>\n");
        sb.append("      <City>Greenbelt</City>\n");
        sb.append("      <StateOrProvince>MD</StateOrProvince>\n");
        sb.append("      <PostCode>20771</PostCode>\n");
        sb.append("      <Country>USA</Country>\n");
        sb.append("    </ContactAddress>\n");
        sb.append("    <ContactVoiceTelephone>+1 301 555-1212</ContactVoiceTelephone>\n");
        sb.append("    <ContactElectronicMailAddress>user@host.com</ContactElectronicMailAddress>\n");
        sb.append("  </ContactInformation>\n");
        sb.append("  <!-- Fees or access constraints imposed. -->\n");
        sb.append("  <Fees>none</Fees>\n");
        sb.append("  <AccessConstraints>none</AccessConstraints>\n");
        sb.append("  <LayerLimit>16</LayerLimit>\n");
        sb.append("  <MaxWidth>512</MaxWidth>\n");
        sb.append("  <MaxHeight>256</MaxHeight>\n");
        sb.append("</Service> \n");



        sb.append("<Capability>\n");
        sb.append("  <Request>\n");
        sb.append("    <GetCapabilities>\n");
        sb.append("      <Format>text/xml</Format>\n");
        sb.append("      <Format>application/vnd.ogc.wms_xml</Format>\n");
        sb.append("      <DCPType>\n");
        sb.append("        <HTTP>\n");
        sb.append("          <Get>\n");
        sb.append("            <OnlineResource xmlns:xlink=\"http://www.w3.org/1999/xlink\" xlink:type=\"simple\" xlink:href=\"http://hostname/path?\" />\n");
        sb.append("          </Get>\n");
        sb.append("          <Post>\n");
        sb.append("            <OnlineResource xmlns:xlink=\"http://www.w3.org/1999/xlink\" xlink:type=\"simple\" xlink:href=\"http://hostname/path?\" />\n");
        sb.append("          </Post>\n");
        sb.append("        </HTTP>\n");
        sb.append("      </DCPType>\n");
        sb.append("    </GetCapabilities>\n");


        // do getmap
        sb.append("    <GetMap>\n");
//        sb.append("      <Format>image/gif</Format>\n");
        sb.append("      <Format>image/png</Format>\n");
//        sb.append("      <Format>image/jpeg</Format>\n");
        sb.append("      <DCPType>\n");
        sb.append("        <HTTP>\n");
        sb.append("          <Get>\n");
        sb.append("            <!-- The URL here for invoking GetCapabilities using HTTP GET is only a prefix to which a query string is appended. -->\n");
        sb.append("            <OnlineResource xmlns:xlink=\"http://www.w3.org/1999/xlink\" xlink:type=\"simple\" xlink:href=\"http://hostname/path?\" />\n");
        sb.append("          </Get>\n");
        sb.append("        </HTTP>\n");
        sb.append("      </DCPType>\n");
        sb.append("    </GetMap>\n");
        sb.append("  </Request>\n");
        sb.append("  <Exception>\n");
        sb.append("    <Format>XML</Format>\n");
        sb.append("    <Format>INIMAGE</Format>\n");
        sb.append("    <Format>BLANK</Format>\n");
        sb.append("  </Exception>\n");


        sb.append(config.getCapabilities("  "));
        sb.append("</Capability>\n");
        sb.append("</WMS_Capabilities>\n");

        return sb.toString();
    } // end getCapabilitiesXML

} // end OCCWMS
