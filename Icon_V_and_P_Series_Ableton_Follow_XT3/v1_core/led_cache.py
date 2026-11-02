# === CACHE ===
_cache = {}

def only_if_changed(key, new_values):
    if _cache.get(key) == new_values:
        return False
    _cache[key] = new_values
    return True

def clear():
    _cache.clear()
