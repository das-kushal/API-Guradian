def extract_paths(spec):
    return spec.get("paths", {})


def extract_schemas(spec):
    return spec.get("components", {}).get("schemas", {})
