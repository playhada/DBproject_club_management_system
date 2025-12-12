# main.py 수정
import db_manager as db

def show_menu():
    print("\n" + "="*40)
    print("교내 단체 관리 시스템 (Final Ver)")
    print("="*40)
    print("1. DB 초기화 및 대규모 데이터 생성")
    print("2. 학생 등록")
    print("3. 학생 삭제")
    print("4. 동아리 가입 (M:N 시연)")
    print("5. 활동 분석 조회")
    print("6. [무결성 테스트] 예산 롤백")
    print("7. [상세 조회] 동아리 회장 및 멤버 찾기")
    print("8. [전체 조회] 전체 동아리 리스트")  # <--- NEW!
    print("0. 종료")
    print("="*40)

if __name__ == "__main__":
    while True:
        show_menu()
        c = input("선택 >> ")
        
        if c == '1':
            db.init_db()
            db.generate_random_data()
        # ... (2~7번 기존 코드 그대로 유지) ...
        
        elif c == '7':
            keyword = input("검색할 동아리 이름(예: 코딩, 댄스): ")
            db.query_club_detail(keyword)

        elif c == '8':  # <--- NEW! 여기가 추가되었습니다
            db.show_all_clubs()
            
        elif c == '0':
            print("종료합니다.")
            break
        else:
            print("잘못된 입력입니다.")