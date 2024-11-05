-- name: get_user :one
SELECT * FROM player
 WHERE id = $1 LIMIT 1;

-- name: get_user_games :many
SELECT g.* FROM game g
                JOIN player_game ug ON g.id = ug.game_id
 WHERE ug.player_id = $1;

-- name: get_user_wins :many
SELECT * FROM game
 WHERE game.winner_id = $1;

-- name: create_player :exec
INSERT INTO player (id) values ($1);

-- name: create_game :one
INSERT INTO game DEFAULT values
            RETURNING *;

-- name: add_game_player :exec
INSERT INTO player_game (player_id, game_id) VALUES (
  $1, $2
);

-- name: update_game_winner :exec
UPDATE game
   SET winner_id = $2
 WHERE id = $1;

-- name: update_player_rating :exec
UPDATE player
   SET rating = $2
 WHERE id = $1;
