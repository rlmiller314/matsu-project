package org.occ.matsu.wms.cache;

import java.io.IOException;

import org.occ.matsu.wms.servlet.OCCWMSEntry;

public class OCCCacheFactory {

    public static OCCCache getOCCCache(OCCWMSEntry entry){

        if(entry.getDirectory() != null){

            return new OCCFileCache(entry);

        } else if(entry.getProperty("zookeepers") != null){

            OCCAccumuloCache tester = new OCCAccumuloCache(entry);
            if (tester.isConnected()) {
                return tester;
            }
        }

        return null;

    } // end constructor

} // end OCCCacheFactory
