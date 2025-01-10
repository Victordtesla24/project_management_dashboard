"""InfluxDB OSS API Service.

The InfluxDB v2 API provides a programmatic interface for all interactions with InfluxDB. Access the InfluxDB API using the `/api/v2/` endpoint.   # noqa: E501

OpenAPI spec version: 2.0.0
Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401

from influxdb_client.service._base_service import _BaseService


class SourcesService(_BaseService):
    """NOTE: This class is auto generated by OpenAPI Generator.

    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        """SourcesService - a operation defined in OpenAPI."""
        super().__init__(api_client)

    def delete_sources_id(self, source_id, **kwargs):
        """Delete a source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_sources_id(source_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.delete_sources_id_with_http_info(source_id, **kwargs)
        else:
            return self.delete_sources_id_with_http_info(source_id, **kwargs)

    def delete_sources_id_with_http_info(self, source_id, **kwargs):
        """Delete a source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_sources_id_with_http_info(source_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str source_id: The source ID. (required)
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
        ) = self._delete_sources_id_prepare(
            source_id,
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/sources/{sourceID}",
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

    async def delete_sources_id_async(self, source_id, **kwargs):
        """Delete a source.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param str source_id: The source ID. (required)
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
        ) = self._delete_sources_id_prepare(
            source_id,
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/sources/{sourceID}",
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

    def _delete_sources_id_prepare(self, source_id, **kwargs):
        local_var_params = locals()

        all_params = ["source_id", "zap_trace_span"]
        self._check_operation_params("delete_sources_id", all_params, local_var_params)
        # verify the required parameter 'source_id' is set
        if "source_id" not in local_var_params or local_var_params["source_id"] is None:
            msg = "Missing the required parameter `source_id` when calling `delete_sources_id`"
            raise ValueError(
                msg,
            )

        path_params = {}
        if "source_id" in local_var_params:
            path_params["sourceID"] = local_var_params["source_id"]

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

    def get_sources(self, **kwargs):
        """List all sources.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_sources(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str zap_trace_span: OpenTracing span context
        :param str org: The name of the organization.
        :return: Sources
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.get_sources_with_http_info(**kwargs)
        else:
            return self.get_sources_with_http_info(**kwargs)

    def get_sources_with_http_info(self, **kwargs):
        """List all sources.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_sources_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str zap_trace_span: OpenTracing span context
        :param str org: The name of the organization.
        :return: Sources
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_sources_prepare(
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/sources",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="Sources",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def get_sources_async(self, **kwargs):
        """List all sources.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param str zap_trace_span: OpenTracing span context
        :param str org: The name of the organization.
        :return: Sources
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_sources_prepare(
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/sources",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="Sources",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _get_sources_prepare(self, **kwargs):
        local_var_params = locals()

        all_params = ["zap_trace_span", "org"]
        self._check_operation_params("get_sources", all_params, local_var_params)

        path_params = {}

        query_params = []
        if "org" in local_var_params:
            query_params.append(("org", local_var_params["org"]))

        header_params = {}
        if "zap_trace_span" in local_var_params:
            header_params["Zap-Trace-Span"] = local_var_params["zap_trace_span"]

        body_params = None
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"],
        )

        return local_var_params, path_params, query_params, header_params, body_params

    def get_sources_id(self, source_id, **kwargs):
        """Retrieve a source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_sources_id(source_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :return: Source
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.get_sources_id_with_http_info(source_id, **kwargs)
        else:
            return self.get_sources_id_with_http_info(source_id, **kwargs)

    def get_sources_id_with_http_info(self, source_id, **kwargs):
        """Retrieve a source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_sources_id_with_http_info(source_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :return: Source
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_sources_id_prepare(
            source_id,
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/sources/{sourceID}",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="Source",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def get_sources_id_async(self, source_id, **kwargs):
        """Retrieve a source.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :return: Source
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_sources_id_prepare(
            source_id,
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/sources/{sourceID}",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="Source",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _get_sources_id_prepare(self, source_id, **kwargs):
        local_var_params = locals()

        all_params = ["source_id", "zap_trace_span"]
        self._check_operation_params("get_sources_id", all_params, local_var_params)
        # verify the required parameter 'source_id' is set
        if "source_id" not in local_var_params or local_var_params["source_id"] is None:
            msg = "Missing the required parameter `source_id` when calling `get_sources_id`"
            raise ValueError(
                msg,
            )

        path_params = {}
        if "source_id" in local_var_params:
            path_params["sourceID"] = local_var_params["source_id"]

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

    def get_sources_id_buckets(self, source_id, **kwargs):
        """Get buckets in a source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_sources_id_buckets(source_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :param str org: The name of the organization.
        :return: Buckets
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.get_sources_id_buckets_with_http_info(source_id, **kwargs)
        else:
            return self.get_sources_id_buckets_with_http_info(source_id, **kwargs)

    def get_sources_id_buckets_with_http_info(self, source_id, **kwargs):
        """Get buckets in a source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_sources_id_buckets_with_http_info(source_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :param str org: The name of the organization.
        :return: Buckets
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_sources_id_buckets_prepare(
            source_id,
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/sources/{sourceID}/buckets",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="Buckets",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def get_sources_id_buckets_async(self, source_id, **kwargs):
        """Get buckets in a source.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :param str org: The name of the organization.
        :return: Buckets
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_sources_id_buckets_prepare(
            source_id,
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/sources/{sourceID}/buckets",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="Buckets",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _get_sources_id_buckets_prepare(self, source_id, **kwargs):
        local_var_params = locals()

        all_params = ["source_id", "zap_trace_span", "org"]
        self._check_operation_params("get_sources_id_buckets", all_params, local_var_params)
        # verify the required parameter 'source_id' is set
        if "source_id" not in local_var_params or local_var_params["source_id"] is None:
            msg = "Missing the required parameter `source_id` when calling `get_sources_id_buckets`"
            raise ValueError(
                msg,
            )

        path_params = {}
        if "source_id" in local_var_params:
            path_params["sourceID"] = local_var_params["source_id"]

        query_params = []
        if "org" in local_var_params:
            query_params.append(("org", local_var_params["org"]))

        header_params = {}
        if "zap_trace_span" in local_var_params:
            header_params["Zap-Trace-Span"] = local_var_params["zap_trace_span"]

        body_params = None
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"],
        )

        return local_var_params, path_params, query_params, header_params, body_params

    def get_sources_id_health(self, source_id, **kwargs):
        """Get the health of a source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_sources_id_health(source_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :return: HealthCheck
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.get_sources_id_health_with_http_info(source_id, **kwargs)
        else:
            return self.get_sources_id_health_with_http_info(source_id, **kwargs)

    def get_sources_id_health_with_http_info(self, source_id, **kwargs):
        """Get the health of a source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_sources_id_health_with_http_info(source_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :return: HealthCheck
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_sources_id_health_prepare(
            source_id,
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/sources/{sourceID}/health",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="HealthCheck",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def get_sources_id_health_async(self, source_id, **kwargs):
        """Get the health of a source.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param str zap_trace_span: OpenTracing span context
        :return: HealthCheck
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_sources_id_health_prepare(
            source_id,
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/sources/{sourceID}/health",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="HealthCheck",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _get_sources_id_health_prepare(self, source_id, **kwargs):
        local_var_params = locals()

        all_params = ["source_id", "zap_trace_span"]
        self._check_operation_params("get_sources_id_health", all_params, local_var_params)
        # verify the required parameter 'source_id' is set
        if "source_id" not in local_var_params or local_var_params["source_id"] is None:
            msg = "Missing the required parameter `source_id` when calling `get_sources_id_health`"
            raise ValueError(
                msg,
            )

        path_params = {}
        if "source_id" in local_var_params:
            path_params["sourceID"] = local_var_params["source_id"]

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

    def patch_sources_id(self, source_id, source, **kwargs):
        """Update a Source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.patch_sources_id(source_id, source, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param Source source: Source update (required)
        :param str zap_trace_span: OpenTracing span context
        :return: Source
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.patch_sources_id_with_http_info(source_id, source, **kwargs)
        else:
            return self.patch_sources_id_with_http_info(source_id, source, **kwargs)

    def patch_sources_id_with_http_info(self, source_id, source, **kwargs):
        """Update a Source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.patch_sources_id_with_http_info(source_id, source, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param Source source: Source update (required)
        :param str zap_trace_span: OpenTracing span context
        :return: Source
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._patch_sources_id_prepare(
            source_id,
            source,
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/sources/{sourceID}",
            "PATCH",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="Source",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def patch_sources_id_async(self, source_id, source, **kwargs):
        """Update a Source.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param str source_id: The source ID. (required)
        :param Source source: Source update (required)
        :param str zap_trace_span: OpenTracing span context
        :return: Source
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._patch_sources_id_prepare(
            source_id,
            source,
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/sources/{sourceID}",
            "PATCH",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="Source",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _patch_sources_id_prepare(self, source_id, source, **kwargs):
        local_var_params = locals()

        all_params = ["source_id", "source", "zap_trace_span"]
        self._check_operation_params("patch_sources_id", all_params, local_var_params)
        # verify the required parameter 'source_id' is set
        if "source_id" not in local_var_params or local_var_params["source_id"] is None:
            msg = "Missing the required parameter `source_id` when calling `patch_sources_id`"
            raise ValueError(
                msg,
            )
        # verify the required parameter 'source' is set
        if "source" not in local_var_params or local_var_params["source"] is None:
            msg = "Missing the required parameter `source` when calling `patch_sources_id`"
            raise ValueError(
                msg,
            )

        path_params = {}
        if "source_id" in local_var_params:
            path_params["sourceID"] = local_var_params["source_id"]

        query_params = []

        header_params = {}
        if "zap_trace_span" in local_var_params:
            header_params["Zap-Trace-Span"] = local_var_params["zap_trace_span"]

        body_params = None
        if "source" in local_var_params:
            body_params = local_var_params["source"]
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"],
        )

        # HTTP header `Content-Type`
        header_params["Content-Type"] = self.api_client.select_header_content_type(
            ["application/json"],
        )

        return local_var_params, path_params, query_params, header_params, body_params

    def post_sources(self, source, **kwargs):
        """Create a source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_sources(source, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param Source source: Source to create (required)
        :param str zap_trace_span: OpenTracing span context
        :return: Source
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.post_sources_with_http_info(source, **kwargs)
        else:
            return self.post_sources_with_http_info(source, **kwargs)

    def post_sources_with_http_info(self, source, **kwargs):
        """Create a source.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_sources_with_http_info(source, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param Source source: Source to create (required)
        :param str zap_trace_span: OpenTracing span context
        :return: Source
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._post_sources_prepare(
            source,
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/sources",
            "POST",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="Source",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def post_sources_async(self, source, **kwargs):
        """Create a source.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param Source source: Source to create (required)
        :param str zap_trace_span: OpenTracing span context
        :return: Source
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._post_sources_prepare(
            source,
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/sources",
            "POST",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="Source",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _post_sources_prepare(self, source, **kwargs):
        local_var_params = locals()

        all_params = ["source", "zap_trace_span"]
        self._check_operation_params("post_sources", all_params, local_var_params)
        # verify the required parameter 'source' is set
        if "source" not in local_var_params or local_var_params["source"] is None:
            msg = "Missing the required parameter `source` when calling `post_sources`"
            raise ValueError(
                msg,
            )

        path_params = {}

        query_params = []

        header_params = {}
        if "zap_trace_span" in local_var_params:
            header_params["Zap-Trace-Span"] = local_var_params["zap_trace_span"]

        body_params = None
        if "source" in local_var_params:
            body_params = local_var_params["source"]
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"],
        )

        # HTTP header `Content-Type`
        header_params["Content-Type"] = self.api_client.select_header_content_type(
            ["application/json"],
        )

        return local_var_params, path_params, query_params, header_params, body_params
