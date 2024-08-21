let sol l =
  String.concat ", " (List.map string_of_int l)

let rec quick al =
    Printf.printf "quick: [%s]\n" (sol al);
    match al with
    | [] -> []
    | [x] -> [x]
    | a::bs ->
        Printf.printf "partition: [%s] on %d\n" (sol bs) a;
        let rec part =
          function
          | (l, r, []) ->
              Printf.printf "combine: [%s] ++ [%s]\n" (sol l) (sol r);
              (quick l) @ (a :: quick r)
          | (l, r, x::xs) ->
              Printf.printf "divide: [%s] [%s] on %d\n" (sol l) (sol r) x;
              if (x <= a) then
                part (x::l, r, xs)
              else
                part (l, x::r, xs)
        in
        part ([], [], bs)

let _ =
(*  let r = quick [4;3;7;1;9;8] in *)
  let r = quick [7;6;5;4;3;2;1] in
  Printf.printf "result: [%s]\n" (sol r)
