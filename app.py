from bson import ObjectId
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from os.path import join, dirname
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
app = Flask(__name__)

@app.route('/',methods=['GET'])
def home():
   fruit = list(db.fruits.find({}))
   return render_template('dashboard.html',fruitse=fruit)


@app.route('/fruits',methods=['GET'])
def fruitsPage():
   fruit = list(db.fruits.find({}))
   return render_template('index.html',fruitse=fruit)


@app.route('/add',methods=['GET','POST'])
def addPage():
   if request.method == 'POST':
      name = request.form["name"]
      price = request.form["price"]
      images  = request.files["gambar"]
      desc = request.form["description"]
      
      today = datetime.now()
      mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
      if images:
         extension = images.filename.split('.')[-1]    
         filename = f'FGD - 2/static/assets/imgFruit/img-{mytime}.{extension}'
         images.save(filename)
      else:
         images = None
      
      doc = {
      'name': name.strip(),
      'price':price,
      'image':filename.split("2/")[1],
      'desc': desc.strip(),
      }
      db.fruits.insert_one(doc)
      return redirect(url_for('home'))   
   return render_template('AddFruit.html')


@app.route('/edit/<_id>',methods=['GET','POST'])
def editPage(_id):
   fruit = db.fruits.find_one({'_id':ObjectId(_id)})
   print(fruit['_id'])
   
   if request.method == "POST":
         name = request.form["name"]
         price = request.form["price"]
         image  = request.files["gambar"]
         desc = request.form["description"]
         doc = {'name': name.strip(), 'price': price, 'desc': desc.strip()}
         today = datetime.now()
         mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
         if image:
            extension = image.filename.split('.')[-1]    
            filename = f'FGD - 2/static/assets/imgFruit/img-{mytime}.{extension}'
            image.save(filename)
            doc['image'] = filename.split("2/")[1]
         else:
            image = fruit['image']
         # print(fruit['_id'])
         db.fruits.update_one({'_id':ObjectId(fruit['_id'])},{'$set': doc})
         return redirect(url_for('fruitsPage'))
   return render_template('EditFruit.html',fruits=fruit)

@app.route('/search',methods=['GET'])
def search():
   # query = request.form['query']
   # print(query)
   queries = request.args['query']
   fruit = db.fruits.find({'name': re.compile(queries, re.IGNORECASE)})
   print(queries)
   return render_template('searchResult.html',fruit=fruit)
   
@app.route('/delete/<_id>',methods=['GET','POST'])
def delete(_id):
   db.fruits.delete_one({'_id': ObjectId(_id)})
   return redirect(url_for("fruitsPage"))
if    __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)