"""InfluxDB OSS API Service.

The InfluxDB v2 API provides a programmatic interface for all interactions with InfluxDB. Access the InfluxDB API using the `/api/v2/` endpoint.   # noqa: E501

OpenAPI spec version: 2.0.0
Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401

from influxdb_client.service._base_service import _BaseService


class PingService(_BaseService):
    """NOTE: This class is auto generated by OpenAPI Generator.

    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        """PingService - a operation defined in OpenAPI."""
        super().__init__(api_client)

    def get_ping(self, **kwargs):
        """Get the status of the instance.

        Retrieves the status and InfluxDB version of the instance.  Use this endpoint to monitor uptime for the InfluxDB instance. The response returns a HTTP `204` status code to inform you the instance is available.  #### InfluxDB Cloud  - Isn't versioned and doesn't return `X-Influxdb-Version` in the headers.  #### Related guides  - [Influx ping](https://docs.influxdata.com/influxdb/latest/reference/cli/influx/ping/)
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_ping(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.get_ping_with_http_info(**kwargs)
        else:
            return self.get_ping_with_http_info(**kwargs)

    def get_ping_with_http_info(self, **kwargs):
        """Get the status of the instance.

        Retrieves the status and InfluxDB version of the instance.  Use this endpoint to monitor uptime for the InfluxDB instance. The response returns a HTTP `204` status code to inform you the instance is available.  #### InfluxDB Cloud  - Isn't versioned and doesn't return `X-Influxdb-Version` in the headers.  #### Related guides  - [Influx ping](https://docs.influxdata.com/influxdb/latest/reference/cli/influx/ping/)
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_ping_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
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
        ) = self._get_ping_prepare(
            **kwargs,
        )

        return self.api_client.call_api(
            "/ping",
            "GET",
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

    async def get_ping_async(self, **kwargs):
        """Get the status of the instance.

        Retrieves the status and InfluxDB version of the instance.  Use this endpoint to monitor uptime for the InfluxDB instance. The response returns a HTTP `204` status code to inform you the instance is available.  #### InfluxDB Cloud  - Isn't versioned and doesn't return `X-Influxdb-Version` in the headers.  #### Related guides  - [Influx ping](https://docs.influxdata.com/influxdb/latest/reference/cli/influx/ping/)
        This method makes an asynchronous HTTP request.

        :param async_req bool
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
        ) = self._get_ping_prepare(
            **kwargs,
        )

        return await self.api_client.call_api(
            "/ping",
            "GET",
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

    def _get_ping_prepare(self, **kwargs):
        local_var_params = locals()

        all_params = []
        self._check_operation_params("get_ping", all_params, local_var_params)

        path_params = {}

        query_params = []

        header_params = {}

        body_params = None
        return local_var_params, path_params, query_params, header_params, body_params

    def head_ping(self, **kwargs):
        """Get the status of the instance.

        Returns the status and InfluxDB version of the instance.  Use this endpoint to monitor uptime for the InfluxDB instance. The response returns a HTTP `204` status code to inform you the instance is available.  #### InfluxDB Cloud  - Isn't versioned and doesn't return `X-Influxdb-Version` in the headers.  #### Related guides  - [Influx ping](https://docs.influxdata.com/influxdb/latest/reference/cli/influx/ping/)
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.head_ping(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """  # noqa: E501
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.head_ping_with_http_info(**kwargs)
        else:
            return self.head_ping_with_http_info(**kwargs)

    def head_ping_with_http_info(self, **kwargs):
        """Get the status of the instance.

        Returns the status and InfluxDB version of the instance.  Use this endpoint to monitor uptime for the InfluxDB instance. The response returns a HTTP `204` status code to inform you the instance is available.  #### InfluxDB Cloud  - Isn't versioned and doesn't return `X-Influxdb-Version` in the headers.  #### Related guides  - [Influx ping](https://docs.influxdata.com/influxdb/latest/reference/cli/influx/ping/)
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.head_ping_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
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
        ) = self._head_ping_prepare(
            **kwargs,
        )

        return self.api_client.call_api(
            "/ping",
            "HEAD",
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

    async def head_ping_async(self, **kwargs):
        """Get the status of the instance.

        Returns the status and InfluxDB version of the instance.  Use this endpoint to monitor uptime for the InfluxDB instance. The response returns a HTTP `204` status code to inform you the instance is available.  #### InfluxDB Cloud  - Isn't versioned and doesn't return `X-Influxdb-Version` in the headers.  #### Related guides  - [Influx ping](https://docs.influxdata.com/influxdb/latest/reference/cli/influx/ping/)
        This method makes an asynchronous HTTP request.

        :param async_req bool
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
        ) = self._head_ping_prepare(
            **kwargs,
        )

        return await self.api_client.call_api(
            "/ping",
            "HEAD",
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

    def _head_ping_prepare(self, **kwargs):
        local_var_params = locals()

        all_params = []
        self._check_operation_params("head_ping", all_params, local_var_params)

        path_params = {}

        query_params = []

        header_params = {}

        body_params = None
        return local_var_params, path_params, query_params, header_params, body_params
