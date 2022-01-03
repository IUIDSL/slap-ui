package edu.indiana.sice.idsl.slap;

/* Location:           /home/jjyang/Downloads/slap/WEB-INF/classes/
 * Qualified Name:     Prediction.SlapUtilities
 * JD-Core Version:    0.6.2
 */
import java.util.*;
import java.io.*;
import java.net.*;
import javax.servlet.*;
import javax.servlet.http.*;

/**	Servlet: Utility functions.
*/
public class SlapUtilities extends HttpServlet
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

  public void destroy() { super.destroy(); }

  public String DoSimilarSlap(String input, String gene, String cids)
  {
    String ret = new String();
    String endpoint = new String("http://"+API_HOST+"/rest/Chem2Bio2RDF/slap/");
    endpoint = endpoint + input + ":" + cids + ":" + gene;
    try {
      URL url_sdf = new URL(endpoint);
      BufferedReader in = new BufferedReader(new InputStreamReader(url_sdf.openStream()));
      String str1 = new String();
      while ((str1 = in.readLine()) != null)
      {
        ret = ret + str1 + "\\" + "\r\n";
      }
    }
    catch (MalformedURLException e1) {
      ret = "failed";
      e1.printStackTrace();
    } catch (IOException e) {
      ret = "failed";
      e.printStackTrace();
    }
    return ret;
  }

  public String CallRESTPredictiveModels(int cid, String gene, String smiles)
  {
    String ret = new String();

    String endpoint = new String("http://"+API_HOST+"/rest/Chem2Bio2RDF/slap/");
    endpoint = endpoint + cid + ":" + gene;
    try {
      URL url_sdf = new URL(endpoint);
      BufferedReader in = new BufferedReader(new InputStreamReader(url_sdf.openStream()));
      String str1 = new String();
      while ((str1 = in.readLine()) != null)
      {
        ret = ret + str1 + "\\" + "\r\n";
      }
      if ((ret.equals("start node is not found\\\r\n")) || (ret.equals("no valid path is found\\\r\n")))
      {
        String cids = this.ut.DoSimilaritySearch(cid, smiles);
        if (cids.equals("failed"))
          ret = "No input compound, even similar ones found!";
        else
          ret = DoSimilarSlap(Integer.toString(cid), gene, cids);
      }
      else if (ret.equals("end node is not found\\\r\n")) {
        ret = "End node is not found!";
      }
    }
    catch (MalformedURLException e1)
    {
      ret = "failed";
      e1.printStackTrace();
    } catch (IOException e) {
      ret = "failed";
      e.printStackTrace();
    }

    return ret;
  }

  public String CallRESTPredictiveModels(String input)
  {
    String ret = new String();

    String endpoint = new String("http://"+API_HOST+"/rest/Chem2Bio2RDF/slap/");
    endpoint = endpoint + input;
    try {
      URL url_sdf = new URL(endpoint);
      BufferedReader in = new BufferedReader(new InputStreamReader(url_sdf.openStream()));
      String str1 = new String();
      while ((str1 = in.readLine()) != null)
      {
        ret = ret + str1 + "\\" + "\r\n";
      }
    }
    catch (MalformedURLException e1) {
      ret = "failed";
      e1.printStackTrace();
    } catch (IOException e) {
      ret = "failed";
      e.printStackTrace();
    }
    return ret;
  }

  public void doGet(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException
  {
    String cid_s = request.getParameter("cid");
    String gene_ori = request.getParameter("gene").toUpperCase();
    String ret = new String();

    if (cid_s.length() == 0)
    {
      String gene = this.ut.RetrieveGene(gene_ori);
      if (gene.equals("failed")) {
        ret = "No input gene found!";
      }
      else {
        ret = gene;
      }

    }
    else if (gene_ori.length() == 0)
    {
      int cid = 0;
      int cid_1 = 0;
      if (this.ut.isNumeric(cid_s))
      {
        ret = cid_s;
      }
      else
      {
        cid_1 = this.ut.CheckIsDrugName(cid_s);

        if ((cid_1 == -1) || (cid_1 == -3) || (cid_1 == -2))
        {
          String cid_temp = this.ut.ConvertSMILESToCID(cid_s);
          if (cid_temp.equals("failed")) {
            ret = "No input compound found!";
          }
          else {
            ret = CallRESTPredictiveModels(cid_temp);
            ret = ret.substring(ret.indexOf("NA\\\r\nNA\\\r\n") + 10, ret.length());
            ret = "Network for Genes asscociated with input Compound" + ret;
          }
        }
        else
        {
          ret = CallRESTPredictiveModels(Integer.toString(cid_1));
          ret = ret.substring(ret.indexOf("NA\\\r\nNA\\\r\n") + 10, ret.length());
          ret = "Network for Genes asscociated with input Compound" + ret;
        }
      }

    }
    else
    {
      int cid = 0;
      int cid_1 = 0;
      String smiles = "smiles";
      if (this.ut.isNumeric(cid_s))
      {
        cid = Integer.parseInt(cid_s);
      }
      else
      {
        cid_1 = this.ut.CheckIsDrugName(cid_s);
        if ((cid_1 == -1) || (cid_1 == -3) || (cid_1 == -2))
        {
          smiles = cid_s;
          String cid_temp = this.ut.ConvertSMILESToCID(smiles);
          if (cid_temp.equals("failed"))
          {
            cid = -1;
          }
          else
          {
            cid = Integer.parseInt(cid_temp);
          }
        }
        else
        {
          cid = cid_1;
        }

      }

      if (cid != -1)
      {
        String gene = this.ut.RetrieveGene(gene_ori);
        if (gene.equals("failed"))
          ret = "No input gene found!";
        else
          ret = CallRESTPredictiveModels(cid, gene, smiles);
      }
      else
      {
        String cids = this.ut.DoSimilaritySearch(-1, smiles);
        if (cids.equals("failed")) {
          ret = "No input compound, even similar ones found!";
        }
        else {
          String gene = this.ut.RetrieveGene(gene_ori);
          if (gene.equals("failed"))
            ret = "No input gene found!";
          else {
            ret = DoSimilarSlap(smiles, gene, cids);
          }
        }
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
    out.print("This is "+getClass()+", using the POST method.");
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
