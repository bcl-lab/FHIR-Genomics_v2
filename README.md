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
