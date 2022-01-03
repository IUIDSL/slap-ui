package edu.indiana.sice.idsl.slap;
/* Location:           /home/jjyang/Downloads/slap/WEB-INF/classes/
 * Qualified Name:     utils.TraceUserFeedback
 * JD-Core Version:    0.6.2
 */
 
import java.util.*;
import java.io.*; //IOException, PrintWriter
import java.sql.*; //Connection, Date, DriverManager, PreparedStatement, SQLException
import javax.servlet.*; //ServletException
import javax.servlet.http.*; //HttpServlet, HttpServletRequest, HttpServletResponse
 
/**	Servlet: User feedback
*/
public class TraceUserFeedback extends HttpServlet
{
  private static String API_HOST=null; //Configured in web.xml
  private static String DBHOST=null; //Configured in web.xml
  private static String DBPORT=null; //Configured in web.xml
  private static String DBSCHEMA=null;  // configured in web.xml
  private static String DBNAME=null;  // configured in web.xml
  private static String DBUSR=null;  // configured in web.xml
  private static String DBPW=null;  // configured in web.xml
  private static ServletContext CONTEXT=null;
  private static String CONTEXTPATH=null;
  private static ServletConfig CONFIG=null;
  private static ResourceBundle RESOURCEBUNDLE=null;

  public void destroy()
  {
    super.destroy();
  }

  public String updateFeedback(String cid, String gene, String like)
    throws Exception
  {
    Class.forName("org.postgresql.Driver");
    String url = "jdbc:postgresql://"+DBHOST+"/"+DBNAME;
    try
    {
      Class.forName("org.postgresql.Driver");
    }
    catch (ClassNotFoundException e) {
      e.printStackTrace();
    }

    Connection connection = null;
    try {
      connection = DriverManager.getConnection(url, DBUSR, DBPW);
    } catch (SQLException e) {
      e.printStackTrace();
    }

    try
    {
      String sql = "INSERT INTO c2b2r_slap_feedback (compound,target,userlike,inputdate) VALUES(?,?,?,?)";
      PreparedStatement pstmt = connection.prepareStatement(sql);

      pstmt.setString(1, cid);
      pstmt.setString(2, gene);
      pstmt.setString(3, like);
      pstmt.setDate(4, new java.sql.Date(System.currentTimeMillis()));

      pstmt.executeUpdate();
      pstmt.close();
    }
    catch (SQLException e) {
      e.printStackTrace();
      connection.close();

      return "0";
    }
    connection.close();

    return "1";
  }

  public void doGet(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException
  {
    String cid = request.getParameter("cid");
    String gene = request.getParameter("gene");
    String like = request.getParameter("like");

    String ret = "";
    try {
      ret = updateFeedback(cid, gene, like);
    }
    catch (Exception e) {
      e.printStackTrace();
    }

    response.setContentType("text/plain;charset=UTF-8");
    response.setHeader("Cache-Control", "no-cache");
    response.getWriter().write(ret);
  }

  public void doPost(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException
  {
    response.setContentType("text/html");
    PrintWriter out = response.getWriter();
    out.println("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">");
    out.println("<HTML>");
    out.println("<HEAD><TITLE>A Servlet</TITLE></HEAD>");
    out.println("<BODY>");
    out.println("This is "+getClass()+", using the POST method.");
    out.println("  </BODY>");
    out.println("</HTML>");
    out.flush();
    out.close();
  }

  /////////////////////////////////////////////////////////////////////////////
  /**   Read context and servlet parameters (from web.xml).
  */
  public void init(ServletConfig conf) throws ServletException
  {
    super.init(conf);
    CONTEXT=getServletContext();        // inherited method
    CONTEXTPATH=CONTEXT.getContextPath();
    CONFIG=conf;

    API_HOST=CONTEXT.getInitParameter("API_HOST");
    if (API_HOST==null) API_HOST="cheminfov.informatics.indiana.edu";
    DBHOST=CONTEXT.getInitParameter("DBHOST");
    if (DBHOST==null) DBHOST="cheminfov.informatics.indiana.edu";
    DBPORT=CONTEXT.getInitParameter("PORT");
    if (DBPORT==null) DBPORT="5432";
    DBSCHEMA=CONTEXT.getInitParameter("DBSCHEMA");
    if (DBSCHEMA==null) DBSCHEMA="public";
    DBNAME=CONTEXT.getInitParameter("DBNAME");
    if (DBNAME==null) DBNAME="chord";
    DBUSR=CONTEXT.getInitParameter("DBUSR");
    if (DBUSR==null) DBUSR="cicc3";
    DBPW=CONTEXT.getInitParameter("DBUSR");
    if (DBPW==null) DBPW="";
  }
}
