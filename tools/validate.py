#!/usr/bin/env python3
"""
CLI Validation Tools for AI Guardrails System
DMT Protocol: Done Means Taught - Comprehensive validation required
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core_logic.parser import StatementParser
from core_logic.reasoner import SimpleLogicEngine

def validate_parser():
    """Validate StatementParser functionality"""
    print("🔍 Validating StatementParser...")
    parser = StatementParser()
    
    test_cases = [
        ("The cat is black", {"subject": "the cat", "object": "black", "negated": False}),
        ("The cat is not black", {"subject": "the cat", "object": "black", "negated": True}),
        ("John is tall", {"subject": "john", "object": "tall", "negated": False}),
        ("It is running", None),  # Should fail to parse
        ("", None),  # Empty string
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected) in enumerate(test_cases):
        print(f"\n  Test {i+1}: '{input_text}'")
        result = parser.parse(input_text)
        
        if result == expected:
            print(f"    ✅ PASS: {result}")
            passed += 1
        else:
            print(f"    ❌ FAIL: Expected {expected}, got {result}")
            failed += 1
    
    print(f"\n📊 Parser Validation Results:")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Success Rate: {(passed/(passed+failed))*100:.1f}%")
    
    return failed == 0

def validate_reasoner():
    """Validate SimpleLogicEngine functionality"""
    print("\n🧠 Validating SimpleLogicEngine...")
    engine = SimpleLogicEngine()
    
    # Test basic functionality
    print("\n  Testing basic fact addition...")
    engine.process_statement("The cat is black")
    assert len(engine.knowledge_base) == 1
    
    print("  Testing duplicate detection...")
    engine.process_statement("The cat is black")
    assert len(engine.knowledge_base) == 1  # Should not add duplicate
    
    print("  Testing contradiction detection...")
    import io
    import sys
    captured_output = io.StringIO()
    sys.stdout = captured_output
    engine.process_statement("The cat is not black")
    sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    assert "CONTRADICTION DETECTED" in output
    assert len(engine.knowledge_base) == 1  # Should not add contradiction
    
    print("  Testing multiple facts...")
    engine.process_statement("The dog is brown")
    assert len(engine.knowledge_base) == 2
    
    print("    ✅ All reasoner tests passed")
    return True

def validate_integration():
    """Validate integration between parser and reasoner"""
    print("\n🔗 Validating Integration...")
    parser = StatementParser()
    engine = SimpleLogicEngine()
    
    # Test that parser output works with reasoner
    test_statements = [
        "The sky is blue",
        "The grass is green", 
        "The sky is not blue",  # Contradiction
        "The sun is yellow"
    ]
    
    print("\n  Processing statements through integrated system...")
    for stmt in test_statements:
        print(f"    Processing: '{stmt}'")
        parsed = parser.parse(stmt)
        if parsed:
            # Convert parsed format to reasoner format
            text_form = f"{parsed['subject']} is {'not ' if parsed['negated'] else ''}{parsed['object']}"
            engine.process_statement(text_form)
        else:
            print(f"    ⚠️  Could not parse: '{stmt}'")
    
    print(f"  Final knowledge base size: {len(engine.knowledge_base)}")
    print("    ✅ Integration test completed")
    return True

def run_full_validation():
    """Run complete validation suite"""
    print("🚀 AI Guardrails - Full Validation Suite")
    print("=" * 50)
    
    results = []
    
    try:
        results.append(("Parser", validate_parser()))
    except Exception as e:
        print(f"❌ Parser validation failed: {e}")
        results.append(("Parser", False))
    
    try:
        results.append(("Reasoner", validate_reasoner()))
    except Exception as e:
        print(f"❌ Reasoner validation failed: {e}")
        results.append(("Reasoner", False))
    
    try:
        results.append(("Integration", validate_integration()))
    except Exception as e:
        print(f"❌ Integration validation failed: {e}")
        results.append(("Integration", False))
    
    print("\n" + "=" * 50)
    print("📋 FINAL VALIDATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for component, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {component:12} : {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("System is ready for development.")
    else:
        print("⚠️  SOME VALIDATIONS FAILED!")
        print("Review failures before proceeding.")
    
    return all_passed

def interactive_mode():
    """Interactive validation mode"""
    print("🎮 Interactive Validation Mode")
    print("Type statements to test, 'quit' to exit")
    
    parser = StatementParser()
    engine = SimpleLogicEngine()
    
    while True:
        try:
            statement = input("\n> ").strip()
            if statement.lower() in ['quit', 'exit', 'q']:
                break
            
            if not statement:
                continue
            
            print(f"\nParsing: '{statement}'")
            parsed = parser.parse(statement)
            
            if parsed:
                print(f"Parsed result: {parsed}")
                text_form = f"{parsed['subject']} is {'not ' if parsed['negated'] else ''}{parsed['object']}"
                print(f"Processing: '{text_form}'")
                engine.process_statement(text_form)
            else:
                print("❌ Could not parse statement")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\nFinal knowledge base ({len(engine.knowledge_base)} facts):")
    for i, fact in enumerate(engine.knowledge_base, 1):
        neg_text = " not" if fact['negated'] else ""
        print(f"  {i}. {fact['subject'].capitalize()}{neg_text} {fact['object']}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            interactive_mode()
        elif sys.argv[1] == "parser":
            validate_parser()
        elif sys.argv[1] == "reasoner":
            validate_reasoner()
        elif sys.argv[1] == "integration":
            validate_integration()
        else:
            print("Usage: python validate.py [interactive|parser|reasoner|integration]")
    else:
        run_full_validation()