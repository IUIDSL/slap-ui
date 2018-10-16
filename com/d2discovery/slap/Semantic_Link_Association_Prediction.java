package com.d2discovery.slap;

import java.util.*;
import java.io.*;
import java.net.*; //URL,MalformedURLException
import java.sql.*;

import javax.servlet.*;
import javax.servlet.http.*;

/**	Servlet: SLAP Model; core functionality provided by this class.

	@author Qian Zhu, Jeremy Yang
*/
public class Semantic_Link_Association_Prediction extends HttpServlet
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

  public Semantic_Link_Association_Prediction() { super(); } //default constructor

  public void destroy() { super.destroy(); } // Just puts "destroy" string in log

  public String DoSimilarSlap(String input, String gene, String cids)
  {
    String ret = new String();
    String endpoint = new String("http://"+API_HOST+"/rest/Chem2Bio2RDF/slap/");
    endpoint += input + ":" + cids + ":" + gene;
    try {
      URL url_sdf = new URL(endpoint);
      BufferedReader in = new BufferedReader(new InputStreamReader(url_sdf.openStream()));
      String str1=new String();
      while ((str1 = in.readLine()) != null) 
      {  
        ret += str1 + "\\" + "\r\n";
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
  //http://"+API_HOST+"/rest/Chem2Bio2RDF/slap/CHEBI_155189:68617&5203&13408686&9882979:SLC6A4

  public String CallRESTPredictiveModels(int cid, String gene, String smiles)
  {
    String ret = new String();
    String endpoint = new String("http://"+API_HOST+"/rest/Chem2Bio2RDF/slap/");
    endpoint += cid + ":" + gene;
    try {
      URL url_sdf = new URL(endpoint);
      BufferedReader in = new BufferedReader(new InputStreamReader(url_sdf.openStream()));
      String str1=new String();
      while ((str1 = in.readLine()) != null) 
      {  
        ret += str1 + "\\" + "\r\n";
      }
      if(ret.equals("start node is not found\\\r\n") || ret.equals("no valid path is found\\\r\n"))
      {
        String cids = ut.DoSimilaritySearch(cid, smiles);
        if(cids.equals("failed"))
          ret = "No input compound, even similar ones found!";
        else
          ret = DoSimilarSlap(Integer.toString(cid), gene, cids);
      }
      else if(ret.equals("end node is not found\\\r\n") )
        ret = "End node is not found!";
      //else if(ret.equals("no valid path is found\\\r\n"))
      //  ret = "No valid path is found!";
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

  public String CallRESTPredictiveModels(String input)//input could be gene or cid
  {
    String ret = new String();
    String endpoint = new String("http://"+API_HOST+"/rest/Chem2Bio2RDF/slap/");
    endpoint += input;
    try {
      URL url_sdf = new URL(endpoint);
      BufferedReader in = new BufferedReader(new InputStreamReader(url_sdf.openStream()));
      String str1=new String();
      while ((str1 = in.readLine()) != null) 
      {  
        ret += str1 + "\\" + "\r\n";
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
    
    if(cid_s.length() == 0)
    {
      ///Retrieve Gene///////

      String gene = ut.RetrieveGene(gene_ori);
      if(gene.equals("failed"))
        ret = "No input gene found!";
      else
      {
        ret = CallRESTPredictiveModels(gene);
        ret = ret.substring(ret.indexOf("NA\\\r\nNA\\\r\n") + 10, ret.length());
        ret = "Network for Compounds asscociated with input Gene" + ret;
      }
    }
    else if(gene_ori.length() == 0)
    {
      ///Retrieve CID/////  
      int cid = 0;
      int cid_1 = 0;//temperary save cid
      if(ut.isNumeric(cid_s))
      {
        //cid = Integer.parseInt(cid_s);
        ret = CallRESTPredictiveModels(cid_s);
        ret = ret.substring(ret.indexOf("NA\\\r\nNA\\\r\n") + 10, ret.length());
        ret = "Network for Genes asscociated with input Compound" + ret;
      }
      else
      {
        cid_1 = ut.CheckIsDrugName(cid_s);
        if(cid_1 == -1 || cid_1 == -3 || cid_1 == -2)
        {
          String cid_temp = ut.ConvertSMILESToCID(cid_s);
          if(cid_temp.equals("failed"))
            ret = "No input compound found!";
          else
          {
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
      ///Retrieve CID/////  
      int cid = 0;
      int cid_1 = 0;//temperary save cid
      String smiles = "smiles";
      if(ut.isNumeric(cid_s))
      {
        cid = Integer.parseInt(cid_s);
      }
      else
      {
        cid_1 = ut.CheckIsDrugName(cid_s);
        if(cid_1 == -1 || cid_1 == -3 || cid_1 == -2)
        {
          smiles = cid_s;
          String cid_temp = ut.ConvertSMILESToCID(smiles);
          if(cid_temp.equals("failed"))
          {
            cid = -1;
          }
          else
          {
            cid = Integer.parseInt(cid_temp);//is smiles            
          }
        }
        else
        {
          cid = cid_1;//is drug name
        }
      }
      ///Retrieve Gene///////

      if(cid != -1)
      {
        String gene = ut.RetrieveGene(gene_ori);
        if (gene.equals("failed"))
          ret = "No input gene found!";
        else
          ret = CallRESTPredictiveModels(cid, gene, smiles);
      }
      else
      {
        String cids = ut.DoSimilaritySearch(-1, smiles);
        if(cids.equals("failed"))
          ret = "No input compound, even similar ones found!";
        else
        {
          String gene = ut.RetrieveGene(gene_ori);
          if(gene.equals("failed"))
            ret = "No input gene found!";
          else
            ret = DoSimilarSlap(smiles, gene, cids);
        }
      }
    }
    response.setContentType("text/plain;charset=UTF-8");
    response.setHeader("Cache-Control", "no-cache");   
    response.getWriter().write(ret);     
  }

  /**
   * The doPost method of the servlet. <br>
   *
   * This method is called when a form has its tag value method equals to post.
   * 
   * @param request the request send by the client to the server
   * @param response the response send by the server to the client
   * @throws ServletException if an error occurred
   * @throws IOException if an error occurred
   */
  public void doPost(HttpServletRequest request, HttpServletResponse response)
      throws ServletException, IOException
  {
    response.setContentType("text/html");
    PrintWriter out = response.getWriter();
    out.println("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">");
    out.println("<HTML>");
    out.println("<HEAD><TITLE>A Servlet</TITLE></HEAD>");
    out.println("<BODY>");
    out.println("This is "+this.getClass()+", using the POST method.");
    out.println("</BODY>");
    out.println("</HTML>");
    out.flush();
    out.close();
  }

  /////////////////////////////////////////////////////////////////////////////
  /**	Read context and servlet parameters (from web.xml).
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
