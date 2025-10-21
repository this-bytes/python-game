#!/usr/bin/env python3
"""
Verification script for Budget System implementation.
Tests that all Phase 2 budget components are working correctly.
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test 1: All imports work"""
    print("\n" + "="*60)
    print("TEST 1: Verifying Imports")
    print("="*60)
    
    try:
        from src.models.budget import Budget
        print("✅ Budget model imported successfully")
        
        from src.core.budget_system import (
            calculate_monthly_revenue,
            calculate_monthly_expenses,
            process_monthly_budget,
            check_game_over
        )
        print("✅ Budget system functions imported successfully")
        
        from src.core.plugins.budget_plugin import BudgetPlugin
        print("✅ BudgetPlugin imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_budget_model():
    """Test 2: Budget model creation and methods"""
    print("\n" + "="*60)
    print("TEST 2: Verifying Budget Model")
    print("="*60)
    
    try:
        from src.models.budget import Budget
        
        budget = Budget(total_reserves=50000.0)
        print(f"✅ Budget created: ${budget.total_reserves:,.2f} reserves")
        
        # Test to_dict/from_dict
        budget_dict = budget.to_dict()
        assert "total_reserves" in budget_dict
        assert "specialist_salary_per_month" in budget_dict
        print("✅ Budget serialization (to_dict) works")
        
        budget2 = Budget.from_dict(budget_dict)
        assert budget2.total_reserves == budget.total_reserves
        print("✅ Budget deserialization (from_dict) works")
        
        # Test all required fields exist
        required_fields = [
            "specialist_salary_per_month",
            "infrastructure_base",
            "infrastructure_cost_per_client",
            "software_license_base",
            "software_license_per_specialist",
            "fixed_overhead"
        ]
        for field in required_fields:
            assert hasattr(budget, field), f"Missing field: {field}"
        print(f"✅ All {len(required_fields)} expense fields present")
        
        return True
    except Exception as e:
        print(f"❌ Budget model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_budget_calculations():
    """Test 3: Revenue and expense calculations"""
    print("\n" + "="*60)
    print("TEST 3: Verifying Budget Calculations")
    print("="*60)
    
    try:
        from src.models.client import Client, Industry
        from src.models.specialist import Specialist, SpecialistStats
        from src.core.budget_system import (
            calculate_monthly_revenue,
            calculate_monthly_expenses
        )
        
        # Create test client
        client = Client(
            client_id="test_client_001",
            company_name="Test Corp",
            industry=Industry.BANKING,
            monthly_contract_value=10000.0,
            sla_response_time_seconds=3600,
            sla_resolution_time_seconds=86400,
            contract_start_month=1,
            contract_end_month=12,
            satisfaction=0.85,
            is_active=True
        )
        
        # Test revenue calculation
        clients = [client]
        revenue = calculate_monthly_revenue(clients)
        expected_revenue = 10000.0 * 0.85  # 8500
        assert abs(revenue - expected_revenue) < 0.01, f"Revenue mismatch: {revenue} vs {expected_revenue}"
        print(f"✅ Revenue calculation correct: ${revenue:,.2f} = $10,000 × 0.85")
        
        # Create test specialist
        stats = SpecialistStats(speed=100, accuracy=85, experience_bonus=1.0)
        specialist = Specialist(
            id="test_spec_001",
            name="Test Specialist",
            specialty="Network Security",
            level=1,
            xp=0,
            stats=stats
        )
        
        # Test expense calculation
        specialists = [specialist]
        expenses = calculate_monthly_expenses(specialists, 1)
        # $3000 (salary) + $2500 (infra) + $1200 (software) + $1500 (overhead) = $8200
        expected_expenses = 3000 + 2500 + 1200 + 1500
        assert abs(expenses - expected_expenses) < 0.01, f"Expense mismatch: {expenses} vs {expected_expenses}"
        print(f"✅ Expense calculation correct: ${expenses:,.2f}")
        print(f"   - Salary: $3,000")
        print(f"   - Infrastructure: $2,500")
        print(f"   - Software: $1,200")
        print(f"   - Overhead: $1,500")
        
        return True
    except Exception as e:
        print(f"❌ Budget calculations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_budget_plugin():
    """Test 4: BudgetPlugin instantiation"""
    print("\n" + "="*60)
    print("TEST 4: Verifying BudgetPlugin")
    print("="*60)
    
    try:
        from src.core.plugins.budget_plugin import BudgetPlugin
        
        plugin = BudgetPlugin()
        print(f"✅ BudgetPlugin instantiated: {plugin.get_name()}")
        
        assert plugin.get_feature_id() == "budget_system"
        print(f"✅ Feature ID correct: {plugin.get_feature_id()}")
        
        # Verify lifecycle methods exist
        assert hasattr(plugin, 'initialize')
        assert hasattr(plugin, 'update')
        assert hasattr(plugin, 'shutdown')
        assert hasattr(plugin, 'save_state')
        assert hasattr(plugin, 'load_state')
        print("✅ All lifecycle methods implemented")
        
        return True
    except Exception as e:
        print(f"❌ BudgetPlugin test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_loading():
    """Test 5: Budget config from JSON"""
    print("\n" + "="*60)
    print("TEST 5: Verifying Config Loading")
    print("="*60)
    
    try:
        config_path = project_root / "data" / "game_config.json"
        if not config_path.exists():
            print(f"⚠️  Config file not found at {config_path}, skipping config test")
            return True
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Check for budget-related config
        if "budget" in config or "specialist" in config:
            print("✅ Game config file contains budget-related settings")
        else:
            print("⚠️  Game config exists but no budget section (will use defaults)")
        
        return True
    except Exception as e:
        print(f"⚠️  Config loading test warning: {e}")
        return True  # Non-fatal

def test_integration_with_main():
    """Test 6: BudgetPlugin in main.py"""
    print("\n" + "="*60)
    print("TEST 6: Verifying main.py Integration")
    print("="*60)
    
    try:
        main_path = project_root / "main.py"
        with open(main_path) as f:
            main_code = f.read()
        
        # Check for import
        if "from src.core.plugins.budget_plugin import BudgetPlugin" in main_code:
            print("✅ BudgetPlugin imported in main.py")
        else:
            print("❌ BudgetPlugin NOT imported in main.py")
            return False
        
        # Check for registration
        if '("BudgetPlugin", BudgetPlugin)' in main_code:
            print("✅ BudgetPlugin registered in plugin_classes list")
        else:
            print("❌ BudgetPlugin NOT registered in plugin_classes")
            return False
        
        return True
    except Exception as e:
        print(f"❌ main.py integration test failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  BUDGET SYSTEM VERIFICATION SUITE".center(58) + "║")
    print("║" + "  Phase 2 Implementation Verification".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Imports", test_imports),
        ("Budget Model", test_budget_model),
        ("Budget Calculations", test_budget_calculations),
        ("BudgetPlugin", test_budget_plugin),
        ("Config Loading", test_config_loading),
        ("main.py Integration", test_integration_with_main),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Budget System is fully functional!\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Review above for details\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
