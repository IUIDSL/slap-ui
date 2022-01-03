package edu.indiana.sice.idsl.slap;

/* Location:           /home/jjyang/Downloads/slap/WEB-INF/classes/
 * Qualified Name:     utils.DrugDB
 * JD-Core Version:    0.6.2
 */

import java.util.*;
import java.io.*; //BufferedReader,InputStreamReader,PrintStream;
import java.net.URL;

/**	May be unused and obsolete.
*/
public class DrugDB
{
  public List<String> getData(String query)
  {
    List matched = new ArrayList();
    query = query.toLowerCase();
    try
    {
      URL url = new URL("http://cheminfov.informatics.indiana.edu:8080/slap/data/drugs.txt");
      BufferedReader in = new BufferedReader(new InputStreamReader(url.openStream()));
      String str;
      while ((str = in.readLine()) != null)
      {
        if (str.toLowerCase().startsWith(query)) {
          matched.add(str);
        }
      }
      in.close();
    } catch (Exception e) {
      System.err.println(e.getMessage());
    }
    return matched;
  }
}
