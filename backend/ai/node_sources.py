"""Apply published material-to-node rules consistently to rule/model evidence."""
from collections.abc import Mapping


def source_verdict(definition, material_type):
    """True: allowed; False: different source; None: material type is unknown."""
    if definition is None:
        return True
    mapping = getattr(material_type, 'date_node_map', None) or {}
    if isinstance(mapping, Mapping) and definition.code in mapping.values():
        return True  # An explicit per-material field mapping is the more specific rule.
    sources = getattr(definition, 'source_material_codes', None) or ()
    if not sources:
        return True  # Keep unrestricted custom/legacy node definitions working.
    code = getattr(material_type, 'code', None)
    if not code:
        return None
    return code in sources


def eligible_nodes(nodes, material_type):
    return [node for node in nodes if node.value_kind != 'DERIVED'
            and source_verdict(node, material_type) is not False]


def bound_sources(rows, nodes, material_type):
    from ai.date_evidence import REVIEW_PREFIX
    definitions = {node.code: node for node in nodes}
    for row in rows:
        if row.get('method') == 'MANUAL':
            continue
        verdict = source_verdict(definitions.get(row['node_code']), material_type)
        if verdict is not True:
            reason = '材料类型未明确，须确认日期所属节点' if verdict is None else '材料类型不在该节点的允许来源中，须核对归属'
            row['invalid_reason'] = REVIEW_PREFIX + reason
    return rows
