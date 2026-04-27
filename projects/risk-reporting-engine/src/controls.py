def control_gap(control_status: str) -> bool:
    return control_status.strip().lower() in {'missing', 'partial', 'weak'}
