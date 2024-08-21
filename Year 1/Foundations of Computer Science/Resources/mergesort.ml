let sol l =
  String.concat ", " (List.map string_of_int l)

let rec merge (ll,rl) =
  Printf.printf "merge: [%s] ++ [%s]\n" (sol ll) (sol rl);
  match (ll,rl) with
  | [], ys -> ys
  | xs, [] -> xs
  | x::xs, y::ys ->
      if x <= y then
        x :: merge (xs, y::ys)
      else
        y :: merge (x::xs, ys)

(*
let _ =
  let r = merge ([1;2;3;4], [3;4;5]) in
  Printf.printf "result: [%s]\n" (sol r)
*)
let rec take i = function
  | [] -> []
  | x::xs ->
      if i > 0 then x :: take (i - 1) xs
      else []

let rec drop i = function
  | [] -> []
  | x::xs ->
      if i > 0 then drop (i-1) xs
      else x::xs

let rec tmergesort = function
  | [] -> []
  | [x] -> [x]
  | xs ->
      let k = List.length xs / 2 in
      let l = tmergesort (take k xs) in
      let r = tmergesort (drop k xs) in
      merge (l, r)

let _ =
(*  let input = [5;7;2;9;3;1;2] in *)
  let input = [7;6;5;4;3;2;1] in
  Printf.printf "---\ninput: [ %s ]\n" (sol input);
  let r = tmergesort input in
  Printf.printf "result: [%s]\n" (sol r)
