#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
import json
import logging


class IseErsApi:

    port = '9060'

    def __init__(self, host, user, password, verify):
        ''' Create a new IseErsApi instance 
        Args:
            host (str): IP or hostname (without https://) of ISE Node
            user (str): Username for ers API
            password (str): Password for ers API user
            verify (bool): enable / disable certificate check for requests to ISE.
        '''
        self.logger = logging.getLogger('IseErsApi')
        self.user = user
        self.password = password
        self.auth = (self.user, self.password)
        # important no trailing / in url, this is expected by path.
        # ISE i picky about double // in query url and might return empty result.
        self.url = f'https://{host}:{IseErsApi.port}'
        if not verify:
            import urllib3
            urllib3.disable_warnings()
        self.kwargs = {
            'verify' : False,
        }


    def _session(self):
        s=requests.Session()
        s.auth = self.auth
        s.headers.update({'accept': "application/json",'cache-control': "no-cache"})
        return s

    def _get(self, s, url):
        '''
        Args:
            response (requests.Response)
        '''
        self.logger.info(url)
        res = s.get(url, **self.kwargs)
        if 200 != res.status_code:
            self.logger.debug(res.headers)
            self.logger.debug(res.text)
            raise RuntimeError(res)
        jsondata = json.loads(res.text)
        return jsondata


    def export_all_network_elements(self):
        '''Queries details of each network element by ID

        Returns:
            list: of dictionaries as returned by get-by-id API result key 'NetworkDevice'
                  see  https://developer.cisco.com/docs/identity-services-engine/2.6/#!network-device/get-by-id
        '''
        all_devices = self.network_device_get_all()
        s = self._session()
        device_list = list()
        for resource in all_devices['SearchResult']['resources']:
            jsondata = self._get(s, resource['link']['href'])
            # see https://developer.cisco.com/docs/identity-services-engine/2.6/#!network-device/get-by-id
            device_list.append(jsondata['NetworkDevice'])

        s.close()
        return device_list

    def network_device_get_all(self):
        '''Gets all network devices from ISE, including pagination.

        Returns json dict, as returned by ISE; resources of all pages are merged into 
        result['SearchResult']['resources'] array.
        https://developer.cisco.com/docs/identity-services-engine/2.6/#!network-device/get-all

        Returns:
            dict: See https://developer.cisco.com/docs/identity-services-engine/2.6/#!network-device/get-all for structure

        '''
        path = '/ers/config/networkdevice'
        s = self._session()
        # max page-size for ise is 100.
        full_url = f'{self.url + path}?size=100'
        jsondata = self._get(s, full_url)
        all_devices = jsondata
        while True:
            if 'nextPage' in jsondata['SearchResult']:
                full_url = jsondata['SearchResult']['nextPage']['href']
                jsondata = self._get(s, full_url)
                all_devices['SearchResult']['resources'] += jsondata['SearchResult']['resources']
            else:
                break
        
        s.close()
        return all_devices


def _setup_logging():
    format = "%(asctime)s %(name)10s %(levelname)8s: %(message)s"
    # logfile='ise.log'
    logfile=None
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S", filename=logfile)

if __name__ == '__main__':
    _setup_logging()
    if 'ISE_USER' not in os.environ or 'ISE_PASSWORD' not in os.environ:
        exit('make sure environment variables `ISE_USER` and `ISE_PASSWORD` are defined')
    if len(sys.argv) != 2:
        exit(f'usage: ./{sys.argv[0]} ISE_HOSTNAME_OR_IP')

    ise = IseErsApi(host=sys.argv[1], user=os.environ.get('ISE_USER'), password=os.environ.get('ISE_PASSWORD'), verify=False)

    result = ise.export_all_network_elements()
    for i in result:
        for j in i['NetworkDeviceIPList']:
            print (j['ipaddress'] + '/' + str(j['mask']))
