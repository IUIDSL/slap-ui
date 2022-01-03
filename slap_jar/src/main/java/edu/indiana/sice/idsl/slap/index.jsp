<%@ page language="java" import="java.util.*" %>

<% ServletContext context = request.getServletContext(); %>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <title>Semantic Link Association Prediction</title>
    <meta http-equiv="pragma" content="no-cache">
    <meta http-equiv="cache-control" content="no-cache">
    <meta http-equiv="expires" content="0">    
    <meta http-equiv="keywords" content="keyword1,keyword2,keyword3">
    <meta http-equiv="description" content="This is my page">

    <!-- <link rel="stylesheet" type="text/css" href="styles.css"> -->
    <link rel="stylesheet" type="text/css" href="css/jquery.autocomplete.css" />

    <script type="text/javascript" src="http://www.google.com/jsapi"></script>  
    <script type="text/javascript">google.load("jquery", "1"); </script>
    <script type="text/javascript" src="js/jquery.autocomplete.js"></script>  
    <script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-23142133-2']);

  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

    </script>
    

    <!-- JSON support for IE (needed to use JS API) -->
    <script type="text/javascript" src="js/json2.min.js"></script>
        
    <!-- Flash embedding utility (needed to embed Cytoscape Web) -->
    <script type="text/javascript" src="js/AC_OETags.min.js"></script>
        
    <!-- Cytoscape Web JS API (needed to reference org.cytoscapeweb.Visualization) -->
    <script type="text/javascript" src="js/cytoscapeweb.min.js"></script>

<SCRIPT LANGUAGE="JavaScript">
String.prototype.trim = function() {
  return this.replace(/^\s+|\s+$/g,"");
}

function getSmiles() 
{
  var drawing = document.JME.smiles();
  document.getElementById("cid").value = drawing;
  document.getElementById("jme").style.display = "none";
  document.getElementById("retrievesmiles").style.display = "none";
}

function launchJME()
{
  document.getElementById("jme").style.display = "block";
  document.getElementById("retrievesmiles").style.display = "block";
}
function launchSequence()
{
  //document.getElementById("sequence").style.display = "block";
  document.getElementById("sequenceArea").style.display = "block";
  document.getElementById("getSequence").style.display = "block";
  
  document.getElementById("sequenceNotice").style.display = "none";
  document.getElementById("sequenceNoticeArea").style.display = "none";
}
var processrunning = 0;
var xmlHttp;
var sequence;
//var API_HOST = "cheminfov.informatics.indiana.edu";
//var API_BASE_PATH = "/rest/Chem2Bio2RDF/slap";
//var API_HOST = "lengua.health.unm.edu";
//var API_BASE_PATH = "/tomcat/slap";
var API_HOST = "<%= context.getInitParameter("API_HOST") %>" ;
var API_BASE_PATH = "<%= context.getInitParameter("API_BASE_PATH") %>" ;

var API_BASE_URI = "http://"+API_HOST+API_BASE_PATH ;

function createXmlHttp() 
{
  try 
  {
    xmlHttp = new XMLHttpRequest();//ff
  }
  catch (trymicrosoft) //ie
  {
    try 
    {
      xmlHttp = new ActiveXObject("Msxml2.XMLHTTP");
    }
    catch (othermicrosoft) 
    {
      try 
      {
        xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
      }
      catch (failed) 
      {
        xmlHttp = false;
      }
    }
  }
  
  if (!xmlHttp){
    alert("Error initializing XMLHttpRequest!");
  }
}

function go_to_chemohub()
{
  var gene = document.getElementById("gene").value;
  var cid = document.getElementById("cid").value;  
  cid=cid.trim();
  gene=gene.trim();
  var link = "slap.jsp?cid=" +cid+"&gene="+gene;
  window.open(link,'_self');
}

function go_to_compound()
{
  var cid = document.getElementById("cid").value;  
  cid=cid.trim();
  var link = API_BASE_PATH+"/cid="+cid;
  window.open(link);
}

function go_to_target()
{
  var gene = document.getElementById("gene").value;  
  gene=gene.trim();
  var link = API_BASE_PATH+"/target=" +gene;
  window.open(link);
}

