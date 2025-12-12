import sqlite3
import pandas as pd
import os
import random
import config as cfg

def get_conn():
    return sqlite3.connect(cfg.DB_PATH)

def init_db():
    if os.path.exists(cfg.DB_PATH):
        os.remove(cfg.DB_PATH)
    conn = get_conn()
    cursor = conn.cursor()
    with open('schema.sql', 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()
    return "시스템 초기화 및 테이블 생성 완료"

def generate_random_data():
    conn = get_conn()
    cursor = conn.cursor()
    
    for cat in ['식비', '운영비', '장소대관료', '물품구매비', '강사비', '홍보비']:
        cursor.execute("INSERT INTO Category (category_name) VALUES (?)", (cat,))
    
    student_ids = []
    for i in range(200):
        while True:
            s_id = f"202{random.choice([1,2,3,4])}{str(random.randint(1,99999)).zfill(5)}"
            if s_id not in student_ids:
                student_ids.append(s_id)
                break
        name = random.choice(cfg.NAMES_LAST) + random.choice(cfg.NAMES_FIRST)
        dept = random.choice(cfg.DEPARTMENTS)
        cursor.execute("INSERT INTO Student VALUES (?, ?, ?, ?, ?)", 
                       (s_id, name, dept, f"user{i}@univ.ac.kr", "010-0000-0000"))
    
    club_ids = []
    for name, desc in cfg.CLUB_NAMES:
        president = random.choice(student_ids)
        cursor.execute("INSERT INTO Club (club_name, president_id, description) VALUES (?, ?, ?)", 
                       (name, president, desc))
        club_ids.append(cursor.lastrowid)

    for s_id in student_ids:
        join_count = random.randint(1, 3)
        targets = random.sample(club_ids, join_count)
        for c_id in targets:
            cursor.execute("INSERT OR IGNORE INTO Membership (student_id, club_id, role, join_date) VALUES (?, ?, ?, ?)",
                           (s_id, c_id, '회원', '2024-03-01'))

    for c_id in club_ids:
        cursor.execute("INSERT INTO Budget (club_id, semester, total_amount) VALUES (?, ?, ?)", 
                       (c_id, '2024-1', random.randint(50, 300) * 10000))
        budget_id = cursor.lastrowid

        cursor.execute("SELECT student_id FROM Membership WHERE club_id = ?", (c_id,))
        members = [row[0] for row in cursor.fetchall()]

        for _ in range(random.randint(5, 10)):
            act_name = random.choice(cfg.ACTIVITY_TYPES)
            act_date = f"2024-0{random.randint(3,6)}-{random.randint(10,28)}"
            cursor.execute("INSERT INTO Activity (club_id, activity_name, activity_date, location, description) VALUES (?, ?, ?, ?, ?)",
                           (c_id, act_name, act_date, random.choice(cfg.LOCATIONS), '설명'))
            act_id = cursor.lastrowid
            
            
            if members:
                attendees = random.sample(members, k=int(len(members) * random.uniform(0.5, 0.8)))
                for att_s in attendees:
                    cursor.execute("INSERT INTO Attendance VALUES (?, ?)", (att_s, act_id))
            
           
            if random.random() > 0.3:
                amount = random.randint(1, 10) * 10000
                cursor.execute("INSERT INTO Expense (budget_id, activity_id, category_id, amount, description, expense_date) VALUES (?, ?, ?, ?, ?, ?)",
                               (budget_id, act_id, 1, amount, "활동비", act_date))

    conn.commit()
    conn.close()
    return "대규모 데이터 생성 완료 (학생, 동아리, 활동, 예산 데이터 적재됨)"

def get_all_clubs():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM Club", conn)
    conn.close()
    return df.to_dict('records')

def add_student(s_id, name, dept, phone):
    try:
        conn = get_conn()
        email = f"{s_id}@univ.ac.kr"
        conn.execute("INSERT INTO Student VALUES (?, ?, ?, ?, ?)", (s_id, name, dept, "email", "000"))
        conn.commit()
        conn.close()
        return True, f"{name} 등록 성공!"
    except Exception as e:
        return False, f"오류: {e}"

def delete_student(s_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Student WHERE student_id = ?", (s_id,))
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return (True, "삭제 완료") if cnt > 0 else (False, "학생 없음")

def join_club(s_id, c_id):
    try:
        conn = get_conn()
        conn.execute("INSERT INTO Membership (student_id, club_id, role, join_date) VALUES (?, ?, ?, ?)",
                     (s_id, c_id, '회원', '2024-11-16'))
        conn.commit()
        conn.close()
        return True, "가입 완료!"
    except:
        return False, "이미 가입됨/오류"

def get_analysis(keyword):
    conn = get_conn()
    
    base_query = """
    SELECT 
        c.club_name, 
        a.activity_name, 
        a.activity_date,
        (SELECT COUNT(*) FROM Attendance WHERE activity_id = a.activity_id) as attendees,
        (SELECT IFNULL(SUM(amount), 0) FROM Expense WHERE activity_id = a.activity_id) as total_expense
    FROM Activity a
    JOIN Club c ON a.club_id = c.club_id
    """

    if not keyword:
        query = base_query + " ORDER BY a.activity_date DESC LIMIT 50"
        params = ()
    else:
        query = base_query + " WHERE c.club_name LIKE ? ORDER BY a.activity_date DESC"
        params = (f'%{keyword}%',)

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df.to_dict('records')
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df.to_dict('records')

def get_club_members(club_id):
    """특정 동아리의 소속 멤버 명단 조회"""
    conn = get_conn()
    
    sql = """
    SELECT s.student_id, s.name, s.department, m.role, s.phone
    FROM Membership m
    JOIN Student s ON m.student_id = s.student_id
    WHERE m.club_id = ?
    ORDER BY CASE WHEN m.role = '회장' THEN 1 ELSE 2 END, s.name
    """
    df = pd.read_sql(sql, conn, params=(club_id,))
    conn.close()
    return df.to_dict('records')

def get_club_details(club_id):
    """특정 동아리의 상세 정보(회장)와 멤버 리스트 반환"""
    conn = get_conn()
    cursor = conn.cursor()

    sql_info = """
    SELECT c.club_name, c.description, s.name, s.department, s.phone
    FROM Club c
    JOIN Student s ON c.president_id = s.student_id
    WHERE c.club_id = ?
    """
    cursor.execute(sql_info, (club_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None

    club_info = {
        'club_name': row[0],
        'description': row[1],
        'president_name': row[2],
        'president_dept': row[3],
        'president_phone': row[4]
    }

    sql_members = """
    SELECT m.role, s.name, s.student_id, s.department, s.phone
    FROM Membership m
    JOIN Student s ON m.student_id = s.student_id
    WHERE m.club_id = ?
    ORDER BY CASE WHEN m.role = '회장' THEN 1 ELSE 2 END, s.name
    """
    df = pd.read_sql(sql_members, conn, params=(club_id,))
    members = df.to_dict('records')
    
    conn.close()
    return {'info': club_info, 'members': members}

def get_budget_status():
    """동아리별 예산 배정액, 사용액, 잔액, 집행률 조회"""
    conn = get_conn()
    sql = """
    SELECT 
        c.club_name,
        b.total_amount,
        IFNULL(SUM(e.amount), 0) as used_amount,
        (b.total_amount - IFNULL(SUM(e.amount), 0)) as balance,
        ROUND((CAST(IFNULL(SUM(e.amount), 0) AS FLOAT) / b.total_amount) * 100, 1) as rate
    FROM Budget b
    JOIN Club c ON b.club_id = c.club_id
    LEFT JOIN Expense e ON b.budget_id = e.budget_id
    GROUP BY b.budget_id
    ORDER BY used_amount DESC
    """
    df = pd.read_sql(sql, conn)
    conn.close()
    return df.to_dict('records')

def test_rollback():
    conn = get_conn()
    cursor = conn.cursor()
    log = []
    try:
        cursor.execute("SELECT total_amount FROM Budget WHERE club_id=1")
        res = cursor.fetchone()
        budget = res[0] if res else 0
        
        conn.execute("BEGIN TRANSACTION")
        cursor.execute("INSERT INTO Expense (budget_id, category_id, amount, description, expense_date) VALUES (1, 1, ?, '횡령', '2024-12-31')", (budget + 100000000,))
        
        if (budget - (budget + 100000000)) < 0:
            raise ValueError("[경고] 예산 초과, 승인 거부.")
        conn.commit()
    except ValueError as e:
        conn.rollback()
        return str(e) + " -> 트랜잭션 ROLLBACK 성공!"
    except Exception as e:
        return f"오류: {e}"
    conn.close()
    return "테스트 완료"


def add_club_activity(club_id, name, date, location, attendee_count, amount, desc):
    """동아리 활동 등록 + 출석 인원 랜덤 배정 + 지출 내역 기록 (트랜잭션)"""
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO Activity (club_id, activity_name, activity_date, location, description) VALUES (?, ?, ?, ?, ?)",
                       (club_id, name, date, location, '운영진 등록'))
        act_id = cursor.lastrowid
        
        cursor.execute("SELECT student_id FROM Membership WHERE club_id = ?", (club_id,))
        members = [row[0] for row in cursor.fetchall()]
        
        if len(members) < int(attendee_count):
            raise ValueError(f"멤버 수({len(members)}명)보다 참석자 수({attendee_count}명)가 많을 수 없습니다.")
            
        if members and int(attendee_count) > 0:
            attendees = random.sample(members, int(attendee_count))
            for s_id in attendees:
                cursor.execute("INSERT INTO Attendance (student_id, activity_id) VALUES (?, ?)", (s_id, act_id))

        if int(amount) > 0:
            cursor.execute("SELECT budget_id, total_amount FROM Budget WHERE club_id = ? ORDER BY budget_id DESC LIMIT 1", (club_id,))
            res = cursor.fetchone()
            if not res:
                raise ValueError("배정된 예산이 없습니다.")
            
            budget_id, total_budget = res
            
            cursor.execute("SELECT IFNULL(SUM(amount), 0) FROM Expense WHERE budget_id = ?", (budget_id,))
            used_amount = cursor.fetchone()[0]
            
            if (total_budget - used_amount - int(amount)) < 0:
                raise ValueError(f"예산 초과, 잔액이 부족합니다. (신청: {amount}원)")
              
            cursor.execute("INSERT INTO Expense (budget_id, activity_id, category_id, amount, description, expense_date) VALUES (?, ?, 1, ?, ?, ?)",
                           (budget_id, act_id, int(amount), desc, date))

        conn.commit()
        return True, "활동 및 지출 등록 성공"
        
    except Exception as e:
        conn.rollback()
        return False, f"등록 실패: {e}"
    finally:
        conn.close()