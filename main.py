from website import create_app
from dotenv import load_dotenv
load_dotenv()     # this will read .env and populate os.environ


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
