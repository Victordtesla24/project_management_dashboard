"""InfluxDB OSS API Service.

The InfluxDB v2 API provides a programmatic interface for all interactions with InfluxDB. Access the InfluxDB API using the `/api/v2/` endpoint.   # noqa: E501

OpenAPI spec version: 2.0.0
Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401

from influxdb_client.service._base_service import _BaseService


class TelegrafPluginsService(_BaseService):
    """NOTE: This class is auto generated by OpenAPI Generator.

    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        """TelegrafPluginsService - a operation defined in OpenAPI."""
        super().__init__(api_client)

    def get_telegraf_plugins(self, **kwargs):
        """List all Telegraf plugins.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_telegraf_plugins(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str zap_trace_span: OpenTracing span context
        :param str type: The type of plugin desired.
        :return: TelegrafPlugins
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.get_telegraf_plugins_with_http_info(**kwargs)
        else:
            return self.get_telegraf_plugins_with_http_info(**kwargs)

    def get_telegraf_plugins_with_http_info(self, **kwargs):
        """List all Telegraf plugins.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_telegraf_plugins_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str zap_trace_span: OpenTracing span context
        :param str type: The type of plugin desired.
        :return: TelegrafPlugins
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_telegraf_plugins_prepare(
            **kwargs,
        )

        return self.api_client.call_api(
            "/api/v2/telegraf/plugins",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="TelegrafPlugins",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    async def get_telegraf_plugins_async(self, **kwargs):
        """List all Telegraf plugins.

        This method makes an asynchronous HTTP request.

        :param async_req bool
        :param str zap_trace_span: OpenTracing span context
        :param str type: The type of plugin desired.
        :return: TelegrafPlugins
                 If the method is called asynchronously,
                 returns the request thread.
        """
        (
            local_var_params,
            path_params,
            query_params,
            header_params,
            body_params,
        ) = self._get_telegraf_plugins_prepare(
            **kwargs,
        )

        return await self.api_client.call_api(
            "/api/v2/telegraf/plugins",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=[],
            files={},
            response_type="TelegrafPlugins",
            auth_settings=[],
            async_req=local_var_params.get("async_req"),
            _return_http_data_only=local_var_params.get("_return_http_data_only"),
            _preload_content=local_var_params.get("_preload_content", True),
            _request_timeout=local_var_params.get("_request_timeout"),
            collection_formats={},
            urlopen_kw=kwargs.get("urlopen_kw", None),
        )

    def _get_telegraf_plugins_prepare(self, **kwargs):
        local_var_params = locals()

        all_params = ["zap_trace_span", "type"]
        self._check_operation_params("get_telegraf_plugins", all_params, local_var_params)

        path_params = {}

        query_params = []
        if "type" in local_var_params:
            query_params.append(("type", local_var_params["type"]))

        header_params = {}
        if "zap_trace_span" in local_var_params:
            header_params["Zap-Trace-Span"] = local_var_params["zap_trace_span"]

        body_params = None
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"],
        )

        return local_var_params, path_params, query_params, header_params, body_params
