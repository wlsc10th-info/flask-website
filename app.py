import sys
import os
import argparse
import subprocess
from pathlib import Path
from PIL import Image
import shutil

from flask import render_template, redirect, request, url_for, flash, abort, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import null
from content import db,app
from content.models import User
from content.forms import RegistrationForm,LoginForm
from werkzeug.utils import secure_filename
from sqlalchemy.orm.attributes import flag_modified

parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, default=None)
parser.add_argument('--port', type=int, default=None)
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

base_path = os.path.dirname(__file__)

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
            flash("您已成功登入系統！")
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
    flash("您已成功登出系統！")
    return redirect(url_for('home'))

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, password = form.password.data)
        check_user = User.query.filter_by(username = form.username.data).first()

        if check_user is not None:
            flash("此名稱已被使用！")
            return redirect(url_for('register'))

        # add to db table
        os.makedirs(os.path.join(base_path, 'content/static/users/' + user.username))
        db.session.add(user)
        db.session.commit()
        flash("感謝註冊本系統成為會員！")
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

def copy_style(src_path):
    for f in Path('std_img/id_1').iterdir():
        f.unlink()
    shutil.copy(src_path, 'std_img/id_1')

@app.route('/step1',methods=['GET','POST'])
@login_required
def step1():
    if request.method == 'POST': 
        #flash("upload Successfully")
        user = User.query.filter_by(username = current_user.username).first()
        f = request.files['file']
        style_name = request.form.get('style_name')

        for name in user.image["name"]:
            if name == style_name:
                flash('此風格名稱已存在！This style name has already existed!')
                return render_template('welcome_user.html', size=350, img=None, op=None)

        root, extension = os.path.splitext(f.filename)
        print(f.filename, root, extension)
        if extension not in ['.bmp', '.gif', '.png', '.jpg', '.jpeg']:
            flash('不支援的檔案格式！Unsupported file format!')
            return render_template('welcome_user.html', size=350, img=None, op=None)

        f.filename = secure_filename(style_name + extension)
        if not f.filename:
            flash('名稱不合法！Invalid style name!')
            return render_template('welcome_user.html', size=350, img=None, op=None)

        save_path = os.path.join(base_path, 'content/static/users/', user.username, f.filename)
        print(save_path)
        f.save(save_path)
        user.input_images(f.filename, style_name)

        flag_modified(user, "image")
        db.session.commit()

        copy_style(save_path)

        # print("len:",len(user.image['name']))
        return render_template('welcome_user.html', size=350,img = f'../static/users/{user.username}/{f.filename}',
                               op = len(user.image['name']) - 1)

    return render_template('welcome_user.html',size=350,img=None,op=None)

@app.route('/step2', methods=['GET', 'POST'])
@login_required
def step2():
    if request.method == 'POST':
        user = User.query.filter_by(username=current_user.username).first()
        o = request.values['styleSelect']
        d = request.form.getlist('deleteCheckbox')
        i = 0
        if o == None:
            return render_template('welcome_user.html', img=None, op=None)
        for name in user.image["name"]:
            if name == o:
                break
            else:
                i += 1
        # print("num:", o)

        if d == ['delete']:
            os.remove(f'content/static/users/{user.username}/' + user.image["path"][i])
            user.delete_image(user.image["path"][i], user.image["name"][i])
            flag_modified(user, "image")
            db.session.commit()
            return render_template('welcome_user.html', img=None, op=None)

        copy_style(f'content/static/users/{user.username}/' + user.image["path"][i])

        return render_template('welcome_user.html',
                               img=f'../static/users/{user.username}/{user.image["path"][i]}', op=i)

    return render_template('welcome_user.html', size=350, img=None, op=None, next=False)

@app.route('/step3',methods=['GET','POST'])
@login_required
def step3():
    if request.method=='POST':
        user=User.query.filter_by(username=current_user.username).first()
        # font_size=request.values['font-size']
        # letterspacing=request.values['space-size']
        text=request.form.get('text')

        f = open('temp.txt', 'w', encoding='utf8')
        f.write(' ')
        f.write(text)
        f.close()

        cnt = len(text)

        std_img_path = Path('std_img/id_0')
        for f in std_img_path.iterdir():
            f.unlink()

        model_name = 'GAN_20220301-145221'

        subprocess.run([sys.executable, '../DG-Font/font2img.py', '--img_size', '80', '--chara_size', '48',
                        '--ttf_path', 'std_font', '--save_path', 'std_img', '--chara' ,'temp.txt'])

        shutil.rmtree('results', ignore_errors=True)
        shutil.rmtree('final', ignore_errors=True)

        subprocess.run([sys.executable, '../DG-Font/main2.py', '--load_model', model_name, '--output_k', '74',
                        '--attr_size', '2', '--data_path', 'std_img', '--val_batch', '1', '--val_num', '1', '--validation',
                        '--batch_size', '1', '--wlsc_val_cnt', str(cnt)])

        results_path = Path('results') / model_name / '1000'
        final_path = Path('final')
        final_path.mkdir()

        char_in_row = int(request.values['char-in-row'])
        if cnt <= char_in_row:
            save = Image.new('RGB', (80 * cnt, 80), (255, 255, 255))
        else:
            save = Image.new('RGB', (80 * char_in_row, 80 * (((cnt - 1) // char_in_row) + 1)), (255, 255, 255))

        for folder in results_path.iterdir():
            num = int(folder.stem)
            img = Image.open(folder/'0_EMA_1000_0_1.jpg')
            img = img.crop((84, 84, 164, 164))
            img.save(final_path / (str(num) + '.png'))
            save.paste(img, (80 * ((num - 1) % char_in_row), 80 * ((num - 1) // char_in_row)))

        save.save('content/static/save.png')

        return render_template('run_model.html', size=350, img='../static/save.png', op=None)

    return render_template('run_model.html',size=350,img=None,op=None)

@app.route('/tutorial')
def tutorial():
    return render_template('how_to_use.html')

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('static', filename, as_attachment=True)

def init():
    check_dirs = ['/content/static/users/', '/std_img/', '/std_img/id_0', '/std_img/id_1']
    for i in check_dirs:
        path = Path(base_path + i)
        if not path.exists():
            path.mkdir()

if __name__ == '__main__':
    init()
    app.run(host=args.host, port=args.port, debug=args.debug)
