from flask import Flask, render_template
import pandas as pd
import mysql.connector
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = Flask(__name__)

# Route to display the output
@app.route('/')
def display_output():
    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
        host='localhost',
        database='internship',
        user='sqluser',
        password='password'
    )
    cursor = connection.cursor()

    # Datatypes
    query = "DESCRIBE titanic"
    cursor.execute(query)
    columns = cursor.fetchall()
    column_names = ['Column', 'Type', 'Null', 'Key', 'Default', 'Extra']
    dt_df = pd.DataFrame(columns, columns=column_names)

    # Dropping unwanted columns
    unwanted_columns = ['Null', 'Key', 'Default', 'Extra']
    dt_df = dt_df.drop(columns=unwanted_columns)

    # Update the "Type" column to remove b'' and keep only the integer value
    dt_df['Type'] = dt_df['Type'].str.decode('utf-8').str.extract(r"(\w+)")

    # Duplicate rows in the table
    query1 = "SELECT * FROM titanic"
    cursor.execute(query1)
    data = cursor.fetchall()
    titanic_data = pd.DataFrame(data, columns=['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age',
                                               'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked'])
    duplicate = titanic_data[titanic_data.duplicated(['Name'])]

    # Null values
    null_values = titanic_data.isnull().sum()

    # Replace None values with NaN
    rows = [tuple(np.nan if value is None else value for value in row) for row in data]
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

    # Check for null rows
    null_rows = df[df.isnull().any(axis=1)]

    # Get the count of duplicates for each column
    duplicates_count = df.duplicated().sum()

    # Descriptive Statistics
    desc_stats = df.describe()[['Age', 'Fare']]

    # Histogram
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=df['Age'], nbinsx=10, name='Age'))
    fig_hist.update_layout(title='Histogram', xaxis_title='Age', yaxis_title='Count')

    # # Box Plot
    # fig_box = go.Figure()
    # fig_box.add_trace(go.Box(y=df['Fare'], name='Fare'))
    # fig_box.update_layout(title='Box Plot', yaxis_title='Fare')

    # # Close the database connection
    # connection.close()

    # return render_template('index.html', dt_df=dt_df, duplicate=duplicate, null_values=null_values,
    #                        null_rows=null_rows, duplicates_count=duplicates_count, desc_stats=desc_stats,
    #                        fig_hist=fig_hist.to_html(full_html=False, include_plotlyjs='cdn'),
    #                        fig_box=fig_box.to_html(full_html=False, include_plotlyjs='cdn'))

    # Calculate variance of the 'Fare' column
    fare_variance = df['Fare'].var()

    # Store validation messages
    validation_messages = []

    # Declare fig_box with a default value
    fig_box = None

    # Validate and create the box plot only if the variance is high
    if fare_variance > 1000:
        # Box Plot
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(y=df['Fare'], name='Fare'))
        fig_box.update_layout(title='Box Plot', yaxis_title='Fare')

        # Add validation message
        validation_messages.append("Box plot created successfully.")
        validation_messages.append(f"Variance of 'Fare' column: {fare_variance}")
    else:
        # Add validation message
        validation_messages.append("Box plot not created. Variance of 'Fare' column is not high enough.")
        validation_messages.append(f"Variance of 'Fare' column: {fare_variance}")

    # Close the database connection
    connection.close()

    fig_box_html = fig_box.to_html(full_html=False, include_plotlyjs='cdn') if fig_box is not None else ''

    return render_template('index.html', dt_df=dt_df, duplicate=duplicate, null_values=null_values,
                           null_rows=null_rows, duplicates_count=duplicates_count, desc_stats=desc_stats,
                           fig_hist=fig_hist.to_html(full_html=False, include_plotlyjs='cdn'),
                           fig_box=fig_box_html,
                           validation_messages=validation_messages)


if __name__ == '__main__':
    app.run(debug=True)
