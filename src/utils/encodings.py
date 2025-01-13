def fix_encoding(text: str) -> str:
    """Исправляет некорректную кодировку текста"""
    if not isinstance(text, str):
        return text

    try:
        text = text.encode().decode('unicode-escape')
    except:
        pass

    try:
        return text.encode('latin1').decode('utf-8')
    except:
        try:
            return text.encode('cp1252').decode('utf-8')
        except:
            return text