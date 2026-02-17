def compare_specs(old, new):

    old_paths = old.get("paths", {})
    new_paths = new.get("paths", {})

    removed_endpoints = []
    added_endpoints = []
    method_changes = []

    for path in old_paths:
        if path not in new_paths:
            removed_endpoints.append(path)
        else:
            old_methods = set(old_paths[path].keys())
            new_methods = set(new_paths[path].keys())

            removed_methods = old_methods - new_methods
            added_methods = new_methods - old_methods

            if removed_methods or added_methods:
                method_changes.append(
                    {
                        "path": path,
                        "removed_methods": list(removed_methods),
                        "added_methods": list(added_methods),
                    }
                )

    for path in new_paths:
        if path not in old_paths:
            added_endpoints.append(path)

    return {
        "removed_endpoints": removed_endpoints,
        "added_endpoints": added_endpoints,
        "method_changes": method_changes,
    }
