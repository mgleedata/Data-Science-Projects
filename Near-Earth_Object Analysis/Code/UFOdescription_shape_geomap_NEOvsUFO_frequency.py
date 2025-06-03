import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import PorterStemmer 
from collections import Counter
from random import choice
import plotly.express as px

import re

df = pd.read_csv("updated_usa_ufo.csv")

df['Date'] = pd.to_datetime(df['Date'])

df = df[df['Date'].dt.year >= 2000]

nltk.download('stopwords')

STOPWORDS = set(stopwords.words('english'))
custom_words = ["note", "nuforc"]  # remove these words because they show up alot and are just administrative 
STOPWORDS.update(custom_words)

def clean_text(text):
    """
    Clean the text.
    """
    text = text.lower()  # convert to lowercase
    
    # remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # remove numbers 
    text = re.sub(r'\d+', '', text)
    
    # remove stopwords
    
    text = ' '.join(word for word in text.split() if word not in STOPWORDS)
    
    stemmer = PorterStemmer() 
    
    #stem words
    
    text = ' '.join([stemmer.stem(word) for word in text.split()])
    
    
    # Remove extra whitespaces
    
    text = ' '.join(text.split())

    
    return text

#clean the text column

df['Summary Clean'] = df['Summary'].apply(clean_text)

""" WORD CLOUD"""

text = ' '.join(df['Summary Clean'])

tokens = text.split()

#some of word endings got taken off in the process of stemming, so adding them back in before visualizing in the word cloud 

tokens = ['orange' if word == 'orang' else word for word in tokens]
tokens = ['fly' if word == 'fli' else word for word in tokens]
tokens = ['triangle' if word == 'triangl' else word for word in tokens]
tokens = ['change' if word == 'chang' else word for word in tokens]
tokens = ['large' if word == 'larg' else word for word in tokens]
tokens = ['slowly' if word == 'slowli' else word for word in tokens]
tokens = ['quickly' if word == 'quickli' else word for word in tokens]
tokens = ['fireball' if word == 'firebal' else word for word in tokens]
tokens = ['strang' if word == 'strange' else word for word in tokens]

#the original color pallete was too neon, so we picked less neon colors for the wordcloud 

def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    colors = [
    '#DAA520', 
    '#4682B4',  
    '#6B8E23', 
    '#FF6347', 
    '#8B4513',  
    '#7B68EE',  
    '#B22222',  
    '#32CD32',  
    '#FF69B4',  
    '#D2691E'   
    ]
    return choice(colors)

token_freq = Counter(tokens)

wordcloud = WordCloud(width=800, height=400, background_color='white',color_func=color_func).generate_from_frequencies(token_freq)

