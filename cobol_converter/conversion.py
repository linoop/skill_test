import re
from gpt4all import GPT4All


def fix_java_code(java_code: str) -> str:
    incomplete_or_pattern = r'if\s*\(\s*([^=\)]+?)\s*==\s*("[^"]*")\s*\|\|\s*("[^"]*")\s*\)'
    
    def fix_incomplete_or(match):
        lhs = match.group(1).strip()
        value1 = match.group(2)
        value2 = match.group(3)
        return f'if({lhs}.equals({value1}) || {lhs}.equals({value2}))'
    
    java_code = re.sub(incomplete_or_pattern, fix_incomplete_or, java_code)
    
    lines = java_code.split('\n')
    for i, line in enumerate(lines):
        if '==' in line and '.equals(' not in line and 'if(' in line:
            lines[i] = re.sub(r'([^=\s]+(?:\.[^=\s]+)*(?:\(\))?)\s*==\s*("[^"]*")', r'\1.equals(\2)', line)
    
    java_code = '\n'.join(lines)
    incomplete_equals_pattern = r'(\w+(?:\.\w+)*(?:\(\))??)\.equals\(("[^"]*")\)\s*\|\|\s*("[^"]*")'
    
    def fix_incomplete_equals(match):
        lhs = match.group(1)
        value1 = match.group(2)
        value2 = match.group(3)
        return f'{lhs}.equals({value1}) || {lhs}.equals({value2})'
    
    java_code = re.sub(incomplete_equals_pattern, fix_incomplete_equals, java_code)
    
    return java_code


def handle_cobol_conversion_scenarios(cobol_code: str) -> tuple[str, list[str]]:
    logs = []
    java_lines = []
    
    # Scenario 1: Type casting issues
    numeric_var_pattern = r'^\s*(\d+)\s+([A-Z0-9\-]+)\s+PIC\s+9\([0-9]+\)(?:\s+VALUE\s+([0-9]+))?\s*\.'
    move_numeric_pattern = r'MOVE\s+[\'"](\d+)[\'"]\s+TO\s+([A-Z0-9\-]+)'
    string_var_pattern = r'^\s*(\d+)\s+([A-Z0-9\-]+)\s+PIC\s+X\(([0-9]+)\)(?:\s+VALUE\s+([A-Z0-9\'"]+))?\s*\.'
    
    lines = cobol_code.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Handle COPY REPLACING scenario
        copy_replacing_match = re.match(r'COPY\s+([A-Z0-9]+)\s+REPLACING\s+==:([A-Z0-9]+):==\s+BY\s+==([A-Z0-9]+)==', line)
        if copy_replacing_match:
            copybook_name = copy_replacing_match.group(1)
            token = copy_replacing_match.group(2)
            replacement = copy_replacing_match.group(3)
            
            logs.append(f"COPY REPLACING found: {copybook_name}, replacing :{token}: with {replacement}")
            
            java_lines.append(f"    // {line}")
            copybook_content = f"""    // === Copybook {copybook_name} content (:{token}: replaced with {replacement}) ===

    // === End of copybook {copybook_name} ==="""
            
            java_lines.append(copybook_content)
            i += 1
            continue
        
        # Handle numeric variable declarations
        numeric_match = re.match(numeric_var_pattern, line)
        if numeric_match:
            level = numeric_match.group(1)
            var_name = numeric_match.group(2)
            initial_value = numeric_match.group(3) or "0"
            
            java_var_name = var_name.lower().replace('-', '_')
            java_lines.append(f"    private int {java_var_name} = {initial_value}; // Level {level} numeric variable")
            logs.append(f"Converted numeric variable: {var_name} -> int {java_var_name}")
            i += 1
            continue
        
        # Handle string variable declarations
        string_match = re.match(string_var_pattern, line)
        if string_match:
            level = string_match.group(1)
            var_name = string_match.group(2)
            length = string_match.group(3)
            initial_value = string_match.group(4) or '""'
            
            if initial_value == 'SPACES':
                initial_value = '""'
            elif not initial_value.startswith('"'):
                initial_value = f'"{initial_value}"'
            
            java_var_name = var_name.lower().replace('-', '_')
            java_lines.append(f"    private String {java_var_name} = {initial_value}; // Level {level} string variable, length {length}")
            logs.append(f"Converted string variable: {var_name} -> String {java_var_name}")
            i += 1
            continue
        
        # Handle MOVE with type casting
        move_match = re.search(move_numeric_pattern, line)
        if move_match:
            numeric_value = move_match.group(1)
            target_var = move_match.group(2)
            java_var_name = target_var.lower().replace('-', '_')
            
            java_lines.append(f"    {java_var_name} = Integer.parseInt(\"{numeric_value}\"); // Type cast string to int")
            logs.append(f"Applied type casting: MOVE '{numeric_value}' TO {target_var}")
            i += 1
            continue
        
        if line and not line.startswith('*'):
            java_lines.append(f"    // {line}")
        
        i += 1
    
    # Scenario 3
    undeclared_vars = set()
    cobol_var_pattern = r'\b([A-Z][A-Z0-9\-]+)\b'
    cobol_keywords = {
        'COPY', 'REPLACING', 'MOVE', 'TO', 'IF', 'ELSE', 'END-IF', 'PERFORM', 
        'UNTIL', 'WHILE', 'DISPLAY', 'ACCEPT', 'COMPUTE', 'ADD', 'SUBTRACT',
        'MULTIPLY', 'DIVIDE', 'PIC', 'VALUE', 'SPACES', 'ZERO', 'ZEROS',
        'IDENTIFICATION', 'DATA', 'PROCEDURE', 'DIVISION', 'SECTION',
        'WORKING-STORAGE', 'PROGRAM-ID', 'STOP', 'RUN', 'BY', 'EQUAL'
    }
    procedure_section = False
    for line in lines:
        if 'PROCEDURE DIVISION' in line:
            procedure_section = True
            continue
        
        if procedure_section and any(stmt in line for stmt in ['MOVE', 'IF', 'PERFORM']):
            vars_in_line = re.findall(cobol_var_pattern, line)
            for var in vars_in_line:
                if (var not in cobol_keywords and 
                    len(var) > 3 and 
                    '-' in var and  # Likely a COBOL variable name
                    not var.endswith('-DIVISION') and
                    not var.endswith('-SECTION')):
                    undeclared_vars.add(var)
    
    if undeclared_vars:
        logs.append(f"Undeclared variables found: {', '.join(sorted(undeclared_vars))}")
        java_lines.insert(0, "    // === SYSVARS copybook - Undeclared variables ===")
        for var in sorted(undeclared_vars):
            java_var_name = var.lower().replace('-', '_')
            java_lines.append(f"    private String {java_var_name}; // Undeclared variable from SYSVARS")
        java_lines.append("    // === End SYSVARS ===")
    
    return '\n'.join(java_lines), logs


