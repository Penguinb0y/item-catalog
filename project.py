from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

app = Flask(__name__)
app.secret_key = 'super secret key'


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


#returns Category.id derrived from its name
def getCategoryid(category_name):
    c = session.query(Category).filter_by(name=category_name).one()
    results = c.id
    return results


#JSON APIs to view Catalog Information
@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).all()
    return jsonify(categories= [c.serialize for c in categories])


@app.route('/catalog/<string:category_name>/JSON')
def categoryJSON(category_name):
    category_id = getCategoryid(category_name)
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(CategoryItem).filter_by(category_id = category_id).all()
    return jsonify(Category_Items=[i.serialize for i in items])


@app.route('/catalog/<string:category_name>/<int:item_id>/JSON')
def categoryItemJSON(category_name, item_id):
    category_id = getCategoryid(category_name)
    Category_Item = session.query(CategoryItem).filter_by(id = item_id).one()
    return jsonify(Category_Item = Category_Item.serialize)


#Show the whole catalog
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).all()
    #return "This page will show all item categories in the catalog"
    return render_template(
        'catalog.html', categories=categories)


#Create a new item in the database
@app.route('/catalog/new', methods=['GET', 'POST'])
def newItem():
    categories = session.query(Category).all()
    if request.method == 'POST':
        newItem = CategoryItem(name=request.form['name'], description=request.form[
                           'description'], category_id=request.form['category'])
        session.add(newItem)
        session.commit()
        flash("new item created!")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newitem.html', categories=categories)


#Show specified category
@app.route('/catalog/<string:category_name>/')
def showCategory(category_name):
    category_id = getCategoryid(category_name)
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(category_id=category_id).all()
    #return "This page is the category for category %s" % category_id
    return render_template(
        'category.html', category=category, items=items, category_name=category_name)


#Edit an existing item
@app.route('/catalog/<string:category_name>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_name, item_id):
    category_id = getCategoryid(category_name)
    editedItem = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.category_id = request.form['category']
        session.add(editedItem)
        session.commit()
        flash("Item has been edited")
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template(
            'edititem.html', category_name=category_name, item_id=item_id, item=editedItem)


#Delete an existing item
@app.route('/catalog/<string:category_name>/<int:item_id>/delete/',methods=['GET', 'POST'])
def deleteItem(category_name, item_id):
    category_id = getCategoryid(category_name)
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Item has been deleted")
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template('deleteitem.html', category_id=category_id, category_name=category_name, item=itemToDelete)






if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)