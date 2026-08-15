# core/utils.py

def parse_percent_val(val_str):
    if not val_str or val_str in ["--", "Lure", "Special", "None"]:
        return None
    try:
        cleaned = str(val_str).replace("%", "").replace(",", ".").strip()
        return float(cleaned)
    except ValueError:
        return None

def format_rate(raw_val, is_horde, is_sweet_scent, horde_scale):
    if raw_val in ["Special", "Lure", "--", None]:
        return str(raw_val) if raw_val else "--"
    
    base_pct = parse_percent_val(raw_val)
    if base_pct is None:
        return str(raw_val)
        
    if is_horde and not is_sweet_scent:
        scaled = min(100.0, round(base_pct * horde_scale, 1))
        return f"{int(scaled)}%" if scaled.is_integer() else f"{scaled}%"
        
    return f"{raw_val}"

def clean_count(value):
    try:
        val = int(value)
        return max(0, val)
    except (ValueError, TypeError):
        return 0