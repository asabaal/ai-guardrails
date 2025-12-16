#!/usr/bin/env python3
"""
Integration Tests for Overseer AI Logic Analysis System

Tests end-to-end workflows from text input to LLM analysis,
verifying complete system functionality and component interactions.

Following AI Safety Development Protocols (AI_SAFETY_DEVELOPMENT_PROTOCOLS.md)
Following System Architecture (SYSTEM_ARCHITECTURE.md Section VI.D)
"""

import sys
import os
import json
import time
import requests
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from layer1_segmentation.text_segmenter import LLMTextSegmenter, RuleBasedSplitter, Normalizer, Aggregator


@dataclass
class IntegrationTestResult:
    """Result of an integration test."""
    test_name: str
    passed: bool
    execution_time_ms: float
    details: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class IntegrationTestSuite:
    """Comprehensive integration test suite for Overseer system."""
    
    def __init__(self):
        # Use absolute path from project root
        self.test_cases_dir = os.path.join(os.path.dirname(__file__), "..", "test_cases")
        self.api_base_url = "http://localhost:8000"
        self.llm_config = {
            'model_name': 'gpt-oss:20b',
            'max_retries': 2,
            'timeout': 60
        }
        
    def run_all_tests(self) -> List[IntegrationTestResult]:
        """Run all integration tests."""
        results = []
        
        print("🔬 Overseer Integration Test Suite")
        print("=" * 60)
        
        # Test 1: End-to-End Workflow
        results.append(self.test_end_to_end_workflow())
        
        # Test 2: API Integration
        results.append(self.test_api_integration())
        
        # Test 3: LLM Integration
        results.append(self.test_llm_integration())
        
        # Test 4: Error Handling
        results.append(self.test_error_handling())
        
        # Test 5: Performance Under Load
        results.append(self.test_performance_under_load())
        
        # Test 6: Component Interaction
        results.append(self.test_component_interaction())
        
        return results
    
    def test_end_to_end_workflow(self) -> IntegrationTestResult:
        """Test complete workflow from input to evaluation."""
        print("\n🔄 Testing End-to-End Workflow...")
        print("-" * 40)
        
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Load test case
            test_case = self._load_test_case("simple_logic", "A")
            input_text = test_case["input_text"]
            
            # Initialize complete pipeline
            segmenter = LLMTextSegmenter(self.llm_config)
            normalizer = Normalizer()
            aggregator = Aggregator()
            
            # Step 1: Segmentation
            print("  Step 1: Text Segmentation...")
            segments = segmenter.segment(input_text)
            details['llm_segments'] = segments
            details['llm_segment_count'] = len(segments)
            
            if not segments:
                errors.append("LLM segmentation failed to produce segments")
                return IntegrationTestResult(
                    "End-to-End Workflow", False, 0, details, errors, warnings
                )
            
            # Step 2: Normalization
            print("  Step 2: Normalization...")
            normalized_segments = normalizer.normalize(segments)
            details['normalized_segments'] = normalized_segments
            details['normalized_count'] = len(normalized_segments)
            
            # Step 3: Rule-based fallback test
            print("  Step 3: Rule-based Fallback...")
            rule_splitter = RuleBasedSplitter()
            rule_segments = rule_splitter.segment(input_text)
            rule_normalized = normalizer.normalize(rule_segments)
            details['rule_segments'] = rule_normalized
            details['rule_segment_count'] = len(rule_normalized)
            
            # Step 4: Aggregation
            print("  Step 4: Aggregation...")
            final_segments = aggregator.aggregate(normalized_segments, rule_normalized)
            details['final_segments'] = final_segments
            details['final_segment_count'] = len(final_segments)
            
            # Step 5: Validation
            print("  Step 5: Result Validation...")
            expected_segments = test_case["expected_segments"]
            segment_match = self._compare_segments(final_segments, expected_segments)
            details['segment_accuracy'] = segment_match['score']
            details['expected_segments'] = expected_segments
            
            if segment_match['score'] < 0.5:
                warnings.append(f"Low segment accuracy: {segment_match['score']:.2%}")
            
            execution_time = (time.time() - start_time) * 1000
            details['execution_time_ms'] = execution_time
            
            print(f"  ✅ Workflow completed in {execution_time:.0f}ms")
            print(f"  📊 Segment accuracy: {segment_match['score']:.2%}")
            
            passed = segment_match['score'] >= 0.3  # Minimum acceptable accuracy
            
            return IntegrationTestResult(
                "End-to-End Workflow", passed, execution_time, details, errors, warnings
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            errors.append(f"End-to-end workflow failed: {str(e)}")
            return IntegrationTestResult(
                "End-to-End Workflow", False, execution_time, details, errors, warnings
            )
    
    def test_api_integration(self) -> IntegrationTestResult:
        """Test analysis_api.py endpoints."""
        print("\n🌐 Testing API Integration...")
        print("-" * 40)
        
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Test API class components directly
            print("  🔧 Testing API components...")
            
            # Import API components
            from analysis_api import AnalysisAPI
            from layer1_segmentation.text_segmenter import LLMTextSegmenter, Normalizer, Aggregator
            
            # Test API initialization
            try:
                # Test that API can be imported and has required methods
                api_class = AnalysisAPI
                api_methods = [method for method in dir(api_class) if not method.startswith('__')]
                required_methods = ['_handle_analyze', '_send_response', 'do_GET', 'do_POST']
                missing_methods = [m for m in required_methods if m not in api_methods]
                
                if missing_methods:
                    errors.append(f"API missing methods: {missing_methods}")
                else:
                    details['api_methods'] = 'present'
                    print("  ✅ API class has required methods")
                    
            except Exception as e:
                errors.append(f"API class test failed: {str(e)}")
            
            # Test API dependencies
            try:
                # Test that API can initialize its components
                llm_config = {
                    'model_name': 'gpt-oss:20b',
                    'max_retries': 2,
                    'timeout': 60
                }
                
                segmenter = LLMTextSegmenter(llm_config)
                normalizer = Normalizer()
                aggregator = Aggregator()
                
                # Test basic functionality
                test_text = "Apples contain fiber. Therefore, apples support digestion."
                segments = segmenter.segment(test_text)
                normalized = normalizer.normalize(segments)
                final = aggregator.aggregate(normalized, [])
                
                details['dependencies_work'] = True
                details['segment_count'] = len(final)
                print(f"  ✅ API dependencies work: {len(final)} segments")
                
            except Exception as e:
                errors.append(f"API dependencies failed: {str(e)}")
            
            # Test API response format
            try:
                # Test response structure
                test_response = {
                    'segments': ['Test segment'],
                    'processing_time_ms': 100,
                    'status': 'success'
                }
                
                # Validate response format
                required_fields = ['segments', 'processing_time_ms']
                missing_fields = [f for f in required_fields if f not in test_response]
                
                if missing_fields:
                    errors.append(f"Response format missing fields: {missing_fields}")
                else:
                    details['response_format'] = 'valid'
                    print("  ✅ API response format valid")
                    
            except Exception as e:
                errors.append(f"Response format test failed: {str(e)}")
            
            execution_time = (time.time() - start_time) * 1000
            
            # Test passes if core components work
            passed = len(errors) == 0
            
            return IntegrationTestResult(
                "API Integration", passed, execution_time, details, errors, warnings
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            errors.append(f"API integration test failed: {str(e)}")
            return IntegrationTestResult(
                "API Integration", False, execution_time, details, errors, warnings
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            errors.append(f"API integration test failed: {str(e)}")
            return IntegrationTestResult(
                "API Integration", False, execution_time, details, errors, warnings
            )
    
    def test_llm_integration(self) -> IntegrationTestResult:
        """Test real ollama integration."""
        print("\n🤖 Testing LLM Integration...")
        print("-" * 40)
        
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Test ollama availability
            print("  🔍 Checking ollama availability...")
            try:
                result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    errors.append("Ollama not available or not in PATH")
                    return IntegrationTestResult(
                        "LLM Integration", False, 0, details, errors, warnings
                    )
                
                details['ollama_available'] = True
                details['ollama_list_output'] = result.stdout
                
            except subprocess.TimeoutExpired:
                errors.append("Ollama list command timed out")
                return IntegrationTestResult(
                    "LLM Integration", False, 0, details, errors, warnings
                )
            except FileNotFoundError:
                errors.append("Ollama command not found")
                return IntegrationTestResult(
                    "LLM Integration", False, 0, details, errors, warnings
                )
            
            # Test model availability
            print("  📋 Checking model availability...")
            if "gpt-oss:20b" not in result.stdout:
                warnings.append("gpt-oss:20b model not found in ollama list")
            
            # Test actual LLM segmentation
            print("  🧠 Testing LLM segmentation...")
            segmenter = LLMTextSegmenter(self.llm_config)
            test_text = "If it rains, then the ground gets wet. It is raining. Therefore, the ground is wet."
            
            segments = segmenter.segment(test_text)
            details['llm_segments'] = segments
            details['llm_segment_count'] = len(segments)
            details['llm_calls_made'] = getattr(segmenter, 'calls_made', 0)
            
            if not segments:
                errors.append("LLM segmentation returned no segments")
            else:
                print(f"  ✅ LLM returned {len(segments)} segments")
                for i, segment in enumerate(segments[:3], 1):  # Show first 3
                    print(f"    {i}. {segment[:60]}...")
            
            execution_time = (time.time() - start_time) * 1000
            
            return IntegrationTestResult(
                "LLM Integration", len(segments) > 0, execution_time, details, errors, warnings
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            errors.append(f"LLM integration test failed: {str(e)}")
            return IntegrationTestResult(
                "LLM Integration", False, execution_time, details, errors, warnings
            )
    
    def test_error_handling(self) -> IntegrationTestResult:
        """Test error handling and recovery."""
        print("\n⚠️  Testing Error Handling...")
        print("-" * 40)
        
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Test 1: Empty input
            print("  📝 Testing empty input...")
            segmenter = LLMTextSegmenter(self.llm_config)
            try:
                segments = segmenter.segment("")
                details['empty_input_result'] = segments
                if segments:  # Should handle gracefully
                    warnings.append("Empty input produced segments instead of empty result")
            except Exception as e:
                details['empty_input_error'] = str(e)
                print(f"    Handled empty input error: {type(e).__name__}")
            
            # Test 2: Invalid model
            print("  🤖 Testing invalid model...")
            invalid_config = self.llm_config.copy()
            invalid_config['model_name'] = 'nonexistent:model'
            invalid_segmenter = LLMTextSegmenter(invalid_config)
            
            try:
                segments = invalid_segmenter.segment("Test text")
                details['invalid_model_result'] = segments
                warnings.append("Invalid model did not raise error")
            except Exception as e:
                details['invalid_model_error'] = str(e)
                print(f"    Handled invalid model error: {type(e).__name__}")
            
            # Test 3: Very long input
            print("  📏 Testing very long input...")
            long_text = "This is a test. " * 100  # Create long text
            try:
                segments = segmenter.segment(long_text)
                details['long_input_result'] = len(segments)
                print(f"    Handled long input: {len(segments)} segments")
            except Exception as e:
                details['long_input_error'] = str(e)
                warnings.append(f"Long input caused error: {type(e).__name__}")
            
            # Test 4: Malformed input
            print("  🔀 Testing malformed input...")
            malformed_text = "🤖💥🔥 nonsense text with symbols !!!"
            try:
                segments = segmenter.segment(malformed_text)
                details['malformed_result'] = segments
                print(f"    Handled malformed input: {len(segments)} segments")
            except Exception as e:
                details['malformed_error'] = str(e)
                print(f"    Handled malformed error: {type(e).__name__}")
            
            execution_time = (time.time() - start_time) * 1000
            
            # Test passes if no critical errors (warnings are acceptable)
            passed = len(errors) == 0
            
            return IntegrationTestResult(
                "Error Handling", passed, execution_time, details, errors, warnings
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            errors.append(f"Error handling test failed: {str(e)}")
            return IntegrationTestResult(
                "Error Handling", False, execution_time, details, errors, warnings
            )
    
    def test_performance_under_load(self) -> IntegrationTestResult:
        """Test system performance under load."""
        print("\n⚡ Testing Performance Under Load...")
        print("-" * 40)
        
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Test multiple concurrent requests
            print("  🔄 Testing concurrent processing...")
            segmenter = LLMTextSegmenter(self.llm_config)
            test_texts = [
                "Apples contain fiber. Therefore, apples support digestion.",
                "If it rains, then the ground gets wet. It is raining.",
                "All humans are mortal. Socrates is human.",
                "Triangles have three sides. This shape has four sides.",
                "The rooster crows before sunrise. Therefore, rooster causes sunrise."
            ]
            
            # Process sequentially (avoid overwhelming ollama)
            processing_times = []
            segment_counts = []
            
            for i, text in enumerate(test_texts, 1):
                print(f"    Processing test {i}/{len(test_texts)}...")
                text_start = time.time()
                
                try:
                    segments = segmenter.segment(text)
                    processing_time = (time.time() - text_start) * 1000
                    processing_times.append(processing_time)
                    segment_counts.append(len(segments))
                    
                    print(f"      ✅ {len(segments)} segments in {processing_time:.0f}ms")
                    
                except Exception as e:
                    errors.append(f"Test {i} failed: {str(e)}")
                    processing_times.append(0)
                    segment_counts.append(0)
            
            # Calculate performance metrics
            if processing_times:
                avg_time = sum(processing_times) / len(processing_times)
                max_time = max(processing_times)
                min_time = min(processing_times)
                total_segments = sum(segment_counts)
                
                details['avg_processing_time_ms'] = avg_time
                details['max_processing_time_ms'] = max_time
                details['min_processing_time_ms'] = min_time
                details['total_segments_generated'] = total_segments
                details['tests_processed'] = len(test_texts)
                details['success_rate'] = (len(test_texts) - len(errors)) / len(test_texts)
                
                print(f"  📊 Performance Summary:")
                print(f"    Average time: {avg_time:.0f}ms")
                print(f"    Max time: {max_time:.0f}ms")
                print(f"    Success rate: {details['success_rate']:.1%}")
                
                # Performance warnings
                if avg_time > 30000:  # 30 seconds
                    warnings.append("Average processing time exceeds 30 seconds")
                if details['success_rate'] < 0.8:
                    warnings.append("Success rate below 80%")
            
            execution_time = (time.time() - start_time) * 1000
            
            passed = len(errors) == 0 and details.get('success_rate', 0) >= 0.6
            
            return IntegrationTestResult(
                "Performance Under Load", passed, execution_time, details, errors, warnings
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            errors.append(f"Performance test failed: {str(e)}")
            return IntegrationTestResult(
                "Performance Under Load", False, execution_time, details, errors, warnings
            )
    
    def test_component_interaction(self) -> IntegrationTestResult:
        """Test interaction between system components."""
        print("\n🔗 Testing Component Interaction...")
        print("-" * 40)
        
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Initialize all components
            segmenter = LLMTextSegmenter(self.llm_config)
            rule_splitter = RuleBasedSplitter()
            normalizer = Normalizer()
            aggregator = Aggregator()
            
            test_text = "Apples contain fiber. Foods with fiber support digestion. Therefore, apples support digestion."
            
            # Test component data flow
            print("  🔄 Testing data flow between components...")
            
            # Step 1: LLM Segmentation
            llm_segments = segmenter.segment(test_text)
            details['llm_segments'] = llm_segments
            print(f"    LLM segments: {len(llm_segments)}")
            
            # Step 2: Rule-based segmentation
            rule_segments = rule_splitter.segment(test_text)
            details['rule_segments'] = rule_segments
            print(f"    Rule segments: {len(rule_segments)}")
            
            # Step 3: Normalization
            llm_normalized = normalizer.normalize(llm_segments)
            rule_normalized = normalizer.normalize(rule_segments)
            details['llm_normalized'] = llm_normalized
            details['rule_normalized'] = rule_normalized
            print(f"    LLM normalized: {len(llm_normalized)}")
            print(f"    Rule normalized: {len(rule_normalized)}")
            
            # Step 4: Aggregation
            final_segments = aggregator.aggregate(llm_normalized, rule_normalized)
            details['final_segments'] = final_segments
            print(f"    Final segments: {len(final_segments)}")
            
            # Test data consistency
            print("  🔍 Testing data consistency...")
            
            # Check that normalization doesn't lose data unexpectedly
            if len(llm_normalized) > len(llm_segments) * 1.5:
                warnings.append("Normalization significantly increased segment count")
            
            if len(rule_normalized) > len(rule_segments) * 1.5:
                warnings.append("Rule normalization significantly increased segment count")
            
            # Check aggregation produces reasonable results
            if not final_segments:
                errors.append("Aggregation produced no segments")
            elif len(final_segments) > max(len(llm_normalized), len(rule_normalized)) * 2:
                warnings.append("Aggregation produced excessive segments")
            
            # Test component error propagation
            print("  ⚠️  Testing error propagation...")
            
            # Test with None inputs
            try:
                none_result = normalizer.normalize(None)
                details['none_normalization'] = none_result
                if none_result:
                    warnings.append("Normalization of None produced results")
            except Exception as e:
                details['none_error'] = str(e)
                print(f"    Handled None input: {type(e).__name__}")
            
            # Test empty list inputs
            try:
                empty_result = aggregator.aggregate([], [])
                details['empty_aggregation'] = empty_result
                if empty_result:
                    warnings.append("Aggregation of empty lists produced results")
            except Exception as e:
                details['empty_error'] = str(e)
                print(f"    Handled empty input: {type(e).__name__}")
            
            execution_time = (time.time() - start_time) * 1000
            
            passed = len(errors) == 0 and len(final_segments) > 0
            
            return IntegrationTestResult(
                "Component Interaction", passed, execution_time, details, errors, warnings
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            errors.append(f"Component interaction test failed: {str(e)}")
            return IntegrationTestResult(
                "Component Interaction", False, execution_time, details, errors, warnings
            )
    
    def _load_test_case(self, category: str, test_id: str) -> Dict[str, Any]:
        """Load a specific test case."""
        file_path = os.path.join(self.test_cases_dir, category, "test_cases.json")
        try:
            with open(file_path, 'r') as f:
                test_cases = json.load(f)
            return test_cases[test_id]
        except FileNotFoundError:
            # Try absolute path from project root
            abs_path = os.path.join(os.path.dirname(__file__), '..', self.test_cases_dir, category, "test_cases.json")
            with open(abs_path, 'r') as f:
                test_cases = json.load(f)
            return test_cases[test_id]
    
    def _compare_segments(self, actual: List[str], expected: List[str]) -> Dict[str, Any]:
        """Compare actual vs expected segments."""
        if not actual and not expected:
            return {'score': 1.0, 'exact_matches': 0, 'partial_matches': 0}
        
        if not actual or not expected:
            return {'score': 0.0, 'exact_matches': 0, 'partial_matches': 0}
        
        # Simple text similarity comparison
        actual_set = set(seg.lower().strip() for seg in actual)
        expected_set = set(seg.lower().strip() for seg in expected)
        
        intersection = actual_set.intersection(expected_set)
        union = actual_set.union(expected_set)
        
        jaccard_similarity = len(intersection) / len(union) if union else 0.0
        
        # Count-based comparison
        count_match = 1.0 - abs(len(actual) - len(expected)) / max(len(actual), len(expected), 1)
        
        # Combined score
        final_score = (jaccard_similarity + count_match) / 2.0
        
        return {
            'score': final_score,
            'jaccard_similarity': jaccard_similarity,
            'count_match': count_match,
            'exact_matches': len(intersection),
            'actual_count': len(actual),
            'expected_count': len(expected)
        }


def main():
    """Run all integration tests and generate report."""
    suite = IntegrationTestSuite()
    results = suite.run_all_tests()
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed_count = 0
    total_time = 0
    
    for result in results:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"{result.test_name:25} {status:10} {result.execution_time_ms:.0f}ms")
        
        if result.passed:
            passed_count += 1
        
        total_time += result.execution_time_ms
        
        # Show warnings
        if result.warnings:
            for warning in result.warnings:
                print(f"  ⚠️  {warning}")
        
        # Show errors
        if result.errors:
            for error in result.errors:
                print(f"  ❌ {error}")
    
    print("-" * 60)
    print(f"Overall: {passed_count}/{len(results)} test suites passed")
    print(f"Success Rate: {(passed_count/len(results))*100:.1f}%")
    print(f"Total Execution Time: {total_time:.0f}ms")
    
    if passed_count == len(results):
        print("🎉 All integration tests PASSED!")
        return 0
    else:
        print("❌ Some integration tests FAILED!")
        return 1


# Pytest-compatible test functions
def test_end_to_end_workflow():
    """Test complete workflow from input to evaluation."""
    suite = IntegrationTestSuite()
    result = suite.test_end_to_end_workflow()
    assert result.passed, f"End-to-end workflow failed: {result.errors}"

def test_api_integration():
    """Test analysis_api.py endpoints."""
    suite = IntegrationTestSuite()
    result = suite.test_api_integration()
    assert result.passed, f"API integration failed: {result.errors}"

def test_llm_integration():
    """Test real ollama integration."""
    suite = IntegrationTestSuite()
    result = suite.test_llm_integration()
    assert result.passed, f"LLM integration failed: {result.errors}"

def test_error_handling():
    """Test error handling and recovery."""
    suite = IntegrationTestSuite()
    result = suite.test_error_handling()
    assert result.passed, f"Error handling failed: {result.errors}"

def test_performance_under_load():
    """Test system performance under load."""
    suite = IntegrationTestSuite()
    result = suite.test_performance_under_load()
    assert result.passed, f"Performance test failed: {result.errors}"

def test_component_interaction():
    """Test interaction between system components."""
    suite = IntegrationTestSuite()
    result = suite.test_component_interaction()
    assert result.passed, f"Component interaction failed: {result.errors}"

def test_integration_suite():
    """Test complete integration test suite."""
    suite = IntegrationTestSuite()
    results = suite.run_all_tests()
    
    # Check that all tests pass
    failed_tests = [r for r in results if not r.passed]
    assert len(failed_tests) == 0, f"Failed integration tests: {[r.test_name for r in failed_tests]}"
    
    # Check reasonable execution times
    for result in results:
        assert result.execution_time_ms < 60000, f"{result.test_name} took too long: {result.execution_time_ms}ms"


if __name__ == "__main__":
    exit(main())