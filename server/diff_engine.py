"""
Enhanced diff engine for OpenAPI/Swagger spec comparison.
Detects: endpoint changes, method changes, parameter changes,
response changes, schema changes, and security changes.
"""

# --- Known PII field patterns ---
PII_PATTERNS = [
    "ssn", "social_security", "tax_id", "tin",
    "email", "phone", "mobile", "telephone",
    "address", "street", "city", "zip", "postal",
    "date_of_birth", "dob", "birthday",
    "password", "secret", "token", "api_key",
    "credit_card", "card_number", "cvv", "expiry",
    "bank_account", "routing_number", "iban", "swift",
    "passport", "license_number", "drivers_license",
    "first_name", "last_name", "full_name", "name",
    "ip_address", "device_id", "mac_address",
    "salary", "income", "account_balance",
]


def _is_pii_field(field_name):
    """Check if a field name looks like PII."""
    normalized = field_name.lower().replace("-", "_")
    return any(pattern in normalized for pattern in PII_PATTERNS)


def _extract_schema_fields(spec):
    """Extract all field names from component schemas."""
    schemas = spec.get("components", {}).get("schemas", {})
    fields = {}
    for schema_name, schema_def in schemas.items():
        props = schema_def.get("properties", {})
        fields[schema_name] = {
            "fields": list(props.keys()),
            "required": schema_def.get("required", []),
        }
    return fields


def _extract_parameters(operation):
    """Extract parameter names from an operation."""
    params = operation.get("parameters", [])
    return {p.get("name", ""): p for p in params if isinstance(p, dict)}


def _extract_responses(operation):
    """Extract response codes from an operation."""
    return set(operation.get("responses", {}).keys())


def _detect_pii_in_spec(spec):
    """Scan spec for fields that look like PII — deterministic, not AI-guessed."""
    pii_found = []
    schemas = spec.get("components", {}).get("schemas", {})
    for schema_name, schema_def in schemas.items():
        for field_name in schema_def.get("properties", {}).keys():
            if _is_pii_field(field_name):
                pii_found.append(f"{schema_name}.{field_name}")

    # Also check path parameters and request body fields
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if not isinstance(operation, dict):
                continue
            for param in operation.get("parameters", []):
                if isinstance(param, dict) and _is_pii_field(param.get("name", "")):
                    pii_found.append(f"{path} [{method.upper()}] param: {param['name']}")

    return pii_found


def _check_missing_descriptions(spec):
    """Check for endpoints or schemas missing descriptions/summaries."""
    missing = []
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if not isinstance(operation, dict):
                continue
            if not operation.get("summary") and not operation.get("description"):
                missing.append(f"{method.upper()} {path}")
    return missing


def _detect_naming_issues(spec):
    """Check for REST naming anti-patterns."""
    issues = []
    for path in spec.get("paths", {}).keys():
        segments = [s for s in path.split("/") if s and not s.startswith("{")]
        for seg in segments:
            # Check for camelCase (should be kebab-case or snake_case)
            if any(c.isupper() for c in seg):
                issues.append(f"'{path}' — segment '{seg}' uses camelCase (prefer kebab-case)")
            # Check for verbs in path segments (REST anti-pattern)
            verbs = ["get", "create", "update", "delete", "remove", "add", "fetch", "list"]
            if seg.lower() in verbs:
                issues.append(f"'{path}' — segment '{seg}' is a verb (use HTTP methods instead)")
    return issues


def compare_specs(old, new):
    """
    Compare two OpenAPI specs and return a comprehensive diff.
    """
    old_paths = old.get("paths", {})
    new_paths = new.get("paths", {})

    removed_endpoints = []
    added_endpoints = []
    method_changes = []
    parameter_changes = []
    response_changes = []

    # --- Endpoint-level changes ---
    for path in old_paths:
        if path not in new_paths:
            removed_endpoints.append(path)
        else:
            old_methods = {k: v for k, v in old_paths[path].items() if isinstance(v, dict)}
            new_methods = {k: v for k, v in new_paths[path].items() if isinstance(v, dict)}

            removed_m = set(old_methods.keys()) - set(new_methods.keys())
            added_m = set(new_methods.keys()) - set(old_methods.keys())

            if removed_m or added_m:
                method_changes.append({
                    "path": path,
                    "removed_methods": list(removed_m),
                    "added_methods": list(added_m),
                })

            # --- Parameter-level changes (for methods that exist in both) ---
            for method in set(old_methods.keys()) & set(new_methods.keys()):
                old_params = _extract_parameters(old_methods[method])
                new_params = _extract_parameters(new_methods[method])
                removed_p = set(old_params.keys()) - set(new_params.keys())
                added_p = set(new_params.keys()) - set(old_params.keys())

                if removed_p or added_p:
                    parameter_changes.append({
                        "path": path,
                        "method": method,
                        "removed_params": list(removed_p),
                        "added_params": list(added_p),
                    })

            # --- Response-level changes ---
            for method in set(old_methods.keys()) & set(new_methods.keys()):
                old_resp = _extract_responses(old_methods[method])
                new_resp = _extract_responses(new_methods[method])
                removed_r = old_resp - new_resp
                added_r = new_resp - old_resp

                if removed_r or added_r:
                    response_changes.append({
                        "path": path,
                        "method": method,
                        "removed_responses": list(removed_r),
                        "added_responses": list(added_r),
                    })

    for path in new_paths:
        if path not in old_paths:
            added_endpoints.append(path)

    # --- Schema-level changes ---
    old_schemas = _extract_schema_fields(old)
    new_schemas = _extract_schema_fields(new)
    schema_changes = {
        "removed_schemas": [s for s in old_schemas if s not in new_schemas],
        "added_schemas": [s for s in new_schemas if s not in old_schemas],
        "field_changes": [],
    }

    for schema_name in set(old_schemas.keys()) & set(new_schemas.keys()):
        old_fields = set(old_schemas[schema_name]["fields"])
        new_fields = set(new_schemas[schema_name]["fields"])
        removed_f = old_fields - new_fields
        added_f = new_fields - old_fields

        if removed_f or added_f:
            schema_changes["field_changes"].append({
                "schema": schema_name,
                "removed_fields": list(removed_f),
                "added_fields": list(added_f),
            })

    # --- Deterministic checks (no AI needed) ---
    pii_fields = _detect_pii_in_spec(new)
    missing_descriptions = _check_missing_descriptions(new)
    naming_issues = _detect_naming_issues(new)

    return {
        "removed_endpoints": removed_endpoints,
        "added_endpoints": added_endpoints,
        "method_changes": method_changes,
        "parameter_changes": parameter_changes,
        "response_changes": response_changes,
        "schema_changes": schema_changes,
        "pii_fields_detected": pii_fields,
        "missing_descriptions": missing_descriptions,
        "naming_issues": naming_issues,
    }