function go_to_advanced()
{
  var link = "fileupload.html";
  window.open(link);
}

function searchTarget()
{
  var sequence;
  var URL;
  sequence=document.getElementById("sequence").value;
  createXmlHttp();
  //sequence="MSVGCPEPEPPRSLTCCGPGTAPGPGAGVPLLTEDMQALTLRTLAASDVTKHYELVRELGKGTYGKVDLVVYKGTGTKMALKFVNKSKTKLKNFLREVSITNSLSSSPFIIKVFDVVFETEDCYVFAQEYAPAGDLFDIIPPQVGLPEDTVKRCVQQLGLALDFMHGRQLVHRDIKPENVLLFDRECRRVKLADFGMTRRVGCRVKRVSGTIPYTAPEVCQAGRADGLAVDTGVDVWAFGVLIFCVLTGNFPWEAASGADAFFEEFVRWQRGRLPGLPSQWRRFTEPALRMFQRLLALEPERRGPAKEVFRFLKHELTSELRRRPSHRARKPPGDRPPAAGPLRLEAPGPLKRTVLTESGSGSRPAPPAVGSVPLPVPVPVPVPVPVPVPEPGLAPQGPPGRTDGRADKSKGQVVLATAIEICV";
  URL = "BlastSearch?sequence=" + encodeURIComponent(sequence) ;//escape(smiles.valueOf());
  xmlHttp.open("get", URL, true);
  xmlHttp.onreadystatechange = function(){load_sequence();};
  xmlHttp.send(null);
  processrunning = 1;
}

