# ********************************************************************************************************
# ***********************************                        *********************************************
# ***********************************       LIBRARIES:       *********************************************
# ***********************************                        *********************************************
# ********************************************************************************************************

# UrlLib: URL handling module for python. It is used to fetch URLs (Uniform Resource Locators).
# It uses the urlopen function and is able to fetch URLs using a variety of different protocols.
# Urllib is a package that collects several modules for working with URLs, such as Request, a module used to download
# web pages
# Used to download the HTML page

# Pandas: pandas is a software library written for the Python programming language for data manipulation
# and analysis.In particular, it offers data structures and operations for manipulating numerical tables
# and time series.
# Used to save the scraped pages into DataFrames objects

# Numpy: NumPy is a library for the Python programming language, adding support for large, multidimensional
# arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays
# Used to Plot results

# BeautifulSoup4: Beautiful Soup is a Python package for parsing HTML and XML documents. It creates a
# parse tree for parsed pages that can be used to extract data from HTML, which is useful for web scraping
# Used to iterate through the pages of the website and grab specific content

# Matplotlib.pyplot: Tools to plot our charts

# Display: Create a display object given raw data.
# Used it to debug the program by printing on the cmd line the scraped pages while downloading them.

import urllib
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from IPython.display import display

# ***********************************       WARNING:     *********************************************
# if the program gives error on the urllib importing module, add the following line of code
# import urllib.request


# ********************************************************************************************************
# ***********************************                        *********************************************
# ***********************************     Global Variables   *********************************************
# ***********************************                        *********************************************
# ********************************************************************************************************

# Scraped website's URL defined as a constant
base_url = "https://nextspaceflight.com"


# or less rocket launches listed
# (ca. 215 pages) and per each of them we will extract info on

# ********************************************************************************************************
# ***********************************                        *********************************************
# ***********************************    SUPPORT FUNCTIONS   *********************************************
# ***********************************                        *********************************************
# ********************************************************************************************************

