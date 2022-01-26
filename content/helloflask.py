from flask import Flask
from flask import url_for
from werkzeug.utils import redirect
from flask import render_template
from flask import request
from flask import flash
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH']=16*16*1024
@app.route('/')
@app.route('/static', methods=['GET','POST']) 
def upload():
    if request.method == 'POST': 
        #flash("upload Successfully")
        f=request.files['file']
        t=request.values['text']
        basepath=os.path.dirname(__file__)
        upload_path=os.path.join(basepath,'static',secure_filename(f.filename))
        f.save(upload_path)
        return render_template('abc.html',t=t,img_stream='static/'+f.filename)
    return render_template('abc.html',t=None,img_stream=None)
if __name__=='__main__':
    app.debug=True
    app.secret_key="Your key"
    app.run()
