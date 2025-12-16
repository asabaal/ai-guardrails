"""
Validation Framework for Overseer AI Development Phases
Defines testing protocols and validation criteria for each development phase.

Following AI Safety Development Protocols (AI_SAFETY_DEVELOPMENT_PROTOCOLS.md)
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class ValidationResult:
    """Result of a validation test."""
    test_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    details: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


@dataclass
class PhaseValidationResult:
    """Complete validation result for a development phase."""
    phase_name: str
    overall_passed: bool
    overall_score: float
    test_results: List[ValidationResult]
    summary: str


class ValidationTest(ABC):
    """Abstract base class for validation tests."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    def run(self, test_data: Dict[str, Any]) -> ValidationResult:
        """Run the validation test."""
        pass


class Layer1ValidationTest(ValidationTest):
    """Validation tests for Layer 1: Segmentation components."""
    
    def __init__(self):
        super().__init__("Layer1_Segmentation", "Tests text segmentation accuracy")
        
    def run(self, test_data: Dict[str, Any]) -> ValidationResult:
        """Test segmentation against expected results."""
        errors = []
        warnings = []
        details = {}
        
        try:
            # Import Layer 1 components
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
            from layer1_segmentation import RuleBasedSplitter, Normalizer, Aggregator
            
            test_cases = test_data.get('test_cases', {})
            total_tests = 0
            passed_tests = 0
            
            segmentation_results = []
            
            for case_id, case_data in test_cases.items():
                if not case_data.get('expected_segments'):
                    continue
                    
                total_tests += 1
                input_text = case_data['input_text']
                expected_segments = case_data['expected_segments']
                
                # Test segmentation
                splitter = RuleBasedSplitter()
                raw_segments = splitter.segment(input_text)
                
                # Test normalization
                normalizer = Normalizer()
                normalized_segments = normalizer.normalize(raw_segments)
                
                # Test aggregation
                aggregator = Aggregator()
                final_segments = aggregator.aggregate(None, normalized_segments)
                
                # Compare with expected
                segment_match = self._compare_segments(final_segments, expected_segments)
                
                if segment_match['score'] >= 0.8:  # 80% match threshold
                    passed_tests += 1
                    
                segmentation_results.append({
                    'case_id': case_id,
                    'expected_count': len(expected_segments),
                    'actual_count': len(final_segments),
                    'match_score': segment_match['score'],
                    'segments': final_segments
                })
                
                if segment_match['score'] < 0.5:
                    errors.append(f"Poor segmentation for case {case_id}: score {segment_match['score']}")
                elif segment_match['score'] < 0.8:
                    warnings.append(f"Weak segmentation for case {case_id}: score {segment_match['score']}")
            
            overall_score = passed_tests / total_tests if total_tests > 0 else 0.0
            passed = overall_score >= 0.7  # 70% pass threshold
            
            details.update({
                'total_test_cases': total_tests,
                'passed_test_cases': passed_tests,
                'overall_score': overall_score,
                'segmentation_results': segmentation_results
            })
            
        except Exception as e:
            errors.append(f"Validation test failed: {str(e)}")
            overall_score = 0.0
            passed = False
            
        return ValidationResult(
            test_name=self.name,
            passed=passed,
            score=overall_score,
            details=details,
            errors=errors,
            warnings=warnings
        )
    
    def _compare_segments(self, actual: List[str], expected: List[str]) -> Dict[str, Any]:
        """Compare actual vs expected segments."""
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
            'intersection_size': len(intersection),
            'union_size': len(union)
        }


class ValidationFramework:
    """Main validation framework for all development phases."""
    
    def __init__(self, test_cases_dir: str = "../test_cases"):
        """Initialize validation framework."""
        self.test_cases_dir = test_cases_dir
        self.phase_tests = {
            'layer1_segmentation': Layer1ValidationTest(),
        }
        
    def validate_phase(self, phase_name: str, test_categories: Optional[List[str]] = None) -> PhaseValidationResult:
        """
        Validate a specific development phase.
        
        Args:
            phase_name: Name of the phase to validate
            test_categories: Specific test categories to include (None for all)
            
        Returns:
            PhaseValidationResult with comprehensive validation results
        """
        if phase_name not in self.phase_tests:
            raise ValueError(f"Unknown phase: {phase_name}")
            
        # Load test data
        test_data = self._load_test_data(test_categories)
        
        # Run phase-specific tests
        test_results = []
        phase_test = self.phase_tests[phase_name]
        result = phase_test.run(test_data)
        test_results.append(result)
        
        # Calculate overall results
        overall_score = sum(r.score for r in test_results) / len(test_results)
        overall_passed = all(r.passed for r in test_results)
        
        # Generate summary
        summary = self._generate_summary(phase_name, test_results)
        
        return PhaseValidationResult(
            phase_name=phase_name,
            overall_passed=overall_passed,
            overall_score=overall_score,
            test_results=test_results,
            summary=summary
        )
    
    def _load_test_data(self, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Load test case data from JSON files."""
        test_data = {'test_cases': {}}
        
        if categories is None:
            # Load all categories
            categories = [d for d in os.listdir(self.test_cases_dir) 
                         if os.path.isdir(os.path.join(self.test_cases_dir, d))]
        
        for category in categories:
            category_path = os.path.join(self.test_cases_dir, category, 'test_cases.json')
            if os.path.exists(category_path):
                with open(category_path, 'r') as f:
                    category_data = json.load(f)
                    test_data['test_cases'].update(category_data)
        
        return test_data
    
    def _generate_summary(self, phase_name: str, test_results: List[ValidationResult]) -> str:
        """Generate human-readable summary of validation results."""
        passed_count = sum(1 for r in test_results if r.passed)
        total_count = len(test_results)
        avg_score = sum(r.score for r in test_results) / total_count if total_count > 0 else 0.0
        
        summary = f"Phase '{phase_name}' Validation Summary:\n"
        summary += f"  Tests Passed: {passed_count}/{total_count}\n"
        summary += f"  Average Score: {avg_score:.2%}\n"
        
        if all(r.passed for r in test_results):
            summary += "  Status: ✅ PASSED\n"
        else:
            summary += "  Status: ❌ FAILED\n"
            
        # Add specific test details
        for result in test_results:
            status = "✅" if result.passed else "❌"
            summary += f"    {status} {result.test_name}: {result.score:.2%}\n"
            
        return summary
    



def main():
    """Main function to run validation framework."""
    framework = ValidationFramework()
    
    print("🔍 Overseer AI Validation Framework")
    print("=" * 50)
    
    # Run Layer 1 validation
    try:
        result = framework.validate_phase('layer1_segmentation')
        print(result.summary)
        
        if result.overall_passed:
            print("🎉 Layer 1 validation PASSED!")
        else:
            print("❌ Layer 1 validation FAILED!")
            
            # Print detailed errors
            for test_result in result.test_results:
                if test_result.errors:
                    print(f"\nErrors in {test_result.test_name}:")
                    for error in test_result.errors:
                        print(f"  - {error}")
                        
                if test_result.warnings:
                    print(f"\nWarnings in {test_result.test_name}:")
                    for warning in test_result.warnings:
                        print(f"  - {warning}")
                        
    except Exception as e:
        print(f"❌ Validation framework error: {e}")
        return 1
        
    return 0 if result.overall_passed else 1


if __name__ == "__main__":
    exit(main())