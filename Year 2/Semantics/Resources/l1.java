//Matthew Parkinson, 1/2004

public class L1 {

    public static void main(String [] args) {
        //test code
	Location l1 = new Location ("l1");
	Location l2 = new Location ("l2");
	Location l3 = new Location ("l3");
	State s1 = new State()
	    .add(l1,new Int(1))
	    .add(l2,new Int(5))
	    .add(l3,new Int(0));

	Environment env = new Environment()
	    .add(l1).add(l2).add(l3);
	
	Expression e =
	    new Seq(new While(new GTeq(new Deref(l2),new Deref(l1)),
		      new Seq(new Assign(l3, new Plus(new Deref(l1),new Deref(l3))),
			      new Assign(l1,new Plus(new Deref(l1),new Int(1))))
		      
			      ),
		    new Deref(l3))
		    ;
	try{
	    //Type check
	    Type t= e.typeCheck(env);
	    System.out.println("Program has type: " + t);

	    //Evaluate program
	    System.out.println(e + "\n \n");
	    while(!(e instanceof Value) ){
		e = e.smallStep(s1);
		//Display each step of reduction
		System.out.println(e + "\n \n");
	    }
	    //Give some output
	    System.out.println("Program has type: " + t);
	    System.out.println("Result has type: " + e.typeCheck(env));
	    System.out.println("Result: " + e);
	    System.out.println("Terminating State: " + s1); 
	} catch (TypeError te) { 
	    System.out.println("Error:\n" + te);
	    System.out.println("From code:\n" + e);
	} catch (CanNotReduce cnr) {
	    System.out.println("Caught Following exception" + cnr);
	    System.out.println("While trying to execute:\n " + e);
	    System.out.println("In state: \n " + s1);
	}
    }
}

class Location {
    String name;
    Location(String n) {
	this.name = n;
    }
    public String toString() {return name;}
}

class State {
    java.util.HashMap store = new java.util.HashMap(); 

    //Used for setting the initial store for testing not used by 
    //semantics of L1
    State add(Location l, Value v) {
	store.put(l,v);
	return this;
    }

    void update(Location l, Value v) throws CanNotReduce {
	if(store.containsKey(l)) {
	    if(v instanceof Int) {
		store.put(l,v);
	    }
	    else throw new CanNotReduce("Can only store integers");
	}
	else throw new CanNotReduce("Unknown location!");
    }

    Value lookup(Location l) throws CanNotReduce {
	if(store.containsKey(l)) {
	    return (Int)store.get(l);
	}
	else throw new CanNotReduce("Unknown location!");
    }
    public String toString() {
	String ret = "[";
	java.util.Iterator iter = store.entrySet().iterator();
	while(iter.hasNext()) {
	    java.util.Map.Entry e = (java.util.Map.Entry)iter.next();
	    ret += "(" + e.getKey() + " |-> " + e.getValue() + ")";
	    if(iter.hasNext()) ret +=", ";
	}
	return ret + "]";
    }
}

class Environment {
    java.util.HashSet env = new java.util.HashSet();

    //Used to initially setup environment, not used by type checker.
    Environment add(Location l) {
	env.add(l); return this;
    }

    boolean contains(Location l) {
	return env.contains(l);
    }
}
class Type {
    int type;
    Type(int t) {type = t;}
    public static final Type BOOL = new Type(1);
    public static final Type INT = new Type(2);
    public static final Type UNIT = new Type(3);
    public String toString() {
	switch(type) {
	case 1: return "BOOL"; 
	case 2: return "INT";
	case 3: return "UNIT";
	}
	return "???";
    }
}


abstract class Expression {
    abstract Expression smallStep(State state) throws CanNotReduce;
    abstract Type typeCheck(Environment env) throws TypeError;
}

abstract class Value extends Expression {
    final Expression smallStep(State state) throws CanNotReduce{
	throw new CanNotReduce("I'm a value");
    }
}

class CanNotReduce extends Exception{
    CanNotReduce(String reason) {super(reason);}
}

class TypeError extends Exception { TypeError(String reason) {super(reason);}}

class Bool extends Value {
    boolean value;

    Bool(boolean b) {
	value = b;
    }
    
    public String toString() {
	return value ? "TRUE" : "FALSE";
    }

    Type typeCheck(Environment env) throws TypeError {
	return Type.BOOL;
    }
}

class Int extends Value {
    int value;
    Int(int i) {
	value = i;
    }
    public String toString(){return ""+ value;}
    
    Type typeCheck(Environment env) throws TypeError {
	return Type.INT;
    }
}

class Skip extends Value {
    public String toString(){return "SKIP";}
    Type typeCheck(Environment env) throws TypeError {
	return Type.UNIT;
    }
}

class Seq extends Expression {
    Expression exp1,exp2;
    Seq(Expression e1, Expression e2) {
	exp1 = e1;
	exp2 = e2;
    }

    Expression smallStep(State state) throws CanNotReduce {
	if(exp1 instanceof Skip) {
	    return exp2;
	} else {
	    return new Seq(exp1.smallStep(state),exp2);
	}
    }
    public String toString() {return exp1 + "; " + exp2;}

