# TODO - for everyone: start migrating other handlers to bring relief to http_api.py
from typing import Optional, List

from inference.core.entities.responses.workflows import ExternalWorkflowsBlockSelectorDefinition, \
    ExternalBlockPropertyPrimitiveDefinition, UniversalQueryLanguageDescription, WorkflowsBlocksDescription
from inference.core.workflows.core_steps.common.query_language.introspection.core import \
    prepare_operations_descriptions, prepare_operators_descriptions
from inference.core.workflows.execution_engine.dynamic_blocks.block_assembler import compile_dynamic_blocks
from inference.core.workflows.execution_engine.dynamic_blocks.entities import DynamicBlockDefinition
from inference.core.workflows.execution_engine.introspection.blocks_loader import describe_available_blocks
from inference.core.workflows.execution_engine.introspection.connections_discovery import discover_blocks_connections


def handle_describe_workflows_blocks_request(
    dynamic_blocks_definitions: Optional[List[DynamicBlockDefinition]] = None
) -> WorkflowsBlocksDescription:
    if dynamic_blocks_definitions is None:
        dynamic_blocks_definitions = []
    dynamic_blocks = compile_dynamic_blocks(
        dynamic_blocks_definitions=dynamic_blocks_definitions,
    )
    blocks_description = describe_available_blocks(dynamic_blocks=dynamic_blocks)
    blocks_connections = discover_blocks_connections(
        blocks_description=blocks_description,
    )
    kinds_connections = {
        kind_name: [
            ExternalWorkflowsBlockSelectorDefinition(
                manifest_type_identifier=c.manifest_type_identifier,
                property_name=c.property_name,
                property_description=c.property_description,
                compatible_element=c.compatible_element,
                is_list_element=c.is_list_element,
                is_dict_element=c.is_dict_element,
            )
            for c in connections
        ]
        for kind_name, connections in blocks_connections.kinds_connections.items()
    }
    primitives_connections = [
        ExternalBlockPropertyPrimitiveDefinition(
            manifest_type_identifier=primitives_connection.manifest_type_identifier,
            property_name=primitives_connection.property_name,
            property_description=primitives_connection.property_description,
            type_annotation=primitives_connection.type_annotation,
        )
        for primitives_connection in blocks_connections.primitives_connections
    ]
    uql_operations_descriptions = prepare_operations_descriptions()
    uql_operators_descriptions = prepare_operators_descriptions()
    universal_query_language_description = (
        UniversalQueryLanguageDescription.from_internal_entities(
            operations_descriptions=uql_operations_descriptions,
            operators_descriptions=uql_operators_descriptions,
        )
    )
    return WorkflowsBlocksDescription(
        blocks=blocks_description.blocks,
        declared_kinds=blocks_description.declared_kinds,
        kinds_connections=kinds_connections,
        primitives_connections=primitives_connections,
        universal_query_language_description=universal_query_language_description,
        dynamic_block_definition_schema=DynamicBlockDefinition.schema()
    )