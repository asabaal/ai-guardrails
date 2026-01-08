import json
from typing import Dict, Any, List
from pathlib import Path


def generate_ui_html(
    function_name: str,
    function_description: str,
    inputs_schema: Dict[str, Any],
    sample_inputs: List[Dict[str, Any]],
    runner_url: str = "http://127.0.0.1:8000"
) -> str:
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brick Verification UI - {function_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e4e4e7;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: rgba(30, 41, 59, 0.9);
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }}
        h1 {{
            color: #38bdf8;
            font-size: 2rem;
            margin-bottom: 20px;
            border-bottom: 2px solid #38bdf8;
            padding-bottom: 10px;
        }}
        .description {{
            background: rgba(56, 189, 248, 0.1);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #38bdf8;
            margin-bottom: 20px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section h2 {{
            color: #a78bfa;
            font-size: 1.3rem;
            margin-bottom: 15px;
        }}
        .sample-buttons {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 15px;
        }}
        .sample-btn {{
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }}
        .sample-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(139, 92, 246, 0.4);
        }}
        .input-group {{
            margin-bottom: 15px;
        }}
        .input-group label {{
            display: block;
            color: #94a3b8;
            margin-bottom: 5px;
            font-weight: 500;
        }}
        .input-group input, .input-group textarea {{
            width: 100%;
            padding: 12px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid #334155;
            border-radius: 8px;
            color: #e4e4e7;
            font-family: monospace;
            font-size: 0.9rem;
        }}
        .input-group input:focus, .input-group textarea:focus {{
            outline: none;
            border-color: #38bdf8;
        }}
        .run-btn {{
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }}
        .run-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(16, 185, 129, 0.4);
        }}
        .run-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        .output {{
            background: rgba(15, 23, 42, 0.9);
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            min-height: 100px;
            font-family: monospace;
            white-space: pre-wrap;
            border: 1px solid #334155;
        }}
        .output.success {{
            border-color: #10b981;
            background: rgba(16, 185, 129, 0.1);
        }}
        .output.error {{
            border-color: #ef4444;
            background: rgba(239, 68, 68, 0.1);
        }}
        .instructions {{
            background: rgba(234, 179, 8, 0.1);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #eab308;
            margin-top: 20px;
        }}
        .instructions h3 {{
            color: #eab308;
            margin-bottom: 10px;
        }}
        .instructions code {{
            background: rgba(0, 0, 0, 0.3);
            padding: 2px 6px;
            border-radius: 4px;
            color: #e4e4e7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧱 Brick Verification: {function_name}</h1>
        
        <div class="description">
            <strong>Function:</strong> {function_name}<br>
            <strong>Description:</strong> {function_description}
        </div>
        
        <div class="section">
            <h2>Sample Inputs</h2>
            <div class="sample-buttons">
'''

    for i, sample in enumerate(sample_inputs):
        label = sample.get('label', f'Sample {i+1}')
        html += f'                <button class="sample-btn" onclick="loadSample({i})">{label}</button>\n'

    html += '''            </div>
        </div>
        
        <div class="section">
            <h2>Custom Input</h2>
'''

    for key, value in inputs_schema.items():
        html += f'''            <div class="input-group">
                <label for="input_{key}">{key}</label>
                <input type="text" id="input_{key}" name="{key}" placeholder="{value.get('example', '')}">
            </div>
'''

    html += f'''        </div>
        
        <button class="run-btn" onclick="runFunction()" id="runBtn">Run Function</button>
        
        <div id="output" class="output"></div>
        
        <div class="instructions">
            <h3>📝 Local Run Instructions</h3>
            <p>To use this UI, first start the local runner:</p>
            <code>python {runner_url}/run</code>
            <p style="margin-top: 10px;">Then open this file in your browser.</p>
        </div>
    </div>
    
    <script>
        const sampleInputs = {json.dumps(sample_inputs)};
        
        function loadSample(index) {{
            const sample = sampleInputs[index];
            const inputs = sample.inputs;
            
            for (const [key, value] of Object.entries(inputs)) {{
                const inputEl = document.getElementById(`input_${{key}}`);
                if (inputEl) {{
                    inputEl.value = JSON.stringify(value);
                }}
            }}
        }}
        
        async function runFunction() {{
            const btn = document.getElementById('runBtn');
            const outputEl = document.getElementById('output');
            
            btn.disabled = true;
            outputEl.textContent = 'Running...';
            outputEl.className = 'output';
            
            const inputs = {{}};
            
'''

    for key in inputs_schema.keys():
        html += f'''            const input_{key} = document.getElementById('input_{key}').value;
            try {{
                inputs['{key}'] = JSON.parse(input_{key});
            }} catch (e) {{
                inputs['{key}'] = input_{key};
            }}
'''

    html += f'''
            try {{
                const response = await fetch('{runner_url}/run', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{ inputs }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    outputEl.textContent = JSON.stringify(result.output, null, 2);
                    outputEl.className = 'output success';
                }} else {{
                    outputEl.textContent = `Error (${{result.error_type}}): ${{result.error}}`;
                    outputEl.className = 'output error';
                }}
            }} catch (error) {{
                outputEl.textContent = `Connection Error: ${{error.message}}`;
                outputEl.className = 'output error';
            }} finally {{
                btn.disabled = false;
            }}
        }}
    </script>
</body>
</html>
'''
    return html


def generate_runner_script(
    function_name: str,
    module_path: str,
    runner_path: str
) -> str:
    return f'''#!/usr/bin/env python3
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run")
async def run_function(request: Request):
    try:
        data = await request.json()
        inputs = data.get("inputs", {{}})
        
        module_path_str = "{module_path}"
        
        module = __import__(Path(module_path_str).stem)
        func_name = "{function_name}"
        func = getattr(module, func_name)
        
        result = func(**inputs)
        
        return JSONResponse({{
            "success": True,
            "output": result,
            "function": func_name
        }})
    except Exception as e:
        return JSONResponse({{
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }}, status_code=400)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
'''
