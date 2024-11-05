CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE player (
  id BIGINT PRIMARY KEY,
  rating INTEGER
);

CREATE TABLE game (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  winner_id BIGINT REFERENCES player
);

CREATE TABLE player_game (
  PRIMARY KEY (player_id, game_id),
  player_id BIGINT REFERENCES player,
  game_id UUID REFERENCES game
);
