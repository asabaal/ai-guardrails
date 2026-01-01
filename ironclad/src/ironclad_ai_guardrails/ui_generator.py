#!/usr/bin/env python3
"""
UI Generator Module

Generates actual UI artifacts from UISpec specifications.
Supports multiple target platforms while maintaining Module Forge architecture.
"""

import os
import json
from typing import Dict, List, Any, Optional
from ironclad_ai_guardrails.ui_spec import UISpec, UIComponent, ComponentType, UIType, UIStyling, UILayout


class UIGenerationError(Exception):
    """Custom exception for UI generation errors"""
    pass


class UIGenerator:
    """Main UI generator class supporting multiple target platforms"""
    
    def __init__(self, ui_spec: UISpec):
        self.ui_spec = ui_spec
        
    def generate(self, output_dir: str) -> Dict[str, str]:
        """Generate UI artifacts and return mapping of files to their content"""
        if self.ui_spec.ui_type == UIType.WEB:
            return self._generate_web_ui(output_dir)
        elif self.ui_spec.ui_type == UIType.CLI_GUI:
            return self._generate_cli_gui(output_dir)
        elif self.ui_spec.ui_type == UIType.DESKTOP:
            return self._generate_desktop_ui(output_dir)
        elif self.ui_spec.ui_type == UIType.API_DOCS:
            return self._generate_api_docs(output_dir)
        elif self.ui_spec.ui_type == UIType.CLI_TUI:
            return self._generate_cli_tui(output_dir)
        else:
            raise UIGenerationError(f"Unsupported UI type: {self.ui_spec.ui_type}")
    
    def _generate_web_ui(self, output_dir: str) -> Dict[str, str]:
        """Generate web-based UI (HTML/CSS/JS)"""
        files = {}
        
        # Generate main HTML file
        files['index.html'] = self._generate_html_main()
        
        # Generate CSS file
        files['styles.css'] = self._generate_css_styles()
        
        # Generate JavaScript file
        files['app.js'] = self._generate_js_logic()
        
        # Generate package.json
        files['package.json'] = self._generate_package_json()
        
        return files
    
    def _generate_cli_gui(self, output_dir: str) -> Dict[str, str]:
        """Generate CLI-based GUI (Tkinter/Qt style)"""
        files = {}
        
        # Generate main GUI script
        files['gui.py'] = self._generate_tkinter_gui()
        
        # Generate requirements file
        files['requirements.txt'] = "tkinter\n"
        
        return files
    
    def _generate_desktop_ui(self, output_dir: str) -> Dict[str, str]:
        """Generate desktop UI (Electron-style)"""
        files = {}
        
        # Generate Electron main file
        files['main.js'] = self._generate_electron_main()
        
        # Generate preload script
        files['preload.js'] = self._generate_electron_preload()
        
        # Generate HTML for Electron
        files['index.html'] = self._generate_electron_html()
        
        # Generate package.json
        files['package.json'] = self._generate_electron_package_json()
        
        return files
    
    def _generate_api_docs(self, output_dir: str) -> Dict[str, str]:
        """Generate API documentation UI"""
        files = {}
        
        # Generate OpenAPI specification
        files['openapi.json'] = self._generate_openapi_spec()
        
        # Generate Swagger UI HTML
        files['swagger.html'] = self._generate_swagger_html()
        
        return files
    
    def _generate_cli_tui(self, output_dir: str) -> Dict[str, str]:
        """Generate terminal UI (rich/textual style)"""
        files = {}
        
        # Generate TUI script
        files['tui.py'] = self._generate_rich_tui()
        
        # Generate requirements file
        files['requirements.txt'] = "rich>=13.0.0\ntextual>=0.41.0\n"
        
        return files
    
    def _generate_html_main(self) -> str:
        """Generate main HTML file"""
        title = self.ui_spec.title
        components_html = self._generate_components_html()
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
        </header>
        <main>
            <form id="mainForm" class="ui-form">
                {components_html}
            </form>
        </main>
        <footer>
            <button type="button" id="executeBtn" class="btn btn-primary">Execute</button>
            <div id="results" class="results"></div>
        </footer>
    </div>
    <script src="app.js"></script>
