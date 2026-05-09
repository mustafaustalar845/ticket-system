import pytest
import sys
import os

if __name__ == "__main__":
    print("="*60)
    print(" TICKET SYSTEM - ALL E2E TESTS STARTING ")
    print("="*60)
    print("\nConnecting to http://localhost:8000 and testing:")
    print(" 1. Creating New Customers, Employees, and Admins.")
    print(" 2. Simulating 20 customers getting tickets concurrently.")
    print(" 3. Simulating employees calling and completing tickets.")
    print(" 4. Checking admin statistics and logs.\n")
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    exit_code = pytest.main(["-v", "-s", test_dir])
    
    if exit_code == 0:
        print("\n" + "="*60)
        print(" ALL TESTS PASSED SUCCESSFULLY! The system is working perfectly.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print(" SOME TESTS FAILED. Please review the output above.")
        print("="*60)

    
    sys.exit(exit_code)
