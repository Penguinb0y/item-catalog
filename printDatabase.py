from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

engine = create_engine('sqlite:///itemcatalog.db')

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
	print item.id
	print item.category_id
print "\n"

category = session.query(Category.name).filter_by(id=1).one()

print "Category Name:\n"
print category.name
print "\n"

categoryid = session.query(Category).filter_by(name='Basketball').one()

print "Category Id:\n"
print categoryid.id
print "\n"

