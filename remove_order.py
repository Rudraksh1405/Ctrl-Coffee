import database as db

def remove_orders_by_name(customer_name):
    """Remove all orders for a specific customer name"""
    conn = db.get_db_connection()
    
    try:
        # First, check if any orders exist for this customer
        orders = conn.execute(
            'SELECT * FROM orders WHERE customer_name = ?', 
            (customer_name,)
        ).fetchall()
        
        if not orders:
            print(f"No orders found for customer: {customer_name}")
            return False
        
        print(f"Found {len(orders)} order(s) for {customer_name}:")
        for order in orders:
            coffee = conn.execute(
                'SELECT name FROM coffee_types WHERE id = ?', 
                (order['coffee_type_id'],)
            ).fetchone()
            coffee_name = coffee['name'] if coffee else "Unknown"
            print(f"  - Order ID: {order['id']}, Coffee: {coffee_name}, Quantity: {order['quantity']}, Total: ${order['total_price']}")
        
        # Confirm deletion
        confirm = input(f"\nAre you sure you want to delete all {len(orders)} order(s) for {customer_name}? (y/n): ")
        
        if confirm.lower() == 'y':
            # Delete the orders
            conn.execute(
                'DELETE FROM orders WHERE customer_name = ?', 
                (customer_name,)
            )
            conn.commit()
            print(f"Successfully deleted {len(orders)} order(s) for {customer_name}")
            return True
        else:
            print("Deletion cancelled.")
            return False
            
    except Exception as e:
        print(f"Error removing orders: {e}")
        return False
    finally:
        conn.close()

def remove_single_order(order_id):
    """Remove a specific order by order ID"""
    conn = db.get_db_connection()
    
    try:
        # Check if order exists
        order = conn.execute(
            'SELECT * FROM orders WHERE id = ?', 
            (order_id,)
        ).fetchone()
        
        if not order:
            print(f"No order found with ID: {order_id}")
            return False
        
        coffee = conn.execute(
            'SELECT name FROM coffee_types WHERE id = ?', 
            (order['coffee_type_id'],)
        ).fetchone()
        coffee_name = coffee['name'] if coffee else "Unknown"
        
        print(f"Order found:")
        print(f"  - Order ID: {order['id']}")
        print(f"  - Customer: {order['customer_name']}")
        print(f"  - Coffee: {coffee_name}")
        print(f"  - Quantity: {order['quantity']}")
        print(f"  - Total: ${order['total_price']}")
        
        # Confirm deletion
        confirm = input(f"\nAre you sure you want to delete this order? (y/n): ")
        
        if confirm.lower() == 'y':
            # Delete the order
            conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
            conn.commit()
            print(f"Successfully deleted order ID: {order_id}")
            return True
        else:
            print("Deletion cancelled.")
            return False
            
    except Exception as e:
        print(f"Error removing order: {e}")
        return False
    finally:
        conn.close()

def show_all_orders():
    """Display all current orders"""
    conn = db.get_db_connection()
    orders = conn.execute('''
        SELECT o.*, c.name as coffee_name 
        FROM orders o 
        JOIN coffee_types c ON o.coffee_type_id = c.id 
        ORDER BY o.order_date DESC
    ''').fetchall()
    conn.close()
    
    if not orders:
        print("No orders found in the database.")
        return
    
    print("\nCurrent Orders:")
    print("-" * 80)
    for order in orders:
        print(f"ID: {order['id']} | Customer: {order['customer_name']:15} | Coffee: {order['coffee_name']:12} | Qty: {order['quantity']:2} | Total: ${order['total_price']:6.2f} | Date: {order['order_date']}")
    print("-" * 80)

def main():
    """Main function to run the order removal utility"""
    print("=" * 50)
    print("    ctrl+coffee - Order Management Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Remove orders by customer name")
        print("2. Remove single order by ID")
        print("3. View all orders")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            customer_name = input("Enter customer name to remove orders: ").strip()
            if customer_name:
                remove_orders_by_name(customer_name)
            else:
                print("Customer name cannot be empty.")
                
        elif choice == '2':
            try:
                order_id = int(input("Enter order ID to remove: ").strip())
                remove_single_order(order_id)
            except ValueError:
                print("Please enter a valid order ID (number).")
                
        elif choice == '3':
            show_all_orders()
            
        elif choice == '4':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()