function load_sequence(){
  if (xmlHttp.readyState == 4) {
    document.getElementById("sequenceArea").style.display = "none";
    document.getElementById("getSequence").style.display = "none";
    document.getElementById("sequenceNotice").style.display = "block";
    document.getElementById("sequenceNoticeArea").style.display = "block";
    
    results=xmlHttp.responseText.split("\t");
    document.getElementById("gene").value=results[0];  
    document.getElementById("sequenceNotice").innerHTML="Hit:"+results[0]+" E value:"+results[1];    
    processrunning = 0;
  }
}
function callRestPrediction(cid, gene, number) 
{
  var URL;
    
  if(number == 0)
  {
    URL = "Sea_Model?cid=" + encodeURIComponent(cid) + "&gene=" + encodeURIComponent(gene);//escape(smiles.valueOf());
    xmlHttp.open("get", URL, true);
    xmlHttp.onreadystatechange = function(){load_Sea_Prediction()};
    xmlHttp.send(null);     
    processrunning = 1;
  }
  if(number == 1)
  {
    URL = "Bayes_Model?cid=" + encodeURIComponent(cid) + "&gene=" + encodeURIComponent(gene);//escape(smiles.valueOf());
    xmlHttp.open("get", URL, true);
    xmlHttp.onreadystatechange = function(){load_Bayes_Prediction()};
    xmlHttp.send(null);     
    processrunning = 1;
  }
  else if(number == 3)
  {
    URL = "Comp_Gene_CoOccurrence?cid=" + encodeURIComponent(cid) + "&gene=" + encodeURIComponent(gene);//escape(smiles.valueOf());
    xmlHttp.open("get", URL, true);
    xmlHttp.onreadystatechange = function(){load_Comp_Gene_CoOccurrence()};
    xmlHttp.send(null);
    processrunning = 1;
  }
  else if(number == 2)
  {
    URL = "Semantic_Link_Association_Prediction?cid=" + encodeURIComponent(cid) + "&gene=" + encodeURIComponent(gene);//escape(smiles.valueOf());
    xmlHttp.open("get", URL, true);
    xmlHttp.onreadystatechange = function(){load_slap();};
    xmlHttp.send(null);
    processrunning = 1;
  }
}
function load_Sea_Prediction()
{
  if (xmlHttp.readyState == 4) {
    //if (xmlHttp.status == 200) {
    document.getElementById("Sea").style.display = "block";
    document.getElementById("Sea").innerHTML=xmlHttp.responseText;
    //document.getElementById("PredictiveResults-title").style.display = "block";
    //document.getElementById("Prediction").style.display = "block";
    document.getElementById("Sea_loading_div").style.display = "none"; 
    processrunning = 0;
  }
}
function load_Bayes_Prediction()
{
  if (xmlHttp.readyState == 4) {
    //if (xmlHttp.status == 200) {
    document.getElementById("Bayes").style.display = "block";
    document.getElementById("Bayes").innerHTML=xmlHttp.responseText;
    //document.getElementById("PredictiveResults-title").style.display = "block";
    //document.getElementById("Prediction").style.display = "block";
    document.getElementById("Bayes_loading_div").style.display = "none"; 
    processrunning = 0;
  }
}
function load_Comp_Gene_CoOccurrence()
{
  if (xmlHttp.readyState == 4) {
    //if (xmlHttp.status == 200) {
    document.getElementById("Co-Occurrence_Medline").style.display = "block";
    document.getElementById("Co-Occurrence_Medline").innerHTML=xmlHttp.responseText;
    //document.getElementById("PredictiveResults-title").style.display = "block";
    //document.getElementById("Prediction").style.display = "block";
    document.getElementById("Medline_loading_div").style.display = "none";
    processrunning = 0;
  }
}
function load_slap()
{
  if (xmlHttp.readyState == 4)
  {
    var ret = xmlHttp.responseText;
    alert(ret);
    processrunning = 0;
    //  if (xmlHttp.status == 200) {
    document.getElementById("note").innerHTML = "";
    document.getElementById("slap").style.display = "block";
    document.getElementById("slap_loading_div").style.display = "none";

    if (ret == "No input gene found!" ||
          ret == "No input compound found!" ||
          ret == "No input compound, even similar ones found!" || 
          ret == "End node is not found!" ||
          ret == "No valid path is found!" || ret == "failed" ||
          ret == "No associations found!")
    {
      document.getElementById("slap").innerHTML= ret;
    }
    else
    {
      var slap_prediction = ret.substring(0, ret.indexOf("<graphml>")-3).replace("\\", "<br \>");
      document.getElementById("slap").innerHTML= slap_prediction;//pre_1 + "<br \>" + pre_2;
      var network=ret.substring(ret.indexOf("<graphml>"), ret.indexOf("</graphml>") + 10);
      callbackslap(network);
    }
  }
}
function MessageBox()
{
  alert("Please input Gene Symbol and CID first!");
}
function DoRESTPrediction(number) 
{
  //document.getElementById("PredictiveResults-title").style.display = "none";
  //document.getElementById("Prediction").style.display = "none";
  var gene = document.getElementById("gene").value;
  var cid = document.getElementById("cid").value;  
  
  if(processrunning == 1)
    alert("Please wait till the previous job you submitted finishes");
  else 
  {
    createXmlHttp();
    if(number == 0)
    {
      if(gene.length == 0 || cid.length == 0)
        MessageBox();  
      else
      {
        document.getElementById("Sea_loading_div").style.display = "block";
        document.getElementById("Sea").style.display = "none";
        callRestPrediction(cid, gene, 0);    
          
      }
    }
    else if(number == 1)
    {  
      if(gene.length == 0 || cid.length == 0)
        MessageBox();  
      else
      {
        document.getElementById("Bayes_loading_div").style.display = "block";
        document.getElementById("Bayes").style.display = "none";
        callRestPrediction(cid, gene, 1);  
      }      
    }
    else if(number == 2)
    {
      if (gene.length == 0 && cid.length == 0){
        alert("Please input compound or protein first!");
      } else if (cid.length >0 && gene.length==0){
        go_to_compound();
      } else if (cid.length >0 && gene.length>0){
        go_to_chemohub();
      } else if (cid.length ==00 && gene.length>0){
        go_to_target();
      } else {
        //document.getElementById("slap_loading_div").style.display = "block";
        //document.getElementById("slap").style.display = "none";
        callRestPrediction(cid, gene, 2);
      }
    }
    else if (number == 3)
    {
      if (gene.length == 0 || cid.length == 0)
         MessageBox();  
      else
      {
        document.getElementById("Medline_loading_div").style.display = "block";
        document.getElementById("Co-Occurrence_Medline").style.display = "none";
        callRestPrediction(cid, gene, 3);
      }
    }
  }
//  else
//  {
//    var cid_id = "cid" + number;
//    cid = document.getElementById(cid_id).value;    
//  }
//  load1(cid, gene);
}
window.onload=function() 
{
};
</script>
        
