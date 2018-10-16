package com.d2discovery.slap;

import java.io.*;
import java.net.*;
import java.sql.*;

/**	Utility functions.
	@author Qian Zhu, Jeremy Yang
*/
public class Utils 
{
  private String api_host; // "cheminfov.informatics.indiana.edu"
  private String dbhost; // "cheminfov.informatics.indiana.edu"
  private String dbport; // "5432"
  private String dbschema; // "public"
  private String dbname; // "chord"
  private String dbusr; // "cicc3"
  private String dbpw; // ""
  private Utils() { } //default-constructor disallowed

  public Utils(
	String _api_host,
	String _dbhost,
	String _dbport,
	String _dbschema,
	String _dbname,
	String _dbusr,
	String _dbpw)
  {
    this.api_host=_api_host;
    this.dbhost=_dbhost;
    this.dbport=_dbport;
    this.dbschema=_dbschema;
    this.dbname=_dbname;
    this.dbusr=_dbusr;
    this.dbpw=_dbpw;
  }

  /////////////////////////////////////////////////////////////////////////////
  public static boolean isNumeric(String s)
  {
    if ((s != null)&&(s!=""))
      return s.matches("^[0-9]*$");
    else
      return false;
  }

  /////////////////////////////////////////////////////////////////////////////
  public String ConvertSMILESToCIDFromPubChem(String smiles)
  {
    String output = new String();
    boolean failed = false;

    String inchi = new String();
    String smiles_inchi = new String("http://"+this.api_host+"/rest/format/inchi/SMILES/" + smiles);//c1ccccc1C(=O)CN(C)(C)");
    String inchi_cid = null;
    String cid = "cid";
        
    try 
    {
      URL url_inchi = new URL(smiles_inchi);
      BufferedReader in = new BufferedReader(new InputStreamReader(url_inchi.openStream()));
   
      while ((inchi_cid = in.readLine()) != null) 
      {
            inchi = inchi_cid;
      }
      in.close();
      if(inchi == null)
            failed = true;
      else
      {
        //  System.out.print(inchi);
        Connection con;
        Statement stmt;
        ResultSet res;
        Statement stmt1;
        ResultSet res1;  
          
        Class.forName("org.postgresql.Driver");
        //String url = "jdbc:postgresql://localhost/"+this.dbname;
        String url = "jdbc:postgresql://"+this.dbhost+"/"+this.dbname;
        con = DriverManager.getConnection(url,this.dbusr,this.dbpw);
        stmt = con.createStatement();
         
        //pubchem_compound_cheminfo
        String selectSQL = "SELECT cid FROM pubchem_compound_cheminfo WHERE md5(std_inchi) = md5('" + inchi + "');";
        res = stmt.executeQuery(selectSQL);  
        int n1 = 0;
        int n2 = 0;
        while(res.next())
        {
          ++n1;
          cid = res.getString(1);
          //System.out.println(cid + ";" + name);
          break;
        }
        //System.out.println(cid);
        res.close();
        stmt.close();
         
        if (n1 == 0)
        {
          //pubchem_compound
          String selectSQL1 = "SELECT cid FROM pubchem_compound WHERE md5(std_inchi) = md5('" + inchi + "');";
          stmt1 = con.createStatement();
          res1 = stmt1.executeQuery(selectSQL1);
           
          while(res1.next())
          {
            ++n2;
            cid = res1.getString(1);
            break;
          }
          res1.close();
          stmt1.close();            
        }
        con.close();
        if (n2 == 0)
          cid = "No input compound found!";
      }
    }
    catch (ClassNotFoundException e) {
       e.printStackTrace();
       failed = true;
    }
    catch (SQLException e) {
       e.printStackTrace();
       failed = true;
    } catch (MalformedURLException e) {
       failed = true;
       e.printStackTrace();
    } catch (IOException e) {
       failed = true;
       e.printStackTrace();
    }
    if (failed == true)
       output = "failed";
    else
       output = cid;
    return output;
  }

