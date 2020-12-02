'''
This is a sample module you can use to code your own modules for the
MicroService Architecture.

The beauty of this MicroService Architecture is the sheer simplicity of how it works.

Everything this MicroService Architecture does is done via pure Python and introspection.  

Everything in Python can be introspected including Modules.  Python can introspect a module to
learn about all the functions in the module.  Once you have all the functions you can use a decorator
to generate some META data to identify how each function can be accessed via the RESTful Interface.

The RESTful interface is also very simple.  One Object called a ServiceRunner and one RestAPI sub-class.  That's it.  Simple.

Some of the work done by the ServiceRunner is not well documented in the Python docs but it was also not difficult to cobble
together from various sources.

The current version supports GET and POST.  Future versions will support the rest of the HTTP Methods however it is more than possible to
build a working RESTful interface with just GET and POST, believe it or not.  Oh, I know there are those out there who have very definite
feelings about this but trust me when I say I was more than able to build a complete CRUD Interface using just one POST endpoint.  Doing this
made the code smaller and easier to maintain than the alternatives.

Rules:

GET functions take parameters as follows:

    GET http://127.0.0.1:8080/rest/services/hello-world/?a=1&b=2&c=3&d=4 HTTP/1.1

POST functions take parameters as follows:

    POST http://127.0.0.1:8080/rest/services/sample-one/ HTTP/1.1
    content-type: application/json

    {
        "args": [1,2,3,4,5,6],
        "name1": "one",
        "name2": "two",
        "name3": "three",
        "name4": "four"
    }

The typical Pythonic method for passing variable arguments to a function can be seen in this sample but this would have to be done
if one wished to publish functions via a RESTful Interface.

Any functions beginning with "__" will not be exposed as RESTful Endpoints.

Objects in the form of classes will not be exposed as RESTful Endpoints however you can add classes to yuour modules and then code
functions that can be exposed that can use any classes via their instances.  Again, this is how one would go about using Objects via
a RESTful Interface.

This interface is fully pluggable which means you can use whatever method you desire to plug new modules into the system and those modules
will be dynamically imported at run-time each time any endpoint is issued.

You may use the following endpoint to discover modules and endpoints known to the system:

    GET http://127.0.0.1:8080/rest/services/__dir__/ HTTP/1.1
    
Plugins:

Plug your modules into the folder called "plugins".  While the "plugins" folder could be placed anywhere it was placed under the "views" folder to facilitate
uploading modules via a RESTful Interface, at some point, however the version you are using does not support this.  A future version may have this feature in
the form on uploading specially encrypted modules to keep unwanted modules from being uploaded.  At present, you must install your "plugins"  manually which
should not pose any issues for you in case you wish to deploy this Microservices Architecture in Production.

Future Development:

Token-based Security.  Temporal Tokens, Randomly Encrypted.  Every token is unique.  Tokens are valid for a limite time, typically 60 seconds.  Tokens can only be used once.  This
type of Security is more secure than Oauth because Oauth Tokens require some time to invaidate and they can be used more than once.  For browser-based clients the Tokens are
generated by WASM code running deep in your browser.

Contact the developer (raychorn@gmail.com) for any specific requirements you may have for your deployments.


'''

from vyperlogix.decorators import expose


@expose.endpoint(method='GET', API='hello-world')
def foo(*args, **kwargs):
    '''
    Notice the @expose.endpoint(method='GET', API='hello-world') decorator.
    
    method= must be GET or POST.
    API= is the name your function will be known to the outside world.
    The module name is obtained via introspection when the decorator is executed.
    
    Sample URLS:
    
        GET http://127.0.0.1:8080/rest/services/hello-world/ HTTP/1.1

        GET http://127.0.0.1:8080/rest/services/hello-world/?a=1&b=2&c=3&d=4 HTTP/1.1

    '''
    response = {}
    response['args'] = {}
    for i, arg in enumerate(args):
        response.get('args', {})[i] = arg
    response['kwargs'] = {}
    for k,v in kwargs.items():
        response.get('kwargs', {})[k] = v
    response['response'] = 'hello-world'
    return response


