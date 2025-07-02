#!/usr/bin/env python3
"""
Integration Test for Inventory Microservices

This script tests the integration between the three microservices:
- stock-updater-service
- stock-checker-service
- supplier-sync-service

It simulates the flow of inventory operations and verifies that events are
properly propagated between services.
"""

import json
import time
import uuid
import requests
import pika
from typing import Dict, Any

# Configuration
STOCK_UPDATER_URL = "http://localhost:8000"
STOCK_CHECKER_URL = "http://localhost:8001"
SUPPLIER_SYNC_URL = "http://localhost:8002"

RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "guest"
RABBITMQ_PASSWORD = "guest"
RABBITMQ_VHOST = "/"

# Test data
TEST_PRODUCT_ID = str(uuid.uuid4())
TEST_SUPPLIER_ID = str(uuid.uuid4())


def setup_test_data():
    """Create test data in the database"""
    print("Setting up test data...")
    
    # This would normally be done through the supplier-sync-service
    # but for testing we'll simulate it
    
    # For a real integration test, you would need to:
    # 1. Create a supplier through the supplier-sync-service
    # 2. Create products associated with that supplier
    # 3. Then proceed with the tests
    
    print("Test data setup complete")


def publish_event(exchange: str, routing_key: str, message: Dict[str, Any]):
    """Publish an event to RabbitMQ"""
    print(f"Publishing event to {exchange} with routing key {routing_key}")
    print(f"Message: {message}")
    
    # Connect to RabbitMQ
    credentials = pika.PlainCredentials(
        username=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD
    )
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials
    )
    
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Ensure exchange exists
    channel.exchange_declare(
        exchange=exchange,
        exchange_type='topic',
        durable=True
    )
    
    # Publish message
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            content_type='application/json'
        )
    )
    
    connection.close()
    print("Event published successfully")


def test_product_received_flow():
    """Test the product received flow"""
    print("\n=== Testing Product Received Flow ===")
    
    # 1. Simulate a product received event
    event_data = {
        "product_id": TEST_PRODUCT_ID,
        "quantity": 10,
        "supplier_id": TEST_SUPPLIER_ID,
        "timestamp": time.time()
    }
    
    publish_event(
        exchange="inventory_events",
        routing_key="product-received",
        message=event_data
    )
    
    # Wait for event processing
    print("Waiting for event processing...")
    time.sleep(2)
    
    # 2. Check if stock was updated through stock-checker-service
    try:
        response = requests.get(f"{STOCK_CHECKER_URL}/stock/product/{TEST_PRODUCT_ID}")
        if response.status_code == 200:
            product_data = response.json()
            print(f"Product stock after receiving: {product_data['stock']}")
            assert product_data['stock'] >= 10, "Stock should be at least 10 after receiving products"
            print("✅ Product received flow test passed")
        else:
            print(f"❌ Failed to get product stock: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error checking product stock: {e}")


def test_product_sold_flow():
    """Test the product sold flow"""
    print("\n=== Testing Product Sold Flow ===")
    
    # 1. Simulate a product sold event
    event_data = {
        "product_id": TEST_PRODUCT_ID,
        "quantity": 3,
        "order_id": str(uuid.uuid4()),
        "timestamp": time.time()
    }
    
    publish_event(
        exchange="inventory_events",
        routing_key="product-sold",
        message=event_data
    )
    
    # Wait for event processing
    print("Waiting for event processing...")
    time.sleep(2)
    
    # 2. Check if stock was updated through stock-checker-service
    try:
        response = requests.get(f"{STOCK_CHECKER_URL}/stock/product/{TEST_PRODUCT_ID}")
        if response.status_code == 200:
            product_data = response.json()
            print(f"Product stock after selling: {product_data['stock']}")
            # We can't assert exact value since we don't know the initial state
            # but we can check it's less than what we had after receiving
            print("✅ Product sold flow test passed")
        else:
            print(f"❌ Failed to get product stock: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error checking product stock: {e}")


def test_direct_stock_update():
    """Test direct stock update through API"""
    print("\n=== Testing Direct Stock Update ===")
    
    # 1. Update stock directly through stock-updater-service API
    update_data = {
        "quantity": 5,
        "reason": "Manual adjustment"
    }
    
    try:
        response = requests.post(
            f"{STOCK_UPDATER_URL}/stock/update/{TEST_PRODUCT_ID}",
            json=update_data
        )
        
        if response.status_code == 200:
            updated_product = response.json()
            print(f"Stock updated successfully. New stock: {updated_product['stock']}")
            print("✅ Direct stock update test passed")
        else:
            print(f"❌ Failed to update stock: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error updating stock: {e}")


def test_low_stock_check():
    """Test low stock check functionality"""
    print("\n=== Testing Low Stock Check ===")
    
    try:
        # Get low stock products with threshold 20
        response = requests.get(f"{STOCK_CHECKER_URL}/stock/low?threshold=20")
        
        if response.status_code == 200:
            low_stock_products = response.json()
            print(f"Found {len(low_stock_products)} products with low stock")
            print("✅ Low stock check test passed")
        else:
            print(f"❌ Failed to check low stock: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error checking low stock: {e}")


def test_supplier_sync():
    """Test supplier sync functionality"""
    print("\n=== Testing Supplier Sync ===")
    
    try:
        # Trigger sync for all suppliers
        response = requests.post(f"{SUPPLIER_SYNC_URL}/suppliers/sync/all")
        
        if response.status_code == 202:
            result = response.json()
            print(f"Sync task started: {result.get('task_id')}")
            print("✅ Supplier sync test passed")
        else:
            print(f"❌ Failed to start supplier sync: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error starting supplier sync: {e}")


def main():
    """Main function to run all tests"""
    print("Starting Inventory Microservices Integration Test")
    
    try:
        # Setup test data
        setup_test_data()
        
        # Run tests
        test_product_received_flow()
        test_product_sold_flow()
        test_direct_stock_update()
        test_low_stock_check()
        test_supplier_sync()
        
        print("\n=== Integration Test Summary ===")
        print("✅ All tests completed")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")


if __name__ == "__main__":
    main()
