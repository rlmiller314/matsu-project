package org.occ.matsu;

public class LngLat {
    public String tileName;
    public String timeStamp;
    public String identifier;
    public double longitude;
    public double latitude;
    public String metadata;

    public LngLat(String tileName_, String timeStamp_, String identifier_, double longitude_, double latitude_, String metadata_) {
	tileName = tileName_;
	timeStamp = timeStamp_;
	identifier = identifier_;
	longitude = longitude_;
	latitude = latitude_;
	metadata = metadata_;
    }
}
