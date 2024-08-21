let sol l =
  String.concat ", " (List.map string_of_int l)

let print_args (x, ll) ret =
  Printf.printf "insert %d => [ %s ] => [ %s ] \n"
    x (sol ll) (sol ret);
  ret

let rec ins al =
  match al with
  | x, [] ->
      Printf.printf "base case: [%d]\n%!" x;
      [x]
  | x, y::ys ->
      if x <= y then
        print_args al (x :: y :: ys)
      else
        print_args al (y :: ins (x, ys))

(*
let _ =
  ins (5, [1;2;3;6;7;8])
*)

let rec insort = function
    | [] -> []
    | x::xs -> ins (x, insort xs)

let _ = 
  Printf.printf "---\n";
(*
  let sl = insort [6;5;4;3;2;1] in
  Printf.printf "[%s]\n---\n" (String.concat ", " (List.map string_of_int sl));
*)
  let sl = insort [1;2;3;4;5;6] in
  Printf.printf "[%s]\n" (String.concat ", " (List.map string_of_int sl))