def __private_function__():
    '''
    This is a private function because the function name begins with "__".
    This function will not appear in the __dir__.
    '''
    return 'bar-none'


def private_function():
    '''
    This is a private function because it was not exposed via the decorator.
    This function will appear in the __dir__ as a function in the module however it cannot be accessed directly via the RESTful Interface.
    '''
    return 'again'


@expose.endpoint(method='GET', API='bar-none')
def bar(*args, **kwargs):
    '''
    This is an exposed function that is accessible via GET via the "bar-none" API.
    
    This function does not accept query string parameters.
    
    Samples:
    
        GET http://127.0.0.1:8080/rest/services/bar-none/ HTTP/1.1

    '''
    return __private_function__() + ' ' + private_function()


my_var = 1.0 # global variables are not exposed via the RESTful Interface.


@expose.endpoint(method='POST', API='sample-one')
def sample1(*args, **kwargs):
    '''
    This is an exposed function that is accessible via POST via the "sample-one" API.
    
    When query string parameters appear they are mixed into the payload.
    
    Samples:
    
        POST http://127.0.0.1:8080/rest/services/sample-one/?a=1&b=2&c=3&d=4 HTTP/1.1
        content-type: application/json

        {
            "args": [1,2,3,4,5,6],
            "name1": "one",
            "name2": "two",
            "name3": "three",
            "name4": "four"
        }

    '''
    response = {}
    response['args'] = {}
    for i, arg in enumerate(args):
        response.get('args', {})[i] = arg
    response['kwargs'] = {}
    for k,v in kwargs.items():
        response.get('kwargs', {})[k] = v
    return response


@expose.endpoint(method='PUT', API='sample-one2')
def sample12(*args, **kwargs):
    '''
    This is an exposed function that is accessible via POST via the "sample-one" API.
    
    When query string parameters appear they are mixed into the payload.
    
    Samples:
    
        PUT http://127.0.0.1:8080/rest/services/sample-one/?a=1&b=2&c=3&d=4 HTTP/1.1
        content-type: application/json

        {
            "args": [1,2,3,4,5,6],
            "name1": "one",
            "name2": "two",
            "name3": "three",
            "name4": "four"
        }

    '''
    response = {}
    response['args'] = {}
    for i, arg in enumerate(args):
        response.get('args', {})[i] = arg
    response['kwargs'] = {}
    for k,v in kwargs.items():
        response.get('kwargs', {})[k] = v
    return response


@expose.endpoint(method='DELETE', API='sample-one2a')
def sample12a(*args, **kwargs):
    '''
    This is an exposed function that is accessible via POST via the "sample-one" API.
    
    When query string parameters appear they are mixed into the payload.
    
    Samples:
    
        PUT http://127.0.0.1:8080/rest/services/sample-one/?a=1&b=2&c=3&d=4 HTTP/1.1
        content-type: application/json

        {
            "args": [1,2,3,4,5,6],
            "name1": "one",
            "name2": "two",
            "name3": "three",
            "name4": "four"
        }

    '''
    response = {}
    response['args'] = {}
    for i, arg in enumerate(args):
        response.get('args', {})[i] = arg
    response['kwargs'] = {}
    for k,v in kwargs.items():
        response.get('kwargs', {})[k] = v
    return response


@expose.endpoint(method='POST', API='sample-two')
def sample2(*args, **kwargs):
    '''
    This is an exposed function that is accessible via POST via the "sample-one" API.
    
    When query string parameters appear they are mixed into the payload.
    
    Samples:
    
        POST http://127.0.0.1:8080/rest/services/sample-two/?a=1&b=2&c=3&d=4 HTTP/1.1
        content-type: application/json

        {
            "args": [1,2,3,4,5,6],
            "name1": "one",
            "name2": "two",
            "name3": "three",
            "name4": "four"
        }

    '''
    response = {}
    response['args'] = {}
    for i, arg in enumerate(args):
        response.get('args', {})[i] = arg
    response['kwargs'] = {}
    for k,v in kwargs.items():
        response.get('kwargs', {})[k] = v
    return response
