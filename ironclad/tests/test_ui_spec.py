#!/usr/bin/env python3
"""
Test suite for UI Specification module
Tests the core data structures and transformation logic
"""

import pytest
import json
import re
from typing import Dict, Any
import sys
import os

from ironclad_ai_guardrails.ui_spec import (
    UIType, ComponentType, UIComponent, UIInteraction, UILayout, UIStyling, UISpec,
    UISpecValidationError, validate_component, validate_ui_spec,
    transform_module_spec_to_ui_spec, ui_spec_to_dict, ui_spec_to_json, ui_spec_from_dict
)


class TestUIComponent:
    """Test UIComponent dataclass and validation"""
    
    def test_valid_component_creation(self):
        """Test creating a valid UI component"""
        component = UIComponent(
            name="test_input",
            type=ComponentType.FORM_INPUT,
            data_binding="main.test_param",
            label="Test Parameter"
        )
        
        assert component.name == "test_input"
        assert component.type == ComponentType.FORM_INPUT
        assert component.data_binding == "main.test_param"
        assert component.label == "Test Parameter"
        assert component.required is True
        assert component.validation is None
    
    def test_component_with_options(self):
        """Test creating a component with options"""
        component = UIComponent(
            name="test_select",
            type=ComponentType.SELECT,
            data_binding="main.choice",
            label="Choice",
            options=["Option 1", "Option 2", "Option 3"]
        )
        
        assert component.options == ["Option 1", "Option 2", "Option 3"]
    
    def test_component_validation_empty_name(self):
        """Test validation of component with empty name"""
        component = UIComponent(
            name="",
            type=ComponentType.FORM_INPUT,
            data_binding="main.test",
            label="Test"
        )
        
        errors = validate_component(component)
        assert len(errors) == 1
        assert "Component name cannot be empty" in errors[0]
    
    def test_component_validation_empty_data_binding(self):
        """Test validation of component with empty data binding"""
        component = UIComponent(
            name="test",
            type=ComponentType.FORM_INPUT,
            data_binding="",
            label="Test"
        )
        
        errors = validate_component(component)
        assert len(errors) == 1
        assert "Component must have a data binding" in errors[0]
    
    def test_component_validation_invalid_data_binding_format(self):
        """Test validation of component with invalid data binding format"""
        component = UIComponent(
            name="test",
            type=ComponentType.FORM_INPUT,
            data_binding="invalid_format",
            label="Test"
        )
        
        errors = validate_component(component)
        assert len(errors) == 1
        assert "Invalid data binding format" in errors[0]
    
    def test_component_validation_select_without_options(self):
        """Test validation of SELECT component without options"""
        component = UIComponent(
            name="test_select",
            type=ComponentType.SELECT,
            data_binding="main.choice",
            label="Choice"
        )
        
        errors = validate_component(component)
        assert len(errors) == 1
        assert "SELECT component requires options" in errors[0]
    
    def test_component_validation_radio_without_options(self):
        """Test validation of RADIO component without options"""
        component = UIComponent(
            name="test_radio",
            type=ComponentType.RADIO,
            data_binding="main.choice",
            label="Choice"
        )
        
        errors = validate_component(component)
        assert len(errors) == 1
        assert "RADIO component requires options" in errors[0]


class TestUIInteraction:
    """Test UIInteraction dataclass"""
    
    def test_interaction_creation(self):
        """Test creating a valid UI interaction"""
        interaction = UIInteraction(
            trigger="button_click",
            action="call_module_function",
            target="main.execute",
            parameters={"validate_inputs": True}
        )
        
        assert interaction.trigger == "button_click"
        assert interaction.action == "call_module_function"
        assert interaction.target == "main.execute"
        assert interaction.parameters == {"validate_inputs": True}
    
    def test_interaction_without_parameters(self):
        """Test creating interaction without parameters"""
        interaction = UIInteraction(
            trigger="on_change",
            action="validate_input",
            target="test_param"
        )
        
        assert interaction.parameters is None


class TestUILayout:
    """Test UILayout dataclass"""
    
    def test_layout_creation(self):
        """Test creating a valid UI layout"""
        layout = UILayout(
            type="grid",
            columns=2,
            spacing="medium",
            alignment="center",
            responsive=True
        )
        
        assert layout.type == "grid"
        assert layout.columns == 2
        assert layout.spacing == "medium"
        assert layout.alignment == "center"
        assert layout.responsive is True
    
    def test_minimal_layout(self):
        """Test creating layout with minimal parameters"""
        layout = UILayout(type="vertical")
        
        assert layout.type == "vertical"
        assert layout.columns is None
        assert layout.spacing is None
        assert layout.alignment is None
        assert layout.responsive is True


