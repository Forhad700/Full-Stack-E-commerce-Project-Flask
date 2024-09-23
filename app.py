import json
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random key
login_manager = LoginManager(app)

# Load product data from JSON file
try:
    with open('products.json') as f:
        products_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    products_data = []  # Handle the case where the file is not found or is invalid
    print(f"Error loading products: {e}")

class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = {}
user_carts = {}  # Initialize the user_carts dictionary

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    brand = request.args.get('brand')

    products = products_data

    if brand:
        products = [p for p in products if p.get('brand') == brand]

    total_products = len(products)
    products = products[(page - 1) * 9:page * 9]

    return render_template('index.html', products=products, total_products=total_products, page=page, brand=brand)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = next((p for p in products_data if p['id'] == product_id), None)
    return render_template('product.html', product=product)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username not in users:
            users[username] = User(username)
        login_user(users[username])
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if username not in users:
            users[username] = User(username)
            flash("Registration successful!", "success")
            return redirect('/login')
        else:
            flash("Username already exists.", "danger")
    return render_template('register.html')

@app.route('/cart')
@login_required
def cart():
    user_cart = user_carts.get(current_user.id, [])
    total_price = sum(float(item['price'].replace('$', '').replace(',', '')) for item in user_cart)
    return render_template('cart.html', cart=user_cart, total_price=total_price, username=current_user.id)

@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    if current_user.id in user_carts:
        # Find the product in the user's cart
        user_cart = user_carts[current_user.id]
        product_to_remove = next((item for item in user_cart if item['id'] == product_id), None)
        if product_to_remove:
            user_cart.remove(product_to_remove)  # Remove the product from the cart
            flash("Product removed from cart!", "success")
        else:
            flash("Product not found in cart.", "danger")
    return redirect('/cart')

@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = next((p for p in products_data if p['id'] == product_id), None)
    if product:
        if current_user.id not in user_carts:
            user_carts[current_user.id] = []
        user_carts[current_user.id].append(product)
        flash("Product added to cart!", "success")
    else:
        flash("Product not found.", "danger")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
