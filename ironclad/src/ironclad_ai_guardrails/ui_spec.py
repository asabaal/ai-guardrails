#!/usr/bin/env python3
"""
UI Specification Module

Defines data structures and transformation logic for UI generation from ModuleSpec.
Maintains the same architectural purity as the rest of the Module Forge system.
"""

import json
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class UIType(Enum):
    """Supported UI target types"""
    WEB = "web"
    CLI_GUI = "cli_gui"
    DESKTOP = "desktop"
    API_DOCS = "api_docs"
    CLI_TUI = "cli_tui"


class ComponentType(Enum):
    """UI component types"""
    FORM_INPUT = "form_input"
    BUTTON = "button"
    DISPLAY = "display"
    TABLE = "table"
    SELECT = "select"
    TEXT_AREA = "text_area"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    PROGRESS_BAR = "progress_bar"
    ALERT = "alert"


@dataclass
class UIComponent:
    """Individual UI component specification"""
    name: str
    type: ComponentType
    data_binding: str  # Maps to module_spec.function.parameter
    label: str
    placeholder: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None
    layout: Optional[Dict[str, Any]] = None
    default_value: Optional[Any] = None
    required: bool = True
    options: Optional[List[str]] = None  # For select/radio/checkbox


@dataclass
class UIInteraction:
    """UI interaction specification"""
    trigger: str
    action: str
    target: str
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class UILayout:
    """UI layout specification"""
    type: str  # "grid", "flex", "vertical", "horizontal"
    columns: Optional[int] = None
    spacing: Optional[str] = None
    alignment: Optional[str] = None
    responsive: bool = True


@dataclass
class UIStyling:
    """UI styling specification"""
    theme: str = "default"
    color_scheme: Optional[str] = None
    font_size: Optional[str] = None
    custom_css: Optional[str] = None


@dataclass
class UISpec:
    """Complete UI specification"""
    ui_type: UIType
    title: str
    components: List[UIComponent]
    layout: UILayout
    interactions: List[UIInteraction] = field(default_factory=list)
    styling: Optional[UIStyling] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class UISpecValidationError(Exception):
    """Custom exception for UI specification validation errors"""
    pass


def validate_component(component: UIComponent) -> List[str]:
    """Validate a single UI component"""
    errors = []
    
    if not component.name:
        errors.append("Component name cannot be empty")
    
    if not component.data_binding:
        errors.append("Component must have a data binding")
    
    # Validate data binding format (module_spec.function.parameter or module.component)
    if component.data_binding and not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)+$', component.data_binding):
        errors.append(f"Invalid data binding format: {component.data_binding}")
    
    # Check for reserved keywords in the last part of the binding
    if component.data_binding:
        parts = component.data_binding.split('.')
        if parts and parts[-1] in ['self', 'class', 'def', 'return', 'import', 'from']:
            errors.append(f"Reserved keyword '{parts[-1]}' cannot be used in data binding")
    
    # Validate component type specific requirements
    if component.type in [ComponentType.SELECT, ComponentType.RADIO] and not component.options:
        errors.append(f"{component.type.name} component requires options")
    
    return errors


def validate_ui_spec(ui_spec: UISpec) -> List[str]:
    """Validate complete UI specification"""
    errors = []
    
    if not ui_spec.title:
        errors.append("UI title cannot be empty")
    
    if not ui_spec.components:
        errors.append("UI must have at least one component")
    
    # Validate each component
    for i, component in enumerate(ui_spec.components):
        component_errors = validate_component(component)
        for error in component_errors:
            errors.append(f"Component {i} ({component.name}): {error}")
    
    # Validate layout
    if ui_spec.layout and ui_spec.layout.type not in ["grid", "flex", "vertical", "horizontal"]:
        errors.append("Invalid layout type")
    
    return errors


def transform_module_spec_to_ui_spec(module_spec: Dict[str, Any], 
                                ui_type: UIType = UIType.WEB,
                                ui_title: Optional[str] = None) -> UISpec:
    """
    Transform ModuleSpec to UISpec using intelligent mapping rules.
    
    This is the core transformation function that bridges module functions to UI components.
    """
    
    module_name = module_spec.get('module_name', 'module')
    functions = module_spec.get('functions', [])
    main_logic = module_spec.get('main_logic_description', '')
    
    # Generate UI components from module functions
    components = []
    
    for func in functions:
        func_name = func['name']
        signature = func.get('signature', '')
        description = func.get('description', '')
        
        # Parse signature to extract parameters
        params = _parse_function_parameters(signature)
        
        # Create UI components for each parameter
        for param in params:
            component = _create_component_from_parameter(func_name, param, description)
            components.append(component)
    
    # Add execution components
    components.append(_create_execution_component(functions, ui_type))
    
    # Create layout based on UI type and number of components
    layout = _create_layout(ui_type, len(components))
    
    # Create interactions
    interactions = _create_interactions(functions)
    
    # Create styling
    styling = _create_styling(ui_type)
    
    # Build UISpec
    title = ui_title or f"{module_name.replace('_', ' ').title()} Interface"
    
    return UISpec(
        ui_type=ui_type,
        title=title,
        components=components,
        layout=layout,
        interactions=interactions,
        styling=styling,
        metadata={
            'module_name': module_name,
            'generated_from': 'module_spec',
            'component_count': len(components)
        }
    )