</body>
</html>"""
    
    def _generate_components_html(self) -> str:
        """Generate HTML for all components"""
        components_html = []
        
        for component in self.ui_spec.components:
            component_html = self._generate_single_component_html(component)
            components_html.append(component_html)
        
        return '\n'.join(components_html)
    
    def _generate_single_component_html(self, component: UIComponent) -> str:
        """Generate HTML for a single component"""
        component_id = f'id="{component.name}"'
        
        if component.type == ComponentType.FORM_INPUT:
            input_type = self._get_html_input_type(component)
            required = "required" if component.required else ""
            placeholder = f'placeholder="{component.placeholder}"' if component.placeholder else ""
            
            return f"""
            <div class="form-group">
                <label for="{component.name}">{component.label}:</label>
                <input type="{input_type}" {component_id} name="{component.name}" {required} {placeholder} class="form-control">
            </div>"""
        
        elif component.type == ComponentType.TEXT_AREA:
            required = "required" if component.required else ""
            placeholder = f'placeholder="{component.placeholder}"' if component.placeholder else ""
            
            return f"""
            <div class="form-group">
                <label for="{component.name}">{component.label}:</label>
                <textarea {component_id} name="{component.name}" {required} {placeholder} class="form-control" rows="4"></textarea>
            </div>"""
        
        elif component.type == ComponentType.SELECT:
            required = "required" if component.required else ""
            options_html = []
            
            if component.options:
                options_html.append('<option value="">Select an option...</option>')
                for option in component.options:
                    options_html.append(f'<option value="{option}">{option}</option>')
            else:
                options_html.append('<option value="">No options available</option>')
            
            return f"""
            <div class="form-group">
                <label for="{component.name}">{component.label}:</label>
                <select {component_id} name="{component.name}" {required} class="form-control">
                    {''.join(options_html)}
                </select>
            </div>"""
        
        elif component.type == ComponentType.CHECKBOX:
            checked = 'checked' if component.default_value else ""
            
            return f"""
            <div class="form-group">
                <label class="checkbox-label">
                    <input type="checkbox" {component_id} name="{component.name}" {checked} class="form-checkbox">
                    {component.label}
                </label>
            </div>"""
        
        elif component.type == ComponentType.RADIO:
            options_html = []
            for i, option in enumerate(component.options or []):
                checked = 'checked' if component.default_value == option else ""
                option_id = f"{component.name}_{i}"
                options_html.append(f"""
                <label class="radio-label">
                    <input type="radio" name="{component.name}" value="{option}" {checked} class="form-radio">
                    {option}
                </label>""")
            
            return f"""
            <div class="form-group">
                <div>{component.label}:</div>
                <div class="radio-group">
                    {''.join(options_html)}
                </div>
            </div>"""
        
        else:
            return f'<div class="form-group"><label>Unsupported component type: {component.type}</label></div>'
    
    def _get_html_input_type(self, component: UIComponent) -> str:
        """Determine HTML input type based on component data"""
        validation = component.validation or {}
        data_type = validation.get('type', 'text')
        
        if data_type == 'email':
            return 'email'
        elif data_type == 'url':
            return 'url'
        elif data_type == 'integer':
            return 'number'
        elif data_type == 'float':
            return 'number'
        elif data_type == 'file_path':
            return 'file'
        else:
            return 'text'
    
    def _generate_css_styles(self) -> str:
        """Generate CSS styles based on UISpec"""
        if not self.ui_spec.styling:
            return self._get_default_css()
        
        theme = self.ui_spec.styling.theme
        color_scheme = self.ui_spec.styling.color_scheme
        custom_css = self.ui_spec.styling.custom_css
        
        if theme == 'modern':
            css = self._get_modern_css(color_scheme)
        elif theme == 'terminal':
            css = self._get_terminal_css(color_scheme)
        else:
            css = self._get_default_css()
        
        if custom_css:
            css = css + '\n' + custom_css
        
        return css
    
    def _get_default_css(self) -> str:
        """Generate default CSS styles"""
        return """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f5f5f5;
    color: #333;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header h1 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
    margin-bottom: 30px;
}

.ui-form {
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #555;
}

.form-control {
    width: 100%;
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
    transition: border-color 0.3s;
}

.form-control:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 5px rgba(52,152,219,0.2);
}

