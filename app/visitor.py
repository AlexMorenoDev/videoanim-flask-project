from app import app, mongo, redirect, url_for, render_template, request, session, g

# Renders index.html
@app.route('/')
def index():
    if g.user: 
        usuario = mongo.db.usuarios.find_one({'email': g.user})
        return redirect(url_for('user', nombre_usuario=usuario.get('name')))

    tiendas = mongo.db.tienda.find({})
    owner = get_remote_ip()
    return render_template('/visitor/index.html', tiendas=tiendas, index=True, owner=owner)

# Renders listProducts.html
@app.route('/<nombre_tienda>')
def listProducts(nombre_tienda):
    tienda = mongo.db.tienda.find_one({'nombre': nombre_tienda})
    
    productos = {}
    if tienda.get('productos'):
        productos = tienda.get('productos')

    return render_template('/visitor/listProducts.html', tienda=tienda, productos=productos)

# Renders showProduct.html
@app.route('/<nombre_tienda>/<nombre_producto>')
def showProduct(nombre_tienda, nombre_producto):
    tienda = mongo.db.tienda.find_one({'nombre': nombre_tienda})
    for producto in tienda.get('productos'):
        if producto.get('nombre') == nombre_producto:
            return render_template('/visitor/showProduct.html', nombreTienda=nombre_tienda, producto=producto, show_product=True)

# Function that returns true if the request is from an owner (owner´s IP are stored in whitelist.txt) or false if not
def get_remote_ip():
    # IMPORTANT: if you are not using a proxy or load balancer uncomment next line
    # remote_ip = request.remote_addr
    
    remote_ip = request.headers['X-Forwarded-For']

    owner = False
    with open('whitelist.txt') as fp:
        line = fp.readline()
        while line:
            if '\n' in line:
                l = line[:-1]
                line = l

            if line == remote_ip:
                owner = True
                break
                
            line = fp.readline()
    
    # ip_list = mongo.db.whitelist.find({})
    # for ip in ip_list:
    #     if ip.get('ip') == remote_ip:
    #         owner = True
    #         break

    return owner