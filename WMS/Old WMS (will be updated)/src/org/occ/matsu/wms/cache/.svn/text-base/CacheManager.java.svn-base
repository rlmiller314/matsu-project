package org.occ.matsu.wms.cache;

import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.ArrayList;

import org.occ.matsu.wms.servlet.OCCRequest;
import org.occ.matsu.wms.servlet.OCCWMSConfiguration;
import org.occ.matsu.wms.servlet.OCCWMSEntry;

/**
 * CacheManager is responsible for connecting to a cache of images and broakering requests
 * to a from the caches.
 *
 *
 * @author alevine@texeltek.com
 *
 */
public class CacheManager {

    private ArrayList<OCCCache> caches;

    public CacheManager() {
        caches = new ArrayList<OCCCache>();
    } // end constructor

    public CacheManager(OCCWMSConfiguration conf) {
        caches = new ArrayList<OCCCache>();

        ArrayList<OCCWMSEntry> entries = conf.getLayers();
        for (int x = 0; x < entries.size(); x++) {
            OCCCache curCache = OCCCacheFactory.getOCCCache(entries.get(x));
            if (curCache != null) {
                caches.add(curCache);
            }
        }
    } // end constructor


    // for now we ignore projection
    public BufferedImage getImage(
            String layer, String style, String projection,
            int w, int h, String bbox) {
        BufferedImage retImage = null;

        OCCCache imageCache = null;
        for (OCCCache curCache : caches) {

            if (curCache.hasLayerStyle(layer, style)) {
                imageCache = curCache;
                break;
            }
        }

        if (imageCache == null) {
            retImage = getErrorImage(w, h, bbox, "Couldn't find cache");
            return retImage;
        }

        //System.out.println("Using cache " + imageCache.getClass().getCanonicalName());

        try{
            //retImage = imageCache.getImage(w, h, bb);
            retImage = imageCache.getImage(layer, style, projection, w, h, bbox);
            if (retImage == null) {
                retImage = getErrorImage(w, h, bbox, "pulled a null image");
            }
        } catch(IOException ioe) {
            retImage = getErrorImage(w, h, bbox, "IO Exception instead of image");
            ioe.printStackTrace();
        }

        return retImage;
    } // end getImage


    public static BufferedImage getErrorImage(int w, int h, String bbox) {
        BufferedImage retImage = new BufferedImage(w, h, BufferedImage.TYPE_4BYTE_ABGR);

        for (int x = 0; x < w; x++) {
            for (int y = 0; y < h; y++) {
                if ((x < 5 || x > w - 5) || (y < 5 || y > h - 5)) {
                    retImage.setRGB(x, y, 0xffff0000);
                }
            }
        }
        Font f = new Font("Serif", Font.BOLD, 14);
        String bStr = "No image at: " + bbox;
        Graphics gr = retImage.getGraphics();

        gr.setFont(f);
        gr.setColor(Color.BLUE);
        gr.drawString(bStr, 20, 20);
        gr.dispose();

        return retImage;
    } // end getErrorImage

    public static BufferedImage getErrorImage(int w, int h, String bbox, String message) {
        BufferedImage retImage = new BufferedImage(w, h, BufferedImage.TYPE_4BYTE_ABGR);

        for (int x = 0; x < w; x++) {
            for (int y = 0; y < h; y++) {
                if ((x < 5 || x > w - 5) || (y < 5 || y > h - 5)) {
                    retImage.setRGB(x, y, 0xffff0000);
                }
            }
        }
        Font f = new Font("Serif", Font.BOLD, 14);
        String bStr = "No image at: " + bbox + " " + message;
        Graphics gr = retImage.getGraphics();

        gr.setFont(f);
        gr.setColor(Color.BLUE);
        gr.drawString(bStr, 20, 20);
        gr.dispose();

        return retImage;
    }

}
