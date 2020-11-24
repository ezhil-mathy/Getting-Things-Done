from flask import Flask, render_template,request,redirect,url_for, session # For flask implementation
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import os
from flask_dance.contrib.google import make_google_blueprint, google

app = Flask(__name__)
app.secret_key = 'mysecret'
title = "Getting Things Done"
heading = "Getting Things Done"

# app.config["GOOGLE_OAUTH_CLIENT_ID"] = "556847905057-doibroqcnu94pecjcb0qf4esl0qslfio.apps.googleusercontent.com"
app.config["GOOGLE_OAUTH_CLIENT_ID"] = "854375375084-vjlsk9d65kba31ke49rtoh4qinjvq1fb.apps.googleusercontent.com"
# app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "4j5PNyUOxikXB-lf-5xddkaK"
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "TBIPHrr6VuQjguZRO1GphjzI"
google_bp = make_google_blueprint(scope=["profile", "email"])
app.register_blueprint(google_bp, url_prefix="/login")
 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

client = MongoClient("mongodb+srv://Admin:vvmsvvms@cluster0.x76r9.mongodb.net/?retryWrites=true&w=majority")
db = client.to_do_list
# grade_content = db.tasks
todos = db.tasks
# doc = grade_content.find_one({'grade': grade})

# client = MongoClient("mongodb://127.0.0.1:27017") #host uri
# db = client.mymongodb    #Select the database
# todos = db.todo #Select the collection name


@app.route('/')
def index():
	if google.authorized:
		# print(" google ", google)
		resp = google.get("/oauth2/v1/userinfo")
		session['username'] = resp.json()["email"]
		assert resp.ok, resp.text
		# user = users.find_one({'username' : resp.json()["email"]})
		# if not user:
		# 	users.insert_one({'username' : resp.json()["email"], 'password' : "", 'cart' : [], 'address': "", 'mobile': "", 'purchased':[], 'rating':{}})
		return redirect(url_for('viewHomepage'))
	if 'username' in session:
		return redirect(url_for('viewHomepage'))
	# if 'manufacturerName' in session:
	# 	return redirect(url_for('adminIndex'))
	return render_template('index.html')

@app.route("/homepage")
def viewHomepage ():
	if 'username' in session:
		todos_l = todos.find()
		a1="active"
		return render_template('homepage.html',username=session['username'], a1=a1,todos=todos_l,t=title,h=heading)
	return redirect(url_for('index'))

# @app.route("/")
def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('index')

@app.route('/login', methods=['POST'])
def login():
	return redirect(url_for('index'))

@app.route('/logout')
def logout():
	if 'username' in session:
		token = google_bp.token["access_token"]
		resp = google.post(
			"https://accounts.google.com/o/oauth2/revoke",
			params={"token": token},
			headers={"Content-Type": "application/x-www-form-urlencoded"}
		)
		del google_bp.token
		session.pop('username')
	# if 'manufacturerName' in session:
	# 	session.pop('manufacturerName')
	return redirect(url_for('index'))

@app.route("/list")
def lists ():
	#Display the all Tasks
	todos_l = todos.find()
	a1="active"
	return render_template('homepage.html', username=session['username'], a1=a1,todos=todos_l,t=title,h=heading)

# @app.route("/")
@app.route("/uncompleted")
def tasks ():
	#Display the Uncompleted Tasks
	todos_l = todos.find({"done":"no"})
	a2="active"
	return render_template('homepage.html', username=session['username'], a2=a2,todos=todos_l,t=title,h=heading)


@app.route("/completed")
def completed ():
	#Display the Completed Tasks
	todos_l = todos.find({"done":"yes"})
	a3="active"
	return render_template('homepage.html', username=session['username'], a3=a3,todos=todos_l,t=title,h=heading)

@app.route("/done")
def done ():
	#Done-or-not ICON
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	if(task[0]["done"]=="yes"):
		todos.update({"_id":ObjectId(id)}, {"$set": {"done":"no"}})
	else:
		todos.update({"_id":ObjectId(id)}, {"$set": {"done":"yes"}})
	redir=redirect_url()	

	return redirect(redir)

@app.route("/action", methods=['POST'])
def action ():
	#Adding a Task
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	# date = ""
	pr=request.values.get("pr")
	# pr = ""
	# todos.insert({ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"})
	todos.insert({ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"})
	return redirect("/list")

@app.route("/remove")
def remove ():
	#Deleting a Task with various references
	key=request.values.get("_id")
	todos.remove({"_id":ObjectId(key)})
	return redirect("/")

@app.route("/update")
def update ():
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	return render_template('update.html',tasks=task,h=heading,t=title)

@app.route("/action3", methods=['POST'])
def action3 ():
	#Updating a Task with various references
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	id=request.values.get("_id")
	todos.update({"_id":ObjectId(id)}, {'$set':{ "name":name, "desc":desc, "date":date, "pr":pr }})
	return redirect("/")

@app.route("/search", methods=['GET'])
def search():
	#Searching a Task with various references

	key=request.values.get("key")
	refer=request.values.get("refer")
	if(key=="_id"):
		todos_l = todos.find({refer:ObjectId(key)})
	else:
		todos_l = todos.find({refer:key})
	return render_template('searchlist.html',todos=todos_l,t=title,h=heading)

@app.route("/google")
def google_login():
	if not google.authorized:
		return redirect(url_for("google.login"))
	resp = google.get("/oauth2/v1/userinfo")
	session['username'] = resp.json()["email"]
	assert resp.ok, resp.text
	user = users.find_one({'username' : resp.json()["email"]})
	# if not user:
	# 	users.insert_one({'username' : resp.json()["email"], 'password' : "", 'cart' : [], 'address': "", 'mobile': "", 'purchased':[], 'rating':{}})
	return redirect(url_for('homepage'))

if __name__ == "__main__":

    app.run()
