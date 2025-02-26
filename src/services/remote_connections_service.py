"""InfluxDB OSS API Service.

The InfluxDB v2 API provides a programmatic interface for all interactions with InfluxDB. Access the InfluxDB API using the `/api/v2/` endpoint.   # noqa: E501

OpenAPI spec version: 2.0.0
Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401

from influxdb_client.service._base_service import _BaseService


class RemoteConnectionsService(_BaseService):
    """NOTE: This class is auto generated by OpenAPI Generator.

    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        """RemoteConnectionsService - a operation defined in OpenAPI."""
        super().__init__(api_client)

    def delete_remote_connection_by_id(self, remote_id, **kwargs):
        """Delete a remote connection.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_remote_connection_by_id(remote_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str remote_id: (required)
        :param str zap_trace_span: OpenTracing span context
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.delete_remote_connection_by_id_with_http_info(
                remote_id,
                **kwargs,
            )
        else:
            return self.delete_remote_connection_by_id_with_http_info(
                remote_id,
                **kwargs,
            )

    def delete_remote_connection_by_id_with_http_info(
        self,
        remote_id,
        **kwargs,
    ):
        """Delete a remote connection.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_remote_connection_by_id_with_http_info(remote_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str remote_id: (required)
        :param str zap_trace_span: OpenTracing span context
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._delete_remote_connection_by_id_prepare(
            remote_id,
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/remotes/{remoteID}",
            "DELETE",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type=None,
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def delete_remote_connection_by_id_async(
        self,
        remote_id,
        **kwargs,
    ):
        """Delete a remote connection.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param str remote_id: (required)
        :param str zap_trace_span: OpenTracing span context
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._delete_remote_connection_by_id_prepare(
            remote_id,
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/remotes/{remoteID}",
            "DELETE",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type=None,
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _delete_remote_connection_by_id_prepare(self, remote_id, **kwargs):
        local_var_params = locals()

        all_params = ["remote_id", "zap_trace_span"]
        self._check_operation_params("delete_remote_connection_by_id", all_params, local_var_params)
        # verify the required parameter 'remote_id' is set
        if "remote_id" not in local_var_params or local_var_params["remote_id"] is None:
            msg = "Missing the required parameter `remote_id` when calling `delete_remote_connection_by_id`"
            raise ValueError(
                msg,
            )

        path_params = {}
        if "remote_id" in local_var_params:
            path_params["remoteID"] = local_var_params["remote_id"]

        query_params = []

        header_params = {}
        if "zap_trace_span" in local_var_params:
            header_params["Zap-Trace-Span"] = local_var_params["zap_trace_span"]

        body_params = None
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"],
        )

        return local_var_params, path_params, query_params, header_params, body_params

    def get_remote_connection_by_id(self, remote_id, **kwargs):
        """Retrieve a remote connection.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_remote_connection_by_id(remote_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str remote_id: (required)
        :param str zap_trace_span: OpenTracing span context
        :return: RemoteConnection
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.get_remote_connection_by_id_with_http_info(
                remote_id,
                **kwargs,
            )
        else:
            return self.get_remote_connection_by_id_with_http_info(
                remote_id,
                **kwargs,
            )

    def get_remote_connection_by_id_with_http_info(
        self,
        remote_id,
        **kwargs,
    ):
        """Retrieve a remote connection.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_remote_connection_by_id_with_http_info(remote_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str remote_id: (required)
        :param str zap_trace_span: OpenTracing span context
        :return: RemoteConnection
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_remote_connection_by_id_prepare(
            remote_id,
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/remotes/{remoteID}",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="RemoteConnection",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def get_remote_connection_by_id_async(self, remote_id, **kwargs):
        """Retrieve a remote connection.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param str remote_id: (required)
        :param str zap_trace_span: OpenTracing span context
        :return: RemoteConnection
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_remote_connection_by_id_prepare(
            remote_id,
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/remotes/{remoteID}",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="RemoteConnection",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _get_remote_connection_by_id_prepare(self, remote_id, **kwargs):
        local_var_params = locals()

        all_params = ["remote_id", "zap_trace_span"]
        self._check_operation_params("get_remote_connection_by_id", all_params, local_var_params)
        # verify the required parameter 'remote_id' is set
        if "remote_id" not in local_var_params or local_var_params["remote_id"] is None:
            msg = "Missing the required parameter `remote_id` when calling `get_remote_connection_by_id`"
            raise ValueError(
                msg,
            )

        path_params = {}
        if "remote_id" in local_var_params:
            path_params["remoteID"] = local_var_params["remote_id"]

        query_params = []

        header_params = {}
        if "zap_trace_span" in local_var_params:
            header_params["Zap-Trace-Span"] = local_var_params["zap_trace_span"]

        body_params = None
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"],
        )

        return local_var_params, path_params, query_params, header_params, body_params

    def get_remote_connections(self, org_id, **kwargs):
        """List all remote connections.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_remote_connections(org_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str org_id: The organization ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :param str name:
        :param str remote_url:
        :return: RemoteConnections
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.get_remote_connections_with_http_info(org_id, **kwargs)
        else:
            return self.get_remote_connections_with_http_info(org_id, **kwargs)

    def get_remote_connections_with_http_info(self, org_id, **kwargs):
        """List all remote connections.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_remote_connections_with_http_info(org_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str org_id: The organization ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :param str name:
        :param str remote_url:
        :return: RemoteConnections
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_remote_connections_prepare(
            org_id,
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/remotes",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="RemoteConnections",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def get_remote_connections_async(self, org_id, **kwargs):
        """List all remote connections.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param str org_id: The organization ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :param str name:
        :param str remote_url:
        :return: RemoteConnections
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_remote_connections_prepare(
            org_id,
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/remotes",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="RemoteConnections",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _get_remote_connections_prepare(self, org_id, **kwargs):
        local_var_params = locals()

        all_params = ["org_id", "zap_trace_span", "name", "remote_url"]
        self._check_operation_params("get_remote_connections", all_params, local_var_params)
        # verify the required parameter 'org_id' is set
        if "org_id" not in local_var_params or local_var_params["org_id"] is None:
            msg = "Missing the required parameter `org_id` when calling `get_remote_connections`"
            raise ValueError(
                msg,
            )

        path_params = {}

        query_params = []
        if "org_id" in local_var_params:
            query_params.append(("orgID", local_var_params["org_id"]))
        if "name" in local_var_params:
            query_params.append(("name", local_var_params["name"]))
        if "remote_url" in local_var_params:
            query_params.append(("remoteURL", local_var_params["remote_url"]))

        header_params = {}
        if "zap_trace_span" in local_var_params:
            header_params["Zap-Trace-Span"] = local_var_params["zap_trace_span"]

        body_params = None
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"],
        )

        return local_var_params, path_params, query_params, header_params, body_params

    def patch_remote_connection_by_id(
        self,
        remote_id,
        remote_connection_update_request,
        **kwargs,
    ):
        """Update a remote connection.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.patch_remote_connection_by_id(remote_id, remote_connection_update_request, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str remote_id: (required)
        :param RemoteConnectionUpdateRequest remote_connection_update_request: (required)
        :param str zap_trace_span: OpenTracing span context
        :return: RemoteConnection
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.patch_remote_connection_by_id_with_http_info(
                remote_id,
                remote_connection_update_request,
                **kwargs,
            )
        else:
            return self.patch_remote_connection_by_id_with_http_info(
                remote_id,
                remote_connection_update_request,
                **kwargs,
            )

    def patch_remote_connection_by_id_with_http_info(
        self,
        remote_id,
        remote_connection_update_request,
        **kwargs,
    ):
        """Update a remote connection.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.patch_remote_connection_by_id_with_http_info(remote_id, remote_connection_update_request, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str remote_id: (required)
        :param RemoteConnectionUpdateRequest remote_connection_update_request: (required)
        :param str zap_trace_span: OpenTracing span context
        :return: RemoteConnection
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._patch_remote_connection_by_id_prepare(
            remote_id,
            remote_connection_update_request,
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/remotes/{remoteID}",
            "PATCH",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="RemoteConnection",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def patch_remote_connection_by_id_async(
        self,
        remote_id,
        remote_connection_update_request,
        **kwargs,
    ):
        """Update a remote connection.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param str remote_id: (required)
        :param RemoteConnectionUpdateRequest remote_connection_update_request: (required)
        :param str zap_trace_span: OpenTracing span context
        :return: RemoteConnection
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._patch_remote_connection_by_id_prepare(
            remote_id,
            remote_connection_update_request,
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/remotes/{remoteID}",
            "PATCH",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="RemoteConnection",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _patch_remote_connection_by_id_prepare(
        self,
        remote_id,
        remote_connection_update_request,
        **kwargs,
    ):
        local_var_params = locals()

        all_params = [
            "remote_id",
            "remote_connection_update_request",
            "zap_trace_span",
        ]
        self._check_operation_params("patch_remote_connection_by_id", all_params, local_var_params)
        # verify the required parameter 'remote_id' is set
        if "remote_id" not in local_var_params or local_var_params["remote_id"] is None:
            msg = "Missing the required parameter `remote_id` when calling `patch_remote_connection_by_id`"
            raise ValueError(
                msg,
            )
        # verify the required parameter 'remote_connection_update_request' is set
        if (
            "remote_connection_update_request" not in local_var_params
            or local_var_params["remote_connection_update_request"] is None
        ):
            msg = "Missing the required parameter `remote_connection_update_request` when calling `patch_remote_connection_by_id`"
            raise ValueError(
                msg,
            )

        path_params = {}
        if "remote_id" in local_var_params:
            path_params["remoteID"] = local_var_params["remote_id"]

        query_params = []

        header_params = {}
        if "zap_trace_span" in local_var_params:
            header_params["Zap-Trace-Span"] = local_var_params["zap_trace_span"]

        body_params = None
        if "remote_connection_update_request" in local_var_params:
            body_params = local_var_params["remote_connection_update_request"]
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"],
        )

        # HTTP header `Content-Type`
        header_params["Content-Type"] = self.api_client.select_header_content_type(
            ["application/json"],
        )

        return local_var_params, path_params, query_params, header_params, body_params

    def post_remote_connection(
        self,
        remote_connection_creation_request,
        **kwargs,
    ):
        """Register a new remote connection.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_remote_connection(remote_connection_creation_request, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param RemoteConnectionCreationRequest remote_connection_creation_request: (required)
        :return: RemoteConnection
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.post_remote_connection_with_http_info(
                remote_connection_creation_request,
                **kwargs,
            )
        else:
            return self.post_remote_connection_with_http_info(
                remote_connection_creation_request,
                **kwargs,
            )

    def post_remote_connection_with_http_info(
        self,
        remote_connection_creation_request,
        **kwargs,
    ):
        """Register a new remote connection.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_remote_connection_with_http_info(remote_connection_creation_request, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param RemoteConnectionCreationRequest remote_connection_creation_request: (required)
        :return: RemoteConnection
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._post_remote_connection_prepare(
            remote_connection_creation_request,
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/remotes",
            "POST",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="RemoteConnection",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def post_remote_connection_async(
        self,
        remote_connection_creation_request,
        **kwargs,
    ):
        """Register a new remote connection.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param RemoteConnectionCreationRequest remote_connection_creation_request: (required)
        :return: RemoteConnection
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._post_remote_connection_prepare(
            remote_connection_creation_request,
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/remotes",
            "POST",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="RemoteConnection",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _post_remote_connection_prepare(
        self,
        remote_connection_creation_request,
        **kwargs,
    ):
        local_var_params = locals()

        all_params = ["remote_connection_creation_request"]
        self._check_operation_params("post_remote_connection", all_params, local_var_params)
        # verify the required parameter 'remote_connection_creation_request' is set
        if (
            "remote_connection_creation_request" not in local_var_params
            or local_var_params["remote_connection_creation_request"] is None
        ):
            msg = "Missing the required parameter `remote_connection_creation_request` when calling `post_remote_connection`"
            raise ValueError(
                msg,
            )

        path_params = {}

        query_params = []

        header_params = {}

        body_params = None
        if "remote_connection_creation_request" in local_var_params:
            body_params = local_var_params["remote_connection_creation_request"]
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"],
        )

        # HTTP header `Content-Type`
        header_params["Content-Type"] = self.api_client.select_header_content_type(
            ["application/json"],
        )

        return local_var_params, path_params, query_params, header_params, body_params
