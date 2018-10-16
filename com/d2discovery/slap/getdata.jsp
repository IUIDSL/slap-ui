<%@page import="java.util.Iterator"%>
<%@page import="java.util.List"%>
<%@page import="com.d2discovery.slap.DrugDB"%>
<%
  DrugDB db = new DrugDB();

  String query = request.getParameter("q");

  List<String> countries = db.getData(query);

  Iterator<String> iterator = countries.iterator();
  while(iterator.hasNext()) {
    String country = (String)iterator.next();
    out.println(country);
  }
%>
