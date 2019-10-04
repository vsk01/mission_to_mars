#!/usr/bin/env python
# coding: utf-8

# # Import the depencies for the scrapping work
# 1.  Browser
# 2.  BeautifulSoup

# In[1]:


# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


# In[2]:
def scrape_all():

    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = news_about_mars(browser)

    # create dictionary to store and send to MongoDB.
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        # "hemispheres": scrape_mars_hemispheres(browser),
        "weather": twitter_weather(browser),
        "facts": scrape_mars_facts(),
        "last_modified": dt.datetime.now()
    }

    # Once data is sucessfully retrieved close the browser
    browser.quit()
    return data

# <div class="alert alert-block alert-info">
#  1.NASA Mars News
# </div>

# In[4]:

def news_about_mars(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
	
    # Wait for page loading
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
	
    # In[5]:
    # Convert the browser html to a soup object and process this object for additional information
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
	
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # In[6]:
        # Get `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
		
        # In[7]:
        # Get paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
		
    except AttributeError:
        return None, None

    return news_title, news_p

##############################################
# <div class="alert alert-block alert-info">
#  2 JPL Mars Images
# </div>
##############################################
# In[11]:

def featured_image(browser):
    # Visit Mars Space Images through splinter module
    image_url_featured = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url_featured)
    # HTML Object 
    html_image = browser.html
    # In[12]:
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html_image, 'html.parser')
    # Retrieve background-image url from style tag 

    try:
        image_url_featured  = soup.find('article')['style'].replace('background-image: url(','').replace(');', '')[1:-1]

    except AttributeError:
        return None

    # In[13]:
    # Website Url 
    main_url = 'https://www.jpl.nasa.gov'
    # Concatenate website url with scrapped route
    image_url_featured = main_url + image_url_featured
    # Display full link to featured image

    return image_url_featured


########################################################
# <div class="alert alert-block alert-info">
#    3 Mars Weather
# </div>
########################################################
# In[17]:
# Visit Mars Weather Twitter through splinter module
def twitter_weather(browser):
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)
    # In[19]:
    # HTML Object 
    html_weather = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html_weather, 'html.parser')
    # In[20]:
    # Find all elements that contain tweets
    latest_tweets = soup.find_all('div', class_='js-tweet-text-container')
    # Retrieve all elements that contain news title in the specified range
    # Look for entries that display weather related words to exclude non weather related tweets 
    for tweet in latest_tweets: 
        weather_tweet = tweet.find('p').text
        if 'Sol' and 'pressure' in weather_tweet:
            return weather_tweet
##############################################################

##############################################################
# <div class="alert alert-block alert-info">
#    4 Mars Facts
# </div>
##############################################################
# In[22]:

def scrape_mars_facts():
    # Visit Mars facts url 
    facts_url = 'https://space-facts.com/mars/'
    # Use Panda's `read_html` to parse the url
    mars_facts = pd.read_html(facts_url)
    # print(mars_facts)
    # Find the mars facts DataFrame in the list of DataFrames as assign it to `mars_df`
    mars_df = mars_facts[1]
    # print(mars_df)
    # Assign the columns `['Description', 'Value']`
    mars_df.columns = ['Description','Value']
    # Set the index to the `Description` column without row indexing
    mars_df.set_index('Description', inplace=True)
    # return data with bootstrap formatting
    data = mars_df.to_html(classes="table table-striped")
    return data

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~``````
# <div class="alert alert-block alert-info">
#    5 Mars Hemisphere
# </div>
# In[23]:
def scrape_mars_hemispheres(browser):

    try: 
        # Visit hemispheres website through splinter module 
        hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(hemispheres_url)
        # In[24]:
        # HTML Object
        html_hemispheres = browser.html
        # Parse HTML with Beautiful Soup
        soup = BeautifulSoup(html_hemispheres, 'html.parser')
        # Retreive all items that contain mars hemispheres information
        items = soup.find_all('div', class_='item')
        # Create empty list for hemisphere urls 
        hemisphere_image_urls = []
        # Store the main_ul 
        hemispheres_main_url = 'https://astrogeology.usgs.gov'
        
        # Loop through the items previously stored
        for i in items: 
            # Store title
            title = i.find('h3').text
            
            # Store link that leads to full image website
            partial_img_url = i.find('a', class_='itemLink product-item')['href']
            
            # Visit the link that contains the full image website 
            browser.visit(hemispheres_main_url + partial_img_url)
            
            # HTML Object of individual hemisphere information website 
            partial_img_html = browser.html
            
            # Parse HTML with Beautiful Soup for every individual hemisphere information website 
            soup = BeautifulSoup( partial_img_html, 'html.parser')
            
            # Retrieve full image source 
            img_url = hemispheres_main_url + soup.find('img', class_='wide-image')['src']
            
            # Append the retreived information into a list of dictionaries 
            hemisphere_image_urls.append({"title" : title, "img_url" : img_url})
        
        # Return mars_data dictionary 
        return hemisphere_image_urls
    finally:
        #if anything fails , close browser
        browser.quit()    

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())