Reference API server of SMART Genomics

## How to use it
1. Install dependency with

	```
    # python 2.7
	# this might require previledge (e.g. sudo)
	# or use virtualenv instead (recommended)
	$ pip install -r requirements.txt
	```
    Install PostgreSQL. Currently we use PostgresSQL for development, and our script `setup_db.py` is written specifically for Postgre. Contributions to support MySQL are welcomed.

2. Edit `config.py`. Fill in settings for database, host, etc. as you desire. See comments in `config.py` for detailed instructions.

3. Optional: load your version of FHIR spec with the script `load_spec.py`, which will update `fhir/fhir_spec.py`. Please read comments in `load_spec.py` carefully before using it.
    The specification for Connectathon 11 can be downloaded at: http://www.hl7.org/fhir/2016Jan/downloads.html

4. If you haven't created the database you specified in `config.py`, simply use command below to create it
	
	```
	$ python setup_db.py
	``` 
5. Load sample data with

	```
	$ python load_example.py
	```
6. To run with `gunicorn` do

	```
	$ python server.py run
	```
7. Alternatively you can use `flask`'s debug instance like this

	```
	$ python server.py run --debug
	```
8. To wipe out the database (for debugging or whatever reason), do

	```
	$ python server.py clear
	```


The server will be running at `localhost` at `port 5000`.
The reload option clears the database and loads sample data. So do not use `reload` if you have something that you want to keep in the database.
* Go to `http://localhost:5000` in your browser, register an account. Once register, you will have an `App id` and an `App secret` (They correspond to **client_id** and **client_secret** in OAuth2) on your app dashboard, where you can setup your app's **redirect uri** and **name**.  

How to get access to the API using OAuth2
* redirect your user to the **authorization** page with following parameters (in this example, you are asking for permission to `read` all of the user's `Patient` and `Sequence` resources),
```
client_id: [your client id]
response_type: "code"
scope: "user/Sequence.read user/Patient.read" // space-delimited list of scope
redirect_uri: [redirect uri you put on your app dashboard]
state: [optional, i.e. you whatever you want here]
```
In the case of using the local API server, the url of the **authorization page** is `http://localhost:5000/auth/authorize`.
* If everything goes well, the user will be redirected to your **redirect uri** with following parameters:
```
code: [authorization code you will be using to exchange for access token]
state: [this will be the `state` you put in last step]
```
* Now you can exchange your `code` with a `access token`, which you can use to access the API.
* Simply make a `POST` request to the server, with following data,
```
grant_type: "authorization_code",
client_id: [client id],
client_secret: [client secret],
redirect_uri: [redirect uri],
code: [code you obatined in last step]
```
In the case of using the local API server, the url is `http://localhost:5000/auth/token`
* You will then get this JSON as a response:
```js
{
'access_token': [access token],
'expires_in': 3600,
'token_type': 'bearer'
}
```
* Now that you have `access token`, you can make an authorized request to the API by using this header in your HTTP request.
```
Authorization: Bearer [your accesstoken]
```
