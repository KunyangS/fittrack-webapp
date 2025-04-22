from app import app

# --- Run the App ---
if __name__ == '__main__':
    # Runs the Flask development server
    # Debug=True allows auto-reloading on code changes
    app.run(debug=True)
    # print(app.url_map)
