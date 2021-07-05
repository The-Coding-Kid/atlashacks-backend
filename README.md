# atlashacks-backend

Repo for atlashacks backend

1. Clone this repo

2. Run `virtualenv -p python3 env`

3. Run `pip install -p requirements.txt`

4. Create a service key from your google cloud console for google-vision-api as a JSON file

5. Save that json file somewhere in your computer(REMEMBER THE PATH!!!!!)

6. In your .zshrc file (or .bashrc) add this line of code: `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/json/file"`

7. Do `source .zshrc` (or `source .bashrc`)

8. Run `python3 wsgi.py`

9. Server is running now
