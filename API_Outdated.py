import os
import urllib.request
import sqlite3
import random
import random
import time
import string
import multiprocessing
import ImageCompatibility

from datetime import datetime
from sqlite3 import Error
from sqlalchemy import true
from app import app
from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
from flask_selfdoc import Autodoc
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'C:/uploads' # Main File folder

DB_URL = 'C:\sqllite\isepDB.db'

MIN_PORT_NUMBER = 10000

app = Flask(__name__)
CORS(app)
auto = Autodoc(app)





app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Configure file main folder
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 #100 MB

ALLOWED_EXTENSIONS = set(['txt', "yaml", "json", "xml","tar","py"])

# Verify allowed files
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/auth', methods=['POST'])
def get_auth():
	try:
		conn = create_connection(DB_URL)

	except:
		resp = jsonify({'message' : "Couldn't access database"})
		resp.status_code = 501
		return resp

	if 'key' not in request.form:
		resp = jsonify({'message' : 'No auth key provided'})
		resp.status_code = 401
		return resp
	if len(get_statement(conn,"select * from apikey where api_key = ?",request.form.to_dict()["key"])) <= 0:
		resp = jsonify({'message' : 'Unauthorized access'})
		resp.status_code = 401
		return resp


	letters = string.ascii_lowercase 
	numbers = string.digits

	key = ''.join(random.choice(letters) for i in range(7))
	key = key.join(random.choice(numbers) for i in range(5))


	insert_auth(conn,key)
	conn.close()
	return key


@app.route('/limits', methods=['GET'])
def get_limits():
	try:
		conn = create_connection(DB_URL)

	except:
		resp = jsonify({'message' : "Couldn't access database"})
		resp.status_code = 501
		return resp

	if 'auth' not in request.args:
		resp = jsonify({'message' : 'No auth provided'})
		resp.status_code = 401
		return resp
	
	if 'id' not in request.args:
		resp = jsonify({'message' : 'No id provided'})
		resp.status_code = 401
		return resp

	try:
		folder_name = request.args.to_dict()["id"]
		

		folder_id = get_statement(conn,"select * from folderid where folder_id = ?",folder_name)
		auth_key = request.args.to_dict()["auth"]
		auth_key = get_statement(conn,"select auth_key from auth where auth_key = ?",auth_key)[0][0]

		if len(auth_key)<10:
			resp = jsonify({'message' : 'Wrong auth key'})
			resp.status_code = 401
			return resp
		

		
		
		#delete_auth(conn,auth_key)
		mini_arr = folder_id[0]
		message = f'CPU {mini_arr[1]} : GPU {mini_arr[2]} : MEM {mini_arr[3]}'
		resp = jsonify({'message' : message})
		resp.status_code = 200
		
	except Exception as e:
		resp = jsonify({'message' : 'Folder id not found or Wrong key'})
		resp.status_code = 401
	conn.close()
	return resp
	

@app.route('/update-limits', methods=['POST'])
def update_limits():
	try:
		conn = create_connection(DB_URL)

	except:
		resp = jsonify({'message' : "Couldn't access database"})
		resp.status_code = 501
		return resp

	if 'key' not in request.form:
		resp = jsonify({'message' : 'No auth key provided'})
		resp.status_code = 401
		return resp
	if len(get_statement(conn,"select * from apikey where api_key = ? and admin_name = 'admin' ",request.form.to_dict()["key"])) <= 0:
		resp = jsonify({'message' : 'Unauthorized access'})
		resp.status_code = 401
		return resp

	if 'limit-cpu' not in request.form or 'limit-gpu' not in request.form or 'limit-mem' not in request.form or 'limit-rep' not in request.form:
		resp = jsonify({'message' : 'Missing some limits parameter'})
		resp.status_code = 401
		return resp
	try:
		limit_cpu = int(request.form["limit-cpu"])
		limit_gpu = int(request.form["limit-gpu"])
		limit_mem = int(request.form["limit-mem"])
		limit_rep = int(request.form["limit-rep"])
	except:
		resp = jsonify({'message' : 'Wrong parameter type'})
		resp.status_code = 401
		return resp
	update_limits(conn,str(limit_cpu),str(limit_gpu),str(limit_mem),str(limit_rep))

	resp = jsonify({'message' : 'Updated Limits'})
	resp.status_code = 201
	conn.close()
	return resp




