def format_output(original_value: float, original_unit: str, converted_value: float, target_unit: str) -> str:
    # Normalize units to first character uppercase
    if not original_unit or not target_unit:
        raise ValueError('Unit string cannot be empty.')
    orig_u = original_unit[0].upper()
    tgt_u = target_unit[0].upper()
    if orig_u not in ('C', 'F') or tgt_u not in ('C', 'F'):
        raise ValueError('Units must be C or F.')
    return f"{original_value:.2f} {orig_u} = {converted_value:.2f} {tgt_u}"