# 1) scrape_page:
# This Function first downloads the HTML page and loops through the 30 the displayed launches (30 launches
# per page) including the link to the 'detail' page of each launch.
#   As Arguments, the function takes the page (integer, here not defined as int) and a flag used to scrape
#   either "Future" or "Past" launches
#   It returns a DataFrame with the scraped launches in it.
def scrape_page(page, future=False):
    # defining the data structures required to store the different crawled elements we will define later on
    # page_launches will contain the launches stored as dictionaries (see later for more info)
    # page_details will contain the detail information of each launch stored as (see later for more info)
    page_launches = []
    page_details = []

    # Now we edit the url of the page to download based on the launches we want to collect, reflecting
    # the structure of the website. The format() method formats the specified value(s) and inserts them
    # inside the string's placeholder, defined using curly brackets: {}.
    if future:
        url = base_url + "/launches/?page={0}".format(page)
    else:
        url = base_url + "/launches/past/?page={0}".format(page)

    # Downloading the page as previously defined
    html = urllib.request.urlopen(url)

    # Parsing the page using the BS4 library, i.e. identifying HTML elements
    soup = BeautifulSoup(html, "html.parser")

    # Storing the  by going through the HTML formatted page and searching for rocket launches as HTML elements:
    # the find() function searches for all the div elements with a specific class in the downloaded page and returns
    # ONLY the first element. In our case, per each page we have one mdl-grid class div containing many "mdl-cell"
    # class divs, which we fetch with the find_all() function and store in the cells Set.
    table = soup.find('div', {'class': 'mdl-grid'})
    cells = table.find_all('div', {'class': 'mdl-cell'})

    # Looping through rocket launches of this page and attempting to collect and store the information of each launch
    for cell in cells:
        try:
            # Company
            # The Company name is always contained inside a span element which is inside a "mdl-card__title" class div
            # we then use the functions replace() and strip() to trim the string (= to get rid of unwanted backspace or tabs)
            comp_cell = cell.find('div', {"class": "mdl-card__title"})
            company = comp_cell.find("span").text
            company = company.replace("\n", "").replace("\t", "").strip()

            # Title
            # The title is always formatted as a h5 div, but since there are sometimes 2 titles divided by a "|" character
            # we collect them both through the split() function
            title = cell.find('h5').text.strip()
            title_1, title_2 = title.split(' | ')

            # Date and Base
            # The Date and Base of the launches are inside a "mdl-card_supporting-text" class div one on top of each other
            # (= divided by a \n character) inside a unique string.
            # For the Dates: In some cases, some dates begin with the "NET" characters when it is estimated or the Day is not available,
            # hence we remove this portion of the string
            # For the past launches we identify the base by splitting the string on the UTC char, always present, we then remove any
            # unneeded backspace "\n" and we trim the string.
            text = cell.find('div', {"class": "mdl-card__supporting-text"}).text.strip()
            date = text.split('\n')[0].replace("NET ", '')
            if future:
                base = text.split("\n")[2].replace("\n", '').strip()
            else:
                base = text.split('UTC')[1].replace("\n", '').strip()

            # Link to additional information
            # As explained, each rocket launch has additional data in a separate page whose link is embedded in a button. Every
            # cell as a "button" HTML element with the onclick HTML property of redirecting the user to the relative page.
            # we scrape the link by removing the unwanted "location.href = '" bit of the string and we select the splitted element
            # after this one '[1]'
            link = cell.find('button').get("onclick").split("location.href = '")[1][:-1]

            # Rocket Launch Identifier
            # Per each rocket, we scrape the ID from the variables that the website uses to fetch the pages and are shown in the url bar,
            # indeed, we notice that the detailed information page is always called with the following url:
            # "https://nextspaceflight.com/launches/details/5056" hence by splitting on "details/" and slicing on the last element [-1]
            # we collect the id of the rocket. To avoid any string stored as integer, we also cast it.
            rocket_id = int(link.split("details/")[-1])

            # Summary
            # We store all the data we scraped inside a Dictionary and we label each element accordingly
            launch = {
                'id': rocket_id,
                'date': date,
                'title_1': title_1,
                'title_2': title_2,
                'company': company,
                'base': base,
                'link': link,
            }

            # We then proceed to get detailed information for this rocket by calling the get_detailed_info()
            # function defined below
            detail = get_detailed_info(rocket_id)

            # We append the DataFrame (i.e. the indexed dictionaire with detailed info returned by the function 2)
            # to the list of DataFrames we defined earlier
            page_details.append(detail)
            # We also append the launch to the list of dictionaries we created to be able to go through
            # them independently
            page_launches.append(launch)

        # getting rid of unwanted exceptions generated while reading through the HTML doc, some of the
        # BS4 ones can be ignored
        except Exception as e:
            pass

    # *************************************** CSV FILE CREATION ***************************************************
    # needed to create a CSV backup and to then read through the CSV ot make the charts
    # we store the result of our scraping in a DataFrame containing a list of dictionaries
    # with the detailed information indexed by the relative uid
    res = pd.DataFrame(page_launches).set_index('id')

    # we convert to a datetime format the date stored as string that we scraped before
    res['date'] = pd.to_datetime(res['date'])

    # we then create a second DataFrame collection by concatenating the page_details (lists of dataframes with
    # the dictionaries inside)
    res_2 = pd.concat(page_details, sort=False)

    # we add to our list of rocket launches the columns of the detailed info and we append the detailed info, in
    # order to have as columns all the information related to a launch in one single data structure
    res[res_2.columns] = res_2

    # creating the csv file
    res.to_csv("file.csv")

    # printing the results to debug and have a live feedback of the scraping
    # note that res has 17 columns vs res 2 only 11 (hence res is comprehensive of all the info) and that they both
    # have 30-31 rows, i.e. the launches per page
    print("RES")
    print(res)
    print("RES2")
    print(res_2)

    # returning the indexed dataframe of page launches (as dictionaries)
    return res


