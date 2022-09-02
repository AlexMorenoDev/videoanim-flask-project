from app import app, mongo, redirect, url_for, render_template, request, sha256_crypt, gettext, session, g

# Process of registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuarios = mongo.db.usuarios.find({})
        if usuarios:
            for usuario in usuarios:
                if usuario.get('email') == request.form['email']:
                    return render_template('/user/register.html', error=gettext("¡Ya existe una cuenta con ese email!"))

            if request.form['password'] != request.form['repeat-password']:
                return render_template('/user/register.html', error=gettext("¡Las contraseñas introducidas son distintas!"))
        
            passwordHash = sha256_crypt.using(salt=request.form['name']).hash(request.form['password'])
            mongo.db.usuarios.insert_one({'email': request.form['email'], 'name': request.form['name'], 'password': passwordHash})
            return render_template('/user/register.html', msg=gettext("¡Te has registrado correctamente!"))
        else:
            passwordHash = sha256_crypt.using(salt=request.form['name']).hash(request.form['password'])
            mongo.db.usuarios.insert_one({'email': request.form['email'], 'name': request.form['name'], 'password': passwordHash})
            return render_template('/user/register.html', msg=gettext("¡Te has registrado correctamente!"))

    return render_template('/user/register.html')

# Process of logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)
        usuario = mongo.db.usuarios.find_one({'email': request.form['email']})
        if usuario:
            passwordHash = sha256_crypt.using(salt=usuario.get('name')).hash(request.form['password'])
            if usuario.get('password') == passwordHash:
                session['user'] = request.form['email']
                return redirect(url_for('user', nombre_usuario=usuario.get('name'), msg=gettext("¡Has iniciado sesión correctamente!")))
            else:
                return render_template('/user/login.html', error=gettext("¡Email y/o contraseña incorrectos, inténtalo de nuevo!"))
        else:
            return render_template('/user/login.html', error=gettext("¡Introduce un email y contraseña válidos!"))

    return render_template('/user/login.html')

# Renders userTemplate.html if user logged.
@app.route('/users/<nombre_usuario>')
def user(nombre_usuario):
    if g.user:
        usuario = mongo.db.usuarios.find_one({'email': g.user})
        tiendas = mongo.db.tienda.find({'usuario_email': g.user})
        if request.args.get('msg'):
            return render_template('/user/userTemplate.html', usuario=usuario, tiendas=tiendas, msg=request.args.get('msg'), userTemplate=True)

        return render_template('/user/userTemplate.html', usuario=usuario, tiendas=tiendas, userTemplate=True)

    return redirect(url_for('login'))

# GET: renders profile.html if user logged. POST: updates user information.
@app.route('/users/<nombre_usuario>/profile', methods=['GET', 'POST'])
def profile(nombre_usuario):
    if request.method == 'POST':
        usuario = mongo.db.usuarios.find_one({'email': g.user})
        usuarios = mongo.db.usuario.find({})
        tiendas = mongo.db.tienda.find({})
        updates = {}

        if (request.form['oldPassword']):
            passwordHash = sha256_crypt.using(salt=usuario.get('name')).hash(request.form['oldPassword'])
            if (usuario.get('password') == passwordHash):
                if (request.form['nombre_a']):
                    updates['nombre'] = request.form['nombre_a']
                else:
                    updates['nombre'] = usuario.get('name')     

                if (request.form['email_a']):
                    for u in usuarios:
                        if u.get('email') == request.form['email_a']:
                            return render_template('/user/profile.html', usuario=usuario, error=gettext("Ya existe un usuario con ese email, prueba de nuevo."), profile=True)
                    updates['email'] = request.form['email_a']
                    for tienda in tiendas:
                        if tienda.get('usuario_email') == usuario.get('email'):
                            mongo.db.tienda.update_one({'nombre': tienda.get('nombre')}, {"$set": {'usuario_email': request.form['email_a']}})
                else:
                    updates['email'] =  usuario.get('email')

                if (request.form['password_a']):
                    oldPasswordHash = sha256_crypt.using(salt=usuario.get('name')).hash(request.form['password_a'])

                    if usuario.get('password') == oldPasswordHash:
                        return render_template('/user/profile.html', usuario=usuario, error=gettext("La nueva password no puede ser igual que la actual. Prueba con otra."), profile=True)

                    if (request.form['nombre_a']):
                        passwordHash = sha256_crypt.using(salt=request.form['nombre_a']).hash(request.form['password_a'])
                        updates['password'] = passwordHash
                    else:
                        updates['password'] = oldPasswordHash
                    
                else:
                    updates['password'] =  usuario.get('password')
                    if (request.form['nombre_a']):
                        passwordHash = sha256_crypt.using(salt=request.form['nombre_a']).hash(request.form['oldPassword'])
                        updates['password'] = passwordHash
        
                mongo.db.usuarios.update_one({'email': g.user}, {"$set": {'name': updates.get('nombre'), 'email': updates.get('email'), 'password': updates.get('password')}})
                
                session.pop('user', None)
                session['user'] = updates.get('email')

                usuario = mongo.db.usuarios.find_one({'email': updates.get('email')})
                return render_template('/user/profile.html', usuario=usuario, msg=gettext("¡Tus datos se han guardado correctamente!"), profile=True)
            else:
                return render_template('/user/profile.html', usuario=usuario, error=gettext("La contraseña introducida no es correcta, inténtalo de nuevo"), profile=True)
        else:
            return render_template('/user/profile.html', usuario=usuario, error=gettext("Tienes que introducir tu contraseña actual para poder actualizar tus datos"), profile=True)
    
    if g.user:
        usuario = mongo.db.usuarios.find_one({'email': g.user})
        return render_template('/user/profile.html', usuario=usuario, profile=True)

    return redirect(url_for('login'))
    