def _parse_function_parameters(signature: str) -> List[Dict[str, str]]:
    """Parse function signature to extract parameters with types"""
    # Simple regex-based parameter parsing
    # This is a simplified version - in production, use ast.parse for robustness
    param_match = re.search(r'def\s+\w+\s*\((.*?)\)', signature)
    if not param_match:
        return []
    
    params_str = param_match.group(1)
    if not params_str or params_str.strip() == '':
        return []
    
    # Split parameters and extract basic info
    params = []
    for param in params_str.split(','):
        param = param.strip()
        if param == 'self':
            continue
            
        # Extract parameter name and type
        if ':' in param:
            name, type_info = param.split(':', 1)
            name = name.strip()
            type_info = type_info.strip()
        else:
            name = param.strip()
            type_info = 'str'
        
        params.append({
            'name': name,
            'type': type_info,
            'param_str': param
        })
    
    return params


def _create_component_from_parameter(func_name: str, param: Dict[str, str], description: str) -> UIComponent:
    """Create UI component from function parameter"""
    param_name = param['name']
    param_type = param['type'].lower()
    
    # Initialize component placeholder
    component_placeholder = None
    
    # Map parameter types to UI component types
    if 'bool' in param_type:
        component_type = ComponentType.CHECKBOX
    elif 'str' in param_type:
        if 'path' in param_name.lower() or 'file' in param_name.lower():
            component_type = ComponentType.FORM_INPUT
            component_placeholder = f"Enter {param_name.replace('_', ' ')} path"
        else:
            component_type = ComponentType.TEXT_AREA
            component_placeholder = f"Enter {param_name.replace('_', ' ')}"
    elif 'int' in param_type or 'float' in param_type:
        component_type = ComponentType.FORM_INPUT
        component_placeholder = f"Enter {param_name.replace('_', ' ')}"
    elif 'list' in param_type:
        component_type = ComponentType.TEXT_AREA
        component_placeholder = f"Enter {param_name.replace('_', ' ')} (one per line)"
    else:
        component_type = ComponentType.FORM_INPUT
        component_placeholder = f"Enter {param_name.replace('_', ' ')}"
    
    # Create validation rules
    validation = _create_validation_rules(param_type, param_name)
    
    return UIComponent(
        name=f"{func_name}_{param_name}",
        type=component_type,
        data_binding=f"{func_name}.{param_name}",
        label=param_name.replace('_', ' ').title(),
        placeholder=component_placeholder,
        validation=validation,
        required=not param_name.startswith('optional_')
    )


def _create_execution_component(functions: List[Dict[str, Any]], ui_type: UIType) -> UIComponent:
    """Create the main execution component (button, etc.)"""
    has_main_function = any(func['name'] == 'main' for func in functions)
    
    if ui_type == UIType.WEB:
        return UIComponent(
            name="execute_button",
            type=ComponentType.BUTTON,
            data_binding="main.execute" if has_main_function else "execute",
            label="Execute",
            layout={"style": "primary", "size": "large"}
        )
    elif ui_type == UIType.CLI_GUI:
        return UIComponent(
            name="execute_button", 
            type=ComponentType.BUTTON,
            data_binding="main.execute" if has_main_function else "execute",
            label="Run"
        )
    else:
        return UIComponent(
            name="execute_button",
            type=ComponentType.BUTTON,
            data_binding="main.execute" if has_main_function else "execute",
            label="Execute"
        )


def _create_layout(ui_type: UIType, component_count: int) -> UILayout:
    """Create layout based on UI type and component count"""
    if component_count <= 3:
        return UILayout(type="vertical", spacing="medium")
    elif component_count <= 9:
        return UILayout(type="grid", columns=2, spacing="medium")
    else:
        return UILayout(type="flex", spacing="small")


def _create_interactions(functions: List[Dict[str, Any]]) -> List[UIInteraction]:
    """Create UI interactions from module functions"""
    interactions = []
    
    # Add execution interaction
    interactions.append(UIInteraction(
        trigger="button_click",
        action="call_module_function",
        target="main.execute",
        parameters={"validate_inputs": True}
    ))
    
    # Add function-specific interactions
    for func in functions:
        if func['name'] != 'main':
            interactions.append(UIInteraction(
                trigger="on_change",
                action="validate_input",
                target=func['name'],
                parameters={"real_time": True}
            ))
    
    return interactions


