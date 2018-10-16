package com.d2discovery.slap;

import java.io.*;
import java.net.*;
import java.sql.*;
import java.util.*;

import javax.servlet.*; //ServletException
import javax.servlet.http.*; //HttpServlet, HttpServletRequest, HttpServletResponse

/**	Servlet: Compound-Gene Co-Occurrence 

	@author Qian Zhu, Jeremy Yang
*/
public class Comp_Gene_CoOccurrence extends HttpServlet
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

  public Comp_Gene_CoOccurrence() { super(); } //default constructor

  public void destroy() { super.destroy(); } // Just puts "destroy" string in log

  public String CallRESTPredictiveModels(int cid, String gene)
  {
    String ret = new String();
    
    String endpoint = new String("http://"+API_HOST+"/rest/Chem2Bio2RDF/pubmed_cocurrence/");
    endpoint += cid + ":" + gene;
    try {
      URL url_sdf = new URL(endpoint);
      BufferedReader in = new BufferedReader(new InputStreamReader(url_sdf.openStream()));
      String str1=new String();
      while ((str1 = in.readLine()) != null) 
      {  
        ret += str1 + "<br />";
      }
    } 
    catch (MalformedURLException e1) {
      // TODO Auto-generated catch block
      e1.printStackTrace();
    } catch (IOException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }
    return ret;
  }

  public String RankPubmed(Map<Integer, Integer> m, Vector<Integer> v, String cid, String gene)
  {
    String pubmed_ids = new String();
    Connection con;
    Statement stmt;
    ResultSet res;
    Statement stmt1;
    ResultSet res1;
    Vector<String> v_pubmedid = new Vector<String>();
    try 
    {
      {
        Class.forName("org.postgresql.Driver");
        //String url = "jdbc:postgresql://localhost/chord";
        String url = "jdbc:postgresql://"+DBHOST+"/chord";
        con = DriverManager.getConnection(url,"cicc3","");
          
        for(int i = 0; i < v.size(); ++i)
        {
          Iterator it_m = m.entrySet().iterator();
          Vector<Integer> v_pubmed_temp = new Vector<Integer>();
          int freq = 0;
          while(it_m.hasNext())
          {
            Map.Entry e_m = (Map.Entry) it_m.next();
            int pubmedid_m = Integer.parseInt(e_m.getKey().toString());
            int freq_m = Integer.parseInt(e_m.getValue().toString());
            if(freq_m == v.get(i))
            {
              if(!v_pubmed_temp.contains(pubmedid_m))
                v_pubmed_temp.add(pubmedid_m);
            }
          }
          if(v_pubmed_temp.size() == 1)
          {
            v_pubmedid.add(Integer.toString(v_pubmed_temp.get(0)));
          }
          else
          {
            Map<Integer, Integer> map = new HashMap<Integer, Integer>();
            Vector<Integer> v_year = new Vector<Integer>();
            for(int j = 0; j < v_pubmed_temp.size(); ++j)
            {        
              String sql1 = "SELECT pub_date_year, pubmed_id FROM medline_biblio WHERE pubmed_id = " + v_pubmed_temp.get(j) + " ORDER BY pub_date_year DESC;";
              stmt1 = con.createStatement();
              res1 = stmt1.executeQuery(sql1);  
              while(res1.next())
              {
                int date = 0;
                if(res1.getString(1).length() == 0)
                  date = 1;
                else
                  date = Integer.parseInt(res1.getString(1));
                int pubmedid = Integer.parseInt(res1.getString(2));
                if(!v_year.contains(date))
                  v_year.add(date);
                map.put(pubmedid, date);            
              }
              res1.close();
              stmt1.close();
            }
            Comparator comp=Collections.reverseOrder();
            Collections.sort(v_year, comp);
            for(int l = 0; l < v_year.size(); ++l)
            {
              int year = v_year.get(l);
              Iterator it = map.entrySet().iterator();
              while(it.hasNext())
              {
                Map.Entry e = (Map.Entry) it.next();
                String pubmedid = e.getKey().toString();
                int year_1 = Integer.parseInt(e.getValue().toString());
                if(year == year_1)
                {
                  v_pubmedid.add(pubmedid);
                //  break;
                }
              }
            }
          }
        }
        int nsize = 0;
        if(v_pubmedid.size() > 10)
          nsize = 10;
        else
          nsize = v_pubmedid.size();
            
        for(int p = 0; p < nsize; ++p)
        {
          String pubmed_link = "http://chem2bio2rdf.org/medline/resource/medline/" + v_pubmedid.get(p);
          pubmed_ids += "<a href=" + pubmed_link + 
            " target='my_window_tab_frame_or_iframe'>" + pubmed_link + "</a><br />";
        }
      }
      con.close();
    }
    catch (ClassNotFoundException e)
    {
      e.printStackTrace();
      pubmed_ids = "failed"; // failed by exception
    }
    catch (SQLException e) {
      e.printStackTrace();
      pubmed_ids = "failed";
    }        
    return pubmed_ids;
  }


  public String get_CoOccurrence_PubMed(int cid, String gene)
  {
    String pubmed_ids = new String();
    Vector<Integer> v_freq = new Vector<Integer>();
    Map<Integer, Integer> pubmed_id = new HashMap<Integer, Integer>();
    Connection con;
    Statement stmt;
    ResultSet res;

    try 
    {
      Class.forName("org.postgresql.Driver");
      //String url = "jdbc:postgresql://localhost/chord";
      String url = "jdbc:postgresql://"+DBHOST+"/chord";
      con = DriverManager.getConnection(url,"cicc3","");
      stmt = con.createStatement();
      
      String sql = "SELECT medline_cids.pubmed_id, medline_cids.freq + medline_gene.freq " +
          " FROM medline_cids inner join medline_gene " +
          " ON medline_cids.pubmed_id = medline_gene.pubmed_id" +
          " WHERE medline_cids.cid = " + cid + " AND UPPER(medline_gene.genesymbol) = UPPER('" + gene + "') " +
          " ORDER BY medline_cids.freq + medline_gene.freq DESC;";
      res = stmt.executeQuery(sql);  
      int n1 = 0;
      while(res.next())
      {
        ++n1;
        int pubmedid = Integer.parseInt(res.getString(1));
        int freq = Integer.parseInt(res.getString(2));
        pubmed_id.put(pubmedid, freq);
        if(!v_freq.contains(freq))
          v_freq.add(freq);
        //pubmed_id.add(pubmedid);
      }
      res.close();
      stmt.close();
      con.close();
      
      if (n1 == 0)
        pubmed_ids = "failed";//no such pubmed_id in database
      else
      {

    /* int nsize = pubmed_id.size();
        if(nsize == 1)
        {
          String pubmed_link = "http://chem2bio2rdf.org/medline/resource/medline/" + pubmed_id.get(0);
          pubmed_ids += "<a href=" + pubmed_link + 
            "' target='my_window_tab_frame_or_iframe'>" + pubmed_link + "</a><br />";

        }
        else
        {*/


          pubmed_ids = RankPubmed(pubmed_id, v_freq, Integer.toString(cid), gene);
        //}


          
      }
    }
    catch (ClassNotFoundException e) {
      e.printStackTrace();
      pubmed_ids = "failed"; // failed by exception
    }
    catch (SQLException e) {
      e.printStackTrace();
      pubmed_ids = "failed";
    }    
    return pubmed_ids;
  }
  /**
   * The doGet method of the servlet. <br>
   *
   * This method is called when a form has its tag value method equals to get.
   * 
   * @param request the request send by the client to the server
   * @param response the response send by the server to the client
   * @throws ServletException if an error occurred
   * @throws IOException if an error occurred
   */
  public void doGet(HttpServletRequest request, HttpServletResponse response)
      throws ServletException, IOException
  {
  /*  int cid = Integer.parseInt(request.getParameter("cid"));  
    String gene = request.getParameter("gene");
    
    //String ret = CallRESTPredictiveModels(cid, gene);
    String ret = get_CoOccurrence_PubMed(cid, gene);
    
    response.setContentType("text/plain;charset=UTF-8");
    response.setHeader("Cache-Control", "no-cache");   
    response.getWriter().write(ret); */    
    
    String cid_s = request.getParameter("cid");  
    String gene_ori = request.getParameter("gene").toUpperCase();
    String ret = new String();
    
    ///Retrieve CID/////  
    int cid = 0;
    int cid_1 = 0;//temperary save cid
    
    if(ut.isNumeric(cid_s))
    {
      cid = Integer.parseInt(cid_s);//it's cid
    }
    else
    {
      cid_1 = ut.CheckIsDrugName(cid_s);//check if input is drug name?
      if(cid_1 == -1 || cid_1 == -3 || cid_1 == -2)
      {
        String cid_temp = ut.ConvertSMILESToCIDFromPubChem(cid_s);//input is smiles
        if(cid_temp.equals("failed") || cid_temp.equals("No input compound found!"))
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
        cid = cid_1;//input is drug name
      }
    }

    ///Retrieve Gene///////
    if(cid == -1)  //no cid found, exit!
      ret = "Failed";
    else
    {
      String gene = ut.RetrieveGene(gene_ori);
      if(gene.equals("failed"))
        ret = "Failed";
      else
        ret = get_CoOccurrence_PubMed(cid, gene);  
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
    out.println("  <HEAD><TITLE>A Servlet</TITLE></HEAD>");
    out.println("  <BODY>");
    out.print("    This is ");
    out.print(this.getClass());
    out.println(", using the POST method");
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
