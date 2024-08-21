
(***  Generic stacks  ***)

exception E ;

functor Stack( T: sig type t end ) = 
struct
  val new
    = let
        val store = ref( []: T.t list )
      in ref{ 
        push = fn x => 
          store := x :: !store ,
        pop = fn () => 
          case !store of
            nil  => raise E
          | h::t => ( store := t ; h ) 
    }end 
end ;


(***  A boolean stack  ***)

local 
  structure boolStackStruct = Stack(struct type t = bool end)
in 
  val boolStack = boolStackStruct.new
end ;


(***  Two integer stacks  ***)

local
  structure INT = struct type t = int end
  structure intStack0Struct = Stack(INT) 
  structure intStack1Struct = Stack(INT)
in
  val intStack0 = intStack0Struct.new
  val intStack1 = intStack1Struct.new
end ;


(***  Examples of stack manipulation  ***)

fun >> object method = method(!object) ;

>>intStack0#push(0) ;

>>intStack1#push(1) ;

>>intStack1(fn r => fn l => l := r)(intStack0) ;

>>intStack0#pop() ;

>>intStack0#push(4) ;

map ( >>intStack0#push )  [3,2,1] ; 

map ( >>intStack0#pop )  [(),(),(),()] ;

