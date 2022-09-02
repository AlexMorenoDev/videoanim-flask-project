# VIDEOANIM
Videoanim is a simple flask project developed for a university project using Python, HTML, CSS and JavaScript. It consists in a web application which its main objective is to provide a way to register shops where videogames and anime products are sold. Doing this, shop owners will be able to advertise their shops and products. 

In the application, owners are allowed to create a user account and after logging in, they will be able to add, update and delete shop/s and products. Moreover, clients interested on this kind of establishments can visit each shop page to see its information and products.

Application architecture:
![alt text](https://github.com/AlexMoreno98/videoanim-flask-project/blob/master/images/diagram.PNG)

## Installation

### Dependencies
- git v2.24.1 --> https://git-scm.com/
- Python v3.8.0 --> https://www.python.org/
- pip v19.3.1

### How to run the application locally

Before running the application, inside "app" folder you have to uncomment line 36 (remote_ip = request.remote_addr) and comment line 38 (remote_ip = request.headers['X-Forwarded-For']) in visitor.py.

Then, execute following commands:

``` bash
cd videoanim-flask-project
python3 -m venv venv  ||  python -m venv venv
<Activate created virtual env with different command depending on the installed operative system>
(venv) pip3 install -r requirements.txt  ||  (venv) pip install -r requirements.txt
(venv) cd app
(venv) python app.py
```
After executing app.py, you can access the website visiting: http://127.0.0.1:5000/

*IMPORTANT*: in case you are not running the application locally and want to add a new owner so he can add his shops and products to the system, all you have to do is add his IP to whitelist.txt file. This is how the application difference between visitors and owners. It could be done using MongoDB database, but instead of having a .txt file it would be necessary to create a new collection where owners IP would be stored.

### Used packages

- dnspython v1.16.0

- Flask v1.1.1 

- Flask-Babel v0.12.2

- Flask-PyMongo v2.3.0  

- Flask-Session v0.3.1 

- gunicorn v20.0.4

- Jinja2 v2.10.3

- passlib v1.7.2

- pymongo v3.10.0

<br/>To install them:
``` bash
pip install <package name>
```
Or if you prefer, use requirements.txt to install all packages automatically:
``` bash
pip install -r requirements.txt
```

## MongoDB
For the application database I have used MongoDB. When I started developing the web application, I used mongo in localhost but now I have deployed it on MongoDB Atlas (https://www.mongodb.com/cloud/atlas).

If you want to download MongoDB to keep it in your file system, download it from here: https://www.mongodb.com/download-center/community <br/>

As I´ve said before, at the beginning of the project I used mongo locally, I specifically downloaded the zip version from previous link. To open MongoDB in localhost, extract the downloaded zip, open a console or terminal inside bin folder and execute the following command:
``` bash
mongod.exe --dbpath="<Path to the folder where the database will be stored>"
```
After that, **don´t close the console or the terminal**. <br/>
If you want to access the database open a new console or terminal inside bin folder and execute:
``` bash
mongo.exe
use db
```
In case you want to connect the application to local database you have to modify one line inside app.py:
``` bash
app.config['MONGO_URI'] = 'mongodb://localhost:27017/db'
```
However, if you want to connect the application to Mongo Atlas database delete or comment previous line and type this:
``` bash
app.config['MONGO_URI'] = '<MongoDB Atlas URI>'
```
(To connect the application to your own database of MongoDB Atlas you have to create a user account in its website, add a new database, get your own database URI and insert it between the quotes)

When the application interacts with Mongo, it makes queries to a database called 'db'. This database has got 4 collections: usuarios, tienda, fs.files and fs.chunks. The latter two are for storing images.

#### Database structure:
``` bash
usuarios
{
    "_id": ,
    "email": "",
    "name": "",
    "password": ""
}

tienda
{  
    "_id": ,
    "nombre": "",
    "direccion": "",
    "telefono": "",
    "usuario_email": "",
    "nombre_imagen_tienda": "",
    "productos": [
        {
            "nombre": "",
            "precio": ,
            "tam_ancho": ,
            "tam_alto": ,
            "materiales": "",
            "nombre_imagen_producto": ""
        }
    ]
}

fs.files
{
    "_id": ,
    "filename": "",
    "contentType": "",
    "md5": ""
    "chunkSize": ,
    "length": ,
    "uploadDate": 
}

fs.chunks
{
    "_id": ,
    "files_id": ,
    "n": ,
    "data": 
}
```

## Heroku
Full application is deployed on Heroku. This makes possible to access the website from anywhere. <br/>Heroku app: https://flaskappdesarrollo.herokuapp.com/

Before the deployment, inside "app" folder you have to comment line 36 (remote_ip = request.remote_addr) and uncomment line 38 (remote_ip = request.headers['X-Forwarded-For']) in visitor.py.

The deployment can be done in a simple way:
1. Create an Heroku user account.
2. Add new app in Heroku website.
3. Link Heroku app with github repository.
4. Deploy master branch.

It´s important to create 2 files before deploying the application: requirements.txt and Procfile. 

## Linux deployment
https://github.com/AlexMoreno98/videoanim-flask-project/blob/master/linux-deployment.md

## i18n - Internationalization
I have used Flask-Babel for this purpose. <br/>
https://pythonhosted.org/Flask-Babel/

First of all, we have to label the text we want to translate inside every .py file with gettext('Text') function, and every .html file with Jinja2. Then, to generate translations, follow these steps:
1. Create babel.cfg file inside app folder with the following content:
``` bash
[python: **.py]
[jinja2: **/templates/**.html]
extensions=jinja2.ext.autoescape,jinja2.ext.with_
```
2. Generate messages.pot file:
``` bash
pybabel extract -F babel.cfg -o messages.pot .
```

3. Initialize and create translations folder:
``` bash
pybabel init -i messages.pot -d translations -l en
```

4. Inside translations folder open messages.po file and write the translations updating "msgstr" fields. For example:
``` bash
msgid "Registro"
msgstr "Register"
```

5. Compile all translations:
``` bash
pybabel compile -d translations
```

## Screenshots

### Index:
![Index](https://github.com/AlexMoreno98/videoanim-flask-project/blob/master/images/index.PNG)
<br/><br/>

### List of products:
![List of products](https://github.com/AlexMoreno98/videoanim-flask-project/blob/master/images/listProduct.PNG)
<br/><br/>

### Show product information:
![Show product](https://github.com/AlexMoreno98/videoanim-flask-project/blob/master/images/showProduct.PNG)
<br/><br/>

### User profile:
![Profile](https://github.com/AlexMoreno98/videoanim-flask-project/blob/master/images/profile.PNG)
<br/><br/>

### Add new products:
![Add products](https://github.com/AlexMoreno98/videoanim-flask-project/blob/master/images/addProducts.PNG)
<br/><br/>

### Modify shop information:
![Modify shop](https://github.com/AlexMoreno98/videoanim-flask-project/blob/master/images/modifyShop.PNG)
<br/><br/>

### Modify product information:
![Modify product](https://github.com/AlexMoreno98/videoanim-flask-project/blob/master/images/modifyProduct.PNG)
<br/><br/>
