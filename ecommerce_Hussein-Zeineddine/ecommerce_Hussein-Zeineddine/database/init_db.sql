-- database/init_db.sql
 -- Enable UUID extension for unique identifiers (optional but recommended)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: customers

CREATE TABLE IF NOT EXISTS customers (id SERIAL PRIMARY KEY,
                                                        full_name VARCHAR(255) NOT NULL,
                                                                               username VARCHAR(50) UNIQUE NOT NULL,
                                                                                                           hashed_password VARCHAR(255) NOT NULL,
                                                                                                                                        age INTEGER NOT NULL,
                                                                                                                                                    address TEXT NOT NULL,
                                                                                                                                                                 gender VARCHAR(20) NOT NULL,
                                                                                                                                                                                    marital_status VARCHAR(20) NOT NULL,
                                                                                                                                                                                                               wallet_balance FLOAT DEFAULT 0.0,
                                                                                                                                                                                                                                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                                                                                                                                                                                                                                         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- Table: inventory

CREATE TABLE IF NOT EXISTS inventory (id SERIAL PRIMARY KEY,
                                                        name VARCHAR(255) NOT NULL,
                                                                          category VARCHAR(50) NOT NULL CHECK (category IN ('food',
                                                                                                                            'clothes',
                                                                                                                            'accessories',
                                                                                                                            'electronics')), price FLOAT NOT NULL CHECK (price >= 0), description TEXT, stock_count INTEGER NOT NULL CHECK (stock_count >= 0), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                                                                                                                                                                                                                                                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- Table: sales

CREATE TABLE IF NOT EXISTS sales
    (id SERIAL PRIMARY KEY,
                       customer_id INTEGER NOT NULL,
                                           item_id INTEGER NOT NULL,
                                                           sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                                                       amount FLOAT NOT NULL CHECK (amount >= 0),
     FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
     FOREIGN KEY (item_id) REFERENCES inventory(id) ON DELETE CASCADE);

-- Table: reviews

CREATE TABLE IF NOT EXISTS reviews
    (id SERIAL PRIMARY KEY,
                       product_id INTEGER NOT NULL,
                                          customer_id INTEGER NOT NULL,
                                                              rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5), comment TEXT, is_flagged BOOLEAN DEFAULT FALSE,
                                                                                                                                                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                                                                                                                                                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE);

-- Indexes for performance optimization

CREATE INDEX IF NOT EXISTS idx_customers_username ON customers(username);


CREATE INDEX IF NOT EXISTS idx_inventory_category ON inventory(category);


CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON sales(customer_id);


CREATE INDEX IF NOT EXISTS idx_sales_item_id ON sales(item_id);


CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id);


CREATE INDEX IF NOT EXISTS idx_reviews_customer_id ON reviews(customer_id);

