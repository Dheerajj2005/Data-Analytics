import re
import pandas as pd

def preprocess(data='string'):
    pattern = '\d{1,2}\/\d{1,2}\/\d{2},\s\d{1,2}:\d{2}\s(?:am\s|pm\s)?-\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    df = pd.DataFrame({'Dates': dates, 'Messages': messages})
    usernames = list()
    messages = list()

    for i in df['Messages']:
        values = re.split('([\w\W]+?):\s', i)

        if len(values) > 2:
            usernames.append(values[1])
            messages.append(values[2])
        else:
            usernames.append('Notifications')
            messages.append(values[0])
    df['User'] = usernames
    df['Message'] = messages
    df.drop(columns='Messages', inplace=True)

    df['Dates'] = df['Dates'].str.split('-', expand=True)[0].str.strip()

    df['Dates'] = pd.to_datetime(df['Dates'], format='%d/%m/%y, %H:%M %p')

    def convert_to_24hr(time_str):
        return pd.to_datetime(time_str, format='%d/%m/%y, %I:%M %p').strftime('%H:%M')

    df['only_date'] = df['Dates'].dt.date
    df['Day'] = df['Dates'].dt.day
    df['Month_num'] = df['Dates'].dt.month
    df['Month'] = df['Dates'].dt.strftime('%b')
    df['Year'] = df['Dates'].dt.year
    df['Day_name'] = df['Dates'].dt.day_name()
    df['Hour'] = df['Dates'].dt.hour
    df['Minute'] = df['Dates'].dt.minute

    period = []
    for hour in df[['Day_name', 'Hour']]['Hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour+1))
        else:
            period.append(str(hour) + "-" + str(hour+1))

    df['period'] = period

    return df
