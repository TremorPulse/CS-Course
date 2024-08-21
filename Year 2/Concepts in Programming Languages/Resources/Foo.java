import java.util.ArrayList;
import java.util.Arrays;

class Fruit {
  int weight;
}

class Apple extends Fruit {
  boolean isRed;
}

public class Foo { 
   public static void main(String[] args) { 
      System.out.println("Starting...");
      Fruit f = new Fruit();
      Apple a = new Apple();

      System.out.println("Simple casting:");
      Fruit OKf = a;
//      Apple ERRORa = f;

      // olde-style arrays:
      Apple[] av = new Apple[10];
      Fruit[] fv = new Fruit[10];
      // make ArrayLists containing the same elements as the arrays av,fv:
      ArrayList<Apple> al = new ArrayList<Apple>(Arrays.asList(av));
      ArrayList<Fruit> fl = new ArrayList<Fruit>(Arrays.asList(fv));
      System.out.println("Checking: al.size="+al.size()+"; fl.size="+fl.size());

      // now explore variance ...
//      ArrayList<Fruit> ERRORq = al; //ERROR!
      ArrayList<? extends Fruit> p = al;
      ArrayList<Fruit> q = fl;
      Fruit gotf = p.get(3);
//      p.set(3,f);    // ERROR!
      q.set(3,f);

      System.out.println("Olde-style arrays and variance:");
      Fruit[] r = av;
      r[3] = f;

      System.out.println("Stopping");
   }
}