def _clean_ai_response(response: str) -> str:
    response = re.sub(r'```java\s*', '', response)
    response = re.sub(r'```\s*', '', response)
    lines = response.split('\n')
    java_lines = []
    in_class = False
    
    for line in lines:
        if any(skip_phrase in line.lower() for skip_phrase in [
            'here is the converted', 'note that', 'i\'ve used', 'the logic of',
            'fibonacci', 'scanner', 'console'
        ]):
            continue
        if 'class ' in line or 'public ' in line or 'private ' in line or in_class:
            in_class = True
            java_lines.append(line)
        elif line.strip().startswith('//') and in_class:
            java_lines.append(line)
        elif line.strip() and in_class and any(java_keyword in line for java_keyword in [
            '{', '}', 'System.out', 'return', 'if ', 'else', 'for', 'while'
        ]):
            java_lines.append(line)
    
    return '\n'.join(java_lines).strip()


def _apply_rule_based_fallback(cobol_code: str, logs: list) -> str:
    converted_content, conversion_logs = handle_cobol_conversion_scenarios(cobol_code)
    logs.extend(conversion_logs)
    java_code = f"""public class ConvertedCobol {{
{converted_content}

    public void processData() {{
        // Main processing logic converted from COBOL
        // TODO: Implement business logic
    }}
}}"""
    return java_code


def _build_gpt4all_prompt(cobol_code: str) -> str:
    return (
        "Convert this COBOL code to Java. Focus on data structures and business logic. "
        "Use proper Java syntax with classes, methods, and variables. "
        "Handle COPY statements, PIC clauses, and MOVE operations appropriately. "
        "Return only clean Java code without explanations.\n\n"
        f"COBOL:\n{cobol_code}\n\nJava:"
    )


def convert_cobol_to_java(cobol_code: str):
    logs: list[str] = []
    
    try:
        model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
        prompt = _build_gpt4all_prompt(cobol_code)
        with model.chat_session():
            response = model.generate(prompt, max_tokens=600, temp=0.1)
        java_code = _clean_ai_response(response)
    
        if not java_code or len(java_code) < 50 or 'fibonacci' in java_code.lower():
            logs.append('AI response was poor quality, using rule-based conversion.')
            java_code = _apply_rule_based_fallback(cobol_code, logs)
        else:
            logs.append('Converted using GPT4All Meta-Llama-3-8B model.')
            enhanced_content, scenario_logs = handle_cobol_conversion_scenarios(cobol_code)
            if enhanced_content.strip():
                # Inject COBOL-specific conversions into AI output
                java_code = java_code.replace('public class', enhanced_content + '\n\npublic class', 1)
                logs.extend(scenario_logs)
        java_code = fix_java_code(java_code)
        logs.append('Applied Java code fixes (string comparison, incomplete OR patterns).')
        
    except Exception as e:
        logs.append(f'GPT4All conversion failed: {e}')
        java_code = _apply_rule_based_fallback(cobol_code, logs)
        java_code = fix_java_code(java_code)
        logs.append('Applied Java code fixes to fallback conversion.')
    
    return java_code, '\n'.join(logs)

