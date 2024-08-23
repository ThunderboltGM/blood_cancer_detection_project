from flask import Flask,render_template,request,url_for
from tensorflow.keras.models import load_model # type:ignore
import sqlite3,os,cv2
import numpy as np
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=API_KEY)

model = load_model('./models/blood_cancer_model.h5')

app = Flask(__name__)

upload_folder = 'upload_folder/'
app.config['upload_folder'] = upload_folder
os.makedirs('./upload_folder',exist_ok=True)

def get_gemini_response(input_message):
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    response = gemini_model.generate_content(input_message)
    return response.text

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/contactForm',methods=['POST','GET'])
def contactForm():
    if request.method == 'POST':
        conn = sqlite3.connect('userData.db')
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        userDetails = (name,email,message)
        insertionQuerry = """
        insert into userQuerry values(?,?,?)
        """
        cur = conn.cursor()
        cur.execute(insertionQuerry,userDetails)
        conn.commit()
        print('user data inserted into database successfully')
        cur.close()
        conn.close()
        return render_template('home.html')
    
@app.route('/project')
def project():
    return render_template('project.html')
    
@app.route('/imageUpload',methods=['POST','GET'])
def imageUpload():
    if request.method == 'POST':
        image = request.files['image']

        if image.filename == '':
            return "NO SELECTED FILE"
        
        if image:
            filename = secure_filename(image.filename)
            file_path = os.path.join(app.config['upload_folder'],filename)
            image.save(file_path)
            final_image = []
            imageArray = cv2.imread(file_path)
            imageArray_resized = cv2.resize(imageArray,(224,224))
            final_image.append(imageArray_resized)
            final_image = np.array(final_image)
            final_image = final_image/255
            prediction = model.predict(final_image)
            pred = np.argmax(prediction)
            labelDict = {
                0:'BENIGN',
                1:'EARLY PRE-B',
                2:'PRE-B',
                3:'PRO-B'
            }
            if pred == 0:
                message = """write about "BENIGN" stage of blood cancer"""
            elif pred == 1:
                message = """write about "Early Pre-B" stage of blood cancer"""
            elif pred == 2:
                message = """write about "Pre-B" stage of blood cancer"""
            elif pred == 3:
                message = """write about "Pro-B" stage of blood cancer"""
            gemini_output1 = get_gemini_response(message)
            return render_template('result.html',output=str(labelDict[pred]),gemini_output1=str(gemini_output1))

if __name__ == '__main__':
    app.run(debug=True)