# 2) get_detailed_info
# This Function opens the page including the data of a specific launch, stores the elements and returns
# the findings.
#   As Arguments, the function takes the rocket launch id (integer)
#   It returns a panda DataFrame with the detailed information of a launch in it as a dictionary and their
#   relative unique id.
def get_detailed_info(rocket_id):
    try:
        # As mentioned, each detail page is characterized by the unique identifier of the rocket launch it describes.
        # In addition, each detailed page's URL is always "/launches/details/000" where 000 is the unique id, which
        # we add through the format() method: it formats the specified value(s) and inserts them
        # inside the string's placeholder, defined using curly brackets: {}.
        url = base_url + "/launches/details/{0}".format(rocket_id)

        # we then download the page, same as before
        html = urllib.request.urlopen(url)

        # and again we parse it through BS4
        soup = BeautifulSoup(html, "html.parser")

        # before creating the data structures to replicate a portion of the HTML structure of the page with the divs
        # we are interested in
        table = soup.find_all("div", {'class': 'mdl-card__supporting-text'})[1]
        cells = table.find_all('div', {'class': 'mdl-cell'})

        # we initialize an empty dictionary to store the information we will retrieve
        infos = {}

        # Launch Details
        # we populate the dictionary by looping through the "mdl-cell" class divs o the detail page. We noticed that
        # every attribute is always divided by a ":" from its correspondent value, hence through the split function
        # we are able to capture all the information. Since there might be "mdl-cell" class divs used for other purposes
        # or left empty, we also handle exceptions by ignoring them
        for cell in cells:
            try:
                label, value = cell.text.split(": ")
                infos[label] = value
            except:
                pass

        # Mission Status
        # As visible in the website, the status appears in Green or Red on top of each page.
        # We therefore try to scrape this information from a "status"-class div and we look for
        # the span element containing the "Success" string. We store it in our
        # infos dictionary under the 'status' key as an integer with 1 being
        # success and 0 a failure. We handle exceptions storing as numpy NaN value all the other elements
        try:
            status = soup.find('h6', {'class': 'status'}).find('span')
            status = int(status.text == 'Success')
        except Exception as e:
            status = np.NaN
        infos['status'] = status

        # if everything goes well, we return a DataFrame containing the dictionary with the information on the launch
        # and the unique identifier for each dictionary wich we set to be the id of the launch
        return pd.DataFrame(infos, index=[rocket_id])

    # otherwise, we print the exception and we return the same datastructure but with an empty dictionary
    except Exception as e:
        print(e)
        return pd.DataFrame({}, index=[rocket_id])


# 3) read CSV
# This Function reads the CSV file created by the scraping functions and returns data in a DataFrame
# structure
#   As Arguments, the function takes a String indicating whether past or future launches have to be read
#   It returns a panda DataFrame with the detailed information of a launch read from the csv file
def read_csv(horizon):
    # we read the file containing future or past launches specifying the date fields as they need
    # to be stored as such, we handle common errors
    try:
        if horizon == "Future":
            res = pd.read_csv("launches_from_2022.csv", parse_dates=['date'])
        elif horizon == "Past":
            res = pd.read_csv("launches_until_2022.csv", parse_dates=['date'])
        else:
            raise Exception(" Error while reading csv file, lines 260-280. "
                            "Please pass as arguments either 'Past' or 'Future'")
            return
    except Exception as e:
        print(e)
        return

    return res


# ********************************************************************************************************
# ***********************************                        *********************************************
# ***********************************   SCRAPING FUNCTIONS   *********************************************
# ***********************************                        *********************************************
# ********************************************************************************************************

# 4) scrape_past_launches()
# This Function uses the previously defined functions to scrape the past launches pages and
# to store data in csv files

def scrape_past_launches(page_scraped):
    # initializing the counter of pages. there should be around 215 past launches pages on the website
    page = 1

    # initializing the url container, again we use the format() function and we take advantage of the URL not changing
    # across pages, i.e. ".../launches/past/?page=1" where 1 changes up to 215
    url = base_url + "/launches/past/?page={0}".format(page)

    # we download the page
    html = urllib.request.urlopen(url)

    # parse it through BS4
    soup = BeautifulSoup(html, "html.parser")

    # we notice that the information related to the number of pages is contained in the bottom-of-the-page button
    # redirecting to the "LAST" page...
    button = soup.find_all('button', {'class': 'mdc-button mdc-button--raised'})[1]

    # ...hence we collect the link from the onclick HTML property and we parse it to scrape the integer we need
    N_PAGES = int(button.get("onclick").split("?page=")[-1].split("&")[0].replace("'", ""))
    print("Pages to scrape for past launches: {0:0.0f}".format(N_PAGES))

    # ***********************************       WARNING:     *********************************************
    # In the interest of time, we debug the program with 2 pages only. Comment the following line to
    # scrape all the pages (it may take a while)
    if page_scraped > 0:
        N_PAGES = page_scraped

    print("Currently Scraping: {0:0.0f}".format(N_PAGES))

    # We loop through the pages of the website and we call on each of them the scrape_page(function)
    # itself calling the detailed info function eventually returning a complete dataframe with all launches
    # and all detailed information as shown before
    res = pd.concat([scrape_page(page) for page in range(1, N_PAGES + 1)], sort=True)

    # We store past launches as CSV and handle common errors
    try:
        res.to_csv("launches_until_2022.csv")
    except Exception as e:
        print("error while creating the csv file. Try closing any previously open .csv")
        print(e)
    return


