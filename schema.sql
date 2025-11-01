-- Create tables for the coffee ordering system
CREATE TABLE IF NOT EXISTS coffee_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    coffee_type_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (coffee_type_id) REFERENCES coffee_types (id)
);

-- Insert sample coffee drinks
INSERT OR IGNORE INTO coffee_types (name, price, description, category) VALUES
('Espresso', 3.50, 'Strong and concentrated coffee', 'Coffee'),
('Cappuccino', 4.50, 'Espresso with steamed milk foam', 'Coffee'),
('Latte', 4.75, 'Espresso with lots of steamed milk', 'Coffee'),
('Americano', 3.75, 'Espresso with hot water', 'Coffee'),
('Mocha', 5.25, 'Chocolate-flavored latte', 'Coffee'),
('Cold Brew', 4.25, 'Smooth cold brewed coffee', 'Coffee'),
('Flat White', 4.50, 'Velvety microfoam over espresso', 'Coffee'),
('Caramel Macchiato', 5.50, 'Vanilla, milk, espresso, caramel', 'Coffee'),

-- Starbucks-style drinks
('Pumpkin Spice Latte', 5.75, 'Seasonal favorite with pumpkin spice', 'Specialty'),
('Matcha Green Tea Latte', 5.25, 'Sweetened matcha with steamed milk', 'Tea'),
('Chai Tea Latte', 4.95, 'Spiced black tea with steamed milk', 'Tea'),
('Iced White Chocolate Mocha', 5.95, 'White chocolate with espresso over ice', 'Cold Drinks'),
('Strawberry Açai Refresher', 4.75, 'Sweet strawberry with green coffee extract', 'Cold Drinks'),
('Mango Dragonfruit Lemonade', 4.95, 'Tropical dragonfruit with lemonade', 'Cold Drinks'),

-- Bakery items
('Croissant', 3.25, 'Buttery French pastry', 'Bakery'),
('Chocolate Chip Cookie', 2.50, 'Fresh baked with chocolate chips', 'Bakery'),
('Blueberry Muffin', 3.75, 'Moist muffin with fresh blueberries', 'Bakery'),
('Cinnamon Roll', 4.25, 'Warm cinnamon swirl with icing', 'Bakery'),
('Almond Croissant', 4.50, 'Croissant filled with almond cream', 'Bakery'),

-- Desserts
('Tiramisu', 6.50, 'Classic Italian coffee-flavored dessert', 'Desserts'),
('New York Cheesecake', 6.25, 'Creamy cheesecake with graham crust', 'Desserts'),
('Chocolate Lava Cake', 5.95, 'Warm cake with molten chocolate center', 'Desserts'),
('Macarons (4pc)', 7.50, 'Assorted French macarons', 'Desserts'),
('Seasonal Fruit Tart', 5.75, 'Pastry cream in tart shell with fresh fruit', 'Desserts');