import json
import time
import requests
import urllib3
import cgi

from . import utils

DEFAULT_BASE_URL = "http://localhost:9888"


class DocsConvClient(object):
    """Docs Conversion Api Client"""

    def __init__(self, baseUrl=DEFAULT_BASE_URL, apiKey=None, timeout=30, retriesTime=2):
        """Create a new client instance.

        :param baseUri: Base URL for the Vault instance being addressed.
        :type baseUri: str
        :param timeout: The timeout value for requests sent to Vault.
        :type timeout: int
        """

        self.baseUri = baseUrl
        self.apiKey = apiKey
        self.timeout = timeout
        self.retriesTime = retriesTime
        self.__manager = urllib3.PoolManager(headers=self.__buildHeaders())
        self.__session = self.__manager.request

    def convert(self, fileName, fileBin, toFormat):
        """_summary_

        Args:
            fileName (string): _description_
            fileBin (binary): _description_
            toFormat (string): _description_

        Returns:
            tuple(fileContent, fileName): _description_
        """
        apiUrl = self.__buildURL("convert")
        rt = 0

        while rt < self.retriesTime:
            res = self.__session(
                "POST",
                apiUrl,
                fields={
                    'to': toFormat,
                    'input': (fileName, fileBin),
                },
                timeout=self.timeout
            )

            if res.status == requests.codes.ok:
                headerContent = res.getheader('Content-Disposition')
                value, params = cgi.parse_header(headerContent)
                fname = params['filename']
                return (res.data, fname)

            statusesNoNeedRetry = [
                requests.codes.bad_request,
                requests.codes.unauthorized,
                requests.codes.forbidden,
                requests.codes.unprocessable_entity,
                requests.codes.request_entity_too_large,
                requests.codes.not_found,
                requests.codes.method_not_allowed,
            ]

            if res.status in statusesNoNeedRetry:
                utils.raise_for_response("POST", apiUrl, res)

            rt += 1
            # sleep for retry
            time.sleep(0.1)

        # Raise exception
        if res.status != requests.codes.ok:
            utils.raise_for_response("POST", apiUrl, res)
    
    def conversion(self):
        """ Return all available conversion

        Returns:
            dict: Available conversion
        """
        apiUrl = self.__buildURL("conversion")
        rt = 0

        while rt < self.retriesTime:
            res = self.__session(
                "GET",
                apiUrl,
                timeout=self.timeout
            )

            if res.status == requests.codes.ok:
                res = json.loads(res.data)
                return res

            statusesNoNeedRetry = [
                requests.codes.bad_request,
                requests.codes.unauthorized,
                requests.codes.forbidden,
                requests.codes.unprocessable_entity,
                requests.codes.request_entity_too_large,
                requests.codes.not_found,
                requests.codes.method_not_allowed,
            ]

            if res.status in statusesNoNeedRetry:
                utils.raise_for_response("GET", apiUrl, res)

            rt += 1
            # sleep for retry
            time.sleep(0.1)

        # Raise exception
        if res.status != requests.codes.ok:
            utils.raise_for_response("GET", apiUrl, res)

    def __del__(self):
        self.close()

    def close(self):
        """
        Close all currently open connections
        """
        try:
            self.__manager.clear()
        except:  # noqa: E722
            pass

    def __buildURL(self, urlPath: str):
        return self.baseUri + "/" + urlPath

    def __buildHeaders(self):
        headers = dict({})
        if self.apiKey is not None and self.apiKey != "":
            headers['X-Api-Key'] = self.apiKey
        return headers
