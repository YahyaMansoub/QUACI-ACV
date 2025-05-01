def validate_csv_factors(uploaded_factors, space_factors):
    """Validate CSV columns match space's factor definition"""
    if len(uploaded_factors) != len(space_factors):
        raise ValueError(
            f"Expected {len(space_factors)} factors, got {len(uploaded_factors)}")

    if set(uploaded_factors) != set(space_factors):
        raise ValueError("Factor names don't match space definition")
