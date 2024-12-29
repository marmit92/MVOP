def parse_dollar_value(value_str):
    """
    Odstrani $ in vejice ter pretvori v float.
    Primer: "$648,125" -> 648125.0
    Če vrednost ni ustrezna, vrne None.
    """
    if not value_str:
        return None
    clean_str = value_str.replace('$', '').replace(',', '')
    try:
        return float(clean_str)
    except ValueError:
        return None

def parse_percentage(value_str):
    """
    Odstrani % in pretvori v float.
    Primer: "32.8%" -> 32.8
    Če je "-", vrne 0 ali None (po izbiri).
    """
    if not value_str or value_str.strip() == '-':
        return 0.0
    clean_str = value_str.replace('%', '').replace(',', '')
    try:
        return float(clean_str)
    except ValueError:
        return None

def parse_int(value_str):
    """
    Npr. "2,100,000" -> 2100000
    """
    if not value_str:
        return None
    clean_str = value_str.replace(',', '')
    try:
        return int(clean_str)
    except ValueError:
        return None

def parse_number(value):
    """
    Pretvori niz z vejicami v celo število.
    Če je vrednost '-', vrne None.
    """
    if value == "-" or value is None:
        return None
    value = value.replace(",", "")
    try:
        return int(float(value))  # Pretvori v float najprej, nato v celo število
    except ValueError:
        return None