.btn {
    background: #3498db;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
    transition: background-color 0.3s;
}

.btn:hover {
    background: #2980b9;
}

.btn-primary {
    background: #28a745;
}

.btn-primary:hover {
    background: #218838;
}

footer {
    margin-top: 30px;
    text-align: center;
}

.results {
    margin-top: 20px;
    padding: 15px;
    background: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 4px;
    display: none;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
}

.form-checkbox {
    margin: 0;
}

.radio-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.radio-label {
    display: flex;
    align-items: center;
    gap: 8px;
}

.form-radio {
    margin: 0;
}"""
    
    def _get_modern_css(self, color_scheme: Optional[str]) -> str:
        """Generate modern CSS styles"""
        base_css = self._get_default_css()
        
        if color_scheme == 'blue':
            return base_css
        elif color_scheme == 'green':
            accent_color = '#28a745'
            hover_color = '#1e7e34'
            return base_css.replace('#3498db', accent_color).replace('#2980b9', hover_color)
        else:
            return base_css
    
    def _get_terminal_css(self, color_scheme: Optional[str]) -> str:
        """Generate terminal-style CSS"""
        return """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Fira Code', 'Courier New', monospace;
    background-color: #1a1a1a;
    color: #00ff00;
    line-height: 1.4;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header h1 {
    color: #00ff00;
    text-shadow: 0 0 5px rgba(0,255,0,0.3);
    border-bottom: 2px solid #00ff00;
    padding-bottom: 10px;
    margin-bottom: 30px;
}

.ui-form {
    background: #0d0d0d;
    border: 1px solid #00ff00;
    border-radius: 0;
    padding: 20px;
    box-shadow: 0 0 10px rgba(0,255,0,0.1);
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: normal;
    color: #00ff00;
}

.form-control {
    width: 100%;
    padding: 10px;
    border: 1px solid #00ff00;
    border-radius: 0;
    background: #1a1a1a;
    color: #00ff00;
    font-family: 'Fira Code', monospace;
    font-size: 14px;
}

.form-control:focus {
    outline: none;
    border-color: #00ff00;
    box-shadow: 0 0 8px rgba(0,255,0,0.3);
}

.btn {
    background: #00ff00;
    color: #1a1a1a;
    padding: 10px 20px;
    border: 1px solid #00ff00;
    cursor: pointer;
    font-family: 'Fira Code', monospace;
    font-weight: bold;
    text-transform: uppercase;
}

.btn:hover {
    background: #00cc00;
}

footer {
    margin-top: 20px;
    text-align: center;
}

.results {
    margin-top: 15px;
    padding: 10px;
    background: #003300;
    border: 1px solid #00ff00;
    color: #00ff00;
    font-family: 'Fira Code', monospace;
}"""
    
    def _generate_js_logic(self) -> str:
        """Generate JavaScript logic for UI interactions"""
        component_validations = self._generate_js_validations()
        interaction_handlers = self._generate_js_interactions()
        
        data_binding_mapping = '\n'.join([f"    // {comp.name}: {comp.data_binding}" for comp in self.ui_spec.components if comp.data_binding])
        return f"""// Generated UI logic for {self.ui_spec.title}
