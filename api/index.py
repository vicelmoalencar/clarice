from app import app

# This is required for Vercel
app.debug = False

if __name__ == '__main__':
    app.run()
