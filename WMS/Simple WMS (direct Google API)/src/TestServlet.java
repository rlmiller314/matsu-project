import java.io.*;
import java.net.*;
import java.text.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class TestServlet extends HttpServlet
{
   protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
       String data = request.getParameter("data");
       PrintWriter out = response.getWriter();
       if(data == null) {
	   out.println("success");
       } else {
	   out.println(data);
       }
       out.close();
   }
}