class TestUIStyling:
    """Test UIStyling dataclass"""
    
    def test_styling_creation(self):
        """Test creating UI styling with all parameters"""
        styling = UIStyling(
            theme="modern",
            color_scheme="blue",
            font_size="16px",
            custom_css="/* Custom CSS */"
        )
        
        assert styling.theme == "modern"
        assert styling.color_scheme == "blue"
        assert styling.font_size == "16px"
        assert styling.custom_css == "/* Custom CSS */"
    
    def test_default_styling(self):
        """Test creating default styling"""
        styling = UIStyling()
        
        assert styling.theme == "default"
        assert styling.color_scheme is None
        assert styling.font_size is None
        assert styling.custom_css is None


class TestUISpec:
    """Test UISpec dataclass and validation"""
    
    def test_valid_ui_spec_creation(self):
        """Test creating a valid UI specification"""
        components = [
            UIComponent(
                name="input1",
                type=ComponentType.FORM_INPUT,
                data_binding="main.param1",
                label="Parameter 1"
            ),
            UIComponent(
                name="select1",
                type=ComponentType.SELECT,
                data_binding="main.choice",
                label="Choice",
                options=["A", "B", "C"]
            )
        ]
        
        layout = UILayout(type="grid", columns=2)
        interactions = [
            UIInteraction(
                trigger="button_click",
                action="execute",
                target="main.execute"
            )
        ]
        
        styling = UIStyling(theme="modern")
        
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="Test Interface",
            components=components,
            layout=layout,
            interactions=interactions,
            styling=styling,
            metadata={"version": "1.0"}
        )
        
        assert ui_spec.ui_type == UIType.WEB
        assert ui_spec.title == "Test Interface"
        assert len(ui_spec.components) == 2
        assert ui_spec.layout.type == "grid"
        assert len(ui_spec.interactions) == 1
        assert ui_spec.styling.theme == "modern"
        assert ui_spec.metadata["version"] == "1.0"
    
    def test_ui_spec_validation_empty_title(self):
        """Test validation of UI spec with empty title"""
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="",
            components=[],
            layout=UILayout(type="vertical")
        )
        
        errors = validate_ui_spec(ui_spec)
        assert "UI title cannot be empty" in errors
    
    def test_ui_spec_validation_no_components(self):
        """Test validation of UI spec with no components"""
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="Test",
            components=[],
            layout=UILayout(type="vertical")
        )
        
        errors = validate_ui_spec(ui_spec)
        assert "UI must have at least one component" in errors
    
    def test_ui_spec_validation_invalid_layout_type(self):
        """Test validation of UI spec with invalid layout type"""
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="Test",
            components=[
                UIComponent(
                    name="test",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.test",
                    label="Test"
                )
            ],
            layout=UILayout(type="invalid_layout")
        )
        
        errors = validate_ui_spec(ui_spec)
        assert "Invalid layout type" in errors


