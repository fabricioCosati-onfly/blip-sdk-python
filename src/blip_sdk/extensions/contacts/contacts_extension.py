from typing import Any, Dict, Optional

from lime_python import Command

from ..extension_base import ExtensionBase
from .content_types import ContentTypes
from .uri_templates import UriTemplates


class ContactsExtension(ExtensionBase):
    """Extension to handle contact operations in BLiP."""

    def __init__(self, client: Any) -> None:
        """Initialize a new instance of ContactsExtension.

        Args:
            client: The BLiP client
        """
        super().__init__(client, 'postmaster@crm.msging.net')

    async def get_async(
        self,
        identity: str,
        **kwargs
    ) -> Command:
        """Get a contact by identity.

        Args:
            identity (str): The contact identity
            kwargs: Any other optional parameters not covered by the method

        Returns:
            Command: The command result
        """
        uri = self.build_uri(UriTemplates.CONTACT, identity)
        uri = self.build_resource_query(uri, kwargs)
        return await self.process_command_async(self.create_get_command(uri))

    async def get_contacts_async(
        self,
        skip: Optional[int] = None,
        take: Optional[int] = None,
        **kwargs
    ) -> Command:
        """Get all contacts.

        Args:
            skip (int, optional): The number of contacts to skip
            take (int, optional): The number of contacts to take
            kwargs: Any other optional parameters not covered by the method

        Returns:
            Command: The command result
        """
        uri = self.build_resource_query(
            UriTemplates.CONTACTS,
            {
                '$skip': skip,
                '$take': take,
                **kwargs
            }
        )
        return await self.process_command_async(self.create_get_command(uri))

    async def set_async(
        self,
        identity: str,
        contact: Dict[str, Any],
        **kwargs
    ) -> Command:
        """Create or update a contact.

        Args:
            identity (str): The contact identity
            contact (Dict[str, Any]): The contact data to be set
            kwargs: Any other optional parameters not covered by the method

        Returns:
            Command: The command result
        """
        uri = self.build_uri(UriTemplates.CONTACT, identity)
        uri = self.build_resource_query(uri, kwargs)
        return await self.process_command_async(
            self.create_set_command(uri, contact, ContentTypes.CONTACT)
        )

    async def merge_async(
        self,
        identity: str,
        contact: Dict[str, Any],
        **kwargs
    ) -> Command:
        """Merge contact data with existing contact.

        Args:
            identity (str): The contact identity
            contact (Dict[str, Any]): The contact data to be merged
            kwargs: Any other optional parameters not covered by the method

        Returns:
            Command: The command result
        """
        uri = self.build_uri(UriTemplates.CONTACT, identity)
        uri = self.build_resource_query(uri, kwargs)
        return await self.process_command_async(
            self.create_merge_command(uri, contact, ContentTypes.CONTACT)
        )

    async def delete_async(
        self,
        identity: str,
        **kwargs
    ) -> Command:
        """Delete a contact.

        Args:
            identity (str): The contact identity
            kwargs: Any other optional parameters not covered by the method

        Returns:
            Command: The command result
        """
        uri = self.build_uri(UriTemplates.CONTACT, identity)
        uri = self.build_resource_query(uri, kwargs)
        return await self.process_command_async(self.create_delete_command(uri))