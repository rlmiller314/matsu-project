package org.occ.matsu.wms.logging;

public class OCCStartupException extends Exception{

	protected String cl;
	protected String er;
	protected String sug;
	
	
	public OCCStartupException(String classMethodName, String errorMessage, String suggestion){
		cl = classMethodName;
		er = errorMessage;
		sug = suggestion;
	}
	
	@Override
	public String toString(){
		StringBuffer sb = new StringBuffer();
		sb.append("Class Name:    " + cl + "\n");
		sb.append("Error Message: " + er + "\n");
		sb.append("Suggestion:    " + sug + "\n");
		
		return sb.toString();
	}
	
} // end OCCStartupException