class TestModuleSpecTransformation:
    """Test transformation from ModuleSpec to UISpec"""
    
    def sample_module_spec(self) -> Dict[str, Any]:
        """Return a sample module specification for testing"""
        return {
            "module_name": "calculator",
            "main_logic_description": "Simple calculator with basic operations",
            "functions": [
                {
                    "name": "add",
                    "signature": "def add(a: int, b: int) -> int:",
                    "description": "Add two numbers"
                },
                {
                    "name": "subtract",
                    "signature": "def subtract(a: int, b: int) -> int:",
                    "description": "Subtract two numbers"
                },
                {
                    "name": "main",
                    "signature": "def main(operation: str, a: int, b: int) -> int:",
                    "description": "Main calculator function"
                }
            ]
        }
    
    def test_transform_module_spec_to_web_ui(self):
        """Test transforming module spec to web UI"""
        module_spec = self.sample_module_spec()
        ui_spec = transform_module_spec_to_ui_spec(module_spec, UIType.WEB)
        
        assert ui_spec.ui_type == UIType.WEB
        assert ui_spec.title == "Calculator Interface"
        assert len(ui_spec.components) > 0
        assert ui_spec.layout.type == "grid"
        assert ui_spec.styling.theme == "modern"
        assert ui_spec.metadata["module_name"] == "calculator"
    
    def test_transform_module_spec_to_cli_gui(self):
        """Test transforming module spec to CLI GUI"""
        module_spec = self.sample_module_spec()
        ui_spec = transform_module_spec_to_ui_spec(module_spec, UIType.CLI_GUI)
        
        assert ui_spec.ui_type == UIType.CLI_GUI
        assert ui_spec.styling.theme == "terminal"
        assert ui_spec.styling.color_scheme == "dark"
    
    def test_transform_module_spec_with_custom_title(self):
        """Test transforming module spec with custom UI title"""
        module_spec = self.sample_module_spec()
        custom_title = "Advanced Calculator UI"
        ui_spec = transform_module_spec_to_ui_spec(
            module_spec, 
            UIType.WEB, 
            ui_title=custom_title
        )
        
        assert ui_spec.title == custom_title
    
    def test_parameter_parsing(self):
        """Test parsing of function parameters"""
        module_spec = {
            "module_name": "test_module",
            "functions": [
                {
                    "name": "complex_function",
                    "signature": "def complex_function(name: str, age: int, active: bool, tags: List[str]) -> None:",
                    "description": "Function with various parameter types"
                }
            ]
        }
        
        ui_spec = transform_module_spec_to_ui_spec(module_spec, UIType.WEB)
        
        # Should have components for each parameter
        param_components = [c for c in ui_spec.components if "complex_function" in c.name]
        assert len(param_components) >= 4
        
        # Check parameter type mappings
        name_component = next((c for c in param_components if "name" in c.name), None)
        assert name_component is not None and name_component.type == ComponentType.TEXT_AREA
        
        age_component = next((c for c in param_components if "age" in c.name), None)
        assert age_component is not None and age_component.type == ComponentType.FORM_INPUT
        
        active_component = next((c for c in param_components if "active" in c.name), None)
        assert active_component is not None and active_component.type == ComponentType.CHECKBOX
    
    def test_module_spec_without_main_function(self):
        """Test transformation when module has no main function"""
        module_spec = {
            "module_name": "helper",
            "functions": [
                {
                    "name": "helper_function",
                    "signature": "def helper_function(param: str) -> str:",
                    "description": "Helper function"
                }
            ]
        }
        
        ui_spec = transform_module_spec_to_ui_spec(module_spec, UIType.WEB)
        
        # Should still create execution button
        execute_components = [c for c in ui_spec.components if "execute_button" in c.name]
        assert len(execute_components) == 1
        assert execute_components[0].data_binding == "execute"