@app.route('/register', methods=['POST'])
def register_entity():
	try:
		conn = create_connection(DB_URL)

	except:
		resp = jsonify({'message' : "Couldn't access database"})
		resp.status_code = 501
		return resp

	if 'id' not in request.args:
		resp = jsonify({'message' : 'No id provided'})
		resp.status_code = 401
		return resp

	if 'key' not in request.form:
		resp = jsonify({'message' : 'No auth key provided'})
		resp.status_code = 401
		return resp

	if len(get_statement(conn,"select * from apikey where api_key = ?",request.form.to_dict()["key"])) <= 0:
		resp = jsonify({'message' : 'Unauthorized access'})
		resp.status_code = 401
		return resp

	folder_name = request.args.to_dict()["id"]
	folder_id = get_statement(conn,"select folder_id from folderid where folder_id = ?",folder_name)
	

	
	if len(folder_id) > 0 :
		resp = jsonify({'message' : 'Unauthorized Overwrite, folder already exist'})
		resp.status_code = 401
		return resp
	try:
		default_limits = get_statement(conn,"select * from limits where admin_id = ?","isep")[0]
	except:
		resp = jsonify({'message' : "Couldn't access database"})
		resp.status_code = 501
		return resp
	insert_folder_id(conn,folder_name,default_limits[1],default_limits[2],default_limits[3],default_limits[4])

	resp = jsonify({'message' : 'Folder successfully created'})
	resp.status_code = 201
	conn.close()
	return resp


# Main Post Request Config
@app.route('/upload', methods=['POST'])
def upload_file():
	''' Start a containerized application using the docker file generated.\n\nGet Parameters:\n id -> folder of the client\n\nPost Parameters:\nkey-> Authentication Key\nname-> Name of the container\nfile-> Image to run in the container\nport-> Port to be exposed\nlimit-mem-> Memory limitation\nlimit-cpu-> Cpu limitation\nlimit-gpu-> Gpu limitation (best used in a jetson xavier)\n'''

	limit_cpu = "0"
	limit_gpu = "0"
	limit_mem = "0"
	replicas = "1"
	container_port_data = "80"

	try:
		dir_verify(UPLOAD_FOLDER)
		conn = create_connection(DB_URL)
	except:
		resp = jsonify({'message' : "Couldn't access database"})
		resp.status_code = 501
		return resp
	
	# check if the post request has the file part
	if 'key' not in request.form:
		resp = jsonify({'message' : 'No auth key provided'})
		resp.status_code = 401
		return resp
	
	if 'name' not in request.form:
		resp = jsonify({'message' : 'No name provided'})
		resp.status_code = 401
		return resp

	if 'imageName' not in request.form:
		resp = jsonify({'message' : 'No id provided'})
		resp.status_code = 401
		return resp
	
	# check if the post request has the id part
	if 'id' not in request.args:
		resp = jsonify({'message' : 'No id provided'})
		resp.status_code = 401
		return resp
	
	

	# check if the post request key is on database
	if len(get_statement(conn,"select * from apikey where api_key = ?",request.form.to_dict()["key"])) <= 0:
		resp = jsonify({'message' : 'Unauthorized access'})
		resp.status_code = 401
		return resp

	folder_name = request.args.to_dict()["id"]
	name_file = request.form.to_dict()["name"]
	image_name = request.form.to_dict()["imageName"]
	folder_id = get_statement(conn,"select * from folderid where folder_id = ?",folder_name)

	# check if the post request folder_id is on database
	
	
	if len(folder_id) <= 0 :
		resp = jsonify({'message' : 'Unauthorized folder id'})
		resp.status_code = 401
		return resp

	mini_arr = folder_id[0]

	try:
		if 'limit-cpu' in request.form:
			limit_cpu = int(request.form["limit-cpu"])
			if not limit_cpu <= int(mini_arr[1]) or not limit_cpu>=0:
				limit_cpu = int(mini_arr[1])
		else:
			limit_cpu = int(int(mini_arr[1])*0.7)

		if 'limit-gpu' in request.form:
			limit_gpu = int(request.form["limit-gpu"])
			if not limit_gpu <= int(mini_arr[2]) or not limit_gpu>=0:
				limit_gpu = int(mini_arr[2])
		else:
			limit_gpu = int(int(mini_arr[2])*0.7)

		if 'limit-mem' in request.form:
			limit_mem = int(request.form["limit-mem"])
			if not limit_mem <= int(mini_arr[3]) or not limit_mem>=0:
				limit_mem = int(mini_arr[3])
		else:
			limit_mem = int(int(mini_arr[3])*0.7)

		if 'port' in request.form:
			container_port_data_arr = []
			try:	
				container_port_data_arr = request.form["port"].split(",")
			except:
				container_port_data_arr.append(request.form["port"]) 


	except:
		resp = jsonify({'message' : 'Wrong parameter Format'})
		resp.status_code = 404
		return resp

	# check if the post parameter file is on the request
	#if 'file' not in request.files:
	#	resp = jsonify({'message' : 'No file part in the request'})
	#	resp.status_code = 400
	#	return resp

	#file = request.files['file']
	
	# check if the a file was selected to send on the request
	#if file.filename == '':
	#	resp = jsonify({'message' : 'No file selected for uploading'})
	#	resp.status_code = 400
	#	return resp

	# check if the file extension is allowed and creating dirs if they dont exist
	#if file and allowed_file(file.filename):
	work_folder = app.config['UPLOAD_FOLDER']+"/"+folder_name
	dir_verify(work_folder)

	#filename = secure_filename(file.filename)
	#file.save(os.path.join(work_folder, filename))

	node_compatibility = ImageCompatibility.main_task(image_name)
	random_string = "-"+str(generate_random_string(8))
	all_port_text = insert_container_port(conn,name_file+random_string,str(limit_cpu/1000),str(limit_mem),image_name,container_port_data_arr)
	writeConfig_kubernetes(name=name_file+random_string, image=image_name,extern_port="extern_port_number",memory=str(limit_mem),cpu=str(limit_cpu/1000),container_port="container_port_data",file_name=work_folder+"/"+name_file+".yaml",all_ports=all_port_text,compatible=node_compatibility)
	resp = jsonify({'message' : 'File successfully uploaded','port-map':port_text_beautify(all_port_text)})
	resp.status_code = 201
	#insert_container_port(conn,name_file,str(limit_cpu/1000),str(limit_mem),filename.split(".")[0],container_port_data_arr)
	conn.close()
	return resp
	#else:
	#	resp = jsonify({'message' : 'Allowed file types are docker images'})
	#	resp.status_code = 400
	#	return resp