# GET: renders addTienda.html if user logged. POST: stores new shop in MongoDB.
@app.route('/users/<nombre_usuario>/add_tienda', methods=['GET', 'POST'])
def addTienda(nombre_usuario):
    if request.method == 'POST':
        tiendas = mongo.db.tienda.find({})
        imagen_tienda = None
        
        if tiendas.count() > 0:
            for tienda in tiendas:
                if tienda.get('nombre') == request.form['nombre']:
                    return render_template('/user/addTienda.html', nombreUsuario=nombre_usuario, error=gettext("¡Esa tienda ya existe!"), addTienda=True)
            
        if 'imagen_tienda' in request.files: 
            imagen_tienda = request.files['imagen_tienda']
            imagen_tienda.filename = 'imagen_' + request.form['nombre']
        
            mongo.save_file(imagen_tienda.filename, imagen_tienda)
            mongo.db.tienda.insert_one({'nombre': request.form['nombre'], 'direccion': request.form['direccion'], 'telefono': request.form['telefono'], 'usuario_email': g.user, 'nombre_imagen_tienda': imagen_tienda.filename})
                
        return render_template('/user/addTienda.html', nombreUsuario=nombre_usuario, msg=gettext("¡Tienda guardada correctamente!"), addTienda=True)

    if g.user:
        return render_template('/user/addTienda.html', nombreUsuario=nombre_usuario, addTienda=True)

    return redirect(url_for('login'))

# GET: Renders modifyTienda.html if user logged. POST: updates shop information.
@app.route('/users/<nombre_usuario>/<nombre_tienda>', methods=['GET', 'POST'])
def modifyTienda(nombre_usuario, nombre_tienda):
    if request.method == 'POST':
        usuario = mongo.db.usuarios.find_one({'email': g.user})
        tiendaAnt = mongo.db.tienda.find_one({'nombre': nombre_tienda})
        updates = {}

        if (request.form['nombre_a']):
            updates['nombre'] = request.form['nombre_a']
        else:
            updates['nombre'] =  tiendaAnt.get('nombre')     

        if (request.form['direccion_a']):
            updates['dir'] = request.form['direccion_a']
        else:
            updates['dir'] =  tiendaAnt.get('direccion') 

        if (request.form['telefono_a']):
            updates['tel'] = request.form['telefono_a']
        else:
            updates['tel'] =  tiendaAnt.get('telefono')

        if (request.files['imagen_a']):
            oldImage = mongo.db.fs.files.find_one({'filename': tiendaAnt.get('nombre_imagen_tienda')}) 
            mongo.db.fs.chunks.remove({'files_id': oldImage.get('_id')})
            mongo.db.fs.files.remove({'filename': tiendaAnt.get('nombre_imagen_tienda')})

            new_image = request.files['imagen_a']
            new_image.filename = 'imagen_' + updates['nombre']
            updates['img'] = new_image.filename
                
            mongo.save_file(new_image.filename, new_image)
        else:
            updates['img'] =  tiendaAnt.get('nombre_imagen_tienda')
        
        mongo.db.tienda.update_one({'nombre': nombre_tienda}, {"$set": { "nombre": updates.get('nombre'), "direccion": updates.get('dir'), "telefono": updates.get('tel'), "nombre_imagen_tienda": updates.get('img') }}, upsert=False)

        tienda = mongo.db.tienda.find_one({'nombre': updates.get('nombre')})

        return render_template('/user/modifyTienda.html', tienda=tienda, usuario=usuario, msg=gettext("¡Tienda actualizada correctamente!"), modifyTienda=True)

    if g.user:
        tienda = mongo.db.tienda.find_one({'nombre': nombre_tienda})
        usuario = mongo.db.usuarios.find_one({'email': g.user})
        return render_template('/user/modifyTienda.html', tienda=tienda, usuario=usuario, modifyTienda=True)

    return redirect(url_for('login'))

