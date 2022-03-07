from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import null
from content import db,app
from content.models import User
from content.forms import RegistrationForm,LoginForm
from werkzeug.utils import secure_filename
from sqlalchemy.orm.attributes import flag_modified
import os
db.create_all()
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash("您已經成功的登入系統")
            next = request.args.get('next')
            if next == None or not next[0]=='/':
                next = url_for('step1')
            return redirect(next)
        flash("使用者或密碼錯誤")    
    return render_template('login.html',form=form)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("您已經登出系統")
    return redirect(url_for('home'))
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
        username=form.username.data, password=form.password.data)
        check_user = User.query.filter_by(username=form.username.data).first()
        if check_user is not None:
            flash("此名稱已被使用")
            return redirect(url_for('register'))
        # add to db table
        os.makedirs('C:\\Users\\ivanw\\OneDrive\\桌面\\flaskWebsite\\content\\static/'+user.username)
        db.session.add(user)
        db.session.commit()
        flash("感謝註冊本系統成為會員")
        return redirect(url_for('login'))
    return render_template('register.html',form=form)
@app.route('/step1',methods=['GET','POST'])
@login_required
def step1():
    if request.method == 'POST': 
        #flash("upload Successfully")
        user=User.query.filter_by(username=current_user.username).first()
        f=request.files['file']
        style_name=request.form.get('style_name')
        for name in user.image["name"]:
            if name==style_name:
                flash('this style name has existed')
                return render_template('welcome_user.html',size=350,img=None,op=None)

        basepath=os.path.dirname(__file__)
        root, extension = os.path.splitext(f.filename)
        f.filename=style_name+extension
        upload_path=os.path.join(basepath,'content/static/'+user.username,secure_filename(f.filename))
        f.save(upload_path)
        user.input_images('../static/'+user.username+'/'+f.filename,style_name)
        flag_modified(user,"image")
        db.session.commit()
        print("len:",len(user.image['name']))
        return render_template('welcome_user.html',size=350,img='../static/'+user.username+'/'+f.filename,op=len(user.image['name'])-1)
    return render_template('welcome_user.html',size=350,img=None,op=None)
@app.route('/step2',methods=['GET','POST'])
@login_required
def step2():
    if request.method=='POST':
        user=User.query.filter_by(username=current_user.username).first()
        o=request.values['optradio']
        d=request.form.getlist('a')
        i=0
        if o==None:
            return render_template('welcome_user.html',img=None,op=None)
        for name in user.image["name"]:
            if name==o:
                break
            else:
                i=i+1
        print("num:",o)
        if d==['delete']:
            os.remove('content/static/'+user.image["path"][i])
            user.delete_image(user.image["path"][i],user.image["name"][i])
            flag_modified(user,"image")
            db.session.commit()
            return render_template('welcome_user.html',img=None,op=None)
        return render_template('welcome_user.html',img=user.image["path"][i],op=i)
    return render_template('welcome_user.html',size=350,img=None,op=None)
@app.route('/step3',methods=['GET','POST'])
@login_required
def step3():
    if request.method=='POST':
        user=User.query.filter_by(username=current_user.username).first()
        font_size=request.values['font-size']
        letterspacing=request.values['space-size']
        text=request.form.get('text')
    return render_template('run-model.html',size=350,img=None,op=None)
@app.route('/tutorial')
def tutorial():
    return render_template('how_to_use.html')
if __name__ == '__main__':
    app.run(debug=True)