document.addEventListener('DOMContentLoaded', function() {{
    const form = document.getElementById('mainForm');
    const executeBtn = document.getElementById('executeBtn');
    const resultsDiv = document.getElementById('results');
    
{data_binding_mapping}
    
    {component_validations}
    
    {interaction_handlers}
    
    executeBtn.addEventListener('click', function() {{
        if (validateForm()) {{
            executeModule();
        }}
    }});
    
    function validateForm() {{
        let isValid = true;
        const errors = [];
        
        {self._generate_js_validation_logic()}
        
        if (errors.length > 0) {{
            showErrors(errors);
            return false;
        }}
        
        hideErrors();
        return true;
    }}
    
    function showErrors(errors) {{
        resultsDiv.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
        resultsDiv.style.display = 'block';
    }}
    
    function hideErrors() {{
        resultsDiv.style.display = 'none';
    }}
    
    function executeModule() {{
        const formData = new FormData(form);
        const data = {{}};
        
        for (let [key, value] of formData.entries()) {{
            data[key] = value;
        }}
        
        // Call backend API
        fetch('/api/execute', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify(data)
        }})
        .then(response => response.json())
        .then(result => {{
            if (result.success) {{
                showResults(result.data);
            }} else {{
                showErrors([result.error]);
            }}
        }})
        .catch(error => {{
            showErrors(['Network error: ' + error.message]);
        }});
    }}
    
    function showResults(data) {{
        resultsDiv.innerHTML = '<div class="success">' + JSON.stringify(data, null, 2) + '</div>';
        resultsDiv.style.display = 'block';
    }}
}});"""
    
    def _generate_js_validations(self) -> str:
        """Generate JavaScript validation functions"""
        validations = []
        
        for component in self.ui_spec.components:
            if component.validation:
                js_validation = self._generate_component_validation(component)
                validations.append(js_validation)
        
        return '\n'.join(validations)
    
    def _generate_component_validation(self, component: UIComponent) -> str:
        """Generate validation for a single component"""
        validation_type = component.validation.get('type', 'text')
        component_id = component.name
        
        if validation_type == 'email':
            return f"""    function validate_{component_id}() {{
        const email = document.getElementById('{component_id}').value;
        const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
        return emailRegex.test(email);
    }}"""
        
        elif validation_type == 'integer':
            min_val = component.validation.get('min', 0)
            return f"""    function validate_{component_id}() {{
        const value = document.getElementById('{component_id}').value;
        const num = parseInt(value);
        return !isNaN(num) && num >= {min_val};
    }}"""
        
        elif validation_type == 'float':
            min_val = component.validation.get('min', 0)
            return f"""    function validate_{component_id}() {{
        const value = document.getElementById('{component_id}').value;
        const num = parseFloat(value);
        return !isNaN(num) && num >= {min_val};
    }}"""
        
        else:
            return f"""    function validate_{component_id}() {{
        const value = document.getElementById('{component_id}').value;
        return value.trim().length > 0;
    }}"""
    
    def _generate_js_validation_logic(self) -> str:
        """Generate main validation logic that calls component validators"""
        logic_parts = []
        
        for component in self.ui_spec.components:
            if component.validation:
                component_id = component.name
                logic_parts.append(f"        if (!validate_{component_id}()) {{ errors.push('Invalid {component.label}'); }}")
        
        return '\n'.join(logic_parts)
    
    def _generate_js_interactions(self) -> str:
        """Generate JavaScript interaction handlers"""
        interactions = []
        
        for interaction in self.ui_spec.interactions:
            if interaction.trigger == 'on_change':
                handler = self._generate_change_handler(interaction)
                interactions.append(handler)
        
        return '\n'.join(interactions)
    
    def _generate_change_handler(self, interaction) -> str:
        """Generate change event handler"""
        target = interaction.target
        action = interaction.action
        return f"""    document.addEventListener('change', function(e) {{
        if (e.target && e.target.name.includes('{target}')) {{
            // Real-time validation for {target}
            if (e.target.id.includes('{target}')) {{
                {action}();
            }}
        }}
    }});"""
    
    def _generate_package_json(self) -> str:
        """Generate package.json for web UI"""
        return json.dumps({
            "name": self.ui_spec.title.lower().replace(' ', '-'),
            "version": "1.0.0",
            "description": f"Generated UI for {self.ui_spec.title}",
            "main": "index.html",
            "scripts": {
                "start": "python -m http.server 8000"
            },
            "devDependencies": {},
            "metadata": self.ui_spec.metadata
        }, indent=2)
    
    def _generate_tkinter_gui(self) -> str:
        """Generate Tkinter GUI"""
        imports = ["import tkinter as tk", "from tkinter import ttk", "import json", "import sys"]
        component_widgets = []
        
        for component in self.ui_spec.components:
            widget = self._generate_tkinter_widget(component)
            component_widgets.append(widget)
        
        return f"""
#!/usr/bin/env python3
# Generated GUI for {self.ui_spec.title}

{chr(10).join(imports)}

