from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Optional

from lime_python import Command, Node
from ..extension_base import ExtensionBase

if TYPE_CHECKING:
    from ...client import Client

DEFAULT_BUILDER_DOMAIN = "builder.msging.net"
POSTMASTER = "postmaster"


class BuilderExtension(ExtensionBase):
    """
    Provides chatbot builder functionality.
    """

    def __init__(self, client: Client, to: str = None) -> None:
        super().__init__(client, to)
        self._builder_address = Node(POSTMASTER, DEFAULT_BUILDER_DOMAIN, None)

    async def get_flow_async(self, flow_id: str) -> Dict:
        """
        Get a flow by ID.
        
        Args:
            flow_id: The flow ID
            
        Returns:
            Dict: The flow configuration
        """
        if not flow_id:
            raise ValueError("flowId cannot be null or empty")

        command = self.create_get_command(f"/flows/{flow_id}")
        command.to = self._builder_address
        
        result = await self.process_command_async(command)
        return result.resource if result.resource else {}

    async def set_flow_async(self, flow_data: Dict) -> None:
        """
        Set/Update a flow.
        
        Args:
            flow_data: The flow configuration data
        """
        if not flow_data:
            raise ValueError("flowData cannot be null")

        command = self.create_set_command("/flows", flow_data)
        command.to = self._builder_address
        
        await self.process_command_async(command)

    async def delete_flow_async(self, flow_id: str) -> None:
        """
        Delete a flow.
        
        Args:
            flow_id: The flow ID to delete
        """
        if not flow_id:
            raise ValueError("flowId cannot be null or empty")

        command = self.create_delete_command(f"/flows/{flow_id}")
        command.to = self._builder_address
        
        await self.process_command_async(command)

    async def get_flows_async(self, skip: int = 0, take: int = 100) -> list:
        """
        Get list of flows.
        
        Args:
            skip: Number of items to skip
            take: Number of items to take
            
        Returns:
            list: List of flows
        """
        uri = f"/flows?$skip={skip}&$take={take}"
        command = self.create_get_command(uri)
        command.to = self._builder_address
        
        result = await self.process_command_async(command)
        return self._parse_flows_response(result)

    def _parse_flows_response(self, result: Command) -> list:
        """Parse flows from command response."""
        if result.resource and isinstance(result.resource, dict):
            items = result.resource.get('items', [])
            return items
        return []