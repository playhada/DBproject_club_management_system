from flask import Flask, render_template, request, redirect, url_for, flash
import db_manager as db

app = Flask(__name__)
app.secret_key = 'secret'

@app.route('/')
def index():
    return render_template('index.html', 
                           clubs=db.get_all_clubs(), 
                           budget_data=db.get_budget_status())

@app.route('/analysis')
def analysis():
    keyword = request.args.get('keyword', '')
    return render_template('index.html', 
                           clubs=db.get_all_clubs(), 
                           budget_data=db.get_budget_status(),
                           analysis=db.get_analysis(keyword), 
                           keyword=keyword)

@app.route('/init', methods=['POST'])
def init_system():
    msg = db.init_db()
    db.generate_random_data()
    flash(msg, "success")
    return redirect(url_for('index'))

@app.route('/student/add', methods=['POST'])
def add_student():
    success, msg = db.add_student(request.form['s_id'], request.form['name'], request.form['dept'], request.form['phone'])
    flash(msg, "success" if success else "danger")
    return redirect(url_for('index'))

@app.route('/student/delete', methods=['POST'])
def delete_student():
    success, msg = db.delete_student(request.form['s_id'])
    flash(msg, "success" if success else "danger")
    return redirect(url_for('index'))

@app.route('/club/join', methods=['POST'])
def join_club():
    success, msg = db.join_club(request.form['s_id'], request.form['c_id'])
    flash(msg, "success" if success else "danger")
    return redirect(url_for('index'))

@app.route('/club/<int:club_id>')
def club_detail(club_id):
    data = db.get_club_details(club_id)
    return render_template('index.html', 
                           clubs=db.get_all_clubs(), 
                           detail_data=data,
                           budget_data=db.get_budget_status())

@app.route('/test/rollback', methods=['POST'])
def test_rollback():
    msg = db.test_rollback()
    flash(msg, "warning")
    return redirect(url_for('index'))

@app.route('/club/activity/add', methods=['POST'])
def add_activity():
    try:
        success, msg = db.add_club_activity(
            request.form['c_id'], request.form['act_name'], request.form['act_date'],
            request.form['location'], request.form['attendee_cnt'], request.form['amount'], request.form['desc']
        )
        flash(msg, "success" if success else "danger")
    except Exception as e:
        flash(f"입력 오류: {e}", "danger")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)