# 5) scrape_future_launches()
# This Function uses the previously defined functions to scrape the upcoming launches pages and
# to store data in csv files

def scrape_future_launches():
    # initializing our counter of pages. There should be around 11 upcoming launches pages on the website
    page = 1

    # initializing the url container, again we use the format() function and we take advantage of the URL not changing
    # across pages, i.e. ".../launches/?page=1" where 1 changes up to 11
    base_url = "https://nextspaceflight.com"
    url = base_url + "/launches/?page={0}".format(page)

    # we download the page
    html = urllib.request.urlopen(url)

    # parse it through BS4
    soup = BeautifulSoup(html, "html.parser")

    # Again we notice that the information related to the number of pages is contained in the bottom-of-the-page button
    # redirecting to the "LAST" page...
    button = soup.find_all('button', {'class': 'mdc-button mdc-button--raised'})[1]

    # ...hence we collect the link from the onclick HTML property and we parse it to
    # scrape the integer we need
    N_PAGES_FUTURE = int(button.get("onclick").split("?page=")[-1].split("&")[0].replace("'", ""))
    print("Pages to scrape for future launches: {0:0.0f}".format(N_PAGES_FUTURE))

    # ***********************************       WARNING:     *********************************************
    # In the interest of time, we debug the program with 2 pages only. Comment the following line to
    # scrape all the pages (it may take a while)
    N_PAGES_FUTURE = 10
    print("Currently Scraping: {0:0.0f}".format(N_PAGES_FUTURE))

    # We loop through the pages of the website and we call on each of them the scrape_page(function)
    # itself calling the detailed info function eventually returning a complete dataframe with all launches
    # and all detailed information as shown beforeN_PAGES_FUTURE = 3
    res = pd.concat([scrape_page(page) for page in range(1, N_PAGES_FUTURE + 1)], sort=True)

    # We store past launches as CSV
    res.to_csv("launches_from_2022.csv")

    return


# **************************************************************************************************************
# ***********************************      CHART GENERATORS    *************************************************
# ***********************************        0) init           *************************************************
# ***********************************                          *************************************************
# **************************************************************************************************************

# we run our scraping functions to generate the database we want to plot
# scrape_future_launches()
page_scraped = int(input("How many pages you'd like to scrape? 100 pages should take around 20 mins. Input 0 to"
                     " scrape them all"))
scrape_past_launches(page_scraped)


# **************************************************************************************************************
# ***********************************      CHART GENERATORS    *************************************************
# ***********************************                          *************************************************
# ***********************************      1) by Country       *************************************************
# **************************************************************************************************************

# we wrap all the processing and printing in a function. Here we have 1 charts as output: number of launches
# by country
def plot_launches_by_country(res):
    # This utility wrapper makes it convenient for us to create layouts of subplots, including the enclosing figure
    # object, in a single call.
    fig, ax1 = plt.subplots(1, 1, figsize=(12, 6))

    # We define the Country of each launch by splitting the base field on each commas and taking the last element
    # i.e. "Site 9401 (SLS-2), Jiuquan Satellite Launch Center, China" we want only "China"
    # the apply() function applies to all element of a list a function passed as argument, in this case lambda..
    res['Country'] = res['base'].str.split(", ").apply(lambda x: x[-1])

    # We want to plot launches by country, hence we group by them, we sort by descending countries per number
    # of launches and we plot them
    res.groupby('Country').size().sort_values(ascending=False).head(10).plot(ax=ax1, kind='bar', rot=30);

    # we set some chart characteristics
    ax1.xaxis.set_label_text("");
    ax1.yaxis.set_label_text("Launches");
    plt.tight_layout();

    # and we create the pdf
    plt.savefig("by_country.pdf");
    return


## **************************************************************************************************************
# ***********************************      CHART GENERATORS    *************************************************
# ***********************************                          *************************************************
# ***********************************    2) by Country, Year   *************************************************
# **************************************************************************************************************

