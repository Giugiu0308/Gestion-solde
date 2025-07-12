#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Payroll Management System
Tests all CRUD operations, balance calculations, and data integrity
"""

import requests
import json
import sys
from datetime import datetime
import time

# Load backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("ERROR: Could not get REACT_APP_BACKEND_URL from frontend/.env")
    sys.exit(1)

API_URL = f"{BASE_URL}/api"
print(f"Testing API at: {API_URL}")

# Test data
test_workers = []
test_transactions = []

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"TESTING: {test_name}")
    print(f"{'='*60}")

def print_test_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")

def test_api_health():
    """Test if API is accessible"""
    print_test_header("API Health Check")
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        success = response.status_code == 200
        print_test_result("API Health Check", success, f"Status: {response.status_code}")
        if success:
            print(f"   Response: {response.json()}")
        return success
    except Exception as e:
        print_test_result("API Health Check", False, f"Error: {e}")
        return False

def test_create_worker():
    """Test creating workers"""
    print_test_header("Worker Creation Tests")
    
    workers_data = [
        {"name": "Jean Dupont", "position": "Maçon", "phone": "+33123456789"},
        {"name": "Marie Martin", "position": "Électricienne", "phone": "+33987654321"}
    ]
    
    all_success = True
    for i, worker_data in enumerate(workers_data):
        try:
            response = requests.post(f"{API_URL}/workers", json=worker_data, timeout=10)
            success = response.status_code == 200
            
            if success:
                worker = response.json()
                test_workers.append(worker)
                print_test_result(f"Create Worker {i+1}", True, f"ID: {worker['id']}, Name: {worker['name']}")
            else:
                print_test_result(f"Create Worker {i+1}", False, f"Status: {response.status_code}")
                all_success = False
                
        except Exception as e:
            print_test_result(f"Create Worker {i+1}", False, f"Error: {e}")
            all_success = False
    
    return all_success

def test_get_workers():
    """Test getting all workers"""
    print_test_header("Get All Workers Test")
    
    try:
        response = requests.get(f"{API_URL}/workers", timeout=10)
        success = response.status_code == 200
        
        if success:
            workers = response.json()
            print_test_result("Get All Workers", True, f"Found {len(workers)} workers")
            for worker in workers:
                print(f"   - {worker['name']} ({worker['position']}) - ID: {worker['id']}")
        else:
            print_test_result("Get All Workers", False, f"Status: {response.status_code}")
            
        return success
    except Exception as e:
        print_test_result("Get All Workers", False, f"Error: {e}")
        return False

def test_get_worker_by_id():
    """Test getting specific worker by ID"""
    print_test_header("Get Worker by ID Test")
    
    if not test_workers:
        print_test_result("Get Worker by ID", False, "No test workers available")
        return False
    
    try:
        worker_id = test_workers[0]['id']
        response = requests.get(f"{API_URL}/workers/{worker_id}", timeout=10)
        success = response.status_code == 200
        
        if success:
            worker = response.json()
            print_test_result("Get Worker by ID", True, f"Found: {worker['name']}")
        else:
            print_test_result("Get Worker by ID", False, f"Status: {response.status_code}")
            
        return success
    except Exception as e:
        print_test_result("Get Worker by ID", False, f"Error: {e}")
        return False

def test_create_transactions():
    """Test creating transactions"""
    print_test_header("Transaction Creation Tests")
    
    if not test_workers:
        print_test_result("Create Transactions", False, "No test workers available")
        return False
    
    transactions_data = [
        {"worker_id": test_workers[0]['id'], "type": "due", "amount": 1500.0, "description": "Travail semaine 1"},
        {"worker_id": test_workers[0]['id'], "type": "paid", "amount": 800.0, "description": "Acompte"},
        {"worker_id": test_workers[1]['id'], "type": "due", "amount": 2000.0, "description": "Installation électrique"},
        {"worker_id": test_workers[1]['id'], "type": "paid", "amount": 2000.0, "description": "Paiement complet"}
    ]
    
    all_success = True
    for i, transaction_data in enumerate(transactions_data):
        try:
            response = requests.post(f"{API_URL}/transactions", json=transaction_data, timeout=10)
            success = response.status_code == 200
            
            if success:
                transaction = response.json()
                test_transactions.append(transaction)
                print_test_result(f"Create Transaction {i+1}", True, 
                                f"Type: {transaction['type']}, Amount: {transaction['amount']}")
            else:
                print_test_result(f"Create Transaction {i+1}", False, f"Status: {response.status_code}")
                all_success = False
                
        except Exception as e:
            print_test_result(f"Create Transaction {i+1}", False, f"Error: {e}")
            all_success = False
    
    return all_success

def test_get_transactions():
    """Test getting all transactions"""
    print_test_header("Get All Transactions Test")
    
    try:
        response = requests.get(f"{API_URL}/transactions", timeout=10)
        success = response.status_code == 200
        
        if success:
            transactions = response.json()
            print_test_result("Get All Transactions", True, f"Found {len(transactions)} transactions")
            for transaction in transactions:
                print(f"   - {transaction['type']}: {transaction['amount']} - {transaction['description']}")
        else:
            print_test_result("Get All Transactions", False, f"Status: {response.status_code}")
            
        return success
    except Exception as e:
        print_test_result("Get All Transactions", False, f"Error: {e}")
        return False

def test_get_worker_transactions():
    """Test getting transactions for specific worker"""
    print_test_header("Get Worker Transactions Test")
    
    if not test_workers:
        print_test_result("Get Worker Transactions", False, "No test workers available")
        return False
    
    try:
        worker_id = test_workers[0]['id']
        response = requests.get(f"{API_URL}/workers/{worker_id}/transactions", timeout=10)
        success = response.status_code == 200
        
        if success:
            transactions = response.json()
            print_test_result("Get Worker Transactions", True, f"Found {len(transactions)} transactions for worker")
            for transaction in transactions:
                print(f"   - {transaction['type']}: {transaction['amount']}")
        else:
            print_test_result("Get Worker Transactions", False, f"Status: {response.status_code}")
            
        return success
    except Exception as e:
        print_test_result("Get Worker Transactions", False, f"Error: {e}")
        return False

def test_worker_balance():
    """Test getting worker balance"""
    print_test_header("Worker Balance Calculation Test")
    
    if not test_workers:
        print_test_result("Worker Balance", False, "No test workers available")
        return False
    
    all_success = True
    for i, worker in enumerate(test_workers):
        try:
            response = requests.get(f"{API_URL}/workers/{worker['id']}/balance", timeout=10)
            success = response.status_code == 200
            
            if success:
                balance_data = response.json()
                total_due = balance_data['total_due']
                total_paid = balance_data['total_paid']
                balance = balance_data['balance']
                expected_balance = total_due - total_paid
                
                balance_correct = abs(balance - expected_balance) < 0.01
                
                print_test_result(f"Worker {i+1} Balance", balance_correct, 
                                f"Due: {total_due}, Paid: {total_paid}, Balance: {balance}")
                
                if not balance_correct:
                    print(f"   ERROR: Expected balance {expected_balance}, got {balance}")
                    all_success = False
            else:
                print_test_result(f"Worker {i+1} Balance", False, f"Status: {response.status_code}")
                all_success = False
                
        except Exception as e:
            print_test_result(f"Worker {i+1} Balance", False, f"Error: {e}")
            all_success = False
    
    return all_success

def test_all_workers_balances():
    """Test getting all workers balances"""
    print_test_header("All Workers Balances Test")
    
    try:
        response = requests.get(f"{API_URL}/workers-balances", timeout=10)
        success = response.status_code == 200
        
        if success:
            balances = response.json()
            print_test_result("All Workers Balances", True, f"Found {len(balances)} worker balances")
            for balance_data in balances:
                worker_name = balance_data['worker']['name']
                balance = balance_data['balance']
                print(f"   - {worker_name}: Balance = {balance}")
        else:
            print_test_result("All Workers Balances", False, f"Status: {response.status_code}")
            
        return success
    except Exception as e:
        print_test_result("All Workers Balances", False, f"Error: {e}")
        return False

def test_data_integrity():
    """Test data integrity scenarios"""
    print_test_header("Data Integrity Tests")
    
    all_success = True
    
    # Test 1: Create transaction for non-existent worker
    try:
        fake_worker_id = "non-existent-worker-id"
        transaction_data = {
            "worker_id": fake_worker_id,
            "type": "due",
            "amount": 100.0,
            "description": "Test transaction"
        }
        response = requests.post(f"{API_URL}/transactions", json=transaction_data, timeout=10)
        success = response.status_code == 404
        print_test_result("Transaction for non-existent worker", success, 
                         f"Expected 404, got {response.status_code}")
        if not success:
            all_success = False
    except Exception as e:
        print_test_result("Transaction for non-existent worker", False, f"Error: {e}")
        all_success = False
    
    # Test 2: Get balance for non-existent worker
    try:
        fake_worker_id = "non-existent-worker-id"
        response = requests.get(f"{API_URL}/workers/{fake_worker_id}/balance", timeout=10)
        success = response.status_code == 404
        print_test_result("Balance for non-existent worker", success, 
                         f"Expected 404, got {response.status_code}")
        if not success:
            all_success = False
    except Exception as e:
        print_test_result("Balance for non-existent worker", False, f"Error: {e}")
        all_success = False
    
    return all_success

def test_edge_cases():
    """Test edge cases for balance calculations"""
    print_test_header("Edge Cases Tests")
    
    # Create a worker for edge case testing
    edge_worker_data = {"name": "Test Edge", "position": "Testeur", "phone": "+33111111111"}
    
    try:
        response = requests.post(f"{API_URL}/workers", json=edge_worker_data, timeout=10)
        if response.status_code != 200:
            print_test_result("Edge Cases Setup", False, "Could not create test worker")
            return False
        
        edge_worker = response.json()
        worker_id = edge_worker['id']
        
        all_success = True
        
        # Test 1: Worker with only "due" transactions (positive balance)
        due_transaction = {
            "worker_id": worker_id,
            "type": "due",
            "amount": 500.0,
            "description": "Only due amount"
        }
        response = requests.post(f"{API_URL}/transactions", json=due_transaction, timeout=10)
        if response.status_code == 200:
            # Check balance
            response = requests.get(f"{API_URL}/workers/{worker_id}/balance", timeout=10)
            if response.status_code == 200:
                balance_data = response.json()
                success = balance_data['balance'] == 500.0 and balance_data['total_paid'] == 0.0
                print_test_result("Only due transactions", success, 
                                f"Balance: {balance_data['balance']}")
                if not success:
                    all_success = False
            else:
                all_success = False
        else:
            all_success = False
        
        # Test 2: Add paid transaction to make zero balance
        paid_transaction = {
            "worker_id": worker_id,
            "type": "paid",
            "amount": 500.0,
            "description": "Full payment"
        }
        response = requests.post(f"{API_URL}/transactions", json=paid_transaction, timeout=10)
        if response.status_code == 200:
            # Check balance
            response = requests.get(f"{API_URL}/workers/{worker_id}/balance", timeout=10)
            if response.status_code == 200:
                balance_data = response.json()
                success = abs(balance_data['balance']) < 0.01
                print_test_result("Zero balance", success, 
                                f"Balance: {balance_data['balance']}")
                if not success:
                    all_success = False
            else:
                all_success = False
        else:
            all_success = False
        
        # Test 3: Add more paid to create negative balance
        overpaid_transaction = {
            "worker_id": worker_id,
            "type": "paid",
            "amount": 200.0,
            "description": "Overpayment"
        }
        response = requests.post(f"{API_URL}/transactions", json=overpaid_transaction, timeout=10)
        if response.status_code == 200:
            # Check balance
            response = requests.get(f"{API_URL}/workers/{worker_id}/balance", timeout=10)
            if response.status_code == 200:
                balance_data = response.json()
                success = balance_data['balance'] == -200.0
                print_test_result("Negative balance", success, 
                                f"Balance: {balance_data['balance']}")
                if not success:
                    all_success = False
            else:
                all_success = False
        else:
            all_success = False
        
        # Cleanup: Delete the edge test worker
        requests.delete(f"{API_URL}/workers/{worker_id}", timeout=10)
        
        return all_success
        
    except Exception as e:
        print_test_result("Edge Cases", False, f"Error: {e}")
        return False

def test_delete_transaction():
    """Test deleting transactions"""
    print_test_header("Delete Transaction Test")
    
    if not test_transactions:
        print_test_result("Delete Transaction", False, "No test transactions available")
        return False
    
    try:
        transaction_id = test_transactions[0]['id']
        response = requests.delete(f"{API_URL}/transactions/{transaction_id}", timeout=10)
        success = response.status_code == 200
        
        if success:
            # Verify transaction is deleted
            response = requests.get(f"{API_URL}/transactions", timeout=10)
            if response.status_code == 200:
                transactions = response.json()
                deleted = not any(t['id'] == transaction_id for t in transactions)
                print_test_result("Delete Transaction", deleted, 
                                f"Transaction {transaction_id} deleted")
                return deleted
        else:
            print_test_result("Delete Transaction", False, f"Status: {response.status_code}")
            
        return success
    except Exception as e:
        print_test_result("Delete Transaction", False, f"Error: {e}")
        return False

def test_delete_worker():
    """Test deleting worker and associated transactions"""
    print_test_header("Delete Worker Test")
    
    if not test_workers:
        print_test_result("Delete Worker", False, "No test workers available")
        return False
    
    try:
        worker_id = test_workers[-1]['id']  # Delete the last worker
        worker_name = test_workers[-1]['name']
        
        # First, check how many transactions this worker has
        response = requests.get(f"{API_URL}/workers/{worker_id}/transactions", timeout=10)
        initial_transactions = len(response.json()) if response.status_code == 200 else 0
        
        # Delete the worker
        response = requests.delete(f"{API_URL}/workers/{worker_id}", timeout=10)
        success = response.status_code == 200
        
        if success:
            # Verify worker is deleted
            response = requests.get(f"{API_URL}/workers/{worker_id}", timeout=10)
            worker_deleted = response.status_code == 404
            
            # Verify worker's transactions are also deleted
            response = requests.get(f"{API_URL}/workers/{worker_id}/transactions", timeout=10)
            transactions_deleted = response.status_code == 404 or len(response.json()) == 0
            
            overall_success = worker_deleted and transactions_deleted
            print_test_result("Delete Worker", overall_success, 
                            f"Worker {worker_name} and {initial_transactions} transactions deleted")
            return overall_success
        else:
            print_test_result("Delete Worker", False, f"Status: {response.status_code}")
            
        return success
    except Exception as e:
        print_test_result("Delete Worker", False, f"Error: {e}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print(f"\n{'='*80}")
    print("PAYROLL MANAGEMENT API COMPREHENSIVE TEST SUITE")
    print(f"{'='*80}")
    print(f"Testing API at: {API_URL}")
    print(f"Timestamp: {datetime.now()}")
    
    test_results = []
    
    # Run all tests
    test_results.append(("API Health Check", test_api_health()))
    test_results.append(("Worker Creation", test_create_worker()))
    test_results.append(("Get All Workers", test_get_workers()))
    test_results.append(("Get Worker by ID", test_get_worker_by_id()))
    test_results.append(("Transaction Creation", test_create_transactions()))
    test_results.append(("Get All Transactions", test_get_transactions()))
    test_results.append(("Get Worker Transactions", test_get_worker_transactions()))
    test_results.append(("Worker Balance Calculation", test_worker_balance()))
    test_results.append(("All Workers Balances", test_all_workers_balances()))
    test_results.append(("Data Integrity", test_data_integrity()))
    test_results.append(("Edge Cases", test_edge_cases()))
    test_results.append(("Delete Transaction", test_delete_transaction()))
    test_results.append(("Delete Worker", test_delete_worker()))
    
    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! The payroll management API is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the detailed output above.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)