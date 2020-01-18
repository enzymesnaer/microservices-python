from flask import Flask, jsonify, make_response, abort, request
import json
import sqlite3


app = Flask(__name__)


# >>> import sqlite3
# >>> conn = sqlite3.connect('mydb.db')
# >>> c = conn.cursor()
# >>> c.execute("SELECT * FROM apirelease");
# <sqlite3.Cursor object at 0x017728E0>
# >>> print(c.fetchall())
# []
# >>> c.execute("INSERT INTO apirelease VALUES ('2020-01-16 18:05:00', 'v1', '/api/v1/users', 'get, post, put, delete')");
# <sqlite3.Cursor object at 0x017728E0>
# >>> c.execute("SELECT * FROM apirelease");
# <sqlite3.Cursor object at 0x017728E0>
# >>> print(c.fetchall())
# [('2020-01-16 18:05:00', 'v1', '/api/v1/users', 'get, post, put, delete')]
# >>> conn.commit()
# >>> conn.close()  


@app.route("/api/v1/info", methods=["GET", "POST"])
def home_index():
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    api_list=[]
    print("Empty list ", api_list)
    cursor = conn.execute("SELECT buildtime, version, methods, links FROM apirelease")
    for row in cursor:
        a_dict = {}
        a_dict['version'] = row[0]
        a_dict['buildtime'] = row[1]
        a_dict['methods'] = row[2]
        a_dict['links'] = row[3]
        print("Single row dict ", a_dict)
        api_list.append(a_dict)
    print("Final list ", api_list)
    conn.close()
    return jsonify({'api_version': api_list}, 200)


# >>> c = conn.cursor()
# >>> c.execute("CREATE TABLE users(username varchar2(30), emailid varchar2(30), 
# password varchar2(30), full_name varchar(30), id integer primary key autoincrement)");
# <sqlite3.Cursor object at 0x030B28E0>


def list_users():
    conn = sqlite3.connect('mydb.db')
    print("Opened database sucessfully")
    api_list = []
    cursor = conn.execute("SELECT username, full_name, emailid, password, id FROM users")
    for row in cursor:
        a_dict = {}
        a_dict['username'] = row[0]
        a_dict['name'] = row[1]
        a_dict['emailid'] = row[2]
        a_dict['password'] = row[3]
        a_dict['id'] = row[4]
        api_list.append(a_dict)
    return jsonify({'user_list': api_list})


@app.route('/api/v1/users', methods=['GET'])
def get_users():
    return list_users()


def list_user(user_id):
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    api_list = []
    cursor = conn.cursor()
    cursor.execute(f"SELECT * from users where id={user_id}")
    data = cursor.fetchall()
    if len(data) != 0:
        user = {}
        user['username'] = data[0][0]
        user['name'] = data[0][1]
        user['emailid'] = data[0][2]
        user['password'] = data[0][3]
        user['id'] = data[0][4]
        api_list.append(user)
        conn.close() 
        return jsonify(api_list)
    else:
        return make_response(jsonify({'error': 'Resource not found!'}), 404)
        

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return list_user(user_id)


def add_user(new_user):
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    api_list = []
    cursor = conn.cursor()
    cursor.execute("SELECT * from users where username=? or emailid=?",(new_user['username'],new_user['emailid']))
    data = cursor.fetchall()
    if len(data) != 0:
        abort(409)
    else:
        cursor.execute("insert into users (username, emailid, password, full_name) values(?,?,?,?)",(new_user['username'],new_user['emailid'], new_user['password'], new_user['name']))
        conn.commit()
        print("Success")
    cursor = conn.execute("SELECT username, full_name, emailid, password, id FROM users")
    for row in cursor:
        a_dict = {}
        a_dict['username'] = row[0]
        a_dict['name'] = row[1]
        a_dict['emailid'] = row[2]
        a_dict['password'] = row[3]
        a_dict['id'] = row[4]
        api_list.append(a_dict)
    conn.close() 
    return api_list

    
@app.route('/api/v1/users', methods=['POST'])
def create_user():
    if not request.json or not 'username' in request.json or not 'emailid' in request.json or not 'password' in request.json:
        abort(400)
    user = {
        'username': request.json['username'],
        'emailid': request.json['emailid'],
        'name': request.json.get('name', ""),
        'password': request.json['password']
    }
    return jsonify({'Added new users ': add_user(user)}, 201)


def del_user(thatname):
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM users WHERE username = "{thatname}"')
    data = cursor.fetchone()
    print("Data", data)
    if len(data) == 0:
        abort(404)
    else:
        cursor.execute(f'delete from users where username = "{thatname}"')
        conn.commit()
        return "Success"


@app.route('/api/v1/users', methods=['DELETE'])
def delete_user():
    if not request.json or not 'username' in request.json:
        abort(400)
    user = request.json['username']
    return jsonify({'status': del_user(user)}, 200)


@app.errorhandler(404)
def resource_not_found(error):
    return make_response(jsonify({'error': 'Resource not found!'}), 404)


@app.errorhandler(400)
def invalid_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


app.run(host='127.0.0.1', port=5000, debug=True)