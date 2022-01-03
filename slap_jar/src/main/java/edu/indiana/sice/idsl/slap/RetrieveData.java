package edu.indiana.sice.idsl.slap;

/* Location:           /home/jjyang/Downloads/slap/WEB-INF/classes/
 * Qualified Name:     Prediction.RetrieveData
 * JD-Core Version:    0.6.2
 */

import java.io.*;
import java.sql.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;
import javax.xml.parsers.*; //DocumentBuilder,DocumentBuilderFactory
import org.w3c.dom.*; //Document,Element,Node,NodeList

/**	Servlet: Maybe only used by Test.
*/
public class RetrieveData extends HttpServlet
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

  Utils ut = new Utils(API_HOST,DBHOST,DBPORT,DBSCHEMA,DBNAME,DBUSR,DBPW);


  public void destroy()
  {
    super.destroy();
  }

  public String getDrugInfo(int cid) throws Exception
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
    Statement dbConn = connection.createStatement();
    try
    {
      ResultSet rs = dbConn.executeQuery("select name,indication from c2b2r_drugbankdrug_042011 where cid='" + cid + "'");
      rs.next();
      if (!rs.wasNull())
        return "<b>Name:</b> " + rs.getString(1) + "\n" + "<b>Indication:</b> " + rs.getString(2);
    }
    catch (SQLException e) {
      return "";
    }

    return "";
  }

  public String getDiseaseInfo(int omim) throws Exception {
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
    Statement dbConn = connection.createStatement();
    try
    {
      ResultSet rs = dbConn.executeQuery("select \"Name\",\"Disorder_class\" from c2b2r_omim_disease where \"Disease_ID\"=" + omim);
      rs.next();
      if (!rs.wasNull())
        return "<b>Name:</b> " + rs.getString(1) + "\n" + "<b>Disorder class:</b> " + rs.getString(2);
    }
    catch (SQLException e) {
      return "";
    }

    return "";
  }

  public String getSideEffectInfo(String id) throws Exception {
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
    Statement dbConn = connection.createStatement();
    try
    {
      ResultSet rs = dbConn.executeQuery("select side_effect from c2b2r_side_effect where  umls_id='" + id + "'");
      rs.next();
      if (!rs.wasNull())
        return "<b>Name:</b> " + rs.getString(1);
    }
    catch (SQLException e) {
      return "";
    }

    return "";
  }

  public String getchebiInfo(String chebi) throws Exception {
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
    Statement dbConn = connection.createStatement();
    try
    {
      ResultSet rs = dbConn.executeQuery("select name,definition from c2b2r_chebi where id='" + chebi + "'");
      rs.next();
      if (!rs.wasNull())
        return "<b>Name:</b> " + rs.getString(1) + "\n" + "<b>Definition:</b> " + rs.getString(2);
    }
    catch (SQLException e) {
      return "";
    }

    return "";
  }

  public String getTargetInfo(String id) throws Exception {
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
    Statement dbConn = connection.createStatement();
    try
    {
      ResultSet rs = dbConn.executeQuery("select \"Approved_Name\" from \"c2b2r_HGNC\" where \"Approved_Symbol\"='" + id + "'");
      rs.next();
      if (!rs.wasNull())
        return "<b>Name:</b> " + rs.getString(1);
    }
    catch (SQLException e) {
      return "";
    }

    return "";
  }

  public String getPathwayInfo(String id) throws Exception {
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
    Statement dbConn = connection.createStatement();
    try
    {
      ResultSet rs = dbConn.executeQuery("select pathwayname from \"c2b2r_KEGG_pathway_info\" where pathwayid_abbr='" + id + "'");
      rs.next();
      if (!rs.wasNull())
        return "<b>Description:</b> " + rs.getString(1);
    }
    catch (SQLException e) {
      return "";
    }

    return "";
  }

  public String getGOInfo(String goid) throws Exception {
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
    Statement dbConn = connection.createStatement();
    try
    {
      ResultSet rs = dbConn.executeQuery("select term,definition from go_terms where goid='" + goid + "'");
      rs.next();
      if (!rs.wasNull())
        return "<b>Term:</b> " + rs.getString(1) + "\n" + "<b>Definition:</b> " + rs.getString(2);
    }
    catch (SQLException e) {
      return "";
    }

    return "";
  }

  private String getDrugs(String sparql)
  {
    ArrayList cList = new ArrayList();
    try
    {
      DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
      DocumentBuilder db = dbf.newDocumentBuilder();
      Document doc = db.parse(sparql);
      doc.getDocumentElement().normalize();
      NodeList nodeLst = doc.getElementsByTagName("binding");

      for (int s = 0; s < nodeLst.getLength(); s++)
      {
        Node fstNode = nodeLst.item(s);

        if (fstNode.getNodeType() == 1)
        {
          Element fstElmnt = (Element)fstNode;
          NodeList fstNmElmntLst = fstElmnt.getElementsByTagName("literal");
          Element fstNmElmnt = (Element)fstNmElmntLst.item(0);
          NodeList fstNm = fstNmElmnt.getChildNodes();

          cList.add(fstNm.item(0).getNodeValue());
        }
      }
    } catch (Exception e) {
      e.printStackTrace();
    }
    return "";
  }

  public void doGet(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException
  {
    String uri = request.getParameter("uri");
    String nodeClass = request.getParameter("nodeclass");
    String id = uri.split("/")[(uri.split("/").length - 1)];
    String ret = new String();

    if (nodeClass.equals("pubchem_compound"))
      try {
        ret = "<b>Class:</b>Chemical Compound/Drug\n" + getDrugInfo(Integer.valueOf(id).intValue());
      }
      catch (NumberFormatException e) {
        e.printStackTrace();
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    else if (nodeClass.equals("GO")) {
      try {
        ret = "<b>Class:</b>Gene Ontology\n" + getGOInfo(id);
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    }
    else if (nodeClass.equals("gene")) {
      try {
        ret = "<b>Class:</b>Target\n" + getTargetInfo(id);
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    }
    else if (nodeClass.equals("kegg_pathway")) {
      try {
        ret = "<b>Class:</b>Pathway\n" + getPathwayInfo(id);
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    }
    else if (nodeClass.equals("chebi")) {
      try {
        ret = "<b>Class:</b>Chemical Ontology\n" + getchebiInfo(id);
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    }
    else if (nodeClass.equals("sider")) {
      try {
        ret = "<b>Class:</b>Side Effect\n" + getSideEffectInfo(id);
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    }
    else if (nodeClass.equals("omim_disease")) {
      try {
        ret = "<b>Class:</b>Disease\n" + getDiseaseInfo(Integer.valueOf(id).intValue());
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    }
    else if (nodeClass.equals("substructure")) {
      try {
        ret = "<b>Class:</b>Substrucutre\n<b>Name:</b>" + id.replace("_", " ");
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    }
    else if (nodeClass.equals("tissue")) {
      try {
        ret = "<b>Class:</b>Tissue\n" + id;
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    }
    else if (nodeClass.equals("gene_family")) {
      try {
        ret = "<b>Class:</b>Gene Family\n<b>Name:</b>" + id;
      }
      catch (Exception e) {
        e.printStackTrace();
      }

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
    out.println("</BODY>");
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

