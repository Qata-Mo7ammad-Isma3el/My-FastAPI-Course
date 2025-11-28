#!! https://jod35.github.io/fastapi-beyond-crud-docs/site/


#!------------------ Managing Requests and Responses ------------------!#
#> There are very many ways that clients can pass request data to a FastAPI API route. These include:
#> • Path Parameters
#> • Query Parameters
#> • Headers e.t.c.
#> Through such ways, we can obtain data from incoming requests to our APIs.

## Parameter type declarations
#> • All parameters in a FastAPI request are required to have a type declaration via type hints. 
#> • Primitive Python types such (None,int,str,bool,float), container types such as (dict,tuples,dict,set) 
#>   and some other complex types are all supported.
#> • Additionally FastAPI also allows all types present within Python's typing module. 
#> • These data types represent common conventions in Python and are utilized for variable type annotations. 
#> • They facilitate type checking and model validation during compilation. 
#> • Examples include Optional, List, Dict, Set, Union, Tuple, FrozenSet, Iterable, and Deque.

from fastapi import FastAPI, Header
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

#!------------------ Creating an API Route ------------------!#
#> We define our first API route by creating a function named read_root. 
#> This function, when accessed, will return a JSON message containing "Hello World!".

#> • The @app decorator associates the function with the HTTP GET method via the get method. 
#> • We then provide the path (route) of the root path (/). 
#> • This means that whenever the / route is accessed, the defined message will be returned.
#> • All HTTP methods such as post,put,head,patch, delete, trace and options are all available on the @app decorator.

## Your first API endpoint
@app.get('/')
async def read_root():
    return {"message": "Hello World!"}




#!------------------ path parameters ------------------!#

#> • All request data supplied in the endpoint URL of a FastAPI API is acquired through a path parameter, 
#>   thus rendering URLs dynamic. 
#> • FastAPI adopts curly braces ({}) to denote path parameters when defining a URL. 
#> • Once enclosed within the braces, FastAPI requires that they be provided as parameters to the route handler
#>   functions we establish for those paths.
#code:..............
@app.get('/greet/{username}')
async def greet(username:str) -> dict:
    return {"message":f"Hello {username}"}
#> • In this example the greet() route handler function will require username which is annotated with str indicating that 
#>   the username shall be a string. 

#!------------------ Query Parameters ------------------!#
#> • These are key-value pairs provided at the end of a URL, indicated by a question mark (?). 
#> • Just like path parameters, they also take in request data. 
#> • Whenever we want to provide multiple query parameters, we use the ampersand (&) sign.

user_list = [
    "Jerry",
    "Joey",
    "Phil"
]

@app.get('/search')
async def search_for_user(username:str):
    for user in user_list:
        if username in user_list :
            return {"message":f"details for user {username}"}
        else:
            return {"message":"User Not Found"}

#> • In this example, we've set up a route for searching users within a simple list. 
#> • Notice that there are no path parameters specified in the route's URL. Instead, we're passing the username 
#>   directly to our route handler, search_for_user. 
#> • In FastAPI, any parameter passed to a route handler, like search_for_user, and is not provided in the path 
#>   as a path param is treated as a query parameter. 
#> • Therefore, to access this route, we need to use /search?username=sample_name, where username is the key and sample_name is
#>   the value.


## Optional Parameters
#> • There may also be cases when the API route can operate as needed even in the presence of a path or query param.
#> • In this case, we can make the parameters optional when annotating their types in the route handler functions.
#> • For example, our first example can be modified to the following:
#! the status code is the value returned when the request is successful by default it's 200.
@app.get('/greet/', status_code=200)
async def greet(username:Optional[str]="User"):
    return {"message":f"Hello {username}"}

#> • This time, we've made the username query parameter optional.
#>   We achieved this by removing it from the route definition. 
#> • Additionally, we updated the type annotation for the username parameter in the greet route handler 
#>   function to make it an optional string, with a default value of "User". 
#> • To accomplish this, we're using the Optional type from Python's typing module.

#!------------------ Request Body ------------------!#
#> • Frequently, clients need to send data to the server for tasks like creating or updating resources through methods
#>   like POST, PATCH, PUT, DELETE, or for various other operations. 
#> • FastAPI simplifies this process by enabling you to define a Pydantic model to establish the structure of the data 
#>   being sent.
#> • Furthermore, it aids in validating data types using type hints. 
#> • Let's delve into a straightforward example to illustrate this concept.

users = {}
#> the User model
#! it's called serialization model or schema
## A simple Pydantic model
class UserSchema(BaseModel):
    username:str
    email:str


@app.post("/create_user")
async def create_user(user_data:UserSchema)->dict:
    new_user = {
        "username" : user_data.username,
        "email": user_data.email
    }
    users.append(new_user)
    print(users)
    return {"message":"User Created successfully","user":new_user}

#> • What we have done in the above example is to create a Pydantic model by inheriting Pydantic's BaseModel class. 
#> • On this class we have defined attributes username and email and also annotated them with the str type.

#!------------------ Request Headers ------------------!#
#> During a request-response transaction, the client not only sends parameters to the server but also provides 
#> information about the context of the request's origin. This contextual information is crucial as it enables 
#> the server to customize the type of response it returns to the client.

## Common request headers include:
#> • User-Agent: This string allows network protocol peers to identify the application responsible for the request, 
#>   the operating system it's running on, or the version of the software being used.
#> • Host: This specifies the domain name of the server, and (optionally) the TCP port number on which the server is listening.
#> • Accept: Informs the server about the types of data that can be sent back.
#> • Accept-Language: This header informs the server about the preferred human language for the response.
#> • Accept-Encoding: The encoding algorithm, usually a compression algorithm, that can be used on the resource sent back.
#> • Referer: This specifies the address of the previous web page from which a link to the currently requested 
#>   page was followed.
#> • Connection: This header controls whether the network connection stays open after the current transaction finishes.

#> To access such headers, FastAPI provides us with the Header function giving us the ability to get the values of 
#> these headers using the exact names but in a snake-case syntax for example, User-Agent is user_agent, Accept-Encoding
#> is accept_encoding and so on. Let us take a look at a small code example.

@app.get('/get_headers')
async def get_all_request_headers(
    user_agent: Optional[str] = Header(default=None),
    accept_encoding: Optional[str] = Header(default=None),
    referer: Optional[str] = Header(default=None),
    connection: Optional[str] = Header(default=None),
    accept_language: Optional[str] = Header(default=None),
    host: Optional[str] = Header(default=None),
):
    request_headers = {}
    request_headers["User-Agent"] = user_agent
    request_headers["Accept-Encoding"] = accept_encoding
    request_headers["Referer"] = referer
    request_headers["Accept-Language"] = accept_language
    request_headers["Connection"] = connection
    request_headers["Host"] = host

    return request_headers
#> • We've started by importing the Header function from FastAPI into our route handler. 
#> • Each header has been added and designated as an optional string. 
#> • A default value has been assigned by invoking the Header function with None as a parameter. 
#> • Using the None argument allows the Header() function to declare the variable optionally, which aligns with best 
#>   practices.