<style>
    * { margin: 0; padding: 0; font-family: Helvetica, Arial, Verdana, sans-serif; }
    html, body { height: 100%; width: 100%; padding: 0; margin: 0; background-color: white; }
    body { line-height: 2.5; color: #000000; font-size: 14px; }
    /* The Cytoscape Web container must have its dimensions set. */
    #cytoscapeweb { width: 800; height: 500; }
    #note { width: 100%; text-align: center; padding-top: 1em; }
    .link { text-decoration: underline; color: #0b94b1; cursor: pointer; }
.style1 {
        text-align: center;
}
</style>

  </head>
  
  <body>
  <div class="style1">
    <br>
    <img alt="SLAP logo" src="images/slap.bmp" width="373" height="150"><br>
    <br>
    <br>
    <table align = "center">
     <tr valign = "top">
      <td width="45%">
        <table>
          <tr>
            <td style="width: 560px">
              <i><b><font face="Acrial" color="#aa5374" size="4">
                  Compound </font></b></i><br />
                  <font face="Acrial" color="#aa5374" size="2">
                  (CID, SMILES, or Drug Name)&nbsp;</font><br />   
                              <%
      
                      String smiles = request.getParameter("smiles");
                      if(smiles == null)
                      {
                      %>
                        <input type="text" id="cid" size="61">

                        <INPUT TYPE="button" VALUE="structure" onClick="launchJME()" style="width: 66px"><br />
                      <%
                      }
                      else
                      {
                      %>
                    <input type="text" id="cid" size="61" value=<%=smiles%>><br />       
                  <%   
                  } %>
                   
                   <font face="Acrial" color="#aa5374" size="1">
                  (Example: 5880, CC12CCC(CC1CCC3C2CCC4(C3CCC4=O)C)O, or Aetiocholanolone)</font>
            </td>          
          </tr>
          <tr>
            <td style="width: 345px">
              &nbsp;<br />          
            </td>
          </tr>
          <tr>
            <td id = "jme" style = "display:none; width: 345px;">
               <applet code="JME.class" name="JME" archive="JME.jar" width="700" height="300"> 
              <param name="options" value="list of keywords"> 
              Enable Java in your browser ! 
              </applet> 
              
              <div id = "retrievesmiles" style = "display:none">
              <br /> 
                <INPUT TYPE="button" VALUE="Get SMILES" onClick="getSmiles()">  
              </div>
            </td>
          </tr>
        </table>
      </td>
      <td width="10%">
      </td>
        <td width="45%">
          <table>
            <tr>
              <td style="width: 560px">
                <i><b><font face="Acrial" color="#aa5374" size="4">
              Protein <br /></font></b></i>
              <font face="Acrial" color="#aa5374" size="2">
              (Gene Symbol, Protein Name, or UniportID)&nbsp;</font><br />
              <input type="text" id="gene" name="gene" size="61"/> 
               <INPUT TYPE="button" VALUE="sequence"  onClick="launchSequence()" style="width: 66px">&nbsp;&nbsp; <br />
              <font face="Acrial" color="#aa5374" size="1">
                  (Example: NR1I2, Pregnane X receptor or O75469)</font>
               </td>
             </tr>
           </table>
           <table>
           <tr>
             <td id = "sequenceNoticeArea" style = "display:none; width: 345px;">
               <div id = "sequenceNotice" style = "display:none"></div>              
             </td>
             <td id = "sequenceArea" style = "display:none; width: 345px;">
              <textarea id="sequence" name="sequence" style="width: 359px; height: 127px"></textarea>
          
              <div id = "getSequence" style = "display:none">
                <INPUT TYPE="button" VALUE="retrieve Target" onClick="searchTarget()">  
              </div>
              
          </td>
           </tr>
           </table>
        </td>    
    </tr>
    </table>
 
    </div>

   
       <script  type="text/javascript"  defer=true>
            $("#cid").autocomplete("getdata.jsp");            
      </script>
         <script  type="text/javascript"  defer=true>
            $("#gene").autocomplete("gettargetdata.jsp");            
      </script>
    
    <p class="style1">  
  <INPUT TYPE="button" VALUE="SLAP" onClick="DoRESTPrediction('<%=2%>')" style="width: 65px; height: 33px;"><strong>&nbsp;&nbsp;</strong><INPUT TYPE="button" VALUE="Advanced" onClick="go_to_advanced()" style="width: 78px; height: 34px;"></p>
  <p class="style1"> 
                  <a href="http://${initParam.DBHOST}/slap/slap.jsp?cid=Troglitazone&amp;gene=PPARG">
                  example1</a>;
                  <a href="http://${initParam.DBHOST}/slap/slap.jsp?cid=Paxil&amp;gene=Beta-1%20adrenergic%20receptor">
                  example 2</a>;
                  <a href="http://${initParam.DBHOST}/slap/slap.jsp?cid=Dexamethasone&amp;gene=annexin%20A1">
                  example 3</a>;
                  <a href="http://${initParam.DBHOST}/slap/slap.jsp?cid=65981&amp;gene=KCNJ1">
                  example 4</a>;
                  <a href="http://${initParam.DBHOST}:8080/slap/slap.jsp?cid=Alendronate&gene=FDPS">
                  example 5</a>
</p>
  <table style="width: 1123px; height: 0">
          <tr>
                  <td width="30%">&nbsp;</td>
                  <td width="70%">
                  <ul>
                          <li>input compound and target to get their association</li>
                          <li>input compound alone to get its targets and its biologically similar drugs (take ~1min)</li>
                          <li>input protein alone to get its ligands</li>
                          <li>click &#39;advanced&#39; to upload your drug target pairs </li>
                  </ul>
                  </td>
                  <td>&nbsp;</td>
          </tr>
          <tr>
                  <td>&nbsp;</td>
                  <td>
                  &nbsp;</td>
                  <td>&nbsp;</td>
          </tr>
</table>
  <div>
</div>
  <p class="style1">
  <a target="_blank" href="http://slapfordrugtargetprediction.wikispaces.com/">Help</a>
  <a target="_blank" href="http://slapfordrugtargetprediction.wikispaces.com/API">API</a>
  <a target="_blank" href="http://${initParam.DBHOST}:8080/download/slap/">Download</a>
  <a target="_blank" href="http://${initParam.DBHOST}:8080/slap/acknowledgement.htm">Acknowledgement</a>
  <a target="_blank" href="http://${initParam.DBHOST}/rest/Chem2Bio2RDF/php/feedback.php">Feedback</a>
  
  </p>
 
    <p class="style1">&nbsp;&nbsp; Recommend: run SLAP in Firefox or Chrome</p>
    <p class="style1">if you are not happy with the result or your compound is a chemical rather than a drug, do let us know, our beta version may be of help.  </p>
    <p class="style1">Cite: Chen B, Ding Y, Wild DJ (2012) Assessing Drug Target Association Using Semantic Linked Data. PLoS Comput Biol 8(7): e1002574. doi:10.1371/journal.pcbi.1002574</p>
   
    <script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-26970021-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
    </script>

<p>DEBUG: request: <%= ((request==null)?"null":"ok, not null") %> </p>
<p>DEBUG: context: <%= ((context==null)?"null":"ok, not null") %> </p>
<p>DEBUG: contextpath: <%= context.getContextPath() %> </p>
<p>DEBUG: API_HOST: <%= context.getInitParameter("API_HOST") %> </p>
<p>DEBUG: API_BASE_PATH: <%= context.getInitParameter("API_BASE_PATH") %> </p>
<ul>
<%
for (Enumeration e=context.getInitParameterNames(); e.hasMoreElements(); )
{
  String key = (String)e.nextElement();
  %>
  <li>DEBUG: context init param: <%= key  %> ; value: <%= context.getInitParameter(key) %>
  <%
}
%>
<ul>
  </body>
</html>