def _create_styling(ui_type: UIType) -> UIStyling:
    """Create styling based on UI type"""
    if ui_type == UIType.WEB:
        return UIStyling(
            theme="modern",
            color_scheme="blue",
            custom_css="/* Custom modern styling */"
        )
    elif ui_type == UIType.CLI_GUI:
        return UIStyling(
            theme="terminal",
            color_scheme="dark"
        )
    else:
        return UIStyling(theme="default")


def _create_validation_rules(param_type: str, param_name: str) -> Dict[str, Any]:
    """Create validation rules based on parameter type"""
    rules = {}
    
    param_lower = param_name.lower()
    
    if 'int' in param_type:
        rules.update({
            'type': 'integer',
            'min': 0,
            'required': not param_lower.startswith('optional_')
        })
    elif 'float' in param_type:
        rules.update({
            'type': 'float',
            'min': 0.0,
            'required': not param_lower.startswith('optional_')
        })
    elif 'str' in param_type:
        if 'email' in param_lower:
            rules.update({
                'type': 'email',
                'required': not param_lower.startswith('optional_')
            })
        elif 'url' in param_lower:
            rules.update({
                'type': 'url',
                'required': not param_lower.startswith('optional_')
            })
        else:
            rules.update({
                'type': 'text',
                'min_length': 1,
                'required': not param_lower.startswith('optional_')
            })
    elif 'bool' in param_type:
        rules.update({
            'type': 'boolean',
            'required': False
        })
    
    # Add path-specific validation
    if 'path' in param_lower or 'file' in param_lower:
        rules['file_path'] = True
    
    return rules


def ui_spec_to_dict(ui_spec: UISpec) -> Dict[str, Any]:
    """Convert UISpec to dictionary for JSON serialization"""
    return {
        'ui_type': ui_spec.ui_type.value,
        'title': ui_spec.title,
        'components': [
            {
                'name': comp.name,
                'type': comp.type.value,
                'data_binding': comp.data_binding,
                'label': comp.label,
                'placeholder': comp.placeholder,
                'validation': comp.validation,
                'layout': comp.layout,
                'default_value': comp.default_value,
                'required': comp.required,
                'options': comp.options
            }
            for comp in ui_spec.components
        ],
        'layout': {
            'type': ui_spec.layout.type,
            'columns': ui_spec.layout.columns,
            'spacing': ui_spec.layout.spacing,
            'alignment': ui_spec.layout.alignment,
            'responsive': ui_spec.layout.responsive
        },
        'interactions': [
            {
                'trigger': inter.trigger,
                'action': inter.action,
                'target': inter.target,
                'parameters': inter.parameters
            }
            for inter in ui_spec.interactions
        ],
        'styling': {
            'theme': ui_spec.styling.theme if ui_spec.styling else 'default',
            'color_scheme': ui_spec.styling.color_scheme,
            'font_size': ui_spec.styling.font_size,
            'custom_css': ui_spec.styling.custom_css
        } if ui_spec.styling else None,
        'metadata': ui_spec.metadata
    }


def ui_spec_to_json(ui_spec: UISpec, indent: int = 2) -> str:
    """Convert UISpec to JSON string"""
    return json.dumps(ui_spec_to_dict(ui_spec), indent=indent)


def ui_spec_from_dict(data: Dict[str, Any]) -> UISpec:
    """Create UISpec from dictionary (for loading from JSON)"""
    try:
        ui_type = UIType(data['ui_type'])
        layout_data = data['layout']
        layout = UILayout(
            type=layout_data['type'],
            columns=layout_data.get('columns'),
            spacing=layout_data.get('spacing'),
            alignment=layout_data.get('alignment'),
            responsive=layout_data.get('responsive', True)
        )
        
        styling_data = data.get('styling')
        styling = UIStyling(
            theme=styling_data.get('theme', 'default'),
            color_scheme=styling_data.get('color_scheme'),
            font_size=styling_data.get('font_size'),
            custom_css=styling_data.get('custom_css')
        ) if styling_data else None
        
        components = []
        for comp_data in data['components']:
            component = UIComponent(
                name=comp_data['name'],
                type=ComponentType(comp_data['type']),
                data_binding=comp_data['data_binding'],
                label=comp_data['label'],
                placeholder=comp_data.get('placeholder'),
                validation=comp_data.get('validation'),
                layout=comp_data.get('layout'),
                default_value=comp_data.get('default_value'),
                required=comp_data.get('required', True),
                options=comp_data.get('options')
            )
            components.append(component)
        
        interactions = []
        for inter_data in data.get('interactions', []):
            interaction = UIInteraction(
                trigger=inter_data['trigger'],
                action=inter_data['action'],
                target=inter_data['target'],
                parameters=inter_data.get('parameters')
            )
            interactions.append(interaction)
        
        return UISpec(
            ui_type=ui_type,
            title=data['title'],
            components=components,
            layout=layout,
            interactions=interactions,
            styling=styling,
            metadata=data.get('metadata', {})
        )
        
    except KeyError as e:
        raise UISpecValidationError(f"Missing required field in UISpec data: {e}")
    except ValueError as e:
        raise