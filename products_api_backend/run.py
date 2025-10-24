from app import app

if __name__ == "__main__":
    # Bind to 0.0.0.0 on port 3001 for preview environment (as required)
    app.run(host="0.0.0.0", port=3001)
