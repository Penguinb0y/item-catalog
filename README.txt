# EDIT:
#### * Facebook now enforces HTTPS meaning that HTTP is not a Valid OAuth Redirect URI. Having issues working around that
#### * After newly implementing a dedicated user page for add, edit, and delete, functionality, the url_for is having issues with passing through item_id, and as a result, is not working correctly, Having issues with that.


# README
This is a project purely dedicated to CRUD functionality based on User Authentication and Authorization by using RESTful web application using the Python framework Flask along with OAuth authentication. The purpose of this project is to have an efficient interaction with data of a web application, to properly implement authentication mechanisms, and appropriately map HTTP methods to CRUD operations.

The Item Catalog project consists of developing an application that provides a list of items within a variety of categories, as well as provide a user registration and authentication system. In order to add, update, or delete item info, the user must first sign in before being able to have access to the user-created item page that allows it.

## System Requirements
* VirtualBox 
(Build 5.1 or older; newer versions than that are INCOMPATIBLE)
https://www.virtualbox.org/wiki/Download_Old_Builds_5_1
* Vagrant
https://www.vagrantup.com/downloads.html
* A unix-style terminal

### Other Requirements
* Your own Google Account

VirtualBox is the program that runs your Linux virtual machine and Vagrant is the program that will download a Linux operating system and run it inside the virtual machine. (All of which will be done through a terminal.)

Provided in item-catalog are these files:
* a static folder for `styles.css`
* a templates folder for all the `.html` files
* `Vagrantfile`
* `client_secrets.json`
* `fb_client_secrets.json`
* `database_setup.py`
* `lotsofitems.py`
* `project.py`

# EDIT: everything else not specified are to be removed in future repositories

# Directions
1. On a terminal, `cd` to `item-catalog` so it's now the working directory.
2. With `item-catalog` as your working directory on your terminal, run the command `$ vagrant up` to have the server running in a Linux Virtual Machine.
3. When the shell prompt is back, run the command `$ vagrant ssh` to log in to the newly installed VM. (The vagrant directory)
4. When logged into vagrant, `cd` into `/vagrant` which is the folder shared with your virtual machine
5. (First time only) Run the commmand: `python database_setup.py` to create the item catalog database
6. (First time only) Run the command: `python lotsofitems.py` to populate the database with items
7. Run the command `python project.py` to run the program 
8. Go to your preferred web browser and go to the url: http://localhost:8000 to go to the item-catalog page. (Welcome!)
9. Click on the login link on the top-right corner
10. Sign-in with your Google account and then you will be redirected back to the main page
11. Click on the link that says "Go to my items"
12. On that page, which should be empty, you will have access to be able to create, edit, and delete your own items


