DROP TABLE IF EXISTS Rectangle;
DROP TABLE IF EXISTS Room;
DROP TABLE IF EXISTS Robot;
DROP TABLE IF EXISTS Scenario;


CREATE TABLE Rectangle (
	RectID INTEGER PRIMARY KEY,
	X REAL,
	Y REAL,
	Width REAL,
	Height REAL,
	Angle REAL,
	RoomID INTEGER,
	FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
);

CREATE TABLE Room (
	RoomID INTEGER PRIMARY KEY,
	Name VARCHAR(15) UNIQUE,
	Width REAL,
	Height REAL,
	DateUsed DATETIME
);

CREATE TABLE Robot (
	RobotID INTEGER PRIMARY KEY,
	Name VARCHAR(15) UNIQUE,
	NumberOfReadings INTEGER,
	DistanceSensorFuzziness REAL,
	AngleSensorFuzziness REAL,
	DistanceMovedFuzziness REAL,
	AngleRotatedFuzziness REAL,
	DateUsed DATETIME
);

CREATE TABLE Scenario (
	ScenarioID INTEGER PRIMARY KEY,
	Name VARCHAR(15) UNIQUE,
	RoomID INTEGER,
	RobotID INTEGER,
	SquareSize INTEGER,
	CartographerGrid TEXT,
	RobotPosX REAL,
	RobotPosY REAL,
	RobotAngle REAL,
	DateUsed DATETIME,
	FOREIGN KEY (RoomID) REFERENCES Room(RoomID),
	FOREIGN KEY (RobotID) REFERENCES Robot(RobotID)
);