<%@ page language="java" import="java.util.*" %>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
  <script  type="text/javascript" src="http://www.google.com/jsapi"></script>  
  <script  type="text/javascript">  
    google.load("jquery", "1");
  </script >
  <script  type="text/javascript" src="js/jquery.autocomplete.js"></script>  


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
    
    <title>Semantic Link Association Prediction</title>
  <meta http-equiv="pragma" content="no-cache">
  <meta http-equiv="cache-control" content="no-cache">
  <meta http-equiv="expires" content="0">    
  <meta http-equiv="keywords" content="keyword1,keyword2,keyword3">
  <meta http-equiv="description" content="This is my page">
  <!--
  <link rel="stylesheet" type="text/css" href="styles.css">
  -->
    <link rel="stylesheet" type="text/css" href="css/jquery.autocomplete.css">

<!-- JSON support for IE (needed to use JS API) -->
        <script type="text/javascript" src="js/min/json2.min.js"></script>
        
        <!-- Flash embedding utility (needed to embed Cytoscape Web) -->
        <script type="text/javascript" src="js/min/AC_OETags.min.js"></script>
        
        <!-- Cytoscape Web JS API (needed to reference org.cytoscapeweb.Visualization) -->
        <script type="text/javascript" src="js/min/cytoscapeweb.min.js"></script>

<SCRIPT LANGUAGE="JavaScript">
var processrunning = 0;
var xmlHttp;
var vis;
var network;

String.prototype.trim = function() {
  return this.replace(/^\s+|\s+$/g,"");
}

function likeSLAP(){
  sendFeedback("like");
}