def port_text_beautify(text):
	arr = text.split('       - "')
	text_after = ''
	for data in arr:
		text_after = text_after + data.split('"\n')[0]+"|"
	return text_after
def port_to_text(arr_data):
	theme=''
	for container_port in arr_data:
		extern_port_number = str(random.randint(10000,20000))
		theme = theme +f'       - "{extern_port_number}:{container_port}"\n'
	return theme



def dir_verify(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)




def writeConfigBeta(**kwargs):
	template = """	apiVersion: v1
	kind: pod
	metadata:
		name: {name}
	spec:
		
		containers:
		- name: {name}
		  image: {image}
		  ports:
		  - containerPort: 80
		resources:
			requests:
				memory: "64Mi"
				cpu: "250m"
			limits:
				nvidia.com/gpu: 1 # requesting 1 GPU
				memory: "64Mi"
				cpu: "250m"
"""
	with open('somefile.yaml', 'w') as yfile:
		yfile.write(template.format(**kwargs))

def writeConfig(**kwargs):
	template = """version: "2.4"
services:
  {name}:
    image: {image}
    restart: always
    ports:
{all_ports}
    mem_limit: {memory}m
    mem_reservation: {memory}m
    cpus: {cpu}
"""  
	with open(kwargs.get('file_name'), 'w') as yfile:
		yfile.write(template.format(**kwargs))

