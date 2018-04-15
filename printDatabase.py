from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User

engine = create_engine('sqlite:///itemcatalogwithusers.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)

session = DBSession()

print "Raw database:\n"
print session.query(Category).all()
print "\n"

categories = session.query(Category).all()

print "List of categories in Catalog:\n"
for category in categories:
	print category.name
	print category.id
print "\n"

items = session.query(CategoryItem).all()

print "All items in all categories:\n"
for item in items:
	print item.name
	print "item_id: " + str(item.id)
	print "category_id: " + str(item.category_id)
	print "user_id: " + str(item.user_id)
	print "\n"
print "\n"

category = session.query(Category.name).filter_by(id=1).one()

print "Category Name: " + str(category.name)
print "\n"

categoryid = session.query(Category).filter_by(name='Basketball').one()

print "Category Id: " + str(categoryid.id)
print "\n"


users = session.query(User).all()

for user in users:
	print "User: " + str(user.id)
print "\n"