plt.figure(figsize=(10, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.title("Most Common Words by Size in UFO Sighting Descriptions")
plt.axis('off')
plt.show()

"""DURATION CLEANING"""

#lower case duration text 

df['Duration'] = df['Duration'].str.lower()

#normalize all duration to mintues with the parse function

def parse_duration(duration_str):
    
    # map word to numeric value
   
    word_to_number = {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
        'ten': 10  
    }
    
    # check if any of the word representations are in the string
    for word, num in word_to_number.items():
        if word in duration_str:
            duration_str = duration_str.replace(word, str(num))

    # extract numeric values
    numbers = re.findall(r"\d+\.?\d*", duration_str)
    if not numbers:
        return None
    
    #handle cases for seconds, minutes, and hour below"

    if "sec" in duration_str:
        if "-" in duration_str:  
            return sum([float(n) / 60.0 for n in numbers]) / len(numbers)  # average the range
        else:
            return float(numbers[0]) / 60.0 

    elif "min" in duration_str:
        if "-" in duration_str:  
            return sum([float(n) for n in numbers]) / len(numbers) 
        else:
            return float(numbers[0])

    elif "hour" in duration_str or  "hr" in duration_str or  "hrs" in duration_str:
        if "-" in duration_str: 
            return sum([float(n) * 60.0 for n in numbers]) / len(numbers)  
        else:
            return float(numbers[0]) * 60.0
        
#make all duration to minutes
        
df['Duration_min'] = df['Duration'].apply(parse_duration)

#combine other and unknown shape

df.loc[(df['Shape'] == "Unknown") | (df['Shape'] == "Other"), "Shape"] = "Unknown/Other"


"""DURATION GRPAH""""

shapewise_avg = df.groupby('Shape')['Duration_min'].mean().sort_values(ascending=False)

plt.figure(figsize=(12, 8))
sns.barplot(y=shapewise_avg.index, x=shapewise_avg.values)
plt.xlabel('Average Duration (minutes)',fontsize=14)
plt.ylabel('UFO Shape',fontsize=14)
plt.title('Average UFO Sighting Duration by Shape',fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=12)

plt.show()


"""UFO GEO MAP"""


#aggregate UFO sightings by state

state_counts = df['State'].value_counts().reset_index()
state_counts.columns = ['State', 'Count']

#areate the choropleth map
fig = px.choropleth(state_counts,
                    locations='State',
                    color='Count',
                    locationmode='USA-states',
                    scope="usa",
                    color_continuous_scale="Viridis",
                    title="UFO Sightings by State"
                   )
fig.update_layout(width=800, height=500)

fig.show()


"""NEO VS UFO GRAPHS BY YEAR, MONTH, DAY OF WEEK, HOUR"""

"""YEAR"""

nasa_data = pd.read_csv("cleaned_nasa_neo_data.csv")

ufo_sightings_year = df.groupby(df['Date'].dt.year).size()

nasa_data['date'] = pd.to_datetime(nasa_data['date'])

object_count_year = nasa_data.groupby(nasa_data['date'].dt.year)['object'].count()

plt.figure(figsize=(15, 7))

# plot ufo data
plt.plot(ufo_sightings_year.index, ufo_sightings_year, label='UFO Sightings', marker='o',color="red")

# plot NEO data
plt.plot(object_count_year.index, object_count_year, label='NEO Object', marker='x',color="blue")

# Labels and title
plt.xlabel("Year",fontsize=16)
plt.ylabel("Frequency (log scale)",fontsize=16)
plt.title("UFO Sightings vs. NEO Object Count Over the Years",fontsize=16)
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.yscale('log')  # Set y-axis to log scale
plt.tight_layout()
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

plt.show()

"""MONTH"""

object_count_month.index = object_count_month.index.astype(int)

plt.figure(figsize=(12, 6))

#plot ufo data
plt.plot(ufo_monthly_freq.index, ufo_monthly_freq.values, label='UFO Sightings', marker="o", color='red')

#plot neo data
plt.plot(object_count_month.index, object_count_month.values, label='NEO Object', marker="x", color='blue')

plt.yscale('log')
plt.legend()
plt.grid(True, which="both", ls="--", c='0.7')
plt.xlabel('Month', fontsize=12)
plt.ylabel('Frequency (Log Scale)', fontsize=12)
plt.title('UFO Sightings vs. NEO Object Count by Month', fontsize=12)
plt.xticks(range(1, 13), fontsize=12)
plt.yticks(fontsize=12)

plt.show()

"""HOUR"""

#The time column was messed up for some reason in the nasa_data, so I cleaned up the time column or "cd" by loading the orignal dataset in which I call "a".
#But it is still the same as nasa_data, just with a time column formatted 

a = pd.read_csv("neo_updated.csv")

a['cd'] = pd.to_datetime(a['cd'])
a['Year'] = a['cd'].dt.year

a = a[a["Year"]>=2000]

a['Time'] = a['cd'].dt.time


df['Hour'] = pd.to_datetime(df['Time']).dt.hour
ufo_hourly_counts = df['Hour'].value_counts().sort_index()

a['Hour'] = a['Time'].apply(lambda x: x.hour)
hourly_counts = a['Hour'].value_counts().sort_index()


plt.figure(figsize=(15,6))


hourly_counts.plot(logy=True, marker='x', linestyle='-', label='NEO Object',color='blue')


ufo_hourly_counts.plot(logy=True, marker='o', linestyle='--', color='red', label='UFO Sightings')

plt.title('UFO Sightings vs. NEO Object Count by Hour', fontsize=16)
plt.xlabel('Hour of the Day',fontsize=16)
plt.ylabel('Frequency (Log Scale)',fontsize=16)
plt.xticks(list(range(24)), [str(i) + ":00" for i in range(24)], rotation=45,fontsize=16)
plt.yticks(fontsize=16)
plt.grid(True, which="both", ls="--", c='0.7')
plt.legend()
plt.tight_layout()
plt.show()

"""DAY OF WEEK"""

#extract day of the week
a['DayOfWeek'] = a['cd'].dt.day_name()
df['DayOfWeek'] = df['Date'].apply(pd.to_datetime).dt.day_name()

days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

neo_day_counts = a['DayOfWeek'].value_counts().reindex(days_order)
ufo_day_counts = df['DayOfWeek'].value_counts().reindex(days_order)

plt.figure(figsize=(8,6))

neo_day_counts.plot(logy=True, marker='x', linestyle='-', label='NEO Object')

ufo_day_counts.plot(logy=True, marker='o', linestyle='--', color='red', label='UFO Sightings')

plt.title('UFO Sightings vs. NEO Object Count by Day of the Week', fontsize=12)
plt.xlabel('Day of the Week',fontsize=12)
plt.ylabel('Frequency (Log Scale)',fontsize=12)
plt.xticks(rotation=45,fontsize=12)
plt.yticks(fontsize=12)

plt.grid(True, which="both", ls="--", c='0.7')

plt.legend()
plt.tight_layout()
plt.show()


