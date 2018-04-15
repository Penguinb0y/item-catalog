from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CategoryItem, User

engine = create_engine('sqlite:///itemcatalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


# Category for Basketball
category1 = Category(name="Basketball")

session.add(category1)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Basketball", description="The very definition of the sport",
                      category=category1)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Jersey", description="Rep your team home boi",
                      category=category1)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id=1, name="Shoes", description="Just not the Jordans",
                      category=category1)

session.add(categoryItem3)
session.commit()


# Category for Students
category2 = Category(name="Students")

session.add(category2)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Laptop", description="A necessity",
                      category=category2)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Backpack", description="All nice and bulky",
                      category=category2)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id=1, name="Notebook", description="Hope you like spiral!",
                      category=category2)

session.add(categoryItem3)
session.commit()


# Category for Colors
category3 = Category(name="Colors")

session.add(category3)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Black", description="you see anything?",
                      category=category3)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Blue", description="Sky color!",
                      category=category3)

session.add(categoryItem2)
session.commit()


categoryItem3 = CategoryItem(user_id=1, name="Red", description="Now where's purple..?",
                      category=category3)

session.add(categoryItem3)
session.commit()


# Category for Fighting Games
category4 = Category(name="Fighting Games")

session.add(category4)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Street Fighter", description="The one that started it all",
                      category=category4)

session.add(categoryItem1)
session.commit()


categoryItem2 = CategoryItem(user_id=1, name="Tekken", description="3d fun!",
                      category=category4)

session.add(categoryItem2)
session.commit()


categoryItem3 = CategoryItem(user_id=1, name="Marvel vs. Capcom 2", description="Oh, he so Pringles!",
                      category=category4)

session.add(categoryItem3)
session.commit()


print "added stuff!"