  /////////////////////////////////////////////////////////////////////////////
  public String ConvertSMILESToCID(String smiles)
  {
    String output = new String();
    boolean failed = false;

    String inchi = new String();
    String smiles_inchi = new String("http://"+this.api_host+"/rest/format/inchi/SMILES/" + smiles);//c1ccccc1C(=O)CN(C)(C)");
    String inchi_cid = null;
    String cid = "cid";
        
    try 
    {
      URL url_inchi = new URL(smiles_inchi);
      BufferedReader in = new BufferedReader(new InputStreamReader(url_inchi.openStream()));
   
      while ((inchi_cid = in.readLine()) != null) 
      {
        inchi = inchi_cid;
      }
      in.close();
      if (inchi == null)
        failed = true;
      else
      {
        //System.out.print(inchi);
        Connection con;
        Statement stmt;
        ResultSet res;
          
        Class.forName("org.postgresql.Driver");
        //String url = "jdbc:postgresql://localhost/"+this.dbname;
        String url = "jdbc:postgresql://"+this.dbhost+"/"+this.dbname;
        con = DriverManager.getConnection(url,this.dbusr,this.dbpw);
        stmt = con.createStatement();
         
/**
        //pubchem_compound_cheminfo
        String selectSQL = "SELECT cid FROM pubchem_compound_cheminfo WHERE md5(std_inchi) = md5('" + inchi + "');";
        res = stmt.executeQuery(selectSQL);  
        int n1 = 0;
        int n2 = 0;
        while(res.next())
        {
          ++n1;
          cid = res.getString(1);
          break;
        }
        res.close();
        stmt.close();
         
        if (n1 == 0)
        {
          //pubchem_compound
          String selectSQL1 = "SELECT cid FROM pubchem_compound WHERE md5(std_inchi) = md5('" + inchi + "');";
          stmt1 = con.createStatement();
          res1 = stmt.executeQuery(selectSQL1);
           
          while(res1.next())
          {
            ++n2;
            cid = res1.getString(1);
          }
          res1.close();
          stmt1.close();            
        }
*/


        String selectSQL = "SELECT cid FROM c2b2r_compound_new WHERE md5(std_inchi) = md5('" + inchi + "');";
        res = stmt.executeQuery(selectSQL);  
        int n1 = 0;
        while (res.next())
        {
          ++n1;
          cid = res.getString(1);
          break;
        }
        res.close();
        stmt.close();
        con.close();
        if (n1 == 0)
          failed = true;
      }
    } 
    catch (ClassNotFoundException e) {
       e.printStackTrace();
       failed = true;
    }
    catch (SQLException e) {
       e.printStackTrace();
       failed = true;
    } catch (MalformedURLException e) {
       failed = true;
       e.printStackTrace();
    } catch (IOException e) {
       failed = true;
       e.printStackTrace();
    }
    if(failed == true)
       output = "failed";
    else
       output = cid;
    return output;
   }

  /////////////////////////////////////////////////////////////////////////////
   public String ConvertGeneNameToGeneSymbol(String genename)
   {
     String gene = new String();
     Connection con;
     Statement stmt;
     ResultSet res;

     try 
     {
       Class.forName("org.postgresql.Driver");
       //String url = "jdbc:postgresql://localhost/"+this.dbname;
       String url = "jdbc:postgresql://"+this.dbhost+"/"+this.dbname;
       con = DriverManager.getConnection(url,"","");
       stmt = con.createStatement();
       
       String sql = "SELECT gene_symbol FROM c2b2r_chembl_02_target_dictionary WHERE UPPER(gene_names) = UPPER('" + genename + "');";
       res = stmt.executeQuery(sql);  
       int n1 = 0;
       while(res.next())
       {
         ++n1;
         String gene_temp = res.getString(1);
         if(gene_temp.length() == 0)
         {
           gene = "no_gene";//no gene found by this uniportid
           break;
         }
         else
           gene = gene_temp;
         break;
       }
       if(n1 == 0)
         gene = "failed";//no such drug in database
       res.close();
       stmt.close();
       con.close();
     }
     catch (ClassNotFoundException e) {
       e.printStackTrace();
       gene = "failed"; // failed by exception
     }
     catch (SQLException e) {
       e.printStackTrace();
       gene = "failed";
     }    
     return gene;
   }

  /////////////////////////////////////////////////////////////////////////////
  public String ConvertUniportIDToGeneSymbol(String uniportID)
  {
    String gene = new String();
    Connection con;
    Statement stmt;
    ResultSet res;

    try 
    {
      Class.forName("org.postgresql.Driver");
      //String url = "jdbc:postgresql://localhost/"+this.dbname;
      String url = "jdbc:postgresql://"+this.dbhost+"/"+this.dbname;
      con = DriverManager.getConnection(url,this.dbusr,this.dbpw);
      stmt = con.createStatement();
       
      String sql = "SELECT \"geneSymbol\" FROM \"c2b2r_GENE2UNIPROT\" WHERE UPPER(uniprot) = UPPER('" + uniportID + "');";
      res = stmt.executeQuery(sql);  
      int n1 = 0;
      while (res.next())
      {
        ++n1;
        String gene_temp = res.getString(1);
        if(gene_temp.length() == 0)
        {
          gene = "no_gene";//no gene record found by this uniportid
          break;
        }
        else
          gene = gene_temp;
        break;
      }
      if (n1 == 0)
        gene = "failed";//no such drug in database
      res.close();
      stmt.close();
      con.close();
    }
    catch (ClassNotFoundException e) {
      e.printStackTrace();
      gene = "failed"; // failed by exception
    }
    catch (SQLException e) {
      e.printStackTrace();
      gene = "failed";
    }    
    return gene;
  }

