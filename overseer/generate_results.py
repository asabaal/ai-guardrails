#!/usr/bin/env python3
"""
Generate Results Script

Processes all test cases through the actual Layer 1 segmentation system
to create real outputs for visual validation.

Following AI Safety Development Protocols (AI_SAFETY_DEVELOPMENT_PROTOCOLS.md)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from layer1_segmentation.text_segmenter import (
    LLMTextSegmenter, RuleBasedSplitter, Normalizer, Aggregator
)


class ResultsGenerator:
    """Generate segmentation results for all test cases."""
    
    def __init__(self):
        """Initialize the results generator."""
        self.llm_segmenter = LLMTextSegmenter({
            'model_name': 'llama3.2:1b',  # Use smaller model for faster processing
            'max_retries': 2,
            'timeout': 30
        })
        self.rule_splitter = RuleBasedSplitter()
        self.normalizer = Normalizer()
        self.aggregator = Aggregator()
        
        # Create output directory
        self.output_dir = Path('generated_results')
        self.output_dir.mkdir(exist_ok=True)
        
        # Results storage
        self.results = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_test_cases': 0,
                'successful_processing': 0,
                'failed_processing': 0
            },
            'categories': {},
            'failed_cases': []
        }
    
    def load_test_cases(self):
        """Load all test case files."""
        test_cases_dir = Path('test_cases')
        categories = {}
        
        for category_dir in test_cases_dir.iterdir():
            if category_dir.is_dir() and (category_dir / 'test_cases.json').exists():
                category_name = category_dir.name
                with open(category_dir / 'test_cases.json', 'r') as f:
                    categories[category_name] = json.load(f)
        
        return categories
    
    def process_single_case(self, case_data, case_id):
        """Process a single test case through the complete pipeline."""
        try:
            text = case_data['input_text']
            
            # Step 1: LLM Segmentation
            print(f"  Processing LLM segmentation for case {case_id}...")
            llm_segments = self.llm_segmenter.segment(text)
            
            # Step 2: Rule-based Segmentation
            print(f"  Processing rule-based segmentation for case {case_id}...")
            rule_segments = self.rule_splitter.segment(text)
            
            # Step 3: Normalization
            print(f"  Normalizing segments for case {case_id}...")
            normalized_llm = self.normalizer.normalize(llm_segments)
            normalized_rules = self.normalizer.normalize(rule_segments)
            
            # Step 4: Aggregation
            print(f"  Aggregating results for case {case_id}...")
            final_segments = self.aggregator.aggregate(normalized_llm, normalized_rules)
            
            # Store results
            result = {
                'case_id': case_id,
                'input_text': text,
                'expected_segments': case_data.get('expected_segments', []),
                'llm_segments': llm_segments,
                'rule_segments': rule_segments,
                'normalized_llm': normalized_llm,
                'normalized_rules': normalized_rules,
                'final_segments': final_segments,
                'processing_success': True,
                'error': None
            }
            
            return result
            
        except Exception as e:
            print(f"  ❌ Error processing case {case_id}: {e}")
            return {
                'case_id': case_id,
                'input_text': case_data.get('input_text', ''),
                'expected_segments': case_data.get('expected_segments', []),
                'llm_segments': [],
                'rule_segments': [],
                'normalized_llm': [],
                'normalized_rules': [],
                'final_segments': [],
                'processing_success': False,
                'error': str(e)
            }
    
    def process_category(self, category_name, test_cases):
        """Process all test cases in a category."""
        print(f"\n📂 Processing category: {category_name}")
        
        # Handle both list and dict formats
        if isinstance(test_cases, dict):
            case_list = list(test_cases.values())
        else:
            case_list = test_cases
            
        print(f"   Found {len(case_list)} test cases")
        
        category_results = []
        successful = 0
        failed = 0
        
        for i, case_data in enumerate(case_list):
            case_id = f"{category_name}_{i+1:03d}"
            print(f"  📝 Case {case_id}: {case_data.get('description', 'No description')}")
            
            result = self.process_single_case(case_data, case_id)
            category_results.append(result)
            
            if result['processing_success']:
                successful += 1
                print(f"  ✅ Case {case_id} completed successfully")
            else:
                failed += 1
                self.results['failed_cases'].append({
                    'case_id': case_id,
                    'category': category_name,
                    'error': result['error']
                })
        
        self.results['categories'][category_name] = {
            'test_cases': category_results,
            'stats': {
                'total': len(case_list),
                'successful': successful,
                'failed': failed
            }
        }
        
        print(f"   Category summary: {successful} successful, {failed} failed")
        
        return successful, failed
    
    def save_results(self):
        """Save results to JSON files."""
        # Update metadata
        total_cases = sum(
            cat_data['stats']['total'] 
            for cat_data in self.results['categories'].values()
        )
        total_successful = sum(
            cat_data['stats']['successful'] 
            for cat_data in self.results['categories'].values()
        )
        total_failed = sum(
            cat_data['stats']['failed'] 
            for cat_data in self.results['categories'].values()
        )
        
        self.results['metadata']['total_test_cases'] = total_cases
        self.results['metadata']['successful_processing'] = total_successful
        self.results['metadata']['failed_processing'] = total_failed
        
        # Save complete results
        output_file = self.output_dir / 'segmentation_results.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Save summary for quick viewing
        summary = {
            'metadata': self.results['metadata'],
            'category_summaries': {
                name: data['stats'] 
                for name, data in self.results['categories'].items()
            }
        }
        
        summary_file = self.output_dir / 'results_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Results saved to:")
        print(f"   Complete results: {output_file}")
        print(f"   Summary: {summary_file}")
    
    def generate_html_report(self):
        """Generate an HTML report for easy viewing."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Layer 1 Segmentation Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .category {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }}
        .category-header {{ background: #e8e8e8; padding: 15px; font-weight: bold; }}
        .case {{ margin: 15px; padding: 15px; border-left: 3px solid #007cba; }}
        .success {{ border-left-color: #28a745; }}
        .failure {{ border-left-color: #dc3545; }}
        .segments {{ margin: 10px 0; }}
        .segment-type {{ font-weight: bold; color: #495057; }}
        .segment-list {{ margin: 5px 0; padding-left: 20px; }}
        .error {{ color: #dc3545; font-style: italic; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Layer 1 Segmentation Results</h1>
        <p>Generated: {self.results['metadata']['generated_at']}</p>
        <p>Total Cases: {self.results['metadata']['total_test_cases']}</p>
        <p>Successful: {self.results['metadata']['successful_processing']}</p>
        <p>Failed: {self.results['metadata']['failed_processing']}</p>
    </div>
"""
        
        for category_name, category_data in self.results['categories'].items():
            html_content += f"""
    <div class="category">
        <div class="category-header">
            {category_name} ({category_data['stats']['successful']}/{category_data['stats']['total']} successful)
        </div>
"""
            
            for case in category_data['test_cases']:
                status_class = "success" if case['processing_success'] else "failure"
                html_content += f"""
        <div class="case {status_class}">
            <h4>{case['case_id']}: {case.get('description', 'No description')}</h4>
            <p><strong>Input:</strong> {case['input_text']}</p>
"""
                
                if case['processing_success']:
                    html_content += f"""
            <div class="segments">
                <div class="segment-type">LLM Segments ({len(case['llm_segments'])}):</div>
                <div class="segment-list">{', '.join(case['llm_segments'])}</div>
            </div>
            <div class="segments">
                <div class="segment-type">Rule Segments ({len(case['rule_segments'])}):</div>
                <div class="segment-list">{', '.join(case['rule_segments'])}</div>
            </div>
            <div class="segments">
                <div class="segment-type">Final Segments ({len(case['final_segments'])}):</div>
                <div class="segment-list">{', '.join(case['final_segments'])}</div>
            </div>
"""
                else:
                    html_content += f'<p class="error"><strong>Error:</strong> {case["error"]}</p>'
                
                html_content += "        </div>\n"
            
            html_content += "    </div>\n"
        
        html_content += """
</body>
</html>
"""
        
        html_file = self.output_dir / 'results_report.html'
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"   HTML report: {html_file}")
    
    def run(self):
        """Run the complete results generation process."""
        print("🚀 Starting Layer 1 Segmentation Results Generation")
        print("=" * 60)
        
        # Load test cases
        print("📖 Loading test cases...")
        categories = self.load_test_cases()
        
        if not categories:
            print("❌ No test cases found!")
            return False
        
        print(f"✅ Found {len(categories)} categories")
        
        # Process each category
        total_successful = 0
        total_failed = 0
        
        for category_name, test_cases in categories.items():
            successful, failed = self.process_category(category_name, test_cases)
            total_successful += successful
            total_failed += failed
        
        # Save results
        print(f"\n💾 Saving results...")
        self.save_results()
        self.generate_html_report()
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 RESULTS GENERATION SUMMARY")
        print("=" * 60)
        print(f"Total Test Cases: {total_successful + total_failed}")
        print(f"Successfully Processed: {total_successful}")
        print(f"Failed: {total_failed}")
        print(f"Success Rate: {(total_successful/(total_successful + total_failed)*100):.1f}%")
        
        if total_failed > 0:
            print(f"\n⚠️  Failed cases:")
            for case in self.results['failed_cases']:
                print(f"   - {case['case_id']}: {case['error']}")
        
        print(f"\n🎉 Results generation completed!")
        return True


def main():
    """Main entry point."""
    generator = ResultsGenerator()
    success = generator.run()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()