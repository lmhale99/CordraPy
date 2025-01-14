# coding: utf-8

# Standard library imports
import getpass
from pathlib import Path

# http://docs.python-requests.org
import requests

# Ignore certification warnings (for now)
from requests.packages.urllib3.exceptions import InsecureRequestWarning # pylint: disable=import-error
requests.packages.urllib3.disable_warnings(InsecureRequestWarning) # pylint: disable=no-member

class RestClient(object):
    """
    Generic class for building REST calls to web databases in Python.
    """
    def __init__(self, host, username=None, password=None, 
                auth=None, cert=None, verify=True):
        """
        Class initializer. Tests and stores access information.
        
        Args:
            host: (str) URL for the database's server.
            username: (str, optional) Username of desired account on the
                server. A prompt will ask for the username if not given.
            password: (str, optional) Password of desired account on the
                server.  A prompt will ask for the password if not given.
            auth: (tuple, optional) Auth tuple to enable
                Basic/Digest/Custom HTTP Auth.  Alternative to giving
                username and password seperately.
            cert: (str, optional) if String, path to ssl client cert file
                (.pem). If Tuple, (‘cert’, ‘key’) pair.
            verify: (bool or str, optional) Either a boolean, in which case
                it controls whether we verify the server’s TLS certificate,
                or a string, in which case it must be a path to a CA
                bundle to use. Defaults to True.
        """
        # Set access information
        self.login(host, username=username, password=password,
                   auth=auth, cert=cert, verify=verify)

    def __str__(self):
        """String representation."""
        return f'RestClient for {self.username} @ {self.host}'
        
    @property
    def host(self):
        """str: The host url for the server."""
        return self.__host
    
    @property
    def username(self):
        """str: The username to use for the server."""
        return self.__user
    
    @property
    def cert(self):
        """str or None: The certification information."""
        return self.__cert

    @property
    def verify(self):
        """bool: The verify setting for the database."""
        return self.__verify

    def login(self, host, username=None, password=None, auth=None, cert=None,
              verify=True):
        """
        Tests and stores access information.
        
        Args:
            host: (str) URL for the database's server.
            username: (str, optional) Username of desired account on the MDCS
                server. A prompt will ask for the username if not given.
            password: (str, optional) Password of desired account on the MDCS
                server.  A prompt will ask for the password if not given.
            auth: (tuple, optional) Auth tuple to enable
                Basic/Digest/Custom HTTP Auth.  Alternative to giving
                username and password seperately.
            cert: (str, optional) if String, path to ssl client cert file
                (.pem). If Tuple, (‘cert’, ‘key’) pair.
            verify: (bool or str, optional) Either a boolean, in which case
                it controls whether we verify the server’s TLS certificate,
                or a string, in which case it must be a path to a CA
                bundle to use. Defaults to True.
        """
        # Handle host
        host = host.strip('/')

        # Handle username and password
        if auth is None:

            # Handle username
            if username is None:
                username = input(f'Enter username for {host}:')
       
            # Handle non-anonymous 
            if username != '':

                # Handle password
                if password is None:
                    password = getpass.getpass(f'Enter password for {username} @ {host}:')
                auth = (username, password)
            
            # Handle anonymous
            else:
                username = None
                auth = None

        # Handle auth 
        else:
            assert username is None and password is None, 'auth cannot be given with username and password'
            username = auth[0]

        # Handle certification
        if isinstance(cert, str):
            cert = Path(cert)
            if cert.is_file():
                cert = str(cert.resolve())
            else:
                raise ValueError('Certification file not found!')
        elif isinstance(cert, (list, tuple)):
            assert len(cert) == 2
            if not Path(cert[0]).is_file() or not Path(cert[1].is_file()):
                raise ValueError('Certification file not found!')
            
        # Set object values
        self.__host = host
        self.__user = username
        self.__auth = auth
        self.__cert = cert
        self.__verify = verify

        # Test login info
        if self.__user is not None:
            self.testcall()
    
    def testcall(self):
        """
        Simple rest call to check if authentication parameters are valid.
        """
        # Default behavior is no test: must be set specific to database type
        pass

    def restrequest(self, method, rest_url, **kwargs):
        """
        Wrapper around requests.request that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            method: (str) Method for the new Request object.
            rest_url: (str) The REST command URL, i.e. URL path after host.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url.  auth, verify, and/or
                cert will default to values set during class initialization.
        
        Returns:
            requests.Response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        
        # Set url and access parameters
        url = self.host + '/' + rest_url.lstrip('/')
        
        auth = kwargs.pop('auth', self.__auth)
        cert = kwargs.pop('cert', self.cert)
        verify = kwargs.pop('verify', self.verify)
        
        # Send request
        response = requests.request(method, url, auth=auth, verify=verify,
                                    cert=cert, **kwargs)
        
        # Check for errors
        if not response.ok:
            try:
                print(response.json())
            except BaseException:
                print(response.text)
            response.raise_for_status()
        else:
            try:
                return response.json()
            except BaseException:
                return response.text
    
    def resthead(self, rest_url, **kwargs):
        """
        Wrapper around requests.head that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url.  auth, verify, and/or
                cert will default to values set during class initialization.
        
        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        # Change default allow_redirects to reflect requests.head()
        if 'allow_redirects' not in kwargs:
            kwargs['allow_redirects'] = False
            
        return self.restrequest('head', rest_url, **kwargs)
    
    def restget(self, rest_url, **kwargs):
        """
        Wrapper around requests.get that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url.  auth, verify, and/or
                cert will default to values set during class initialization.
        
        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        return self.restrequest('get', rest_url, **kwargs)
        
    def restpost(self, rest_url, data=None, **kwargs):
        """
        Wrapper around requests.post that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            data: (dict or bytes, optional) Data to send in the body of the
                Request.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url.  auth, verify, and/or
                cert will default to values set during class initialization.
        
        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        return self.restrequest('post', rest_url, data=data, **kwargs)
    
    def restput(self, rest_url, data=None, **kwargs):
        """
        Wrapper around requests.put that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            data: (dict or bytes, optional) Data to send in the body of the
                Request.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url.  auth, verify, and/or
                cert will default to values set during class initialization.

        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        return self.restrequest('put', rest_url, data=data, **kwargs)
    
    def restpatch(self, rest_url, data=None,**kwargs):
        """
        Wrapper around requests.patch that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            data: (dict or bytes, optional) Data to send in the body of the
                Request.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url.  auth, verify, and/or
                cert will default to values set during class initialization.
        
        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        return self.restrequest('patch', rest_url, data=data, **kwargs)
    
    def restdelete(self, rest_url, **kwargs):
        """
        Wrapper around requests.delete that automatically sets any access
        parameters based on the stored login information.
        
        Args:
            rest_url: (str) The REST command URL, i.e. URL path after host.
            **kwargs: (any, optional) Any other arguments supported by
                requests.request() except for url.  auth, verify, and/or
                cert will default to values set during class initialization.
        
        Returns:
            requests.Response: The response
        
        Raises:
            Any requests errors if the response code is not ok.
        """
        return self.restrequest('delete', rest_url, **kwargs)