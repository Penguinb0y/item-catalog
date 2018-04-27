#!/usr/bin/env python
#
# code runs the item catalog website on dedicated host:
# http://localhost:8000/
# (Includes user authorized CRUD functionality)

from flask import Flask, \
                    render_template, \
                    request, redirect, \
                    url_for, \
                    flash, \
                    jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog App"


# Connect to database and create database session
engine = create_engine('sqlite:///itemcatalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    """Create anti-forgery state token"""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/githubconnect')
def githubconnect():
    """GitHub login authorization"""
    print "Request state"
    print request
    print "Login session " + login_session['state']
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.args.get('code')
    print "Code is"
    print code
    # Exchange client token for long-lived server-side token
    app_id = json.loads(
        open('github_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('github_client_secrets.json', 'r').read())['web']['app_secret']

    url = 'https://github.com/login/oauth/access_token'
    payload = {
        'client_id': app_id,
        'client_secret': app_secret,
        'code': request.args.get('code')
    }
    headers = {'Accept': 'application/json'}
    r = requests.post(url, params=payload, headers=headers)

    response = r.json()
    print "Printing Response"
    print response
    if 'access_token' not in response:
        response = make_response(json.dumps('Github did not return an access token.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = response['access_token']
    url = 'https://api.github.com/user?access_token=%s' % login_session['access_token']
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    print "User is "
    print result
    data = json.loads(result)
    login_session['provider'] = 'github'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['client_id'] = app_id
    login_session['picture'] = data["avatar_url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return redirect(url_for('showCatalog'))

@app.route('/githubdisconnect')
def githubdisconnect():
    client_id = login_session['client_id']
    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    url = 'https://api.github.com/applications/%s/tokens/%s' % (client_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Facebook Authorization"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    #exchange client token for long-lived server-side token with GET
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.11/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    print "data: ",data
    token = 'access_token=' + data['access_token']

    # Use token to get user info from API
    # make API call with new token
    url = 'https://graph.facebook.com/v2.11/me?%s&fields=name,id,email,picture' % token

    #new: put the "picture" here, it is now part of the default "public_profile"

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    login_session['picture'] = data['picture']["data"]["url"]
    login_session['access_token'] = access_token

    #see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1><img src="'
    output += login_session['picture']
    output += ' ">'

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """Disconnect Facebook User"""
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connects user through Google Account"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """
                'style = "width: 300px; height: 300px;
                border-radius: 150px;-webkit-border-radius: 150px;
                -moz-border-radius: 150px;"> '
                """
    flash("you are now logged in as %s" % login_session['username'])
    return output


# User Helper functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    user = session.query(User).filter_by(email=email).one()
    return user.id

@app.route('/gdisconnect')
def gdisconnect():
    """Disconnects Goole Account User"""
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Catalog Information
@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/catalog/<string:category_name>/JSON')
def categoryJSON(category_name):
    category_id = getCategoryid(category_name)
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(
        CategoryItem).filter_by(category_id=category_id).all()
    return jsonify(Category_Items=[i.serialize for i in items])


@app.route('/catalog/<string:category_name>/<int:item_id>/JSON')
def categoryItemJSON(category_name, item_id):
    category_id = getCategoryid(category_name)
    Category_Item = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(Category_Item=Category_Item.serialize)


@app.route('/catalog/user/JSON')
def userItemsJSON():
    user_id = getUserID(login_session['email'])
    user_items = session.query(CategoryItem).filter_by(user_id=user_id).all()
    return jsonify(user_items=[i.serialize for i in user_items])


# Helper Function: returns Category.id derrived from its name
def getCategoryid(category_name):
    c = session.query(Category).filter_by(name=category_name).one()
    results = c.id
    return results


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    """Main Page: Show Catalog"""
    categories = session.query(Category).all()
    return render_template('catalog.html', categories=categories)


@app.route('/catalog/<path:category_name>/')
def showCategory(category_name):
    """Page that shows Items based on category"""
    category_id = getCategoryid(category_name)
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(
        CategoryItem).filter_by(category_id=category_id).all()
    return render_template(
        'category.html', category=category,
        items=items, category_name=category_name)


@app.route('/catalog/new', methods=['GET', 'POST'])
def newItem():
    """User create a new item in the database"""
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    if request.method == 'POST':
        newItem = CategoryItem(
            name=request.form['name'], description=request.form[
                'description'], category_id=request.form['category'],
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("new item created!")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newitem.html', categories=categories)


@app.route('/catalog/user/')
def showUserItems():
    """Show items based on User_id"""
    if 'username' not in login_session:
        return redirect('/login')
    else:
        user_id = getUserID(login_session['email'])
        uitems = session.query(CategoryItem).filter_by(user_id=user_id).all()
        return render_template('usercatalog.html', uitems=uitems)


@app.route('/catalog/user/<path:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    """User edits an existing item"""
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CategoryItem).filter_by(id=item_id).one()
    if login_session['user_id'] != editedItem.user_id:
        return """
            <script>function myFunction()
            {alert('You are not authorized to edit this item.
             Please create your own item in order to edit it.');}
            </script><body onload='myFunction()'>"""
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("Item has been edited")
        return redirect(url_for('showUserItems'))
    else:
        return render_template(
            'edititem.html', item_id=item_id, item=editedItem)


@app.route('/catalog/user/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    """User deletes an existing item"""
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    if login_session['user_id'] != itemToDelete.user_id:
        return """
            <script>function myFunction()
            {alert('unauthorized to delete this item.');}
            </script>
            <body onload='myFunction()'>"""
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Item has been deleted")
        return redirect(url_for('showUserItems'))
    else:
        return render_template(
            'deleteitem.html', item_id=item_id, item=itemToDelete)


@app.route('/disconnect')
def disconnect():
    """Disconnect user based on provider"""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        if login_session['provider'] == 'github':
            githubdisconnect()
            del login_session['client_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
