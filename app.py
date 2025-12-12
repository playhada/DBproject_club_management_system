# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import db_manager as db

app = Flask(__name__)
app.secret_key = 'secret'

@app.route('/')
def index():
    return render_template('index.html', 
                           clubs=db.get_all_clubs(), 
                           budget_data=db.get_budget_status())

@app.route('/init', methods=['POST'])
def init_system():
    msg = db.init_db()
    db.generate_random_data()
    flash(msg, "success")
    return redirect(url_for('index'))

@app.route('/club/<int:club_id>')
def club_detail(club_id):
    data = db.get_club_details(club_id)
    return render_template('index.html', 
                           clubs=db.get_all_clubs(), 
                           detail_data=data)

@app.route('/club/<int:club_id>/members')
def view_members(club_id):
    members = db.get_club_members(club_id)
    clubs = db.get_all_clubs()
    selected_club_name = next((c['club_name'] for c in clubs if c['club_id'] == club_id), "동아리")
    
    return render_template('index.html', clubs=clubs, members=members, selected_club_name=selected_club_name)

@app.route('/student/add', methods=['POST'])
def add_student():
    s_id = request.form['s_id']
    name = request.form['name']
    dept = request.form['dept']
    phone = request.form['phone'] 
    success, msg = db.add_student(s_id, name, dept, phone)
    
    flash(msg, "success" if success else "danger")
    return redirect(url_for('index'))

@app.route('/club/join', methods=['POST'])
def join_club():
    s_id = request.form['s_id']
    c_id = request.form['c_id']
    
    success, msg = db.join_club(s_id, c_id)
    
    flash(msg, "info" if success else "danger")
    return redirect(url_for('index'))

@app.route('/test/rollback', methods=['POST'])
def test_rollback():
    msg = db.test_rollback()
    flash(msg, "warning")
    return redirect(url_for('index'))

@app.route('/analysis')
def analysis():
    keyword = request.args.get('keyword', '')
   
    return render_template('index.html', 
                           clubs=db.get_all_clubs(), 
                           budget_data=db.get_budget_status(),
                           analysis=db.get_analysis(keyword), 
                           keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True)