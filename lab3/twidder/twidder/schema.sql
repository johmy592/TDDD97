DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS loggedInUsers;
DROP TABLE IF EXISTS messages;

CREATE TABLE users(
	email text not null,
	password text not null,
	firstname text not null,
	familyname text not null,
	gender text not null,
	city text not null,
	country text not null,
	primary key(email)
);

CREATE TABLE loggedInUsers(
	email text not null,
	token text not null,
	FOREIGN KEY (email) REFERENCES users(email)
);

CREATE TABLE messages(
	reciever text not null,
	sender text not null,
	message text,
	FOREIGN KEY (reciever) REFERENCES users(email),
	FOREIGN KEY (sender) REFERENCES users(email)
);