class {self.ui_spec.title.replace(' ', '')}GUI:
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("{self.ui_spec.title}")
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        {chr(10).join(component_widgets)}
        
        # Execute button
        execute_btn = ttk.Button(main_frame, text="Execute", command=self.execute_module)
        execute_btn.grid(row={len(component_widgets)}, column=0, pady=10)
        
        # Results display
        self.results_text = tk.Text(main_frame, height=10, width=50)
        self.results_text.grid(row={len(component_widgets)+1}, column=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def execute_module(self):
        # Collect data from form
        data = {{}}
        
        {self._generate_tkinter_data_collection()}
        
        try:
            # Here you would call the actual module
            results = f"Module executed with data: {{json.dumps(data, indent=2)}}"
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, results)
        except Exception as e:
            error_msg = f"Error: {{str(e)}}"
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = {self.ui_spec.title.replace(' ', '')}GUI(root)
    root.mainloop()
"""
    
    def _generate_tkinter_widget(self, component: UIComponent) -> str:
        """Generate Tkinter widget for component"""
        row = self.ui_spec.components.index(component)
        
        if component.type == ComponentType.FORM_INPUT:
            return f'''        ttk.Label(main_frame, text="{component.label}:").grid(row={row}, column=0, sticky=tk.W, pady=2)
        self.{component.name}_var = tk.StringVar()
        {component.name}_entry = ttk.Entry(main_frame, textvariable=self.{component.name}_var)
        {component.name}_entry.grid(row={row}, column=1, sticky=(tk.W, tk.E), pady=2)'''
        
        elif component.type == ComponentType.TEXT_AREA:
            return f'''        ttk.Label(main_frame, text="{component.label}:").grid(row={row}, column=0, sticky=tk.NW, pady=2)
        self.{component.name}_var = tk.StringVar()
        {component.name}_text = tk.Text(main_frame, height=5, width=40)
        {component.name}_text.grid(row={row}, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)'''
        
        else:
            return f'''        ttk.Label(main_frame, text="{component.label}:").grid(row={row}, column=0, sticky=tk.W, pady=2)
        ttk.Label(main_frame, text="Unsupported component: {component.type}").grid(row={row}, column=1, sticky=tk.W)'''
    
    def _generate_tkinter_data_collection(self) -> str:
        """Generate data collection code for Tkinter"""
        collections = []
        
        for component in self.ui_spec.components:
            if component.type in [ComponentType.FORM_INPUT]:
                collections.append(f'        data["{component.name}"] = self.{component.name}_var.get()')
            elif component.type == ComponentType.TEXT_AREA:
                collections.append(f'        data["{component.name}"] = self.{component.name}_text.get("1.0", tk.END).strip()')
        
        return '\n'.join(collections)
    
    def _generate_rich_tui(self) -> str:
        """Generate terminal UI using rich/textual"""
        return f"""
#!/usr/bin/env python3
# Generated Terminal UI for {self.ui_spec.title}

import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm

class {self.ui_spec.title.replace(' ', '')}TUI:
    def __init__(self):
        self.console = Console()
        
    def run(self):
        self.console.print(Panel(f"[bold blue]{self.ui_spec.title}[/bold blue]", expand=False))
        
        data = {{}}
        
        {self._generate_rich_data_collection()}
        
        # Execute module
        self.console.print("\\n[bold green]Executing module...[/bold green]")
        
        try:
            # Here you would call the actual module
            result = json.dumps(data, indent=2)
            self.console.print(Panel(result, title="Results", border_style="green"))
        except Exception as e:
            self.console.print(f"[bold red]Error: {{str(e)}}[/bold red]")
    
    {self._generate_rich_input_methods()}

if __name__ == "__main__":
    app = {self.ui_spec.title.replace(' ', '')}TUI()
    app.run()
"""
    
    def _generate_rich_data_collection(self) -> str:
        """Generate data collection code for Rich TUI"""
        collections = []
        
        for component in self.ui_spec.components:
            if component.type == ComponentType.FORM_INPUT:
                collections.append(f'        data["{component.name}"] = Prompt.ask("[bold]{component.label}[/bold]")')
            elif component.type == ComponentType.TEXT_AREA:
                collections.append(f'        data["{component.name}"] = Prompt.ask("[bold]{component.label}[/bold]", multiline=True)')
            elif component.type == ComponentType.CHECKBOX:
                collections.append(f'        data["{component.name}"] = Confirm.ask("[bold]{component.label}[/bold]")')
        
        return '\n'.join(collections)
    
    def _generate_rich_input_methods(self) -> str:
        """Generate input method definitions for Rich TUI"""
        return ""  # Rich handles different input types natively
    
    def _generate_electron_main(self) -> str:
        """Generate Electron main.js"""
        return f"""const {{ app, BrowserWindow }} = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {{
    mainWindow = new BrowserWindow({{
        width: 1200,
        height: 800,
        webPreferences: {{
            nodeIntegration: true,
            contextIsolation: false
        }}
    }});
    
    mainWindow.loadFile(path.join(__dirname, 'index.html'));
    mainWindow.on('closed', () => {{
        mainWindow = null;
    }});
}}

