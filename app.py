from flask import Flask, render_template,request,flash,redirect,url_for,session
import sqlite3
from tensorflow import keras
from keras.preprocessing import image
import numpy as np
import os, secrets


model = keras.models.load_model('my_model.h5')

app = Flask(__name__)
app.secret_key=secrets.token_hex(16)

dic = {0: 'daisy', 1: 'dandelion', 2: 'roses', 3: 'sunflowers', 4: 'tulips'}

con=sqlite3.connect("database.db")
con.execute("create table if not exists customer(pid integer primary key,name text,password test,mail text)")
con.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from customer where name=? and password=?",(name,password))
        data=cur.fetchone()

        if data:
            session["name"]=data["name"]
            session["password"]=data["password"]
            return redirect("main")
        else:
            flash("Username and Password Mismatch","danger")
    return redirect(url_for("index"))

@app.route('/main',methods=["GET","POST"])
def customer():
    return render_template("main.html")

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            name=request.form['name']
            password=request.form['password']
            mail=request.form['mail']
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            cur.execute("insert into customer(name,password,mail)values(?,?,?)",(name,password,mail))
            con.commit()
            flash("Record Added  Successfully","success")
        except:
            flash("Error in Insert Operation","danger")
        finally:
            return redirect(url_for("index"))
            con.close()

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

img_size = (180, 180)

@app.route('/classify', methods=['POST'])
def classify():
    if 'image' not in request.files:
        return "No file part"

    file = request.files['image']

    if file.filename == '':
        return "No selected file"

    if file:
        # Save the uploaded image temporarily
        file_path = 'static/uploads/' + file.filename
        file.save(file_path)

        img = image.load_img(file_path, target_size=img_size)
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        
        # Make predictions
        predictions = model.predict(img)
        predicted_class = dic[np.argmax(predictions)] 

        return render_template('main.html', image_path=file_path, prediction=f'Predicted flower: {predicted_class}')

    return render_template('main.html', image_path=None, prediction='No image uploaded')

if __name__ == '__main__':
    # Create the upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
