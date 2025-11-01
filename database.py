import sqlite3
import os

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect('coffee_orders.db')
    conn.row_factory = sqlite3.Row
    return conn

def database_exists():
    """Check if database file exists"""
    return os.path.exists('coffee_orders.db')

def tables_exist():
    """Check if all required tables exist"""
    conn = get_db_connection()
    try:
        # Check if all three tables exist
        tables = ['coffee_types', 'orders', 'order_items']
        for table in tables:
            result = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
            if not result:
                return False
        return True
    finally:
        conn.close()

def init_db():
    """Initialize the database only if it doesn't exist or tables are missing"""
    # Check if database file exists and tables are present
    if database_exists() and tables_exist():
        print("Database already exists. Skipping initialization.")
        return
    
    print("Initializing database...")
    conn = get_db_connection()
    
    # Read and execute schema
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def get_coffee_types():
    """Get all available coffee types"""
    conn = get_db_connection()
    coffee_types = conn.execute('SELECT * FROM coffee_types ORDER BY category, name').fetchall()
    conn.close()
    return coffee_types

def get_coffee_types_by_category():
    """Get coffee types grouped by category"""
    conn = get_db_connection()
    coffee_types = conn.execute('SELECT * FROM coffee_types ORDER BY category, name').fetchall()
    conn.close()
    
    # Group by category
    categories = {}
    for item in coffee_types:
        category = item['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(dict(item))
    
    return categories

def place_order(customer_name, order_items):
    """Place a new order with multiple items"""
    conn = get_db_connection()
    
    try:
        # Calculate total amount
        total_amount = 0
        for item in order_items:
            coffee_type_id = item['coffee_type_id']
            quantity = item['quantity']
            
            # Get coffee price
            coffee = conn.execute(
                'SELECT price FROM coffee_types WHERE id = ?', 
                (coffee_type_id,)
            ).fetchone()
            
            if coffee:
                total_amount += coffee['price'] * quantity
            else:
                raise ValueError(f"Invalid coffee type ID: {coffee_type_id}")
        
        # Create order
        cursor = conn.execute(
            'INSERT INTO orders (customer_name, total_amount) VALUES (?, ?)',
            (customer_name, total_amount)
        )
        order_id = cursor.lastrowid
        
        # Add order items
        for item in order_items:
            coffee_type_id = item['coffee_type_id']
            quantity = item['quantity']
            
            # Get coffee price
            coffee = conn.execute(
                'SELECT price FROM coffee_types WHERE id = ?', 
                (coffee_type_id,)
            ).fetchone()
            
            conn.execute(
                'INSERT INTO order_items (order_id, coffee_type_id, quantity, price) VALUES (?, ?, ?, ?)',
                (order_id, coffee_type_id, quantity, coffee['price'])
            )
        
        conn.commit()
        return order_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_order_details(order_id):
    """Get complete order details including items"""
    conn = get_db_connection()
    
    # Get order basic info
    order_result = conn.execute(
        'SELECT * FROM orders WHERE id = ?', 
        (order_id,)
    ).fetchone()
    
    if not order_result:
        conn.close()
        return None
    
    # Convert order to dictionary
    order = {
        'id': order_result['id'],
        'customer_name': order_result['customer_name'],
        'order_date': order_result['order_date'],
        'total_amount': order_result['total_amount'],
        'status': order_result['status']
    }
    
    # Get order items with coffee details
    items_result = conn.execute('''
        SELECT oi.*, ct.name as coffee_name, ct.category as category
        FROM order_items oi 
        JOIN coffee_types ct ON oi.coffee_type_id = ct.id 
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    
    # Convert items to list of dictionaries
    items = []
    for row in items_result:
        items.append({
            'id': row['id'],
            'coffee_type_id': row['coffee_type_id'],
            'quantity': row['quantity'],
            'price': row['price'],
            'coffee_name': row['coffee_name'],
            'category': row['category']
        })
    
    conn.close()
    
    return {
        'order': order,
        'items': items
    }

def get_all_orders():
    """Get all orders with item information"""
    conn = get_db_connection()
    
    # Get all orders
    orders_result = conn.execute('''
        SELECT o.*, 
               GROUP_CONCAT(ct.name || ' (x' || oi.quantity || ')') as items_description,
               COUNT(oi.id) as item_count
        FROM orders o 
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN coffee_types ct ON oi.coffee_type_id = ct.id
        GROUP BY o.id
        ORDER BY o.order_date DESC
    ''').fetchall()
    
    # Convert to list of dictionaries
    orders = []
    for row in orders_result:
        orders.append({
            'id': row['id'],
            'customer_name': row['customer_name'],
            'order_date': row['order_date'],
            'total_amount': row['total_amount'],
            'status': row['status'],
            'items_description': row['items_description'],
            'item_count': row['item_count']
        })
    
    conn.close()
    return orders

def get_database_stats():
    """Get database statistics"""
    conn = get_db_connection()
    
    stats = {
        'coffee_types_count': conn.execute('SELECT COUNT(*) FROM coffee_types').fetchone()[0],
        'orders_count': conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0],
        'order_items_count': conn.execute('SELECT COUNT(*) FROM order_items').fetchone()[0],
        'total_revenue': conn.execute('SELECT SUM(total_amount) FROM orders').fetchone()[0] or 0
    }
    
    conn.close()
    return stats