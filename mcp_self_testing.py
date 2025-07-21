#!/usr/bin/env python3
"""
MCP Self-Testing Framework
Allows Jarvis to test its own performance and identify improvement areas
"""

import asyncio
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    score: float  # 0.0 to 1.0
    expected_output: str
    actual_output: str
    issues_found: List[str]
    execution_time: float
    metadata: Dict[str, Any]

@dataclass
class TestSuite:
    """Collection of tests with overall performance metrics"""
    name: str
    tests: List[TestResult]
    overall_score: float
    improvement_suggestions: List[str]
    failed_components: List[str]

class SelfTestingFramework:
    """Complete self-testing system for Jarvis"""
    
    def __init__(self, server_url: str = "http://localhost:5001"):
        self.server_url = server_url
        self.test_history = []
        self.performance_baseline = 0.7  # Target minimum performance
        
        # Test scenarios with expected behaviors
        self.test_scenarios = {
            "basic_chat": {
                "input": "What can you do?",
                "expected_elements": ["help", "urgent", "actions", "assist"],
                "weight": 0.1
            },
            "item_resolution": {
                "input": "do item 1",
                "expected_elements": ["GitHub", "security", "step"],
                "weight": 0.3
            },
            "urgent_analysis": {
                "input": "What's urgent?",
                "expected_elements": ["urgent", "items", "priority"],
                "weight": 0.2
            },
            "context_memory": {
                "input": "Remember I'm working on security review",
                "expected_elements": ["remember", "noted", "security"],
                "weight": 0.15
            },
            "follow_up": {
                "input": "What did I just tell you?",
                "expected_elements": ["security", "review", "working"],
                "weight": 0.15
            },
            "complex_request": {
                "input": "Help me prepare for tomorrow's board meeting about Q4 revenue",
                "expected_elements": ["board", "meeting", "revenue", "prepare"],
                "weight": 0.1
            }
        }
        
        # Performance rubrics for self-evaluation
        self.evaluation_rubrics = {
            "response_relevance": {
                "description": "How relevant is the response to the user's request?",
                "criteria": [
                    "Addresses the specific question asked",
                    "Provides actionable information",
                    "Stays on topic"
                ]
            },
            "completeness": {
                "description": "Does the response provide complete information?",
                "criteria": [
                    "Covers all aspects of the request",
                    "Provides sufficient detail",
                    "Includes next steps when appropriate"
                ]
            },
            "accuracy": {
                "description": "Is the information provided accurate?",
                "criteria": [
                    "Facts are correct",
                    "Context is properly understood",
                    "No misleading information"
                ]
            },
            "efficiency": {
                "description": "How efficiently does the system respond?",
                "criteria": [
                    "Response time under 3 seconds",
                    "Uses appropriate tools",
                    "Minimal unnecessary processing"
                ]
            }
        }

    async def run_comprehensive_test_suite(self) -> TestSuite:
        """Run complete self-testing suite"""
        logger.info("🧪 Starting Comprehensive Self-Testing Suite")
        logger.info("=" * 50)
        
        test_results = []
        
        # 1. Basic Functionality Tests
        basic_results = await self._test_basic_functionality()
        test_results.extend(basic_results)
        
        # 2. Memory and Context Tests
        memory_results = await self._test_memory_system()
        test_results.extend(memory_results)
        
        # 3. Item Resolution Tests
        resolution_results = await self._test_item_resolution()
        test_results.extend(resolution_results)
        
        # 4. End-to-End Scenario Tests
        scenario_results = await self._test_scenarios()
        test_results.extend(scenario_results)
        
        # 5. Performance Tests
        performance_results = await self._test_performance()
        test_results.extend(performance_results)
        
        # 6. Self-Evaluation Tests
        eval_results = await self._test_self_evaluation()
        test_results.extend(eval_results)
        
        # Calculate overall performance
        overall_score = sum(result.score * self.test_scenarios.get(result.test_name, {}).get('weight', 0.1) 
                          for result in test_results) / len(test_results)
        
        # Identify improvement areas
        improvement_suggestions = self._analyze_improvement_areas(test_results)
        failed_components = [r.test_name for r in test_results if r.score < 0.6]
        
        test_suite = TestSuite(
            name=f"Comprehensive_Test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            tests=test_results,
            overall_score=overall_score,
            improvement_suggestions=improvement_suggestions,
            failed_components=failed_components
        )
        
        # Store results for future analysis
        self.test_history.append(test_suite)
        
        self._report_results(test_suite)
        return test_suite

    async def _test_basic_functionality(self) -> List[TestResult]:
        """Test basic chat functionality"""
        logger.info("🔧 Testing Basic Functionality...")
        results = []
        
        for test_name, test_config in self.test_scenarios.items():
            if test_name in ["basic_chat", "urgent_analysis"]:
                result = await self._execute_single_test(test_name, test_config)
                results.append(result)
        
        return results

    async def _test_memory_system(self) -> List[TestResult]:
        """Test memory and context retention"""
        logger.info("🧠 Testing Memory System...")
        results = []
        
        # Test context memory
        context_test = self.test_scenarios["context_memory"]
        context_result = await self._execute_single_test("context_memory", context_test)
        results.append(context_result)
        
        # Test follow-up (requires memory)
        follow_up_test = self.test_scenarios["follow_up"]
        follow_up_result = await self._execute_single_test("follow_up", follow_up_test)
        results.append(follow_up_result)
        
        return results

    async def _test_item_resolution(self) -> List[TestResult]:
        """Test item resolution capabilities"""
        logger.info("🎯 Testing Item Resolution...")
        results = []
        
        # Test basic item resolution
        item_test = self.test_scenarios["item_resolution"]
        item_result = await self._execute_single_test("item_resolution", item_test)
        results.append(item_result)
        
        # Test multiple item references
        multi_item_test = {
            "input": "do items 1 and 2",
            "expected_elements": ["GitHub", "Companies", "security", "verification"],
            "weight": 0.2
        }
        multi_result = await self._execute_single_test("multi_item_resolution", multi_item_test)
        results.append(multi_result)
        
        return results

    async def _test_scenarios(self) -> List[TestResult]:
        """Test end-to-end scenarios"""
        logger.info("🌟 Testing End-to-End Scenarios...")
        results = []
        
        complex_test = self.test_scenarios["complex_request"]
        complex_result = await self._execute_single_test("complex_request", complex_test)
        results.append(complex_result)
        
        return results

    async def _test_performance(self) -> List[TestResult]:
        """Test performance metrics"""
        logger.info("⚡ Testing Performance...")
        results = []
        
        # Response time test
        start_time = time.time()
        response = await self._send_test_request("Quick test")
        end_time = time.time()
        
        response_time = end_time - start_time
        score = 1.0 if response_time < 3.0 else max(0.0, 1.0 - (response_time - 3.0) / 10.0)
        
        performance_result = TestResult(
            test_name="response_time",
            score=score,
            expected_output="< 3 seconds",
            actual_output=f"{response_time:.2f} seconds",
            issues_found=[] if response_time < 3.0 else [f"Slow response: {response_time:.2f}s"],
            execution_time=response_time,
            metadata={"target_time": 3.0, "actual_time": response_time}
        )
        results.append(performance_result)
        
        return results

    async def _test_self_evaluation(self) -> List[TestResult]:
        """Test self-evaluation capabilities"""
        logger.info("🔍 Testing Self-Evaluation...")
        results = []
        
        # Ask Jarvis to evaluate its own response
        eval_request = "Rate your last response from 1-10 and explain why"
        response = await self._send_test_request(eval_request)
        
        # Check if it can self-evaluate
        has_rating = any(str(i) in response for i in range(1, 11))
        has_explanation = len(response) > 50 and any(word in response.lower() 
                                                   for word in ["because", "since", "due to", "reason"])
        
        score = 0.5 * has_rating + 0.5 * has_explanation
        
        eval_result = TestResult(
            test_name="self_evaluation",
            score=score,
            expected_output="Rating with explanation",
            actual_output=response[:200] + "..." if len(response) > 200 else response,
            issues_found=[] if score > 0.7 else ["Cannot provide proper self-evaluation"],
            execution_time=0.0,
            metadata={"has_rating": has_rating, "has_explanation": has_explanation}
        )
        results.append(eval_result)
        
        return results

    async def _execute_single_test(self, test_name: str, test_config: Dict) -> TestResult:
        """Execute a single test and evaluate results"""
        start_time = time.time()
        
        try:
            response = await self._send_test_request(test_config["input"])
            end_time = time.time()
            
            # Score based on expected elements
            expected_elements = test_config["expected_elements"]
            found_elements = [elem for elem in expected_elements 
                            if elem.lower() in response.lower()]
            
            score = len(found_elements) / len(expected_elements)
            
            # Self-evaluation score
            self_eval_score = await self._get_self_evaluation_score(
                test_config["input"], response
            )
            
            # Combine scores
            final_score = 0.7 * score + 0.3 * self_eval_score
            
            issues_found = []
            missing_elements = [elem for elem in expected_elements if elem not in found_elements]
            if missing_elements:
                issues_found.append(f"Missing elements: {missing_elements}")
            
            return TestResult(
                test_name=test_name,
                score=final_score,
                expected_output=f"Contains: {expected_elements}",
                actual_output=response[:200] + "..." if len(response) > 200 else response,
                issues_found=issues_found,
                execution_time=end_time - start_time,
                metadata={
                    "found_elements": found_elements,
                    "expected_elements": expected_elements,
                    "self_eval_score": self_eval_score
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_name,
                score=0.0,
                expected_output=f"Contains: {test_config['expected_elements']}",
                actual_output=f"ERROR: {str(e)}",
                issues_found=[f"Test execution failed: {str(e)}"],
                execution_time=time.time() - start_time,
                metadata={"error": str(e)}
            )

    async def _send_test_request(self, message: str) -> str:
        """Send a test request to Jarvis"""
        try:
            response = requests.post(
                f"{self.server_url}/api/jarvis/chat",
                json={
                    "message": message,
                    "personality": {"conscientiousness": 80}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("message", "No response message")
            else:
                return f"HTTP Error {response.status_code}"
                
        except Exception as e:
            return f"Request failed: {str(e)}"

    async def _get_self_evaluation_score(self, input_text: str, output_text: str) -> float:
        """Get Jarvis to evaluate its own response"""
        eval_prompt = f"""
        Rate the following response on a scale of 0.0 to 1.0:
        
        Input: {input_text}
        Output: {output_text}
        
        Consider:
        - Relevance to the question
        - Completeness of the answer
        - Clarity and helpfulness
        
        Respond with just a number between 0.0 and 1.0
        """
        
        try:
            eval_response = await self._send_test_request(eval_prompt)
            # Extract number from response
            import re
            numbers = re.findall(r'\b0?\.\d+\b|\b[01]\.?\d*\b', eval_response)
            if numbers:
                score = float(numbers[0])
                return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            return 0.5  # Default if no score found
        except:
            return 0.5

    def _analyze_improvement_areas(self, test_results: List[TestResult]) -> List[str]:
        """Analyze test results and suggest improvements"""
        suggestions = []
        
        # Check for consistently low scores
        low_scoring_tests = [r for r in test_results if r.score < 0.6]
        if low_scoring_tests:
            suggestions.append(f"Low performance in: {[r.test_name for r in low_scoring_tests]}")
        
        # Check for slow responses
        slow_tests = [r for r in test_results if r.execution_time > 3.0]
        if slow_tests:
            suggestions.append("Response time optimization needed")
        
        # Check for missing memory functionality
        memory_tests = [r for r in test_results if "memory" in r.test_name or "follow" in r.test_name]
        if any(r.score < 0.7 for r in memory_tests):
            suggestions.append("Memory system needs improvement")
        
        # Check for item resolution issues
        resolution_tests = [r for r in test_results if "item" in r.test_name]
        if any(r.score < 0.7 for r in resolution_tests):
            suggestions.append("Item resolution system needs enhancement")
        
        return suggestions

    def _report_results(self, test_suite: TestSuite):
        """Generate comprehensive test report"""
        logger.info("📊 SELF-TESTING RESULTS")
        logger.info("=" * 50)
        logger.info(f"🎯 Overall Score: {test_suite.overall_score:.2f}/1.0")
        logger.info(f"📈 Performance: {'PASS' if test_suite.overall_score >= self.performance_baseline else 'NEEDS IMPROVEMENT'}")
        logger.info("")
        
        logger.info("📋 Individual Test Results:")
        for test in test_suite.tests:
            status = "✅ PASS" if test.score >= 0.7 else "❌ FAIL" if test.score < 0.4 else "⚠️ MARGINAL"
            logger.info(f"  {test.test_name}: {test.score:.2f} {status}")
            if test.issues_found:
                for issue in test.issues_found:
                    logger.info(f"    Issue: {issue}")
        
        logger.info("")
        logger.info("🔧 Improvement Suggestions:")
        for suggestion in test_suite.improvement_suggestions:
            logger.info(f"  • {suggestion}")
        
        if test_suite.failed_components:
            logger.info("")
            logger.info("❌ Failed Components:")
            for component in test_suite.failed_components:
                logger.info(f"  • {component}")
        
        logger.info("=" * 50)

    async def identify_code_improvement_targets(self, test_suite: TestSuite) -> Dict[str, List[str]]:
        """Map test failures to specific code areas that need improvement"""
        improvement_map = {
            "memory_system": [],
            "item_resolution": [],
            "response_generation": [],
            "performance_optimization": [],
            "self_evaluation": []
        }
        
        for test in test_suite.tests:
            if test.score < 0.7:
                if "memory" in test.test_name or "follow" in test.test_name:
                    improvement_map["memory_system"].append(
                        f"Fix memory retention in {test.test_name}: {test.issues_found}"
                    )
                elif "item" in test.test_name:
                    improvement_map["item_resolution"].append(
                        f"Enhance item resolution in {test.test_name}: {test.issues_found}"
                    )
                elif test.execution_time > 3.0:
                    improvement_map["performance_optimization"].append(
                        f"Optimize {test.test_name} response time: {test.execution_time:.2f}s"
                    )
                elif "eval" in test.test_name:
                    improvement_map["self_evaluation"].append(
                        f"Improve self-evaluation in {test.test_name}: {test.issues_found}"
                    )
                else:
                    improvement_map["response_generation"].append(
                        f"Enhance response quality in {test.test_name}: {test.issues_found}"
                    )
        
        return improvement_map

async def main():
    """Run the self-testing framework"""
    framework = SelfTestingFramework()
    
    # Run comprehensive test suite
    test_suite = await framework.run_comprehensive_test_suite()
    
    # Identify specific code areas for improvement
    improvement_targets = await framework.identify_code_improvement_targets(test_suite)
    
    print("\n🎯 CODE IMPROVEMENT TARGETS:")
    print("=" * 50)
    for area, improvements in improvement_targets.items():
        if improvements:
            print(f"\n📁 {area.upper()}:")
            for improvement in improvements:
                print(f"  • {improvement}")
    
    return test_suite

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 