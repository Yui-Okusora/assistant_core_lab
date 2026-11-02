-- A tiny school database for practising SQL. All names are invented.
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS courses;

CREATE TABLE students (
    id        INTEGER PRIMARY KEY,
    name      TEXT    NOT NULL,
    year      INTEGER NOT NULL,           -- 1..4
    program   TEXT    NOT NULL            -- 'CS', 'SE', 'IS', 'AI'
);

CREATE TABLE courses (
    code      TEXT    PRIMARY KEY,        -- e.g. 'CSC10014'
    title     TEXT    NOT NULL,
    credits   INTEGER NOT NULL
);

CREATE TABLE enrollments (
    student_id  INTEGER NOT NULL REFERENCES students(id),
    course_code TEXT    NOT NULL REFERENCES courses(code),
    grade       REAL,                     -- NULL = not graded yet
    PRIMARY KEY (student_id, course_code)
);

INSERT INTO students (id, name, year, program) VALUES
 (1, 'An', 1, 'CS'), (2, 'Binh', 2, 'SE'), (3, 'Chi', 2, 'CS'), (4, 'Dung', 3, 'AI'),
 (5, 'Giang', 1, 'IS'), (6, 'Hoa', 4, 'CS'), (7, 'Khoa', 3, 'SE'), (8, 'Linh', 2, 'AI');

INSERT INTO courses (code, title, credits) VALUES
 ('CSC10001', 'Fundamentals of Programming', 4),
 ('CSC10004', 'Data Structures and Algorithms', 4),
 ('CSC10003', 'Object-Oriented Programming', 4),
 ('CSC10014', 'Computational Thinking', 3),
 ('MTH00003', 'Calculus 1', 3);

INSERT INTO enrollments (student_id, course_code, grade) VALUES
 (1, 'CSC10001', 8.5), (1, 'MTH00003', 6.0),
 (2, 'CSC10001', 7.0), (2, 'CSC10004', 5.5), (2, 'CSC10014', NULL),
 (3, 'CSC10001', 9.0), (3, 'CSC10004', 8.0), (3, 'CSC10003', 7.5),
 (4, 'CSC10004', 4.0), (4, 'CSC10014', 8.0),
 (5, 'MTH00003', 7.5),
 (6, 'CSC10003', 9.5), (6, 'CSC10014', 9.0),
 (7, 'CSC10014', 6.5), (7, 'CSC10004', 3.5),
 (8, 'CSC10001', 8.0), (8, 'CSC10014', NULL);
