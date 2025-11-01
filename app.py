from flask import Flask, render_template, request, redirect, url_for, session
import database as db
import os

app = Flask(__name__)
app.secret_key = 'ctrl-coffee-secret-key-123'

@app.route('/')
def index():
    """Home page - show coffee menu"""
    categories = db.get_coffee_types_by_category()
    cart_count = len(session.get('cart', []))
    
    # Show database stats on home page
    stats = db.get_database_stats()
    
    return render_template('index.html', 
                         categories=categories, 
                         cart_count=cart_count,
                         stats=stats)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Add item to shopping cart"""
    if 'cart' not in session:
        session['cart'] = []
    
    coffee_type_id = int(request.form['coffee_type_id'])
    quantity = int(request.form['quantity'])
    
    # Check if item already in cart
    cart = session['cart']
    item_found = False
    for item in cart:
        if item['coffee_type_id'] == coffee_type_id:
            item['quantity'] += quantity
            item_found = True
            break
    
    if not item_found:
        cart.append({
            'coffee_type_id': coffee_type_id,
            'quantity': quantity
        })
    
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    """View shopping cart"""
    cart_items = []
    total = 0
    
    if 'cart' in session and session['cart']:
        conn = db.get_db_connection()
        for item in session['cart']:
            coffee = conn.execute(
                'SELECT * FROM coffee_types WHERE id = ?', 
                (item['coffee_type_id'],)
            ).fetchone()
            
            if coffee:
                item_total = coffee['price'] * item['quantity']
                cart_items.append({
                    'id': coffee['id'],
                    'name': coffee['name'],
                    'price': coffee['price'],
                    'quantity': item['quantity'],
                    'total': item_total,
                    'category': coffee['category']
                })
                total += item_total
        conn.close()
    
    cart_count = len(session.get('cart', []))
    return render_template('cart.html', cart_items=cart_items, total=total, cart_count=cart_count)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Update cart item quantities"""
    if 'cart' not in session:
        return redirect(url_for('view_cart'))
    
    cart = session['cart']
    coffee_type_id = int(request.form['coffee_type_id'])
    quantity = int(request.form['quantity'])
    
    if quantity <= 0:
        # Remove item if quantity is 0 or less
        cart = [item for item in cart if item['coffee_type_id'] != coffee_type_id]
    else:
        # Update quantity
        for item in cart:
            if item['coffee_type_id'] == coffee_type_id:
                item['quantity'] = quantity
                break
    
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/remove_from_cart/<int:coffee_type_id>')
def remove_from_cart(coffee_type_id):
    """Remove item from cart"""
    if 'cart' in session:
        cart = session['cart']
        cart = [item for item in cart if item['coffee_type_id'] != coffee_type_id]
        session['cart'] = cart
    
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    """Process checkout and create order"""
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('index'))
    
    customer_name = request.form['customer_name']
    if not customer_name.strip():
        return "Please enter your name"
    
    try:
        order_id = db.place_order(customer_name, session['cart'])
        
        # Get order details for the summary
        order_details = db.get_order_details(order_id)
        
        # Clear cart after successful order
        session.pop('cart', None)
        
        # Show simple order summary
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Order Complete - ctrl+coffee</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f8f4e9; margin: 0; padding: 2rem; }}
                .container {{ max-width: 600px; margin: 2rem auto; background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(139, 69, 19, 0.1); }}
                .success {{ color: #10b981; font-size: 3rem; text-align: center; margin-bottom: 1rem; }}
                .order-info {{ background: #f0f8ff; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; }}
                .item {{ display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #eee; }}
                .total {{ font-size: 1.3rem; font-weight: bold; text-align: right; margin-top: 1rem; padding-top: 1rem; border-top: 2px solid #8B4513; }}
                .btn {{ background: #8B4513; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 8px; display: inline-block; margin: 0.5rem; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">✓</div>
                <h1 style="text-align: center; color: #8B4513;">Order Complete!</h1>
                <p style="text-align: center;">Thank you, {customer_name}!</p>
                
                <div class="order-info">
                    <h3>Order Summary</h3>
                    <p><strong>Order #:</strong> {order_id}</p>
                    <p><strong>Date:</strong> {order_details['order']['order_date']}</p>
                    
                    <h4>Items:</h4>
                    {''.join(f'<div class="item"><span>{item["coffee_name"]} x {item["quantity"]}</span><span>${item["price"] * item["quantity"]:.2f}</span></div>' for item in order_details['items'])}
                    
                    <div class="total">
                        Total: ${order_details['order']['total_amount']:.2f}
                    </div>
                </div>
                
                <p style="text-align: center; background: #ffe6e6; padding: 1rem; border-radius: 8px;">
                    <strong>Please proceed to the counter to pay and collect your order.</strong>
                </p>
                
                <div style="text-align: center; margin-top: 2rem;">
                    <a href="/" class="btn">Back to Home</a>
                    <a href="/menu" class="btn" style="background: #6b7280;">Order More</a>
                </div>
            </div>
        </body>
        </html>
        '''
        
    except Exception as e:
        return f"Error placing order: {str(e)}"

@app.route('/orders')
def orders():
    """Show all orders"""
    all_orders = db.get_all_orders()
    return render_template('orders.html', orders=all_orders)

@app.route('/menu')
def menu():
    """Show coffee menu"""
    categories = db.get_coffee_types_by_category()
    cart_count = len(session.get('cart', []))
    return render_template('menu.html', categories=categories, cart_count=cart_count)

@app.route('/admin/remove_order', methods=['GET', 'POST'])
def remove_order():
    """Web interface to remove orders"""
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        conn = db.get_db_connection()
        
        # First delete order items, then orders
        conn.execute('DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE customer_name = ?)', (customer_name,))
        conn.execute('DELETE FROM orders WHERE customer_name = ?', (customer_name,))
        conn.commit()
        conn.close()
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Order Removed - ctrl+coffee</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f8f4e9; margin: 0; padding: 2rem; }}
                .container {{ max-width: 600px; margin: 2rem auto; background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(139, 69, 19, 0.1); text-align: center; }}
                .success {{ color: #10b981; font-size: 4rem; margin-bottom: 1rem; }}
                .btn {{ background: #8B4513; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 8px; display: inline-block; margin: 0.5rem; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">✓</div>
                <h1 style="color: #8B4513;">Orders Removed</h1>
                <p>All orders for <strong>{customer_name}</strong> have been successfully removed.</p>
                <div style="margin-top: 2rem;">
                    <a href="/admin/remove_order" class="btn">Remove More Orders</a>
                    <a href="/" class="btn" style="background: #6b7280;">Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        '''
    
    return render_template('remove_order.html')

if __name__ == '__main__':
    # Initialize database only if it doesn't exist
    db.init_db()
    
    # Show current database stats
    stats = db.get_database_stats()
    print(f"Database Stats: {stats['orders_count']} orders, {stats['order_items_count']} items, ${stats['total_revenue']:.2f} total revenue")
    
    # Run the application
    print("Starting ctrl+coffee app...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)