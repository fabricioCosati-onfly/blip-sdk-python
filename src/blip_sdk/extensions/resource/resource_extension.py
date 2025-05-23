from typing import Any, Dict, Optional

from lime_python import Command

from ..extension_base import ExtensionBase
from .content_types import ContentTypes
from .uri_templates import UriTemplates


class ResourceExtension(ExtensionBase):
    """Extension to handle BLiP resources.
    
    This extension allows to get and set resources in a centralized BLiP location.
    """
    
    def __init__(self, client, to: str = "postmaster@msging.net"):
        """Initialize ResourceExtension with a client and destination.
        
        Args:
            client: The BLiP client
            to (str): The destination, defaults to "postmaster@msging.net"
        """
        super().__init__(client, to)
    
    async def get_async(self, id: str) -> Command:
        """Get a resource by ID.
        
        Args:
            id (str): The resource ID
            
        Returns:
            Command: The command response with the resource
        """
        if not id:
            raise ValueError("The 'id' parameter is required")
            
        uri = self.build_uri(UriTemplates.RESOURCE, id)
        return await self.process_command_async(self.create_get_command(uri))
    
    async def set_async(self, id: str, resource: Any) -> Command:
        """Set a resource with a specific ID.
        
        Args:
            id (str): The resource ID
            resource (Any): The resource to be set
            
        Returns:
            Command: The command response
        """
        if not id:
            raise ValueError("The 'id' parameter is required")
            
        if resource is None:
            raise ValueError("The 'resource' parameter is required")
            
        uri = self.build_uri(UriTemplates.RESOURCE, id)
        return await self.process_command_async(
            self.create_set_command(uri, resource, ContentTypes.RESOURCE)
        )
    
    async def delete_async(self, id: str) -> Command:
        """Delete a resource by ID.
        
        Args:
            id (str): The resource ID to be deleted
            
        Returns:
            Command: The command response
        """
        if not id:
            raise ValueError("The 'id' parameter is required")
            
        uri = self.build_uri(UriTemplates.RESOURCE, id)
        return await self.process_command_async(self.create_delete_command(uri))
    
    async def get_all_async(
        self, 
        take: Optional[int] = None, 
        skip: Optional[int] = None,
        **kwargs
    ) -> Command:
        """Get all resources with pagination.
        
        Args:
            take (int, optional): Limit of total of items to be returned.
                The maximum value allowed is 100
            skip (int, optional): The number of elements to be skipped
            kwargs: Any other optional parameters not covered by the method
            
        Returns:
            Command: The command response with the resources
        """
        uri = self.build_resource_query(
            UriTemplates.RESOURCES,
            {
                '$take': take,
                '$skip': skip,
                **kwargs
            }
        )
        return await self.process_command_async(self.create_get_command(uri))