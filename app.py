from flask import Flask, jsonify, make_response, abort, request
import json
import sqlite3
from time import strftime, gmtime

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


def upd_user(user_dict):
    conn = sqlite3.connect('mydb.db')
    print("Opened database successsfully")
    cursor = conn.cursor()
    cursor.execute(f'SELECT * from users where id = "{user_dict["id"]}"')
    data = cursor.fetchall()
    # print(data)
    if len(data) == 0:
        abort(404)
    else:
        user = {}
        key_list = user_dict.keys()
        for i in key_list:
            if i != "id":
                print (user_dict, i)
                cursor.execute("""UPDATE users set {0} = ? WHERE id = ?""".format(i), (user_dict[i], user_dict['id']))
                conn.commit()
        return "Success"


@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = {}
    if not request.json:
        abort(400)
    user['id'] = user_id
    key_list = request.json.keys()
    for i in key_list:
        user[i] = request.json[i]
    # print(user)
    return jsonify({'status': upd_user(user)},200)


def list_tweets():
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    api_list = []
    cursor = conn.execute('SELECT  username, body, tweet_time, id FROM tweets')
    data = cursor.fetchall()
    
    if len(data) != 0:
        for row in data:
            tweets = {}
            tweets['username'] = row[0]
            tweets['body'] = row[1]
            tweets['timestamp'] = row[2]
            tweets['id'] = row[3]
            api_list.append(tweets)
            conn.close()
        return api_list
    else:
        return api_list
    


@app.route('/api/v2/tweets', methods=['GET'])
def get_tweets():
    return jsonify({'tweets_list': list_tweets()})


def add_tweet(new_tweets):
    conn = sqlite3.connect('mydb.db')
    print("Opened database succesfully")
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM users WHERE username="{new_tweets["username"]}"')
    data = cursor.fetchall()

    if len(data) == 0:
        abort(404)
    else:
        cursor.execute("INSERT INTO tweets (username, body, tweet_time) VALUES (?,?,?)", (new_tweets['username'],new_tweets['body'],new_tweets['created_at']))
        conn.commit()
        return "Success"
        

@app.route('/api/v2/tweets', methods=['POST'])
def add_tweets():
    user_tweet = {}
    if not request.json or not 'username' in request.json or not 'body' in request.json:
        abort(400)
    user_tweet['username'] = request.json['username']
    user_tweet['body'] = request.json['body']
    user_tweet['created_at'] = strftime("%Y-%m-%d T%H:%M:%SZ", gmtime())
    print(user_tweet)
    return jsonify({'status': add_tweet(user_tweet)}, 200)


def list_tweet(uid):
    print(uid)
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    api_list = []
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM tweets WHERE id={uid}')
    data = cursor.fetchall()
    print(data)
    if len(data) == 0:
        abort(404)
    else:
        user = {}
        user['id'] = data[0][0]
        user['username'] = data[0][1]
        user['body'] = data[0][2]
        user['tweet_time'] = data[0][3]
    api_list.append(user)
    conn.close()
    return jsonify(api_list)
        

@app.route('/api/v2/tweets/<int:id>', methods=['GET'])
def get_tweet(id):
    return list_tweet(id)


@app.errorhandler(404)
def resource_not_found(error):
    return make_response(jsonify({'error': 'Resource not found!'}), 404)


@app.errorhandler(400)
def invalid_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

# -------------------------------------------------------------------
#--------------------------------------------------------------------

from flask import render_template
@app.route('/adduser')
def adduser():
    return render_template('adduser.html')

@app.route('/addtweets')
def addtweetjs():
    return render_template('addtweets.html')


# -------------------------------------------------------------------
# -------------------------------------------------------------------

from flask_cors import CORS, cross_origin
# To enable CORS
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


# -------------------------------------------------------------------
# -------------------------------------------------------------------
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/addname')
def addname():
    

app.run(host='127.0.0.1', port=5000, debug=True)