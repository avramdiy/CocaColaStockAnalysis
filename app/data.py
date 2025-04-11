from flask import Flask, render_template_string, send_file
import pandas as pd
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Path to your CSV file
CSV_FILE_PATH = r'C:\\Users\\Ev\\Desktop\\TRG Week 19\\CocaCola.csv'

# HTML for rendering the table
HTML = """
<!doctype html>
<html lang="en">
<head>
    <title>CSV Data</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #000; /* Adds solid black borders */
            padding: 8px; /* Adds padding for readability */
        }
        th {
            background-color: #f4f4f4; /* Light background for headers */
        }
        tr:nth-child(even) {
            background-color: #f9f9f9; /* Alternating row colors */
        }
        tr:hover {
            background-color: #f1f1f1; /* Highlight row on hover */
        }
    </style>
</head>
<body>
    <h1>CSV Data</h1>
    {{ table | safe }}
</body>
</html>
"""


@app.route('/')
def display_csv():
    try:
        # Load CSV file into a DataFrame
        df = pd.read_csv(CSV_FILE_PATH)

        # Ensure the 'date' column is in datetime format with UTC
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], utc=True)

            # Define the start and end dates in UTC
            start_date = pd.Timestamp('1962-01-01', tz='UTC')
            end_date = pd.Timestamp('1962-12-31', tz='UTC')

            # Filter for dates between January 1, 1962, and December 31, 1962
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

        if 'close' in df.columns:
            df.drop(columns=['close'], inplace=True)
        if 'adj_close' in df.columns:
            df.rename(columns={'adj_close': 'close'}, inplace=True)

        # Convert DataFrame to HTML table
        table_html = df.to_html(index=False, classes='dataframe', border=0)

        # Render the table in the HTML template
        return render_template_string(HTML, table=table_html)
    except Exception as e:
        return f"Error loading CSV file: {str(e)}"
    
@app.route('/plot')
def plot_chart():
    try:
        # Load CSV file into DataFrame
        df = pd.read_csv(CSV_FILE_PATH)

        # Ensure the 'date' column is in datetime format with UTC
        df['date'] = pd.to_datetime(df['date'], utc=True)

        # Filter for dates in 1962
        df = df[(df['date'] >= '1962-01-01') & (df['date'] <= '1962-12-31')]

        # Group by month and calculate the average values
        df['month'] = df['date'].dt.to_period('M')
        monthly_avg = df.groupby('month').mean()

        # Plot the averages for open, close, high, and low
        plt.figure(figsize=(12, 8))
        plt.plot(monthly_avg.index.astype(str), monthly_avg['open'], label='Average Open', marker='o')
        plt.plot(monthly_avg.index.astype(str), monthly_avg['close'], label='Average Close', marker='o')
        plt.plot(monthly_avg.index.astype(str), monthly_avg['high'], label='Average High', marker='s', linestyle='--')
        plt.plot(monthly_avg.index.astype(str), monthly_avg['low'], label='Average Low', marker='s', linestyle='--')

        plt.xlabel('Month')
        plt.ylabel('Price')
        plt.title('Average Monthly Prices (1962)')
        plt.legend()
        plt.grid(True)

        # Save the plot to a BytesIO object
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()

        return send_file(img, mimetype='image/png')
    except Exception as e:
        return f"Error generating plot: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