# GET: renders addProducts.html if user logged. POST: stores new product in MongoDB.
@app.route('/users/<nombre_usuario>/<nombre_tienda>/add_product', methods=['GET', 'POST'])
def addProducts(nombre_usuario, nombre_tienda):
    if request.method == 'POST':
        tienda = mongo.db.tienda.find_one({'nombre': nombre_tienda})
        usuario = mongo.db.usuarios.find_one({'email': g.user})

        if tienda.get('productos'):
            for producto in tienda.get('productos'):
                if producto.get('nombre') == request.form['nombre']:
                    return render_template('/user/addProducts.html', tienda=tienda, usuario=usuario, error=gettext("¡Ese producto ya existe!"), addProducts=True)

        if 'imagen_producto' in request.files:
            imagen_producto = request.files['imagen_producto']
            imagen_producto.filename = 'imagen_' + nombre_tienda + '_' + request.form['nombre']

            mongo.save_file(imagen_producto.filename, imagen_producto)
            mongo.db.tienda.update_one({'nombre': nombre_tienda}, {"$push": { 'productos': {"nombre": request.form['nombre'], "precio": request.form['precio'], "tam_ancho": request.form['ancho'], "tam_alto": request.form['alto'], "materiales": request.form['materiales'], "nombre_imagen_producto": imagen_producto.filename}}})
        
        tienda = mongo.db.tienda.find_one({'nombre': nombre_tienda})
        return render_template('/user/addProducts.html', tienda=tienda, usuario=usuario, msg=gettext("¡Producto guardado correctamente!"), addProducts=True)

    if g.user:
        tienda = mongo.db.tienda.find_one({'nombre': nombre_tienda})
        usuario = mongo.db.usuarios.find_one({'email': g.user})
        return render_template('/user/addProducts.html', tienda=tienda, usuario=usuario, addProducts=True)

    return redirect(url_for('login'))