    Type typeCheck(Environment env) throws TypeError {
	if(exp1.typeCheck(env) == Type.UNIT) {
	    return exp2.typeCheck(env);
	}
	else throw new TypeError("Not a unit before ';'.");
    }
}

class GTeq extends Expression {
    Expression exp1, exp2;
    GTeq(Expression e1,Expression e2) {
	exp1 = e1; 
	exp2 = e2;
    }
    
    Expression smallStep(State state) throws CanNotReduce {
	if(!( exp1 instanceof Value)) {
	    return new GTeq(exp1.smallStep(state),exp2);
	} else if (!( exp2 instanceof Value)) {
	    return new GTeq(exp1, exp2.smallStep(state));
	} else {
	    if( exp1 instanceof Int && exp2 instanceof Int ) {
		return new Bool(((Int)exp1).value >= ((Int)exp2).value);
	    }
	    else throw new CanNotReduce("Operands are not both integers.");
	}
    }
    public String toString(){return exp1 + " >= " + exp2;}
    
    Type typeCheck(Environment env) throws TypeError {
	if(exp1.typeCheck(env) == Type.INT && exp2.typeCheck(env) == Type.INT) {
	    return Type.BOOL;
	}
	else throw new TypeError("Arguments not both integers.");
    }
}

class Plus extends Expression {
    Expression exp1, exp2;
    Plus(Expression e1,Expression e2) {
	exp1 = e1; 
	exp2 = e2;
    }
    
    Expression smallStep(State state) throws CanNotReduce {
	if(!( exp1 instanceof Value)) {
	    return new Plus(exp1.smallStep(state),exp2);
	} else if (!( exp2 instanceof Value)) {
	    return new Plus(exp1, exp2.smallStep(state));
	} else {
	    if( exp1 instanceof Int && exp2 instanceof Int ) {
		return new Int(((Int)exp1).value + ((Int)exp2).value);
	    }
	    else throw new CanNotReduce("Operands are not both integers.");
	}
    }
    public String toString(){return exp1 + " + " + exp2;}    

    Type typeCheck(Environment env) throws TypeError {
	if(exp1.typeCheck(env) == Type.INT && exp2.typeCheck(env) == Type.INT) {
	    return Type.INT;
	}
	else throw new TypeError("Arguments not both integers.");
    }
}


class IfThenElse extends Expression {
    Expression exp1,exp2,exp3;

    IfThenElse (Expression e1, Expression e2,Expression e3) {
	exp1 = e1;
	exp2 = e2;
	exp3 = e3;
    }

    Expression smallStep(State state) throws CanNotReduce {
	if(exp1 instanceof Value) {
	    if(exp1 instanceof Bool) {
		if(((Bool)exp1).value) 
		    return exp2;
		else 
		    return exp3;
	    }
	    else throw new CanNotReduce("Not a boolean in test.");
	}
	else {
	    return new IfThenElse(exp1.smallStep(state),exp2,exp3);
	}
    }
    public String toString() {return "IF " + exp1 + " THEN " + exp2 + " ELSE " + exp3;}

    Type typeCheck(Environment env) throws TypeError {
	if(exp1.typeCheck(env) == Type.BOOL) {
	    Type t = exp2.typeCheck(env);
	    if(exp3.typeCheck(env) == t) 
		return t;
	    else throw new TypeError("If branchs not the same type.");
	}
	else throw new TypeError("If test is not bool.");
    }
}

class Assign extends Expression {
    Location l;
    Expression exp1;

    Assign(Location l, Expression exp1) {
	this.l = l;
	this.exp1 = exp1;
    }

    Expression smallStep(State state) throws CanNotReduce{
	if(exp1 instanceof Value) {
	    state.update(l,(Value)exp1);
	    return new Skip();
	}
	else {
	    return new Assign(l,exp1.smallStep(state));
	}
    }
    public String toString() {return l + " = " + exp1;}

    Type typeCheck(Environment env) throws TypeError {
	if(env.contains(l) && exp1.typeCheck(env) == Type.INT) {
	    return Type.UNIT;
	}
	else throw new TypeError("Invalid assignment");
    }
}
    
class Deref extends Expression {
    Location l;
    
    Deref(Location l) {
	this.l = l;
    }

    Expression smallStep(State state) throws CanNotReduce {
	return state.lookup(l);
    } 
    public String toString() {return "!" + l;}

    Type typeCheck(Environment env) throws TypeError {
	if(env.contains(l)) return Type.INT;
	else throw new TypeError("Location not known about!");				
    }
}
    
class While extends Expression {
    Expression exp1,exp2;
	
    While(Expression e1, Expression e2) {
	exp1 = e1;
	exp2 = e2;
    }
    
    Expression smallStep(State state) throws CanNotReduce {
	return new IfThenElse(exp1,new Seq(exp2, this), new Skip());
    }

    public String toString(){return "WHILE " + exp1 + " DO {" + exp2 +"}";}

    Type typeCheck(Environment env) throws TypeError {
	if(exp1.typeCheck(env) == Type.BOOL && exp2.typeCheck(env) == Type.UNIT) 
	    return Type.UNIT;
	else throw new TypeError("Error in while loop");
    }
}
