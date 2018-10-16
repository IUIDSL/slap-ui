package com.d2discovery.slap;

/* Location:           /home/jjyang/Downloads/slap/WEB-INF/classes/
 * Qualified Name:     Prediction.Test
 * JD-Core Version:    0.6.2
 */

import java.io.*;

/**	Simple test program.
*/
public class Test
{
  public static void main(String[] args)
    throws Exception
  {
    RetrieveData test1 = new RetrieveData();
    System.out.println(test1.getDrugInfo(5591));
  }
}