def writeConfig_kubernetes(**kwargs):
    template = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}-deployment
  labels:
    app: {name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      restartPolicy: Always
      nodeSelector:
        node_type: {compatible}
      containers:
        - name: {name}
          image: {image}
          ports:
          - containerPort: {all_ports}
          resources:
              requests:
                  memory: "{memory}Mi"
                  cpu: "{cpu}m"
              limits:
                  memory: "{memory}Mi"
                  cpu: "{cpu}m"
"""  
	
    with open(kwargs.get('file_name'), 'w') as yfile:
        yfile.write(template.format(**kwargs))

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def insert_auth(con,key):
	cur = con.cursor()
	cur.execute("INSERT OR IGNORE INTO auth VALUES(?);",(key,))
	con.commit()

def delete_auth(con,key):
	cur = con.cursor()
	cur.execute("delete from auth where auth_key = ?",(key,))
	con.commit()

def update_limits(con,cpu,gpu,mem,repl):
	admin_id = "isep"
	cur = con.cursor()
	cur.execute("delete from limits where admin_id = ?",(admin_id,))
	con.commit()
	cur.execute("INSERT OR IGNORE INTO limits VALUES(?,?,?,?,?);",(admin_id,cpu,gpu,mem,repl,))
	con.commit()

def insert_folder_id(con,folderID,cpu,gpu,mem,repl):
	cur = con.cursor()
	cur.execute("INSERT OR IGNORE INTO folderid VALUES(?,?,?,?,?);",(folderID,cpu,gpu,mem,repl,))
	con.commit()

def del_tokens(con):
	cur = con.cursor()
	cur.execute("delete from auth where length(auth_key) > 1")
	con.commit()

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def insert_container_port(con,name,limit_cpu,limit_mem,image,port):
	cur = con.cursor()
	cur.execute("INSERT OR IGNORE INTO container VALUES(?,?,?,?,?);",(None,name,limit_mem,limit_cpu,image,))
	con.commit()
	theme=''
	for port_given in port:
		container_id = cur.execute("select container_id from container where image_name = '"+image+"' and container_name = '"+name+"';").fetchall()
		res = cur.execute("select MAX(port_extern) from port;")
		extern_port_number=0
		try:
			extern_port_number = int(res.fetchone()[0])+1
		except:
			extern_port_number = MIN_PORT_NUMBER
		#(str(extern_port_number))
		cur.execute("INSERT OR IGNORE INTO port VALUES(?,?,?);",(int(extern_port_number),int(port_given),int(container_id[0][0]),))
		theme = theme +f'       - "{extern_port_number}:{port_given}"\n'
			
	con.commit()
	return theme
	

def get_statement(con,select,specific):
	cur = con.cursor()
	if specific == "":
		res = cur.execute(select)
	else:
		res = cur.execute(select,(specific,))
	return res.fetchall()

for rule in app.url_map.iter_rules():
    auto.doc()(app.view_functions[rule.endpoint])

@app.route('/documentation')
def documentation():
    return auto.html()


def monitoring_tokens():
	try:
		conn = create_connection(DB_URL)
		while(1):
			now = datetime.now()
			current_time = now.strftime("%H:%M:%S")
			min = current_time.split(":")[1]
			print("Monitoring at minute: "+ str(min))
			if(int(min)%10==0):
				del_tokens(conn)
			time.sleep(50)


	except Exception as e:
		print(e)
		time.sleep(10)
		monitoring_tokens()

@app.route('/services', methods=['GET'])
def get_services():
	con = None
	try:
		con = create_connection(DB_URL)
	except:
		resp = jsonify({'message' : "Couldn't access database"})
		resp.status_code = 501
		return resp
	
	cur = con.cursor()

# check if the post request has the id part
	if 'id' not in request.args:
		resp = jsonify({'message' : 'No id provided'})
		resp.status_code = 401
		return resp


	folder_name = request.args.to_dict()["id"]
	folder_id = get_statement(con,"select * from folderid where folder_id = ?",folder_name)

	# check if the post request folder_id is on database
	if len(folder_id) <= 0 :
		resp = jsonify({'message' : 'Unauthorized folder id'})
		resp.status_code = 401
		return resp
	if 'key' not in request.form:
		resp = jsonify({'message' : 'No auth key provided'})
		resp.status_code = 401
		return resp
	
	if len(get_statement(con,"select * from apikey where api_key = ?",request.form.to_dict()["key"])) <= 0:
		resp = jsonify({'message' : 'Unauthorized access'})
		resp.status_code = 401
		return resp

	
	
	servicesId = cur.execute("select * from port;").fetchall()
	services = {'list' : []}
	for x in servicesId:
		#print(str(x[2]))
		servicesName = cur.execute("select container_name,image_name from container where container_id = '"+str(x[2])+"';").fetchall()
		message = "Name: "+str(servicesName[0][1])+" Image: "+str(servicesName[0][0])+" Ports: "+str(x[0])
		services['list'].append(str(message))
	resp = jsonify(services)
	resp.status_code = 200
	return resp
		

def start_api():
	app.run()
if __name__ == "__main__":
	proc = multiprocessing.Process(target=start_api)
	proc2 = multiprocessing.Process(target=monitoring_tokens)
	proc.start()
	proc2.start()
	proc.join()
	proc2.join()
	#get_services()
    
