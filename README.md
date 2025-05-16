# Fittrack-Webapp

Fitness tracking data analysis and sharing app for CITS5505 Agile Web Dev project.

## Project Overview

FitTrack is a web application designed for comprehensive fitness tracking, data analysis, and secure sharing. It empowers users to log their workouts, nutritional intake, and emotional well-being, providing insightful visualizations to monitor progress and achieve health goals. The platform also facilitates sharing achievements and data with other users under configurable permissions, fostering a supportive fitness community.

## Key Features

*   **User Authentication:** Secure registration and login for a personalized user experience.
*   **Comprehensive Data Logging:**
    *   Log various fitness activities with details like duration, calories burned, activity type, intensity, and associated emotions.
    *   Record food intake, including meal types (breakfast, lunch, dinner, snack), food items, quantities, and calories.
    *   Track emotional well-being to understand its correlation with fitness activities.
*   **Interactive Data Visualization:**
    *   Dynamic charts displaying trends in workout duration, calories burned, calorie efficiency (calories per minute), and workout intensity.
    *   Performance radar chart for a holistic view of fitness metrics such as consistency, average duration, average intensity, activity frequency, and diversity.
    *   Emotion tracking charts (e.g., pie charts) to visualize mood patterns associated with workouts.
    *   Goal progress tracker for user-defined or predefined goals (e.g., weekly activity sessions, daily movement minutes, calorie burn targets, activity diversity).
    *   Nutrition analysis charts, including calorie balance (consumed vs. burned) and breakdown of calories by meal type.
*   **Data Sharing & Collaboration:**
    *   Securely share selected fitness data (e.g., activity logs, meal logs, data summaries) with other users on the platform.
    *   Fine-grained control over sharing permissions, allowing users to specify which data categories are shared and for how long.
    *   View data shared by other users, subject to their permissions.
    *   Manage active shares and revoke sharing access at any time.
    *   Access a history of sharing activities.
*   **Community & Ranking:**
    *   User ranking system based on configurable metrics like total calories burned or total workout duration over specific time periods (e.g., weekly, monthly).
    *   Medal emojis for top-ranked users.
*   **Personalization & User Experience:**
    *   Light and Dark mode support for user preference, with automatic detection of system preference.
    *   Responsive design for optimal viewing and interaction across various devices (desktops, tablets, mobiles).
    *   Integrated To-Do list feature on the data upload page for daily planning.
    *   User-friendly interface with clear navigation, including a "Back to Top" button and smooth scrolling.
    *   Informative flash messages for user feedback on actions (e.g., success, error, warning).
    *   Client-side form validation and enhanced user input fields.

## Technology Stack

*   **Backend:**
    *   Python
    *   Flask (Web Framework)
    *   SQLAlchemy (Object-Relational Mapper)
    *   Alembic (Database Migrations)
*   **Frontend:**
    *   HTML5
    *   Tailwind CSS (Utility-first CSS Framework)
    *   JavaScript (ES6+)
    *   jQuery
    *   Chart.js (Data Visualization Library)
    *   Font Awesome (Icons)
*   **Database:**
    *   (Not specified, but compatible with SQLAlchemy, e.g., PostgreSQL, MySQL, SQLite)
*   **Development & Deployment:**
    *   Python Virtual Environment (`venv`)
    *   Git & GitHub for version control.

## Project Structure

A brief overview of the main directories and files:

```
fittrack-webapp/
├── static/               # Static assets
│   ├── css/              # Compiled CSS (output.css) and custom styles (style.css)
│   ├── js/               # JavaScript files (main.js, visualise.js, upload.js, share.js)
│   └── img/              # Image assets (favicon, logos, etc.)
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base layout template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── upload.html       # Data upload page
│   ├── visualise.html    # Data visualization page
│   ├── share.html        # Data sharing page
│   ├── privacy_policy.html # Privacy Policy page
│   └── terms_of_service.html # Terms of Service page
├── migrations/           # Alembic database migration scripts
├── app.py                # Main Flask application (assumed location)
├── models.py             # SQLAlchemy models (assumed location)
├── requirements.txt      # Python dependencies
├── tailwind.config.js    # Tailwind CSS configuration
└── README.md             # This file
```

## Setup and Installation

1.  **Prerequisites:**
    *   Python 3.x
    *   `pip` (Python package installer)
    *   `git` (Version control)

