<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" 
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <link rel="stylesheet" type="text/css" href="css/jquery.autocomplete.css" />
  <script src="http://www.google.com/jsapi"></script>  
  <script>  
    google.load("jquery", "1");
  </script>
  <script src="js/jquery.autocomplete.js"></script>  
  <style>
    input {
      font-size: 120%;
    }
  </style>
</head>
<body>
  
  <h3>Country</h3>
  <input type="text" id="country" name="country"/>
  
  <script>
    $("#country").autocomplete("getdata.jsp");
  </script>
  
            <table>
            <tr>
              <td style="width: 560px">
                <i><b><font face="Acrial" color="#aa5374" size="4">
              Protein <br /></font></b></i>
              <font face="Acrial" color="#aa5374" size="2">
              (Gene Symbol, Gene Name, or UniportID)&nbsp;</font><br />
              dd
              <input type="text" id="gene" name="gene" size="61"/> 
  <script>
    $("#gene").autocomplete("getdata.jsp");
  </script>  
               <INPUT TYPE="button" VALUE="sequence"  onClick="launchSequence()" style="width: 66px">&nbsp;&nbsp; <br />
              <font face="Acrial" color="#aa5374" size="1">
                  (Example: NR1I2, Pregnane X receptor or O75469)</font>
               </td>
             </tr>
           </table>
</body>
</html>
