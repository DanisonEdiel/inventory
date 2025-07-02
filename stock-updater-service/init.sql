-- Create tables for the inventory database

-- Create suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    supplier_id UUID REFERENCES suppliers(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_products_supplier_id ON products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);

-- Insert some sample data
INSERT INTO suppliers (id, name, contact_email) VALUES 
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'ABC Suppliers', 'contact@abcsuppliers.com'),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'XYZ Distributors', 'info@xyzdist.com');

INSERT INTO products (id, name, stock, supplier_id, is_active) VALUES 
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'Product A', 100, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a44', 'Product B', 50, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE),
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a55', 'Product C', 75, 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', TRUE),
    ('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a66', 'Product D', 0, 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', FALSE);
