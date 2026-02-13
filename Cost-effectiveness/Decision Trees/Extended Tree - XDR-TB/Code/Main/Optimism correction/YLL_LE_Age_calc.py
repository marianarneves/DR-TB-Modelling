
def classify_age(age):
    """
    Classifies the given age into the specified age categories.

    Parameters:
    age (int): The age to classify.

    Returns:
    str: The category that the age falls into.
    """
    if age < 1:
        return "<1 year"
    elif 1 <= age <= 4:
        return "1-4 years"
    elif 5 <= age <= 9:
        return "5-9 years"
    elif 10 <= age <= 14:
        return "10-14 years"
    elif 15 <= age <= 19:
        return "15-19 years"
    elif 20 <= age <= 24:
        return "20-24 years"
    elif 25 <= age <= 29:
        return "25-29 years"
    elif 30 <= age <= 34:
        return "30-34 years"
    elif 35 <= age <= 39:
        return "35-39 years"
    elif 40 <= age <= 44:
        return "40-44 years"
    elif 45 <= age <= 49:
        return "45-49 years"
    elif 50 <= age <= 54:
        return "50-54 years"
    elif 55 <= age <= 59:
        return "55-59 years"
    elif 60 <= age <= 64:
        return "60-64 years"
    elif 65 <= age <= 69:
        return "65-69 years"
    elif 70 <= age <= 74:
        return "70-74 years"
    elif 75 <= age <= 79:
        return "75-79 years"
    elif 80 <= age <= 84:
        return "80-84 years"
    else:
        return "85+ years"


def filter_dataframe(df, sex, ageband, period_value):
    """
    Filters the DataFrame based on provided conditions and retrieves the 'Value' column.

    Parameters:
    df (pd.DataFrame): The input DataFrame to filter.
    dim2_value (str): The value for the Dim2 column.
    dim1_value (str): The value for the Dim1 column.
    period_value (int): The value for the Period column.

    Returns:
    float or None: The value from the 'Value' column that matches the filter conditions, or None if no match is found.
    """
    # Apply the filter based on the provided conditions
    filtered_df = df[(df['Dim2'] == ageband) & (df['Dim1'] == sex) & (df['Period'] == period_value)]

    # Retrieve the 'Value' column for the filtered row
    if not filtered_df.empty:
        return filtered_df['Value'].values[0]
    else:
        return None


# # Assuming the file is saved as '/mnt/data/life_expectancy.csv'
# file_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/LE_Moldova.csv'
#
# # Load the CSV file into a DataFrame
# df = pd.read_csv(file_path)
#
# result = filter_dataframe(df,'Male' , '1-4 years', 2019)
#
# print(result)