# we wrap all the processing and printing in a function. Here we have 2 charts as outputs: number of launches by
# by country and by year
def plot_launches_byCountryYear(res):
    # This utility wrapper makes it convenient for us to create layouts of subplots, including the enclosing figure
    # object, in a single call.
    fig, ax1 = plt.subplots(1, 1, figsize=(12, 6))

    # We define the Country of each launch by splitting the base field on each commas and taking the last element
    # i.e. "Site 9401 (SLS-2), Jiuquan Satellite Launch Center, China" we want only "China"
    # the apply() function applies to all element of a list a function passed as argument, in this case lambda..
    res['Country'] = res['base'].str.split(", ").apply(lambda x: x[-1])

    # We also need to extract the year from the date, which we can easily do by invoking the properties of the date
    # as we stored it earlier as a datetime object
    res['year'] = res['date'].dt.year

    # we group by the variables we want to show in the x axis
    res.groupby('year').size().plot(ax=ax1, marker='o', color='#3f9624', markersize=10);

    # we set some chart characteristics
    ax1.xaxis.set_label_text("Take Off Countries");
    ax1.yaxis.set_label_text("Launches");
    ax1.grid(True)
    plt.tight_layout();
    plt.savefig("by_year.pdf");

    # This utility wrapper makes it convenient for us to create layouts of subplots, including the enclosing figure
    # object, in a single call.
    fig, ax1 = plt.subplots(1, 1, figsize=(12, 6))

    # we define the legend
    res['Decade'] = (res['year'] / 10).astype(int) * 10

    # we group by the variables we want to show in the x axis
    order = res.groupby('Country').size().sort_values(ascending=False).head(10).index

    res.groupby(['Decade', 'Country']).size() \
        .unstack(level=0).loc[order].head(10).fillna(0) \
        .plot(ax=ax1, kind='bar', stacked=True, rot=30);

    # we set some chart characteristics
    ax1.xaxis.set_label_text("Countries");
    ax1.yaxis.set_label_text("Launches");
    plt.tight_layout();
    plt.savefig("by_country_year.pdf");

    return


# **************************************************************************************************************
# ***********************************      CHART GENERATORS    *************************************************
# ***********************************                          *************************************************
# ***********************************     3) USA vs RUSSIA     *************************************************
# **************************************************************************************************************

# we wrap all the processing and printing in a function. Here we have 1 chart as output: number of launches by
# year of US vs Russia
def plot_launches_USAvsRUSSIA(res):
    fig, ax1 = plt.subplots(1, 1, figsize=(12, 6))
    ax2 = ax1.twinx()

    # We define the Country of each launch by splitting the base field on each commas and taking the last element
    # i.e. "Site 9401 (SLS-2), Jiuquan Satellite Launch Center, China" we want only "China"
    # the apply() function applies to all element of a list a function passed as argument, in this case lambda..
    res['Country'] = res['base'].str.split(", ").apply(lambda x: x[-1])

    # We also need to extract the year from the date, which we can easily do by invoking the properties of the date
    # as we stored it earlier as a datetime object
    res['year'] = res['date'].dt.year

    te = res[res['Country'].isin(['USA', 'Russia'])]

    te.groupby(['year', 'Country']).size().unstack().cumsum().fillna(0).plot(
        ax=ax2, marker='o', color=['r', 'b'], markersize=10)

    te.groupby(['year', 'Country']).size().unstack().fillna(0).plot(
        ax=ax1, color=['r', 'b'], kind='area', alpha=0.1, legend=False, stacked=False)

    ax1.xaxis.set_label_text("");
    ax2.yaxis.set_label_text("TotalLaunches");
    ax1.yaxis.set_label_text("LaunchesperYear");
    plt.savefig("usa_russia.pdf");
    return


# **************************************************************************************************************
# ***********************************        CORE PROGRAM      *************************************************
# ***********************************                          *************************************************
# ***********************************                          *************************************************
# **************************************************************************************************************

# we read the file by calling the relative function. Here we plot paste launches, it can be changed to Future
# res = read_csv("Future")

res = read_csv("Past")

# we call the function to plot the data stored in res
plot_launches_by_country(res)

# we call the function to plot the data stored in res
plot_launches_byCountryYear(res)

# we call the function to plot the data stored in res
plot_launches_USAvsRUSSIA(res)

print("*************************************************************************************************************\n"
      "Thank you for using our program\n"
      "*************************************************************************************************************\n")
