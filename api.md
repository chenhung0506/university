curl -XPOST localhost:8336/vote/getUniversity

curl -XPOST localhost:8336/vote/editUniversity --header 'Content-Type: application/json' --data-raw '{
  "u_name": "test2",
  "kind": "colleage",
  "descri": "2021-02-19 19:27:35",
  "pdf1_path": 10000000,
  "pdf2_path": 1,
  "reward": 10000000,
  "medal": 1
}'

curl -XPOST localhost:8336/vote/delUniversity --header 'Content-Type: application/json' --data-raw '{
  "u_name": "outbound2",
  "kind": "colleage",
  "descri": "2021-02-19 19:27:35",
  "pdf1_path": 10000000,
  "pdf2_path": 1,
  "reward": 10000000,
  "medal": 1
}'

curl -XPOST localhost:8336/vote/jwt