  /////////////////////////////////////////////////////////////////////////////
  public int CheckIsDrugName(String drug)
  {
    int cid = -1;
    Connection con;
    Statement stmt;
    ResultSet res;

    try 
    {
      Class.forName("org.postgresql.Driver");
      //String url = "jdbc:postgresql://localhost/"+this.dbname;
      String url = "jdbc:postgresql://"+this.dbhost+"/"+this.dbname;
      con = DriverManager.getConnection(url,this.dbusr,this.dbpw);
      stmt = con.createStatement();
       
      String sql = "SELECT \"CID\" FROM \"c2b2r_DrugBankDrug\" WHERE UPPER(\"Generic_Name\") = UPPER('" + drug + "');";
      res = stmt.executeQuery(sql);  
      int n1 = 0;
      while(res.next())
      {
        ++n1;
        String cid_s = res.getString(1);
        if (cid_s == null)
        {
          cid = -2;//no cid found by this drugname
          break;
        }
        else
          cid = Integer.parseInt(cid_s);
        break;
      }
      if (n1 == 0)
         cid = -3;//no such drug in database
      res.close();
      stmt.close();
      con.close();
    }
    catch (ClassNotFoundException e) {
      e.printStackTrace();
      cid = -1; // failed by exception
    }
    catch (SQLException e) {
      e.printStackTrace();
      cid = -1;
    }
    return cid;
  }

  /////////////////////////////////////////////////////////////////////////////
  public String DoSimilaritySearch(int cid, String smiles)
  {
    boolean failed = false;
    Connection con;
    Statement stmt;
    ResultSet res;
    Statement stmt1;
    ResultSet res1;
    String smiles_new = new String();
    String cid_list = new String();
    try 
    {
       Class.forName("org.postgresql.Driver");
       //String url = "jdbc:postgresql://localhost/"+this.dbname;
       String url = "jdbc:postgresql://"+this.dbhost+"/"+this.dbname;
       con = DriverManager.getConnection(url,this.dbusr,this.dbpw);
       stmt = con.createStatement();
       
       if(smiles.equals("smiles"))
       {
         String sql = "SELECT openeye_can_smiles FROM c2b2r_compound_new WHERE cid = " + cid + ";";
         res = stmt.executeQuery(sql);  
         int n1 = 0;
         while(res.next())
         {
           ++n1;
           smiles_new = res.getString(1);
           break;
         }
         res.close();
         stmt.close();

         if(n1 == 0)
         {
           failed = true;
           return "failed";
         }
       }
       else
         smiles_new = smiles;
       String sql1 = "SELECT cid, tanimoto(gfp, public166keys(keksmiles('" + smiles_new + "')))FROM c2b2r_compound_new WHERE gfpbcnt" +
           " BETWEEN (nbits_set(public166keys(keksmiles('" + smiles_new + "'))) * 0.85)::integer" +
           " AND (nbits_set(public166keys(keksmiles('" + smiles_new + "'))) / 0.85)::integer" +
           " AND tanimoto(gfp, public166keys(keksmiles('" + smiles_new + "'))) > 0.85 ORDER BY tanimoto DESC";
       stmt1 = con.createStatement();
       res1 = stmt1.executeQuery(sql1);  
       int n2 = 0;
       
       while(res1.next())
       {
         ++n2;
         String cid_1 = res1.getString(1);
         cid_list += cid_1 + "&";
       //  break;
       }
       res1.close();
       stmt1.close();
       if(n2 == 0)
         failed = true;  
       else
         cid_list = cid_list.substring(0, cid_list.length()-1);          
    }
    catch (ClassNotFoundException e) {
       e.printStackTrace();
       failed = true;
    }
    catch (SQLException e) {
       e.printStackTrace();
       failed = true;
    }
    if (failed == true)
       return "failed";
    else
       return cid_list;
  }

  /////////////////////////////////////////////////////////////////////////////
  public String RetrieveGene(String gene_ori)
  {
    String gene = new String();
    String gene_1 = new String();
    String gene_2 = new String();
     
    if(gene_ori.length() == 6)//the length of uniportid == 6
    {
       gene_1 = ConvertUniportIDToGeneSymbol(gene_ori);
       if(gene_1.equals("no_gene")) //i
       {
         gene = "failed";
       }
       else if(gene_1.equals("failed"))
       {
         gene_2 = ConvertGeneNameToGeneSymbol(gene_ori);
         if(gene_2.equals("failed") || gene_2.equals("no_gene"))
         {
           gene = gene_ori;
         }
         else
           gene = gene_2;
       }
       else
         gene = gene_1;
    }
    else
    {
      gene_2 = ConvertGeneNameToGeneSymbol(gene_ori);
      if(gene_2.equals("failed") || gene_2.equals("no_gene"))
      {
        gene = gene_ori;
      }
      else
        gene = gene_2;
    }
    return gene;
  }
}