app.whenReady().then(createWindow);"""
    
    def _generate_electron_preload(self) -> str:
        """Generate Electron preload script"""
        return f"""const {{ contextBridge, ipcRenderer }} = require('electron');

// Expose module functions to renderer process
contextBridge.exposeInMainWorld('executeModule', (data) => {{
    return ipcRenderer.invoke('execute-module', data);
}});"""
    
    def _generate_electron_html(self) -> str:
        """Generate Electron HTML (simpler than web)"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.ui_spec.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .form-group {{ margin-bottom: 15px; }}
        .btn {{ background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{self.ui_spec.title}</h1>
        <div id="ui-container"></div>
        <button class="btn" onclick="executeModule()">Execute</button>
    </div>
    <script src="preload.js"></script>
</body>
</html>"""
    
    def _generate_electron_package_json(self) -> str:
        """Generate Electron package.json"""
        return json.dumps({
            "name": self.ui_spec.title.lower().replace(' ', '-'),
            "version": "1.0.0",
            "description": f"Electron app for {self.ui_spec.title}",
            "main": "main.js",
            "scripts": {
                "start": "electron ."
            },
            "keywords": ["electron", "app"],
            "author": "Module Forge",
            "license": "MIT",
            "devDependencies": {
                "electron": "^22.0.0"
            }
        }, indent=2)
    
    def _generate_openapi_spec(self) -> str:
        """Generate OpenAPI specification"""
        paths = {}
        
        for component in self.ui_spec.components:
            paths[f"/execute"] = {
                "post": {
                    "summary": "Execute module with provided parameters",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        component.name: {
                                            "type": "string",
                                            "description": component.label
                                        }
                                        for component in self.ui_spec.components
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful execution",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        
        return json.dumps({
            "openapi": "3.0.0",
            "info": {
                "title": self.ui_spec.title,
                "version": "1.0.0",
                "description": f"Generated API for {self.ui_spec.title}"
            },
            "paths": paths
        }, indent=2)
    
    def _generate_swagger_html(self) -> str:
        """Generate Swagger UI HTML"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{self.ui_spec.title} API</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: './openapi.json',
                dom_id: '#swagger-ui'
            }});
        }};
    </script>
</body>
</html>"""


def save_ui_artifacts(ui_spec: UISpec, output_dir: str) -> Dict[str, str]:
    """Generate and save UI artifacts to output directory"""
    generator = UIGenerator(ui_spec)
    files = generator.generate(output_dir)
    
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = {}
    for filename, content in files.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        saved_files[filepath] = content
    
    return saved_files


def generate_ui_from_module_spec(module_spec: Dict[str, Any], 
                                ui_type: str = "web",
                                output_dir: str = "ui_output") -> Dict[str, str]:
    """
    Convenience function to generate UI directly from module specification.
    
    Args:
        module_spec: The module specification from module_designer
        ui_type: Target UI type ('web', 'cli_gui', 'desktop', 'api_docs', 'cli_tui')
        output_dir: Directory to save UI artifacts
    
    Returns:
        Dictionary mapping file paths to their content
    """
    from ironclad_ai_guardrails.ui_spec import transform_module_spec_to_ui_spec, UIType
    
    # Convert string ui_type to enum
    ui_type_enum = UIType(ui_type) if ui_type in UIType._value2member_map_ else UIType.WEB
    
    # Transform module spec to UI spec
    ui_spec = transform_module_spec_to_ui_spec(module_spec, ui_type_enum)
    
    # Generate UI artifacts
    return save_ui_artifacts(ui_spec, output_dir)