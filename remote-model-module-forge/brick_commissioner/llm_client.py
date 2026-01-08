import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from openai import OpenAI
from brick_commissioner.config import Config


class LLMClient:
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            api_key=config.zai_api_key,
            base_url=config.zai_base_url,
            timeout=config.limits.per_call_timeout
        )
        self.call_count = 0
        self.total_tokens_used = 0
        self.logs_dir = Path(config.logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _mock_dry_run(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        print("\n" + "=" * 80)
        print("DRY RUN MODE - Request would be:")
        print("=" * 80)
        print(f"\nSystem Prompt:\n{system_prompt}")
        print(f"\nUser Prompt:\n{user_prompt}")
        if output_schema:
            print(f"\nExpected Output Schema:\n{json.dumps(output_schema, indent=2)}")
        print("=" * 80)
        
        mock_module_name = "test_module"
        mock_module_desc = f"Module for: {system_prompt[:50]}..."
        mock_functions = [
            {
                "name": "example_function",
                "description": "A function that does something",
                "inputs": ["param: str"],
                "outputs": "str",
                "side_effects": "None"
            }
        ]
        
        return {
            "dry_run": True,
            "mock_response": "In dry-run mode, no actual API call is made. " +
                          "Use a real API key to test with actual LLM calls.",
            "module_name": mock_module_name,
            "module_description": mock_module_desc,
            "required_public_functions": mock_functions,
            "questions": [],
            "is_complete": True
        }
        
        return {
            "dry_run": True,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "mock_response": "In dry-run mode, no actual API call is made. " +
                          "Use a real API key to test with actual LLM calls.",
            "mock_data": {
                "module_name": "test_module",
                "module_description": f"Module for: {system_prompt[:50]}...",
                "required_public_functions": [
                    {
                        "name": "example_function",
                        "description": "A function that does something",
                        "inputs": ["param: str"],
                        "outputs": "str",
                        "side_effects": "None"
                    }
                ]
            },
            "is_complete": True
        }

    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Optional[Dict[str, Any]] = None,
        dry_run: Optional[bool] = None
    ) -> Dict[str, Any]:
        dry_run = self.config.dry_run if dry_run is None else dry_run
        
        if dry_run:
            return self._mock_dry_run(system_prompt, user_prompt, output_schema)
        
        if self.call_count >= self.config.limits.max_calls_per_brick:
            raise TimeoutError(f"Max LLM calls per brick limit ({self.config.limits.max_calls_per_brick}) exceeded")
        
        start_time = time.time()
        self.call_count += 1
        call_log_file = self.logs_dir / f"call_{self.call_count}_{int(start_time)}.json"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        request_payload = {
            "model": self.config.zai_model_name,
            "messages": messages,
            "max_tokens": self.config.limits.max_tokens_per_call
        }
        
        if output_schema:
            request_payload["response_format"] = {
                "type": "json_object",
                "schema": output_schema
            }
        
        self._log_request(call_log_file, request_payload, start_time)
        
        try:
            response = self.client.chat.completions.create(**request_payload)
            elapsed = time.time() - start_time
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")
            
            result = json.loads(content)
            tokens_used = response.usage.total_tokens if response.usage else 0
            self.total_tokens_used += tokens_used
            
            log_entry = {
                "request": request_payload,
                "response": content,
                "parsed_result": result,
                "tokens_used": tokens_used,
                "elapsed_seconds": elapsed,
                "timestamp": start_time
            }
            
            with open(call_log_file, "w") as f:
                json.dump(log_entry, f, indent=2)
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            log_entry = {
                "request": request_payload,
                "error": str(e),
                "elapsed_seconds": elapsed,
                "timestamp": start_time,
                "failed": True
            }
            with open(call_log_file, "w") as f:
                json.dump(log_entry, f, indent=2)
            raise

    def _log_request(self, log_file: Path, request_payload: Dict[str, Any], timestamp: float) -> None:
        """Log LLM request to file."""
        pass

    def get_stats(self) -> Dict[str, Any]:
        return {
            "calls_made": self.call_count,
            "total_tokens_used": self.total_tokens_used,
            "max_calls": self.config.limits.max_calls_per_brick,
            "max_tokens": self.config.limits.max_tokens_per_call
        }
