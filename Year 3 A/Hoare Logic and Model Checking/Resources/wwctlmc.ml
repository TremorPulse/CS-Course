(* Original code by Jean Pichon-Pharabod. One original version can be found on
   the 2020/2021 Hoare Logic and Model Checking course material website. *)
(* Later changes by Christopher Pulte. *)


(* A naive CTL model checker *)


(* Here temporal model states are just integers. Temporal models are
   polymorphic in the type of atomic propositions. *)
type state = int
module States = Set.Make(Int)



type 'ap tmodel = {
  s : States.t;
  s0 : state -> bool;
  t : state -> state -> bool;
  l : state -> 'ap -> bool;
}


let left_total m = 
  States.for_all (fun s -> States.exists (fun s' -> m.t s s') m.s) m.s


(* CTL formulas are polymorphic in the type of atomic propositions. *)
type 'ap state_prop =
  | True
  | False
  | Not of 'ap state_prop
  | And of 'ap state_prop * 'ap state_prop
  | Or of 'ap state_prop * 'ap state_prop
  | Impl of 'ap state_prop * 'ap state_prop
  | AP of 'ap
  | A of 'ap path_prop
  | E of 'ap path_prop

and 'ap path_prop =
  | X of 'ap state_prop
  | F of 'ap state_prop
  | G of 'ap state_prop
  | U of 'ap state_prop * 'ap state_prop



let rec fixpoint (f : States.t -> States.t) (s : States.t) : States.t =
  let s' = f s in
  if States.equal s s' then s else fixpoint f s'


let rec mca (m : 'ap tmodel) (psi : 'ap state_prop) : States.t = 
  match psi with
  | True -> 
     m.s
  | False -> 
     States.empty
  | AP p -> 
     States.filter (fun s -> m.l s p) m.s
  | Not psi' ->
     let v = mca m psi' in
     States.diff m.s v
  | And (psi1, psi2) -> 
     let v1 = mca m psi1 in
     let v2 = mca m psi2 in
     States.inter v1 v2
  | Or (psi1, psi2) -> 
     let v1 = mca m psi1 in
     let v2 = mca m psi2 in
     States.union v1 v2
  | Impl (psi1, psi2) -> 
     mca m (Or (Not psi1, psi2))
  | A (X psi') ->
     mca m (Not (E (X (Not psi'))))
  | A (G psi') ->
     mca m (Not (E (F (Not psi'))))
  | A (F _) -> 
     failwith "TODO: exercise"
  | A (U (psi1, psi2)) ->
     failwith "TODO: tricky exercise"
  | E (F psi') -> 
     mca m (E (U (True, psi')))
  | E (X psi') ->
     let v = mca m psi' in
     States.filter (fun s ->
         States.exists (fun s' ->
             m.t s s'
           ) v
       ) m.s
  | E (G psi') ->
     let v = mca m psi' in
     fixpoint (fun v' ->
         States.filter (fun s ->
             States.exists (fun s' ->
                 m.t s s'
               ) v'
           ) v'
       ) v
  | E (U (psi1, psi2)) -> 
     let v1 = mca m psi1 in
     let v2 = mca m psi2 in
     fixpoint (fun v' ->
         States.union v'
           (States.filter (fun s ->
                States.exists (fun s' ->
                    m.t s s'
                  ) v'
              ) v1)
       ) v2

let mc (m : 'ap tmodel) (psi : 'ap state_prop) : bool =
  assert (left_total m);
  let v = mca m psi in
  States.for_all (fun s -> 
      not (m.s0 s) || States.mem s v
    ) m.s


(* auxiliary functions for creating temporal models *)
let make_s (number_states : int) : States.t = 
  States.of_list (List.init number_states (fun i -> i))
let make_s0 (initial_states : int list) : (state -> bool) = 
  fun s -> List.mem s initial_states
let make_t (transitions : (int * int) list) : (state -> state -> bool) =
  fun src tgt -> List.mem (src, tgt) transitions
let make_l (labelling: (int * 'ap) list) : (state -> 'ap -> bool) =
  fun s ap -> List.mem (s, ap) labelling 




(* The tea and coffee machine example *)
module TeaCoffee = struct

  type ap = 
    | Idle
    | Coin
    | Tea
    | Coffee

  let good_machine : ap tmodel = {
      s = make_s 4;
      s0 = make_s0 [0];
      t = make_t [(0, 1); (1, 2); (1, 3); (2, 0); (3, 0)];
      l = make_l [(0, Idle); (1, Coin); (2, Tea); (3, Coffee)];
    }

  let bad_machine : ap tmodel = {
      s = make_s 5;
      s0 = make_s0 [0];
      t = make_t [(0, 1); (0, 2); (1, 3); (2, 4); (3, 0); (4, 0)];
      l = make_l [(0, Idle); (1, Coin); (2, Coin); (3, Tea); (4, Coffee)];
    }

  let spec_good_machine : ap state_prop =
    A (G (Impl (AP Coin, E (X (AP Tea)))))


  let () = assert (mc good_machine spec_good_machine)
  let () = assert (not (mc bad_machine spec_good_machine))

end