# GET: renders modifyProduct.html if user logged. POST: updates product information.
@app.route('/users/<nombre_usuario>/<nombre_tienda>/<nombre_producto>', methods=['GET', 'POST'])
def modifyProduct(nombre_usuario, nombre_tienda, nombre_producto):
    if request.method == 'POST':
        usuario = mongo.db.usuarios.find_one({'email': g.user})
        tienda = mongo.db.tienda.find_one({'nombre': nombre_tienda})
        producto = None
        for p in tienda.get('productos'):
            if (p.get('nombre') == nombre_producto):
                producto = p
                break

        updates = {}
        if (request.form['nombre_a']):
            updates['nombre'] = request.form['nombre_a']
        else:
            updates['nombre'] =  producto.get('nombre')      

        if (request.form['precio_a']):
            updates['precio'] = request.form['precio_a']
        else:
            updates['precio'] =  producto.get('precio') 

        if (request.form['ancho_a']):
            updates['ancho'] = request.form['ancho_a']
        else:
            updates['ancho'] =  producto.get('tam_ancho')

        if (request.form['alto_a']):
            updates['alto'] = request.form['alto_a']
        else:
            updates['alto'] =  producto.get('tam_alto')

        if (request.form['materiales_a']):
            updates['materiales'] = request.form['materiales_a']
        else:
            updates['materiales'] =  producto.get('materiales')

        if (request.files['imagen_a']):
            oldImage = mongo.db.fs.files.find_one({'filename': producto.get('nombre_imagen_producto')})
            mongo.db.fs.chunks.remove({'files_id': oldImage.get('_id')})
            mongo.db.fs.files.remove({'filename': producto.get('nombre_imagen_producto')})

            new_image = request.files['imagen_a']
            new_image.filename = 'imagen_' + nombre_tienda + '_' + nombre_producto
            updates['img'] = new_image.filename
            
            mongo.save_file(new_image.filename, new_image)
        else:
            updates['img'] =  producto.get('nombre_imagen_producto')
        
        mongo.db.tienda.update_one({'nombre': nombre_tienda}, {"$pull": { 'productos': {"nombre": producto.get('nombre')}}})
        mongo.db.tienda.update_one({'nombre': nombre_tienda}, {"$push": { 'productos': {"nombre": updates.get('nombre'), "precio": updates.get('precio'), "tam_ancho": updates.get('ancho'), "tam_alto": updates.get('alto'), "materiales": updates.get('materiales'), "nombre_imagen_producto": updates.get('img')}}})    

        tienda = mongo.db.tienda.find_one({'nombre': nombre_tienda})
        if tienda.get('productos'):
            for producto in tienda.get('productos'):
                    if producto.get('nombre') == updates.get('nombre'):
                        return render_template('/user/modifyProduct.html', producto=producto, tienda=tienda, usuario=usuario, msg=gettext("¡Producto actualizado correctamente!"))

    if g.user:
        usuario = mongo.db.usuarios.find_one({'email': g.user})
        tienda = mongo.db.tienda.find_one({'nombre': nombre_tienda})
        producto = None
        for p in tienda.get('productos'):
            if (p.get('nombre') == nombre_producto):
                producto = p
                break
        
        return render_template('/user/modifyProduct.html', producto=producto, tienda=tienda, usuario=usuario)

    return redirect(url_for('login'))  

# Removes a product from a shop if user logged
@app.route('/users/<nombre_tienda>/remove_producto/<nombre_producto>')
def removeProducto(nombre_tienda, nombre_producto):
    if g.user:
        producto = None
        t = mongo.db.tienda.find_one({'nombre': nombre_tienda})
        for p in t.get('productos'):
            if p.get('nombre') == nombre_producto:
                producto = p

        mongo.db.tienda.update_one({'nombre': nombre_tienda}, {"$pull": { 'productos': {"nombre": producto.get('nombre')}}})
        
        oldImage = mongo.db.fs.files.find_one({'filename': producto.get('nombre_imagen_producto')})
        mongo.db.fs.chunks.remove({'files_id': oldImage.get('_id')})
        mongo.db.fs.files.remove({'filename': producto.get('nombre_imagen_producto')})

        usuario = mongo.db.usuarios.find_one({'email': g.user})
        return redirect(url_for('modifyTienda', nombre_usuario=usuario.get('name'), nombre_tienda=nombre_tienda))

    return redirect(url_for('login'))

# Removes a shop if user logged
@app.route('/users/remove_tienda/<nombre_tienda>')
def removeTienda(nombre_tienda):
    if g.user:
        tienda = mongo.db.tienda.find_one({'nombre': nombre_tienda})
        if tienda.get('productos'):
            for p in tienda.get('productos'):
                #mongo.db.tienda.update_one({'nombre': nombre_tienda}, {"$pull": { 'productos': {"nombre": p.get('nombre')}}})
                oldImage = mongo.db.fs.files.find_one({'filename': p.get('nombre_imagen_producto')})
        
                mongo.db.fs.chunks.remove({'files_id': oldImage.get('_id')})
                mongo.db.fs.files.remove({'filename': p.get('nombre_imagen_producto')})

        mongo.db.tienda.delete_one({'nombre': nombre_tienda})

        imagen_tienda = tienda.get('nombre_imagen_tienda')
        oldImage = mongo.db.fs.files.find_one({'filename': imagen_tienda})
        
        mongo.db.fs.chunks.remove({'files_id': oldImage.get('_id')})
        mongo.db.fs.files.remove({'filename': imagen_tienda})

        usuario = mongo.db.usuarios.find_one({'email': g.user})
        return redirect(url_for('user', nombre_usuario=usuario.get('name')))
    
    return redirect(url_for('login'))