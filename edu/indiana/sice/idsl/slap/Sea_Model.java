package edu.indiana.sice.idsl.slap;

import java.util.*;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.MalformedURLException;
import java.net.URL;

import javax.servlet.*; //ServletException
import javax.servlet.http.*; //HttpServlet, HttpServletRequest, HttpServletResponse
import javax.xml.rpc.ParameterMode;
import javax.xml.rpc.ServiceException;

import org.apache.axis.client.Call;
import org.apache.axis.client.Service;
import org.apache.axis.encoding.XMLType;

/**	Servlet: Similarity Ensemble Approach (SEA)

	@author Qian Zhu, Jeremy Yang
*/
public class Sea_Model extends HttpServlet
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

  public Sea_Model() { super(); } //default constructor

  public void destroy() { super.destroy(); } // Just puts "destroy" string in log
  public String CallSeaWs(String smiles, String gene)
  {
    String ret = new String();
    String newendpoint = "http://"+DBHOST+":8080/polypharmacology/services/Sea";
    try 
    {                               
      Service  service = new Service();
      Call     call    = (Call) service.createCall();
      call.setTargetEndpointAddress( new java.net.URL(newendpoint) );
      call.setOperationName ("getPrediction");
      call.addParameter ("op1", XMLType.SOAP_STRING, ParameterMode.IN );
      call.addParameter ("op2", XMLType.SOAP_STRING, ParameterMode.IN );
      call.addParameter ("op3", XMLType.SOAP_INTEGER, ParameterMode.IN );
      call.setReturnType(XMLType.SOAP_STRING);                
      ret = (String) call.invoke( new Object[]{smiles, gene, new Integer(200)});
      call.clearOperation();
    }  
    catch (ServiceException e) 
    {
      ret = "failed";
      e.printStackTrace();
    }
      catch (IOException e) 
    {
      ret = "failed";
      e.printStackTrace();
    }
      catch (Exception ex) 
    {
      ret = "failed";
      ex.printStackTrace();
    }
    return ret;
  }

  public String CallSeaREST(int cid, String gene)
  {
    String ret = new String();
    
    String endpoint = new String("http://"+API_HOST+"/rest/Chem2Bio2RDF/Sea_Model/");
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
    }catch (IOException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }
    return ret;
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
    String cid_s = request.getParameter("cid");  
    String gene_ori = request.getParameter("gene").toUpperCase();
    String ret = new String();

    Utils ut = new Utils(API_HOST,DBHOST,DBPORT,DBSCHEMA,DBNAME,DBUSR,DBPW);

    /*    int cid = 0;
    if(ut.isNumeric(cid_s))
    {
      cid = Integer.parseInt(cid_s);
    }
    else
    {
      String cid_temp = ut.ConvertSMILESToCID(cid_s);
      if(cid_temp.equals("failed"))
        ret = "Failed to convert SMILES to CID! Please try another one!";
      else
      {
        cid = Integer.parseInt(cid_temp);
              
      }
    }*/
    ///Retrieve CID/////  
    int cid = 0;
    int cid_1 = 0;//temperary save cid
    String smiles = new String();
    if(ut.isNumeric(cid_s))
    {
      cid = Integer.parseInt(cid_s);//it's cid
    }
    else
    {
      smiles = cid_s;
      cid_1 = ut.CheckIsDrugName(cid_s);//check if input is drug name?
      if(cid_1 == -1 || cid_1 == -3 || cid_1 == -2)
      {
        String cid_temp = ut.ConvertSMILESToCID(cid_s);//input is smiles
        if(cid_temp.equals("failed"))
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
    
    String gene = ut.RetrieveGene(gene_ori);
    if(gene.equals("failed"))
      ret = "No input gene found!";
    else
    {
      if(cid != -1)
      {
        ret = CallSeaREST(cid, gene);
      }
      else
      {
        ret = CallSeaWs(smiles, gene);
      }      
    }

    /*    if(cid == -1)  //no cid found, exit!
      ret = "Failed";
    else
    {
      String gene = ut.RetrieveGene(gene_ori);
      if(gene.equals("failed"))
        ret = "Failed";
      else
        ret = CallSeaREST(cid, gene);  
    }*/
    //ret = CallSeaWs(cid, gene);
    //ret = CallSeaREST(cid, gene);
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