2.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd fittrack-webapp
    ```

3.  **Create and activate a virtual environment:**
    *   If `python3-venv` is not installed (Debian/Ubuntu):
        ```bash
        sudo apt update
        sudo apt install python3-venv
        ```
    *   Create a virtual environment (e.g., named `.venv`):
        ```bash
        python3 -m venv .venv
        ```
    *   Activate the virtual environment:
        *   On macOS or Linux:
            ```bash
            source .venv/bin/activate
            ```
        *   On Windows:
            ```bash
            .venv\Scripts\activate
            ```

4.  **Install required packages:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Database Setup:**
    *   Configure your database connection string (e.g., in a `.env` file or directly in `config.py`, depending on project setup - details should be added if specific).
    *   Initialize and apply database migrations:
        ```bash
        flask db upgrade
        ```
        (This assumes Flask-Migrate is set up. If it's the first time: `flask db init`, `flask db migrate -m "Initial migration"`, then `flask db upgrade`)

## Running the Application

1.  Ensure your virtual environment is activated:
    ```bash
    source .venv/bin/activate
    ```
    (Or `.venv\Scripts\activate` on Windows)

2.  Compile Tailwind CSS (if not automatically done by Flask or a build script):
    ```bash
    # (Add command if manual Tailwind compilation is needed, e.g., npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch)
    # For this project, output.css seems to be pre-compiled or managed by Tailwind JIT via CDN script in base.html.
    ```

3.  Run the Flask development server:
    ```bash
    flask run
    ```

4.  Open your web browser and navigate to `http://127.0.0.1:5000/` (or the address shown in your terminal).

## Usage

1.  **Register/Login:** Create a new user account or log in with existing credentials.
2.  **Upload Data:**
    *   Navigate to the "Upload" page.
    *   Enter basic information (date, time, gender).
    *   Log exercise details: activity type, duration, calories burned, intensity, and how you felt (emotion).
    *   Record food intake: food item, meal type (Breakfast, Lunch, Dinner, Snack), quantity, and calories.
    *   Utilize the "To-Do List" notebook on the upload page to jot down daily plans or fitness notes (data saved in browser's local storage).
3.  **Visualize Progress:**
    *   Go to the "Visualize" page.
    *   Select a date range for the data you want to analyze.
    *   Explore various interactive charts:
        *   Trends for workout duration, calories burned, calorie efficiency, and intensity.
        *   A performance radar chart summarizing consistency, duration, intensity, frequency, and diversity.
        *   Emotion distribution related to your workouts.
        *   Progress towards your fitness goals.
        *   Calorie balance and nutritional breakdown by meal type.
    *   If enabled, view your position on the user ranking leaderboard.
4.  **Share Data:**
    *   Access the "Share" page.
    *   Configure new sharing permissions: select a user, choose data categories (e.g., activity log, meal log, daily summary), and set an optional expiration date.
    *   View data that other users have shared with you.
    *   Manage your active shares and revoke access if needed.
    *   Review your history of sharing activities (who you shared with, what was shared, and when).
5.  **User Profile & Settings:** (Details depend on implementation)
    *   Manage your account details.
    *   Toggle between light and dark themes using the navigation bar icon.

## Group Members

| UWA STUDENT ID | NAME          | GITHUB ACCOUNT  |
| -------------- | ------------- | --------------- |
| 23917077       | Vincent Wang  | VincentWang2961 |
| 24201328       | Ethika Biswas | ethika-biswas   |
| 24400725       | Yidan Xu      | EdenXu886       |
| 24447687       | Kunyang Xie   | KunyangS        |

## Contributing

Contributions are welcome! If you'd like to contribute to FitTrack, please follow these general steps:

1.  **Fork the repository** on GitHub.
2.  **Clone your forked repository** to your local machine.
3.  **Create a new branch** for your feature or bug fix:
    ```bash
    git checkout -b feature/your-amazing-feature
    ```
4.  **Make your changes** and commit them with clear, descriptive messages:
    ```bash
    git commit -m "Add: Implement the amazing feature"
    ```
5.  **Push your changes** to your forked repository:
    ```bash
    git push origin feature/your-amazing-feature
    ```
6.  **Open a Pull Request** from your branch to the main FitTrack repository.
7.  Ensure your code adheres to the project's coding standards and includes tests if applicable.

## License

This project is licensed under the MIT License.

