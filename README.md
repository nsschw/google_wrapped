# Google Wrapped

This project is a web application built with Dash, a Python framework for building analytical web applications. The application allows users to analyze their online activity data.

## Features

- **Data Input**: Users can input their activity data file, specify the language, and set a date range for the analysis.
- **Basic Facts**: The application provides basic facts about the user's online activity, such as the total number of searches, the day with the most searches, and the longest time span without any searches. These facts are displayed in a clear and readable format, with relevant icons for easy understanding.
- **Searches Over Time**: The application visualizes the user's search activity over time in various ways. It provides a line chart of searches per week, a heatmap of search activity, and a bar chart of the most searched terms.

## How to Run

First you need to request your Google data at: https://takeout.google.com/?continue=https://myaccount.google.com/dashboard. You need to request the Searches in the MyActivity Dataset in JSON Format and unzip it. 

To run this application, you need to have Python and Dash installed. You can then clone this repository and run `app.py`.

```bash
git clone https://github.com/nsschw/google_wrapped/
cd <repository-name>
python app.py
```

The application will start a local server and you can access the application in your web browser at `http://localhost:8050`.

## Dependencies

This project uses the following libraries:

- Dash
- Dash Bootstrap Components
- Plotly
- pandas
- numpy

Make sure to install these dependencies before running the application.

```bash
pip install dash dash-bootstrap-components plotly pandas dash[diskcache] numpy
```

## License

This project is licensed under the terms of the MIT license.
