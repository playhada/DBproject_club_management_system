-- schema.sql
-- 1. 기초 정보 테이블
CREATE TABLE IF NOT EXISTS Student (
    student_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    department VARCHAR(50),
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS Club (
    club_id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_name VARCHAR(100) NOT NULL,
    president_id VARCHAR(10),
    description TEXT,
    FOREIGN KEY (president_id) REFERENCES Student(student_id)
);

CREATE TABLE IF NOT EXISTS Category (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(50) NOT NULL
);

-- 2. 주요 활동 및 예산 테이블
CREATE TABLE IF NOT EXISTS Budget (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER NOT NULL,
    semester VARCHAR(20) NOT NULL,
    total_amount INTEGER NOT NULL,
    FOREIGN KEY (club_id) REFERENCES Club(club_id)
);

CREATE TABLE IF NOT EXISTS Activity (
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER NOT NULL,
    activity_name VARCHAR(100) NOT NULL,
    activity_date DATE NOT NULL,
    location VARCHAR(100) NOT NULL,
    description TEXT,
    FOREIGN KEY (club_id) REFERENCES Club(club_id)
);

-- 3. 상세 내역 및 관계 테이블
CREATE TABLE IF NOT EXISTS Expense (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER NOT NULL,
    activity_id INTEGER,
    category_id INTEGER,
    amount INTEGER NOT NULL,
    description VARCHAR(200),
    expense_date DATE NOT NULL,
    FOREIGN KEY (budget_id) REFERENCES Budget(budget_id),
    FOREIGN KEY (activity_id) REFERENCES Activity(activity_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);

CREATE TABLE IF NOT EXISTS Membership (
    student_id VARCHAR(10),
    club_id INTEGER,
    role VARCHAR(20),
    join_date DATE,
    PRIMARY KEY (student_id, club_id),
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (club_id) REFERENCES Club(club_id)
);

CREATE TABLE IF NOT EXISTS Attendance (
    student_id VARCHAR(10),
    activity_id INTEGER,
    PRIMARY KEY (student_id, activity_id),
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (activity_id) REFERENCES Activity(activity_id)
);