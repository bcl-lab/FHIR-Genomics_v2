Instructions

1. Make sure the FHIR server and Genetics Report app are running in the background
python server.py -d (located here in this repo)
python app.py -d (located outside in the private Genetics Report repo)

2. Install the test requirements (from the "automated_tests" folder)
pip install -r test_requirements.txt

3. Install Firefox if it's not already installed on the system
sudo apt-get install firefox
(You can also run "./install_firefox" from the automated_tests folder)

4. Run the basic tests
py.test genomics_viewer_tests.py --with-selenium
(Or run "./run_tests.sh" from the automated_tests folder)