class TestUISpecSerialization:
    """Test UISpec serialization and deserialization"""
    
    def create_sample_ui_spec(self) -> UISpec:
        """Create a sample UI spec for testing"""
        return UISpec(
            ui_type=UIType.WEB,
            title="Sample Interface",
            components=[
                UIComponent(
                    name="input_field",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.input",
                    label="Input Field",
                    validation={"type": "text", "min_length": 1},
                    required=True
                )
            ],
            layout=UILayout(type="vertical", spacing="medium"),
            interactions=[
                UIInteraction(
                    trigger="button_click",
                    action="execute",
                    target="main.execute"
                )
            ],
            styling=UIStyling(theme="modern", color_scheme="blue"),
            metadata={"version": "1.0", "author": "test"}
        )
    
    def test_ui_spec_to_dict(self):
        """Test converting UISpec to dictionary"""
        ui_spec = self.create_sample_ui_spec()
        data = ui_spec_to_dict(ui_spec)
        
        assert data["ui_type"] == "web"
        assert data["title"] == "Sample Interface"
        assert len(data["components"]) == 1
        assert data["layout"]["type"] == "vertical"
        assert len(data["interactions"]) == 1
        assert data["styling"]["theme"] == "modern"
        assert data["metadata"]["version"] == "1.0"
        
        # Check component serialization
        component = data["components"][0]
        assert component["name"] == "input_field"
        assert component["type"] == "form_input"
        assert component["data_binding"] == "main.input"
        assert component["validation"]["type"] == "text"
        assert component["required"] is True
    
    def test_ui_spec_to_json(self):
        """Test converting UISpec to JSON string"""
        ui_spec = self.create_sample_ui_spec()
        json_str = ui_spec_to_json(ui_spec)
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert data["title"] == "Sample Interface"
        assert data["ui_type"] == "web"
    
    def test_ui_spec_from_dict(self):
        """Test creating UISpec from dictionary"""
        original_spec = self.create_sample_ui_spec()
        data = ui_spec_to_dict(original_spec)
        restored_spec = ui_spec_from_dict(data)
        
        assert restored_spec.ui_type == original_spec.ui_type
        assert restored_spec.title == original_spec.title
        assert len(restored_spec.components) == len(original_spec.components)
        assert restored_spec.layout.type == original_spec.layout.type
        assert len(restored_spec.interactions) == len(original_spec.interactions)
        assert restored_spec.styling.theme == original_spec.styling.theme
        assert restored_spec.metadata == original_spec.metadata
    
    def test_ui_spec_from_dict_missing_required_field(self):
        """Test creating UISpec from dict missing required field"""
        incomplete_data = {
            "ui_type": "web",
            "title": "Test"
            # Missing components and layout
        }
        
        with pytest.raises(UISpecValidationError) as exc_info:
            ui_spec_from_dict(incomplete_data)
        
        assert "Missing required field" in str(exc_info.value)
    
    def test_ui_spec_from_dict_invalid_enum_value(self):
        """Test creating UISpec from dict with invalid enum value"""
        invalid_data = {
            "ui_type": "invalid_type",
            "title": "Test",
            "components": [],
            "layout": {"type": "vertical"}
        }
        
        with pytest.raises(ValueError) as exc_info:
            ui_spec_from_dict(invalid_data)
        
        assert "invalid_type" in str(exc_info.value)
    
    def test_round_trip_serialization(self):
        """Test full round-trip serialization"""
        original_spec = self.create_sample_ui_spec()
        
        # Convert to dict and back
        data = ui_spec_to_dict(original_spec)
        restored_spec = ui_spec_from_dict(data)
        
        # Convert to JSON and back
        json_str = ui_spec_to_json(restored_spec)
        json_data = json.loads(json_str)
        final_spec = ui_spec_from_dict(json_data)
        
        # Final spec should match original
        assert final_spec.ui_type == original_spec.ui_type
        assert final_spec.title == original_spec.title
        assert len(final_spec.components) == len(original_spec.components)


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_module_spec_transformation(self):
        """Test transforming empty module spec"""
        empty_spec = {
            "module_name": "empty",
            "functions": []
        }
        
        ui_spec = transform_module_spec_to_ui_spec(empty_spec, UIType.WEB)
        
        # Should still create a valid UI spec with execute button
        assert ui_spec.title == "Empty Interface"
        assert len(ui_spec.components) >= 1  # At least execute button
    
    def test_module_spec_with_invalid_signature(self):
        """Test transforming module spec with invalid function signature"""
        invalid_spec = {
            "module_name": "invalid",
            "functions": [
                {
                    "name": "bad_function",
                    "signature": "invalid signature without def",
                    "description": "Bad function"
                }
            ]
        }
        
        # Should handle gracefully and create UI anyway
        ui_spec = transform_module_spec_to_ui_spec(invalid_spec, UIType.WEB)
        assert ui_spec.ui_type == UIType.WEB
    
    def test_component_validation_edge_cases(self):
        """Test component validation with edge cases"""
        # Component with self parameter (should be ignored)
        component = UIComponent(
            name="test",
            type=ComponentType.FORM_INPUT,
            data_binding="main.self",  # This might be from self parameter
            label="Test"
        )
        
        errors = validate_component(component)
        # Should still validate format even if it's self
        assert len(errors) > 0 if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*$', component.data_binding) else len(errors) == 0
    
    def test_optional_parameter_handling(self):
        """Test handling of optional parameters"""
        module_spec = {
            "module_name": "test",
            "functions": [
                {
                    "name": "function_with_optionals",
                    "signature": "def function_with_optionals(required_param: str, optional_param: str = 'default') -> None:",
                    "description": "Function with optional parameters"
                }
            ]
        }
        
        ui_spec = transform_module_spec_to_ui_spec(module_spec, UIType.WEB)
        
        # Find the optional parameter component
        optional_component = next(
            (c for c in ui_spec.components if "optional_param" in c.name),
            None
        )
        
        if optional_component:
            # Optional parameter should not be required
            assert optional_component.required is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])