function dislikeSLAP(){
  sendFeedback("dislike");
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

function go_to_compound()
{
  var cid = document.getElementById("cid").value;  
  cid=cid.trim();

  var link = "http://${initParam.API_HOST}${initParam.API_BASE_PATH}/slap/cid=" +cid;
  window.open(link);
}

function go_to_target()
{
  var gene = document.getElementById("gene").value;  
  gene=gene.trim();

  var link = "http://${initParam.API_HOST}${initParam.API_BASE_PATH}/slap/target=" +gene;
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

function sendFeedback(like)
{
  var URL;
  createXmlHttp();
      URL = "TraceUserFeedback?cid=" + encodeURIComponent(document.getElementById("cid").value)+"&gene=" + encodeURIComponent(document.getElementById("gene").value)+"&like="+like;
  xmlHttp.open("get", URL, true);
  xmlHttp.onreadystatechange = function(){load_feedback();};
  xmlHttp.send(null);
}

function load_feedback(){
    if (xmlHttp.readyState == 4) {  
    if (xmlHttp.responseText=="1")
      alert("thanks for your feedback");  
    else
      alert("oops, something wrong in taking your feedback, please contact us, thanks.");  
      
    }

}

function retrieveData(uri,nodeclass)
{
  var URL;
  createXmlHttp();
    URL = "RetrieveData?uri=" + encodeURIComponent(uri)+"&nodeclass=" + encodeURIComponent(nodeclass);//escape(smiles.valueOf());
  xmlHttp.open("get", URL, true);
  xmlHttp.onreadystatechange = function(){load_node_data();};
  xmlHttp.send(null);
  processrunning = 1;
}

function load_node_data(){
    if (xmlHttp.readyState == 4) {  
    results=xmlHttp.responseText;
    results=results.replace("\n","<br>");
    if (results.length>600)
      results=results.substr(0,600)+"...";
    document.getElementById("noteFromServer").innerHTML=results;  
      processrunning = 0;
    }

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
      xmlHttp.onreadystatechange = function(){load_slap()};
      xmlHttp.send(null);
      processrunning = 1;
  }
            
}
function load_Sea_Prediction() {
    if (xmlHttp.readyState == 4) {
  //  if (xmlHttp.status == 200) {
        document.getElementById("Sea").style.display = "block";
        document.getElementById("Sea").innerHTML=xmlHttp.responseText;
  //      document.getElementById("PredictiveResults-title").style.display = "block";
  //      document.getElementById("Prediction").style.display = "block";
      document.getElementById("Sea_loading_div").style.display = "none"; 
      processrunning = 0;
    }
}

function load_Bayes_Prediction() {
    if (xmlHttp.readyState == 4) {
  //  if (xmlHttp.status == 200) {
        document.getElementById("Bayes").style.display = "block";
        document.getElementById("Bayes").innerHTML=xmlHttp.responseText;
  //      document.getElementById("PredictiveResults-title").style.display = "block";
  //      document.getElementById("Prediction").style.display = "block";
      document.getElementById("Bayes_loading_div").style.display = "none"; 
      processrunning = 0;
    }
}

function load_Comp_Gene_CoOccurrence() {
    if (xmlHttp.readyState == 4) {
  //  if (xmlHttp.status == 200) {
      document.getElementById("Co-Occurrence_Medline").style.display = "block";
        document.getElementById("Co-Occurrence_Medline").innerHTML=xmlHttp.responseText;
    //    document.getElementById("PredictiveResults-title").style.display = "block";
    //    document.getElementById("Prediction").style.display = "block";
      document.getElementById("Medline_loading_div").style.display = "none";
      processrunning = 0;
    }
}

function load_slap() {
    if (xmlHttp.readyState == 4) {
      var ret = xmlHttp.responseText;
  //  if (xmlHttp.status == 200) {
      document.getElementById("note").innerHTML = "";
        document.getElementById("slap").style.display = "block";
        document.getElementById("slap_loading_div").style.display = "none";
        processrunning = 0;
        if(ret.indexOf("found")>0 || ret.indexOf("failed")>0)
        {
          document.getElementById("slap").innerHTML= ret;
        }
        else
         {
          var slap_prediction = ret.substring(0, ret.indexOf("<graphml>")-3).replace("\\", "<br \>");
          slap_prediction=slap_prediction.split("\\");
          document.getElementById("slap").innerHTML= slap_prediction[0]+"<br>"+ slap_prediction[1]+"<br>"+"<br>"+slap_prediction[2]; //"<br \>" + pre_2;
          var network=ret.substring(ret.indexOf("<graphml>"), ret.indexOf("</graphml>") + 10);
        callbackslap(network,"Tree");
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
  
  cid=cid.trim();
  gene=gene.trim();

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
      if(gene.length == 0 && cid.length == 0){
        alert("Please input compound or protein first!");
      }
      else if (cid.length >0 && gene.length==0){
        go_to_compound();
      }
      else if (cid.length ==00 && gene.length>0){
        go_to_target();

      }else{
        document.getElementById("slap_loading_div").style.display = "block";
        document.getElementById("slap").style.display = "none";
        callRestPrediction(cid, gene, 2);
      }
    }
    else if(number == 3)
    {
      if(gene.length == 0 || cid.length == 0)
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
      //smiles = request.getParameter("smiles");
  var queryString = window.top.location.search.substring(1);
  var cid=getParameter(queryString,"cid");
  var gene=getParameter(queryString,"gene");
  if (cid!=null && gene!=null){
    document.getElementById("gene").value=gene;
    document.getElementById("cid").value=cid
    DoRESTPrediction(2);
  }else{
network='\
<graphml>\
  <key id="label" for="all" attr.name="label" attr.type="string"/>\
  <key id="class" for="all" attr.name="class" attr.type="string"/>\
  <key id="uri" for="all" attr.name="uri" attr.type="string"/>\
  <key id="startnode" for="all" attr.name="startnode" attr.type="string"/>\
  <key id="evidence" for="all" attr.name="evidence" attr.type="string"/>\
  <key id="weight" for="all" attr.name="weight" attr.type="double"/>\
  <key id="childnodes" for="all" attr.name="childnodes" attr.type="string"/>\
  <key id="nodesize" for="all" attr.name="nodesize" attr.type="string"/>\
  <graph edgedefault="undirected">\
  <node id="http://chem2bio2rdf.org/kegg/resource/kegg_pathway/hsa04920">\
    <data key="childnodes">http://chem2bio2rdf.org/kegg/resource/kegg_pathway/hsa00071</data>\
    <data key="label">hsa04920(1)</data>\
    <data key="class">kegg_pathway</data>\
    <data key="nodesize">3</data>\
    <data key="startnode">no</data>\
  </node>\
  <node id="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL4">\
    <data key="label">ACSL4</data>\
    <data key="class">gene</data>\
    <data key="nodesize">5</data>\
    <data key="startnode">yes</data>\
  </node>\
  <node id="http://chem2bio2rdf.org/hgnc/resource/gene_family/ACS">\
    <data key="label">ACS</data>\
    <data key="class">gene_family</data>\
    <data key="nodesize">1</data>\
    <data key="startnode">no</data>\
  </node>\
  <node id="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL3">\
    <data key="label">ACSL3</data>\
    <data key="class">gene</data>\
    <data key="nodesize">1</data>\
    <data key="startnode">no</data>\
  </node>\
  <node id="http://chem2bio2rdf.org/kegg/resource/kegg_pathway/hsa03320">\
    <data key="label">hsa03320</data>\
    <data key="class">kegg_pathway</data>\
    <data key="nodesize">1</data>\
    <data key="startnode">no</data>\
  </node>\
  <node id="http://bio2rdf.org/GO/GO:0007584">\
    <data key="label">GO:0007584</data>\
    <data key="class">GO</data>\
    <data key="nodesize">1</data>\
    <data key="startnode">no</data>\
  </node>\
  <node id="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/446284">\
    <data key="label">446284</data>\
    <data key="class">pubchem_compound</data>\
    <data key="nodesize">5</data>\
    <data key="startnode">yes</data>\
  </node>\
  <node id="http://chem2bio2rdf.org/uniprot/resource/gene/PPARG">\
    <data key="label">PPARG</data>\
    <data key="class">gene</data>\
    <data key="nodesize">1</data>\
    <data key="startnode">no</data>\
  </node>\
  <node id="http://chem2bio2rdf.org/uniprot/resource/gene/FADS1">\
    <data key="childnodes">http://chem2bio2rdf.org/uniprot/resource/gene/SLC8A1</data>\
    <data key="label">FADS1(1)</data>\
    <data key="class">gene</data>\
    <data key="nodesize">3</data>\
    <data key="startnode">no</data>\
  </node>\
  <node id="http://bio2rdf.org/GO/GO:0016874">\
    <data key="childnodes">http://bio2rdf.org/GO/GO:0006629  http://bio2rdf.org/GO/GO:0005741  http://bio2rdf.org/GO/GO:0005792  http://bio2rdf.org/GO/GO:0005778  http://bio2rdf.org/GO/GO:0005777  http://bio2rdf.org/GO/GO:0004467</data>\
    <data key="label">GO:0016874(6)</data>\
    <data key="class">GO</data>\
    <data key="nodesize">3</data>\
    <data key="startnode">no</data>\
  </node>\
  <node id="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/5591">\
    <data key="label">5591</data>\
    <data key="class">pubchem_compound</data>\
    <data key="nodesize">1</data>\
    <data key="startnode">no</data>\
  </node>\
  <node id="http://chem2bio2rdf.org/uniprot/resource/gene/PPARD">\
    <data key="label">PPARD</data>\
    <data key="class">gene</data>\
    <data key="nodesize">1</data>\
    <data key="startnode">no</data>\
  </node>\
  <node id="http://chem2bio2rdf.org/uniprot/resource/gene/PTGS2">\
    <data key="label">PTGS2</data>\
    <data key="class">gene</data>\
    <data key="nodesize">1</data>\
    <data key="startnode">no</data>\
  </node>\
  <node id="http://bio2rdf.org/GO/GO:0015908">\
    <data key="label">GO:0015908</data>\
    <data key="class">GO</data>\
    <data key="nodesize">1</data>\
    <data key="startnode">no</data>\
  </node>\
  <edge source="http://bio2rdf.org/GO/GO:0016874" target="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL4">\
    <data key="weight">0.0544147482263</data>\
    <data key="label">GO_ID</data>\
    <data key="uri">http://chem2bio2rdf.org/uniprot/resource/GO_ID</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/kegg/resource/kegg_pathway/hsa04920" target="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL4">\
    <data key="weight">0.000479226231734</data>\
    <data key="label">protein</data>\
    <data key="uri">http://chem2bio2rdf.org/kegg/resource/protein</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL3" target="http://chem2bio2rdf.org/kegg/resource/kegg_pathway/hsa04920">\
    <data key="weight">0.000479226231734</data>\
    <data key="label">protein</data>\
    <data key="uri">http://chem2bio2rdf.org/kegg/resource/protein</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/uniprot/resource/gene/PPARD" target="http://bio2rdf.org/GO/GO:0015908">\
    <data key="weight">0.0851373022978</data>\
    <data key="label">GO_ID</data>\
    <data key="uri">http://chem2bio2rdf.org/uniprot/resource/GO_ID</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/446284" target="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL3">\
    <data key="weight">0.000110027791106</data>\
    <data key="label">chemogenomics</data>\
    <data key="uri">http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics</data>\
    <data key="evidence">http://${initParam.API_HOST}${initParam.API_BASE_PATH}/cid_gene/446284:ACSL3</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/kegg/resource/kegg_pathway/hsa03320" target="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL4">\
    <data key="weight">0.000544677003865</data>\
    <data key="label">protein</data>\
    <data key="uri">http://chem2bio2rdf.org/kegg/resource/protein</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL3" target="http://chem2bio2rdf.org/hgnc/resource/gene_family/ACS">\
    <data key="weight">0.0115446558799</data>\
    <data key="label">Gene_Family_Name</data>\
    <data key="uri">http://chem2bio2rdf.org/hgnc/resource/Gene_Family_Name</data>\
  </edge>\
  <edge source="http://bio2rdf.org/GO/GO:0007584" target="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL4">\
    <data key="weight">0.00644022290265</data>\
    <data key="label">GO_ID</data>\
    <data key="uri">http://chem2bio2rdf.org/uniprot/resource/GO_ID</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/446284" target="http://chem2bio2rdf.org/uniprot/resource/gene/PTGS2">\
    <data key="weight">0.140439832446</data>\
    <data key="label">chemogenomics</data>\
    <data key="uri">http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics</data>\
    <data key="evidence">http://${initParam.API_HOST}${initParam.API_BASE_PATH}/cid_gene/446284:PTGS2</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL3" target="http://bio2rdf.org/GO/GO:0007584">\
    <data key="weight">0.00644022290265</data>\
    <data key="label">GO_ID</data>\
    <data key="uri">http://chem2bio2rdf.org/uniprot/resource/GO_ID</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL3" target="http://bio2rdf.org/GO/GO:0016874">\
    <data key="weight">0.0544147482263</data>\
    <data key="label">GO_ID</data>\
    <data key="uri">http://chem2bio2rdf.org/uniprot/resource/GO_ID</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/uniprot/resource/gene/PPARG" target="http://chem2bio2rdf.org/kegg/resource/kegg_pathway/hsa03320">\
    <data key="weight">0.336829750479</data>\
    <data key="label">protein</data>\
    <data key="uri">http://chem2bio2rdf.org/kegg/resource/protein</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/446284" target="http://chem2bio2rdf.org/uniprot/resource/gene/PPARG">\
    <data key="weight">0.0005206791406</data>\
    <data key="label">chemogenomics</data>\
    <data key="uri">http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics</data>\
    <data key="evidence">http://${initParam.API_HOST}${initParam.API_BASE_PATH}/cid_gene/446284:PPARG</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/446284" target="http://chem2bio2rdf.org/uniprot/resource/gene/FADS1">\
    <data key="weight">0.0277188543683</data>\
    <data key="label">chemogenomics</data>\
    <data key="uri">http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics</data>\
    <data key="evidence">http://${initParam.API_HOST}${initParam.API_BASE_PATH}/cid_gene/446284:FADS1</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/hgnc/resource/gene_family/ACS" target="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL4">\
    <data key="weight">0.0115446558799</data>\
    <data key="label">Gene_Family_Name</data>\
    <data key="uri">http://chem2bio2rdf.org/hgnc/resource/Gene_Family_Name</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/uniprot/resource/gene/PPARG" target="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/5591">\
    <data key="weight">0.0005206791406</data>\
    <data key="label">chemogenomics</data>\
    <data key="uri">http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics</data>\
    <data key="evidence">http://${initParam.API_HOST}${initParam.API_BASE_PATH}/cid_gene/5591:PPARG</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/uniprot/resource/gene/FADS1" target="http://bio2rdf.org/GO/GO:0007584">\
    <data key="weight">0.0277188543683</data>\
    <data key="label">GO_ID</data>\
    <data key="uri">http://chem2bio2rdf.org/uniprot/resource/GO_ID</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL3" target="http://chem2bio2rdf.org/kegg/resource/kegg_pathway/hsa03320">\
    <data key="weight">0.000544677003865</data>\
    <data key="label">protein</data>\
    <data key="uri">http://chem2bio2rdf.org/kegg/resource/protein</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/446284" target="http://chem2bio2rdf.org/uniprot/resource/gene/PPARD">\
    <data key="weight">0.0851373022978</data>\
    <data key="label">chemogenomics</data>\
    <data key="uri">http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics</data>\
    <data key="evidence">http://${initParam.API_HOST}${initParam.API_BASE_PATH}/cid_gene/446284:PPARD</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/uniprot/resource/gene/PTGS2" target="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/5591">\
    <data key="weight">0.140439832446</data>\
    <data key="label">expression</data>\
    <data key="uri">http://chem2bio2rdf.org/chemogenomics/resource/expression</data>\
  </edge>\
  <edge source="http://bio2rdf.org/GO/GO:0015908" target="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL4">\
    <data key="weight">0.0851373022978</data>\
    <data key="label">GO_ID</data>\
    <data key="uri">http://chem2bio2rdf.org/uniprot/resource/GO_ID</data>\
  </edge>\
  <edge source="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/5591" target="http://chem2bio2rdf.org/uniprot/resource/gene/ACSL4">\
    <data key="weight">0.0005206791406</data>\
    <data key="label">chemogenomics</data>\
    <data key="uri">http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics</data>\
    <data key="evidence">http://${initParam.API_HOST}${initParam.API_BASE_PATH}/cid_gene/5591:ACSL4</data>\
  </edge>\
  </graph>\
</graphml>\
'
    
    callbackslap(network,"tree");
  }

};
      


function getParameter ( queryString, parameterName ) {
// Add "=" to the parameter name (i.e. parameterName=value)
var parameterName = parameterName + "=";
if ( queryString.length > 0 ) {
// Find the beginning of the string
begin = queryString.indexOf ( parameterName );
// If the parameter name is not found, skip it, otherwise return the value
if ( begin != -1 ) {
// Add the length (integer) to the beginning
begin += parameterName.length;
// Multiple parameters are separated by the "&" sign
end = queryString.indexOf ( "&" , begin );
if ( end == -1 ) {
end = queryString.length
}
// Return the string
return unescape ( queryString.substring ( begin, end ) );
}
// Return "null" if no parameter has been found
return "null";
}
}


function callbackslap(network,layout) 
//window.onload=function() 
{
    // id of Cytoscape Web container div
 //   var div_id = "cytoscapeweb";
    
    // NOTE: - the attributes on nodes and edges
    //       - it also has directed edges, which will automatically display edge arrows
 //   var xml = '\

// '; 
    
    function rand_color() {
        function rand_channel() {
            return Math.round( Math.random() * 255 );
        }
        
        function hex_string(num) {
            var ret = num.toString(16);
            
            if (ret.length < 2) {
                return "0" + ret;
            } else {
                return ret;
            }
        }
        
        var r = rand_channel();
        var g = rand_channel();
        var b = rand_channel();
        
        return "#" + hex_string(r) + hex_string(g) + hex_string(b); 
    }
    
    // visual style we will use
    var visual_style = {
        global: {
            backgroundColor: "#FFFFFF"
        },
        nodes: {
            shape: 
            {
              defaultValue: "OCTAGON",
              discreteMapper:{ 
                attrName: "startnode",
                entries:[
                  {attrValue: "yes", value: "RECTANGLE"},
                   {attrValue: "no", value: "OCTAGON"},                 
                    ]
              }
            },
                
            borderWidth: 
       {
              defaultValue: 1,
              discreteMapper:{ 
                attrName: "startnode",
                entries:[
                  {attrValue: "yes", value: 5},
                   {attrValue: "no", value: 1},                 
                    ]
              }
            },
                          
            borderColor: 
       {
              defaultValue: "#aa5374",
              discreteMapper:{ 
                attrName: "startnode",
                entries:[
                  {attrValue: "yes", value: "#110e0e"},
                   {attrValue: "no", value: "#aa5374"},                 
                    ]
              }
            },
            
           
            size: {
                defaultValue: 30,
              discreteMapper:{ 
                attrName: "nodesize",
                entries:[
                  {attrValue: "1", value: 30},
                   {attrValue: "3", value: 40},      
                   {attrValue: "5", value: 50},             
                    ]
              }
            },
      
      color: {
             defaultValue: "#FFFFFF",
                       discreteMapper: {

                           attrName: "class",

                           entries: [

                               { attrValue: "pubchem_compound", value: "#f31e1b" },

                               { attrValue: "gene", value: "#f31bd4" },

                               { attrValue: "GO", value: "#f3dc1b" },

                               { attrValue: "kegg_pathway", value: "#98f31b" },

                               { attrValue: "gene_family", value: "#1ba7f3" },

                               { attrValue: "sider", value: "#b3a3d1" },
                               
                               { attrValue: "omim_disease", value: "#acd9fb" },

                               { attrValue: "substructure", value: "#bac0c5" },

                               { attrValue: "chebi", value: "#bff708" },

                               { attrValue: "tissue", value: "#35f708" },

                           ]

                       }

                   },

            labelHorizontalAnchor: "center"
        },
        edges: {
            width: 1,
            color: {
             defaultValue: "#b6b5c4",
                       discreteMapper: {

                           attrName: "uri",

                           entries: [

                               { attrValue: "http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics", value: "#f31e1b" },

                               { attrValue: "http://chem2bio2rdf.org/chemogenomics/resource/expression", value: "#f31bd4" },

                               { attrValue: "http://chem2bio2rdf.org/uniprot/resource/GO_ID", value: "#f3dc1b" },

                               { attrValue: "http://chem2bio2rdf.org/kegg/resource/protein", value: "#98f31b" },

                               { attrValue: "http://chem2bio2rdf.org/hgnc/resource/Gene_Family_Name", value: "#1ba7f3" },

                               { attrValue: "http://chem2bio2rdf.org/hprd", value: "#98f31b" },
                               
                               { attrValue: "http://chem2bio2rdf.org/hprd/resource/tissue", value: "#35f708" },
                               
                               { attrValue: "http://chem2bio2rdf.org/omim/resource/gene", value: "#acd9fb" },
                               
                               { attrValue: "http://chem2bio2rdf.org/omim/resource/drug", value: "#acd9fb" },
                               
                               { attrValue: "http://chem2bio2rdf.org/chebi", value: "#bff708" },

                               { attrValue: "http://chem2bio2rdf.org/sider/resource/cid", value: "#b3a3d1" },

                               { attrValue: "http://chem2bio2rdf.org/substructure", value: "#bac0c5" },

                           ]

                       }

                   }

        }
    };
    
    // initialization options
    var options = {
        swfPath: "swf/CytoscapeWeb",
        flashInstallerPath: "swf/playerProductInstall"
    };
    
    vis = new org.cytoscapeweb.Visualization("cytoscapeweb", options);
    
    vis.ready(function() {
        // set the style programmatically
        //document.getElementById("color").onclick = function()
        //{
        //    visual_style.global.backgroundColor = rand_color();
        //    vis.visualStyle(visual_style);
            
       // };
        vis.addListener("click", "nodes", function(event) {
            handle_click_node(event);
        })
        .addListener("click", "edges", function(event) {
            handle_click_edge(event);
        });
        
        
        function handle_click_node(event) 
        {
             var target = event.target;
             
             clear();
             var isGene = 1;
             var name = "";
             var nodeClass="";
             var nodeID="";
             var childNodes="";
             for (var i in target.data) 
             {
                var variable_name = i;
                var variable_value = target.data[i];

                if(variable_name == "class")
                  nodeClass=variable_value;
                  
                  if(variable_value == "gene")
                    isGene = 2;
                  else if(variable_value == "pubchem_compound")
                    isGene = 0;
                    
                if(variable_name == "label")
                  name = variable_value;
                  
                if(variable_name == "id")
                  nodeID=variable_value;
                  
                if(variable_name == "childnodes")
                    childNodes=variable_value;
             }
             
             retrieveData(nodeID,nodeClass);
             
             var nodeMessage='';

    if (childNodes==null){
                  if (nodeClass=="pubchem_compound"){
                     nodeMessage="<img src='http://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?t=l&cid="+name +"' width='200' height='150' />";  
              nodeMessage=nodeMessage+"<br>"+ "<a href='http://pubchem.ncbi.nlm.nih.gov/summary/summary.cgi?cid="+name+"' target='my_window_tab_frame_or_iframe'>" + "PubChem Summary" + "</a>";              
                 }
                  if (nodeClass=="chebi"){
              nodeMessage=nodeMessage+"<br>"+ "<a href='http://www.ebi.ac.uk/chebi/advancedSearchFT.do?searchString="+name+"' target='my_window_tab_frame_or_iframe'>" + "ChEBI Summary" + "</a>";              
           }

                  if (nodeClass=="gene"){
              nodeMessage=nodeMessage+"<br>"+ "<a href='http://en.wikipedia.org/wiki/"+name+"' target='my_window_tab_frame_or_iframe'>" + "wiki" + "</a>";              
           }
           
       if (nodeClass!="substructure"){
        nodeMessage=nodeMessage+"<br>"+ "<a href='" + nodeID + "' target='my_window_tab_frame_or_iframe'>" + "more info..." + "</a>";
      }
      
    }else{               
              nodeMessage=nodeMessage+"<br>"+ "node list:"+"<a href='" + nodeID + "' target='my_window_tab_frame_or_iframe'>" + " 0" + "</a>";      
        childNodes=childNodes.split("\t");
        var count=0;
        for (node in childNodes){
          count=count+1;
          nodeMessage=nodeMessage+ "&nbsp;&nbsp;"+"<a href='" + childNodes[node] + "' target='my_window_tab_frame_or_iframe'>" + count + "</a>";      
        }
    }
        
        document.getElementById("note").innerHTML=nodeMessage;

      

             if(isGene == 2)
               document.getElementById("gene").value = name;
             else if(isGene == 0)
               document.getElementById("cid").value = name;
             
        }

        function handle_click_edge(event) {
             var target = event.target;
             
             clear();
             var noteinfo = "";
             var sou = "";
             var tar = "";
             var uri = "";
             var evidence="";
             var edgeType="";
             //print("event.group = " + event.group);
             for (var i in target.data) {
                var variable_name = i;
                var variable_value = target.data[i];
                if(variable_name == "source") 
                 sou = "<a href='" + variable_value + "' target='my_window_tab_frame_or_iframe'>" + "source node" + "</a><br />";
                else if(variable_name == "target")
                    tar = "<a href='" + variable_value + "' target='my_window_tab_frame_or_iframe'>" + "target node" + "</a><br />";
                else if(variable_name == "evidence" && variable_value!=null)
                   evidence = "<a href='" + variable_value + "' target='my_window_tab_frame_or_iframe'>" + "evidence" + "</a><br />";
                else if(variable_name == "uri")
                   if (variable_value=="http://chem2bio2rdf.org/chemogenomics/resource/chemogenomics")
                     edgeType="bind";
                   else if (variable_value=="http://chem2bio2rdf.org/chemogenomics/resource/expression")
                     edgeType="express";
                   else if (variable_value=="http://chem2bio2rdf.org/uniprot/resource/GO_ID")
                     edgeType="hasGO";
                   else if (variable_value=="http://chem2bio2rdf.org/kegg/resource/protein")
                     edgeType="hasPathway";
                   else if (variable_value=="http://chem2bio2rdf.org/hgnc/resource/Gene_Family_Name")
                     edgeType="hasGeneFamily";
                   else if (variable_value=="http://chem2bio2rdf.org/hprd")
                     edgeType="proteinProteinInteraction";
                   else if (variable_value=="http://chem2bio2rdf.org/hprd/resource/tissue")
                     edgeType="expressIn";
                   else if (variable_value=="http://chem2bio2rdf.org/omim/resource/gene")
                     edgeType="causeDisease";
                   else if (variable_value=="http://chem2bio2rdf.org/omim/resource/drug")
                     edgeType="treatDisease";
                   else if (variable_value=="http://chem2bio2rdf.org/chebi")
                     edgeType="hasChemicalOntology";
                   else if (variable_value=="http://chem2bio2rdf.org/sider/resource/cid")
                     edgeType="causeSideEffect";
                   else if (variable_value=="http://chem2bio2rdf.org/substructure")
                     edgeType="hasSubstructure";
                  
                   uri = "<a href='" + variable_value + "' target='my_window_tab_frame_or_iframe'>" + "edge type"  + "</a><br />"; 
             }
             if (evidence.length<1)
                 noteinfo = sou + tar;
              else
                 noteinfo = sou + tar +"<br>"+evidence;
             document.getElementById("note").innerHTML = noteinfo;
             document.getElementById("noteFromServer").innerHTML ="<b>Edge Type: </b>"+edgeType;
        }
              
        function clear() {
            document.getElementById("note").innerHTML = "";
        }
    
        function print(msg) {
            document.getElementById("note").innerHTML += "<p>" + msg + "</p>";
        }
    });        

    var draw_options = {
        // your data goes here
        network: network,
        
        // show edge labels too
        edgeLabelsVisible: false,
        
        // let's try another layout
        layout: layout,
        
        // set the style at initialisation
        visualStyle: visual_style,
        
        // hide pan zoom
        panZoomControlVisible: true 
    };
    
    vis.draw(draw_options);
};

function goLowPvalue()
{

pvalue=parseFloat(document.getElementById("txtPvalue").value);
document.getElementById("txtPvalue").value=pvalue-0.01;

vis.filter("edges", function(edge) {
    return edge.data.weight <= pvalue-0.01;
}, true);

}

function goHighPvalue()
{
var pvalue=parseFloat(document.getElementById("txtPvalue").value);
document.getElementById("txtPvalue").value=pvalue+0.01;

vis.filter("edges", function(edge) {
    return edge.data.weight <= pvalue+0.01;
}, true);

}

function changeLayout(){
  vis.layout(document.getElementById("networklayout").value);
}

function SavePDF()
{
    var options = {
        swfPath: "swf/CytoscapeWeb",
        flashInstallerPath: "swf/playerProductInstall"
    };
  var vis = new org.cytoscapeweb.Visualization("cytoscapeweb", options);
  vis.pdf(400, 400);
}
function exportNetwork()
{
  phpLocation='http://${initParam.API_HOST}${initParam.API_BASE_PATH}/php/export.php?type='
  format=document.getElementById("exportNetworkFormat").value;
  if (format=='xgmml')
    vis.exportNetwork('xgmml', phpLocation+'xml');
  else if (format=='png')
    vis.exportNetwork('png', phpLocation+'png');
  else if (format=='pdf')
    vis.exportNetwork('pdf', phpLocation+'pdf');
  else if (format=='svg')
    vis.exportNetwork('svg', phpLocation+'svg');
  else if (format=='sif')
    vis.exportNetwork('pdf', phpLocation+'txt');
  else if (format=='graphml')
    vis.exportNetwork('graphml', phpLocation+'xml');    
}
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
        margin-right: 1;
}
.style2 {
        border-style: solid;
        border-width: 1px;
}
.style3 {
        font-size: smaller;
}
.style4 {
        font-size: smaller;
        font-weight: normal;
}
.style6 {
        color: #0B94B1;
        font-weight: bold;
        text-decoration: underline;
        font-size: xx-small;
}
.style7 {
        color: #FF0000;
}
.style8 {
        border-width: 0px;
}
</style>

  </head>
  
  <body>
        <form id="form1" runat="server">
        <table align = "center">
     <tr valign = "top">
      <td style="width: 37%">
        <table style="width: 481px">
          <tr>
            <td style="width: 450px">
              <i><b><font face="Acrial" color="#aa5374" size="4">
                  Compound </font></b></i><br />
                  <font face="Acrial" color="#aa5374" size="2">
                  (CID, SMILES, or Drug Name)&nbsp;</font><br />   
                              <%
      
                      String smiles = request.getParameter("smiles");
                      if(smiles == null)
                      {
                      %>
                        <input type="text" id="cid" size="61" tabindex="1">
                      <%
                      }
                      else
                      {
                      %>
                    <input type="text" id="cid0" size="61" value=<%=smiles%>><br />       
                  <%   
                  } %>
                   
                   <font face="Acrial" color="#aa5374" size="1">
                  (Example: 5880, CC12CCC(CC1CCC3C2CCC4(C3CCC4=O)C)O, or Aetiocholanolone)</font>
              <br>
              <INPUT TYPE="button" VALUE="draw structure" onClick="launchJME()" style="width: 96px" tabindex="5"></td>          
          </tr>
          <tr>
            <td style="width: 450px">
              &nbsp;<br />          
            </td>
          </tr>
          <tr>
            <td id = "jme" style = "display:none; width: 450px;">
               <applet code="JME.class" name="JME" archive="JME.jar" height="300" style="width: 462px"> 
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
      <td style="width: 2%">
      </td>
        <td width="45%">
          <table>
            <tr>
              <td style="width: 777px">
                <b>
                <i><font face="Acrial" color="#aa5374" size="4">
              Protein&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
              <span class="style3">&nbsp;&nbsp; </span><br /></i>
              </b></font>
              <font face="Acrial" color="#aa5374" size="2">
              (Gene Symbol, Protein Name, or UniportID)&nbsp;</font><br />
              <input type="text" id="gene" size="61" tabindex="2" style="width: 358px">


 &nbsp;&nbsp;   
              <INPUT TYPE="button" VALUE="SLAP" onClick="DoRESTPrediction('<%=2%>')" style="width: 62px; height: 26px;" tabindex="3"><INPUT TYPE="button" VALUE="Advanced" onClick="go_to_advanced()" style="width: 70px; height: 26px;" class="style1" tabindex="4"><br />
              <font face="Acrial" color="#aa5374" size="1">
                  (Example: NR1I2, Pregnane X receptor or O75469)</font>
                 <br>
              <INPUT TYPE="button" VALUE="input sequence"  onClick="launchSequence()" style="width: 106px" tabindex="6"></td>
             </tr>
            <tr>
              <td style="width: 777px">
                &nbsp;</td>
             </tr>
           </table>
           <table>
           <tr>
             <td id = "sequenceNoticeArea" style = "display:none; width: 345px;">
               <div id = "sequenceNotice" style = "display:none"></div>              
             </td>
             <td id = "sequenceArea" style = "display:none; width: 444px;">
              <textarea id="sequence" name="sequence" style="width: 359px; height: 127px" rows="1" cols="20"></textarea>
          
              <div id = "getSequence" style = "display:none">
                <INPUT TYPE="button" VALUE="retrieve Target" onClick="searchTarget()">  
              </div>
              
          </td>
           </tr>
           </table>
        </td>
        <td>
        <font face="Acrial" color="#aa5374" size="4">
              <span class="style3">
              <a target="_blank" href="http://slapfordrugtargetprediction.wikispaces.com/">
              help</a></span><b><i> </i>
              <span class="style4">
              <a target="_blank" href="http://${initParam.API_HOST}${initParam.API_BASE_PATH}/php/feedback.php">
              feedback</a></span></b></font>
      <br>
      <a href="index.jsp">
      <img alt="" src="images/slap.bmp" width="120" height="60" class="style8"></a>

      </td>    
    </tr>
    </table>


   <table  width="100%" id = "PredictiveInfo" align="left" class="style2">
      <tr>
        <td width="60%">
 
        <table  width="100%" border="0" id = "Network">           
            <tr>
              <td>
                <div id = "PredictiveNetwork">
                           <table id="networkNavigator">
          <td style="width: 150px">Save <select id="exportNetworkFormat" name="Select1" onchange="exportNetwork()" >
                  <option value="png" selected>png</option>
                  <option value="svg">svg</option>
                  <option value="pdf">pdf</option>
                  <option value="xgmml">xgmml</option>
                  <option value="graphml">graphml</option>
                  <option value="sif">sif</option>                  
                                    
                  </select>
            </td>
            <td style="width: 188px"> lay out 
                  <select id="networklayout" name="networklayout" onchange="changeLayout()" >
                  <option value="Tree" SELECTED>Tree</option>
                  <option value="ForceDirected">ForceDirected</option>
                  <option value="Circle">Circle</option>
                  <option value="Radial">Radial</option>
                  </select>
            </td>
            <td>
                      <input name="weaking" type="button" value="<<" onclick="goLowPvalue()">  
                  <label>score 
                  <input type="text" id="txtPvalue" size="30" value="0.05" style="width: 43px" maxlength="5"></label>
                  <input name="stronging" type="button" value='>>' onclick="goHighPvalue()"> 
            </td>
          </table> 
          </div>
                <div id="cytoscapeweb"></div>
            </td>
          </tr>
        </table>
        </td>
        
        <td width="40%" valign = "top">
        <table  width="100%" id = "Prediction" class="style2">    
          <tr><td class="style7"><strong>SLAP Results:</strong></td></tr>       
            <tr> 
              <td>
                
                <div id = "slap" style = "display:none"></div>
                <div id = "slap_loading_div" style = "display:none">
                  <p>Loading...</p>
                </div>
                    <br>
                    <table>  
                      <tr>      
                    <td><div id="like" style="display:block" onclick="likeSLAP()" class="style6">like</div>                
                    </td>
                    <td>
                      <div id="dislike" style="display:block" onclick="dislikeSLAP()" class="style6">dislike</div>
                  </td>
                </tr>  
              </table>
            </td>
          </tr>
        </table>

        <table style="width: 100%; height: 390px" class="style2" align="left" ><tr><td valign="top">
        <table  width="100%"   align="left" >          
                  <tr>
          <td id="noteFromServer" valign="top" align="left"></td>
          </tr>
 
            <tr> 
              <td id = "note" valign="top" align="left">
            </td>
          </tr>
        </table>
        </td>
        </tr>
        </table>
        </td>
      </tr>
      </table>    
    <table style="width: 866px">
      <tr>
        <td style="width: 200px"  >
         Other Predictive Models:
        <br />          
        </td>
        <td>
        <INPUT TYPE="button" VALUE="Similarity Ensemble Approach" onClick="DoRESTPrediction('<%=0%>')" style="width: 201px">
        <div id = "Sea" style = "display:none"></div>
                <div id = "Sea_loading_div" style = "display:none">
                  <p>Loading...</p>
                </div>
                
        </td>
        <td>
        <INPUT TYPE="button" VALUE="Naive Bayes Model" onClick="DoRESTPrediction('<%=1%>')" style="width: 179px">
        <div id = "Bayes" style = "display:none"></div>
                <div id = "Bayes_loading_div" style = "display:none">
                  <p>Loading...</p>
                </div>
        </td>
        <td>
        <INPUT TYPE="button" VALUE="Occurences in Literatures" onClick="DoRESTPrediction('<%=3%>')" style="width: 240px">
        <div id = "Co-Occurrence_Medline" style = "display:none"></div>
                <div id = "Medline_loading_div" style = "display:none">
                  <p>Loading...</p>
                </div>
        </td>
      </tr>
  </table>
  
  
        </form>
</body>
</html>
