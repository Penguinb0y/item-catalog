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


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).all()
    #return "This page will show all item categories in the catalog"
    return render_template(
        'catalog.html', categories=categories)



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


@app.route('/catalog/<string:category_name>')
@app.route('/catalog/<int:category_id>/')
def showCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(category_id=category_id)
    #return "This page is the category for category %s" % category_id
    return render_template(
        'category.html', category=category, items=items, category_id=category_id)


@app.route('/catalog/<int:category_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    editedItem = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("Item has been edited")
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template(
            'edititem.html', category_id=category_id, item_id=item_id, item=editedItem)


@app.route('/catalog/<int:category_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Item has been deleted")
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('deleteitem.html', category_id=category_id, item=itemToDelete)






if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)