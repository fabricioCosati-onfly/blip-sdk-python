from typing import Any, Dict, Optional
from datetime import timedelta

from lime_python import Command
from ..extension_base import ExtensionBase
from .uri_templates import UriTemplates


class BucketExtension(ExtensionBase):
    """Extension to handle blip bucket storage.
    
    This extension allows the manipulation of Blip Buckets for storing 
    JSON documents that can be used for sharing data between extensions 
    or storing contextual information about users.
    """

    async def get_async(
        self,
        id: str,
        **kwargs
    ) -> Command:
        """Gets an existing document from the bucket by the id.

        Args:
            id (str): The bucket identifier
            kwargs: any other optional parameter not covered by the method

        Raises:
            ValueError: If id is None or empty

        Returns:
            Command: Command response with the bucket value
        """
        if not id:
            raise ValueError("id cannot be None or empty")
            
        uri = self.build_uri(UriTemplates.BUCKET_ITEM, id)
        uri = self.build_resource_query(uri, kwargs)
        return await self.process_command_async(self.create_get_command(uri))

    async def get_ids_async(
        self,
        skip: int = 0, 
        take: int = 100,
        **kwargs
    ) -> Command:
        """Gets the stored documents ids.

        Args:
            skip (int): Number of documents to be skipped
            take (int): Number of documents to be returned
            kwargs: any other optional parameter not covered by the method

        Returns:
            Command: Command response with the bucket ids collection
        """
        uri = self.build_resource_query(
            UriTemplates.BUCKET,
            {
                '$skip': skip, 
                '$take': take,
                **kwargs
            }
        )
        return await self.process_command_async(self.create_get_command(uri))

    async def set_async(
        self,
        id: str,
        document: Any,
        expiration: Optional[timedelta] = None,
        type_n: str = None,
        **kwargs
    ) -> Command:
        """Stores a document in the bucket.

        Args:
            id (str): The bucket identifier
            document (Any): The document to be stored
            expiration (timedelta, optional): The expiration time
            type_n (str, optional): The MIME type of the document
            kwargs: any other optional parameter not covered by the method

        Raises:
            ValueError: If id is None or empty, or if document is None

        Returns:
            Command: Command response confirming the operation
        """
        if not id:
            raise ValueError("id cannot be None or empty")
        if document is None:
            raise ValueError("document cannot be None")
            
        uri = self.build_uri(UriTemplates.BUCKET_ITEM, id)
        
        if expiration:
            # Convert timedelta to milliseconds for the API
            query_params = {
                'expiration': int(expiration.total_seconds() * 1000),
                **kwargs
            }
            uri = self.build_resource_query(uri, query_params)
        elif kwargs:
            uri = self.build_resource_query(uri, kwargs)
            
        return await self.process_command_async(
            self.create_set_command(uri, document, type_n)
        )

    async def delete_async(
        self,
        id: str,
        **kwargs
    ) -> Command:
        """Deletes a document from the bucket.

        Args:
            id (str): The bucket identifier
            kwargs: any other optional parameter not covered by the method

        Raises:
            ValueError: If id is None or empty

        Returns:
            Command: Command response confirming the operation
        """
        if not id:
            raise ValueError("id cannot be None or empty")
            
        uri = self.build_uri(UriTemplates.BUCKET_ITEM, id)
        uri = self.build_resource_query(uri, kwargs)
        return await self.process_command_async(self.create_delete_command(uri))
        
    async def get_text_async(
        self,
        id: str,
        **kwargs
    ) -> str:
        """Gets an existing text from the bucket by the id.

        Args:
            id (str): The bucket identifier
            kwargs: any other optional parameter not covered by the method

        Returns:
            str: The stored text or None if not found
        """
        command = await self.get_async(id, **kwargs)
        if command and command.resource:
            return command.resource.get('text')
        return None

    async def set_text_async(
        self,
        id: str,
        text: str,
        expiration: Optional[timedelta] = None,
        **kwargs
    ) -> Command:
        """Stores a text in the bucket.

        Args:
            id (str): The bucket identifier
            text (str): The text to be stored
            expiration (timedelta, optional): The expiration time
            kwargs: any other optional parameter not covered by the method

        Returns:
            Command: Command response confirming the operation
        """
        if text is None:
            raise ValueError("text cannot be None")
            
        return await self.set_async(
            id,
            {'text': text},
            expiration,
            'text/plain',
            **kwargs
        )