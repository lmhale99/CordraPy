import json
from .RestClient import RestClient
from lucenequerybuilder import Q

class CordraClient(RestClient):

    def __str__(self):
        """String representation."""
        return f'CordraClient for {self.username} @ {self.host}'

    def testcall(self):
        """
        Simple rest call to check if authentication parameters are valid.
        """
        # Call check_credentials()
        self.check_credentials()


    def retrieve(self, id, jsonPointer=None, filter=None, payload=None,
                 pretty=None, text=False, disposition=None, full=False):
        """
        Retrieve an object or part of an object using its id.

        Parameters
        ----------
        id: str
            The id of the desired object.
        jsonPointer: str, optional
            The jsonPointer into the subcomponent of the target object
        filter: list? str?, optional
            A json array of jsonPointers used to restrict the result object
        payload: str, optional
            The name of the payload to retrieve
        pretty: str (bool?), optional
            Format returned json
        text: bool, optional
            When present on a request which would normally result in a JSON
            string, the response is the contents of the JSON string.
        disposition: str, optional 
            For payload requests. Can be used to set the Content-Disposition header
            on the response; “disposition=attachment” will cause a standard web browser
            to perform a download operation.
        full: bool, optional
            If present the response is the full Cordra object, including properties id,
            type, content, acl, metadata, and payloads. By default only the content is
            returned.)
        """
        # Set the rest URL
        rest_url = f'objects/{id}'

        # Build the parameters dict
        params = {}
        if jsonPointer is not None:
            params['jsonPointer'] = jsonPointer
        if filter is not None:
            params['filter'] = filter
        if payload is not None:
            params['payload'] = payload
        if pretty is not None:
            params['pretty'] = pretty
        if text:
            params['text'] = text
        if disposition is not None:
            params['disposition'] = disposition
        if full:
            params['full'] = full
        
        return self.restget(rest_url, params=params)

    
    def create(self, obj, obj_type, payloads=None, dryrun=False,
               acls=None, suffix=None, handle=None, full=False):
        """
        obj
        obj_type: str
            The type of the object being created. In this case “Document”.
        dryrun: bool, optional
            Do not actually create the object. Will return results as if object had been created.
        suffix: str, optional
            The suffix of the handle used to identify this object. One will be generated if
            neither ‘suffix’ nor ‘handle’ is specified.
        handle: str, optional
            The handle used to identify this object. One will be generated if neither ‘suffix’
            nor ‘handle’ is specified.
        full bool, optional
            If present the response is the full Cordra object, including properties id, type,
            content, acl, metadata, and payloads. By default only the content is returned.
        """
        params = {}
        params['type'] = obj_type
        if dryrun:
            params['dryRun'] = dryrun
        if suffix is not None:
            params['suffix'] = suffix
        if handle is not None:
            params['handle'] = handle
        if full:
            params['full'] = full

        if payloads:
            data = {}
            
            # Convert obj to json
            if isinstance(obj, dict):
                data['content'] = json.dumps(obj)
            else:
                data['content'] = obj.json()

            # Convert acls to json
            if acls is None:
                pass
            elif isinstance(acls, dict):
                data['acl'] = json.dumps(acls)
            else:
                data['acl'] = acls.json()

            # Convert payloads to json
            if not isinstance(payloads, dict):
                payloads = payloads.json()

            return self.restpost('objects', params=params, data=data, files=payloads)

        else:
            if acls:
                params['full'] = True
            
            # Convert obj to json
            if isinstance(obj, dict):
                data = json.dumps(obj)
            else:
                data = obj.json()
            obj_r = self.restpost('objects',  params=params, data=data)

            if acls and not dryrun:

                # Convert acls to json
                if isinstance(acls, dict):
                    data['acl'] = json.dumps(acls)
                else:
                    data['acl'] = acls.json()
                
                acl_r = self.restput(f'acls/{obj_r["id"]}', params=params, data=data)
                return [obj_r, acl_r]
            else:
                return obj_r

    def find(self, query, token=None, ids=False, jsonFilter=None, full=False):
        '''Find a Cordra object by query'''

        params = dict()
        params['query'] = query
        params['full'] = full

        if jsonFilter:
            params['filter'] = str(jsonFilter)
        
        if ids:
            params['ids'] = True 
        
        r = self.restget('objects', params=params, headers=None)
        return r

    def check_credentials(self):
        self.restget('check-credentials')

    def delete(self, obj_id, jsonPointer=None):
        '''Delete a Cordra object'''

        params = {}
        if jsonPointer:
            params['jsonPointer'] = jsonPointer

        return self.restdelete(f'objects/{obj_id}', params=params)