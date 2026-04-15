"""
Project: P4 - Webscraping General Conference
Description: Scrapes talk data and scripture references from the October 2025 General Conference 
             and stores it in a PostgreSQL database. Allows users to view summary charts of the data.
Authors: Tye, Kyle, and Tanner
"""

# IMPORTING LIBRARIES:
# BeautifulSoup: Used to parse (read and navigate) the HTML code of the webpages.
# requests: Used to actually fetch the webpage data from the internet.
# pandas (pd): Used to organize our data into tables (DataFrames) and easily send it to SQL.
# sqlalchemy: Used to connect our Python script to our PostgreSQL database.
# matplotlib.pyplot (plot): Used to draw the bar charts for our summaries.
from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plot

# --- DATABASE CONNECTION ---
# This engine acts as the bridge between our Python code and the pgAdmin4 database.
# Format: 'postgresql://username:password@localhost:5432/database_name'
engine = sqlalchemy.create_engine('postgresql://postgre:admin@localhost:5432/is303')

# --- DATA DICTIONARY ---
# This dictionary holds all the 87 standard works books we need to look for.
# It acts as a blank template. For every new talk we scrape, we will make a copy 
# of this dictionary and fill it with that specific talk's data.
base_dict = {
    'Speaker_Name': '', 'Talk_Name': '', 'Kicker': '', 'Matthew': 0, 'Mark': 0, 'Luke': 0, 'John': 0,
    'Acts': 0, 'Romans': 0, '1 Corinthians': 0, '2 Corinthians': 0, 'Galatians': 0, 'Ephesians': 0, 
    'Philippians': 0, 'Colossians': 0, '1 Thessalonians': 0, '2 Thessalonians': 0, '1 Timothy': 0, 
    '2 Timothy': 0, 'Titus': 0, 'Philemon': 0, 'Hebrews': 0, 'James': 0, '1 Peter': 0, '2 Peter': 0, 
    '1 John': 0, '2 John': 0, '3 John': 0, 'Jude': 0, 'Revelation': 0, 'Genesis': 0, 'Exodus': 0, 
    'Leviticus': 0, 'Numbers': 0, 'Deuteronomy': 0, 'Joshua': 0, 'Judges': 0, 'Ruth': 0, '1 Samuel': 0, 
    '2 Samuel': 0, '1 Kings': 0, '2 Kings': 0, '1 Chronicles': 0, '2 Chronicles': 0, 'Ezra': 0, 
    'Nehemiah': 0, 'Esther': 0, 'Job': 0, 'Psalm': 0, 'Proverbs': 0, 'Ecclesiastes': 0, 
    'Song of Solomon': 0, 'Isaiah': 0, 'Jeremiah': 0, 'Lamentations': 0, 'Ezekiel': 0, 'Daniel': 0, 
    'Hosea': 0, 'Joel': 0, 'Amos': 0, 'Obadiah': 0, 'Jonah': 0, 'Micah': 0, 'Nahum': 0, 'Habakkuk': 0, 
    'Zephaniah': 0, 'Haggai': 0, 'Zechariah': 0, 'Malachi': 0, '1 Nephi': 0, '2 Nephi': 0, 'Jacob': 0, 
    'Enos': 0, 'Jarom': 0, 'Omni': 0, 'Words of Mormon': 0, 'Mosiah': 0, 'Alma': 0, 'Helaman': 0, 
    '3 Nephi': 0, '4 Nephi': 0, 'Mormon': 0, 'Ether': 0, 'Moroni': 0, 'Doctrine and Covenants': 0, 
    'Moses': 0, 'Abraham': 0, 'Joseph Smith-Matthew': 0, 'Joseph Smith-History': 0, 'Articles of Faith': 0
}

# --- MAIN MENU ---
# Using \n creates a new line, making the menu print vertically in the terminal for better readability.
user_input = input(
    "\n--- MAIN MENU ---\n"
    "1 - Scrape new General Conference data\n"
    "2 - See summaries of stored data\n"
    "Enter any other value to exit the program.\n"
    "> "
)

if user_input == '1':
    # --- PART 1: WEBSCRAPING ---
    print("\nStarting the webscraper... please wait.\n")

    # 1. Drop table if it exists
    # We do this so that if we run the script multiple times, we don't just keep adding 
    # the exact same talks to the database over and over (creating duplicates).
    drop_table_query = sqlalchemy.text("drop table if exists general_conference;")
    with engine.connect() as conn:
        conn.execute(drop_table_query)
        conn.commit()

    # 2. Load the main conference page
    main_url = 'https://www.churchofjesuschrist.org/study/general-conference/2025/10?lang=eng'
    response = requests.get(main_url) # Downloads the page
    soup = BeautifulSoup(response.content, 'html.parser') # Turns the raw code into a searchable object

    # 3. Find all links on the main page
    # This finds every 'a' tag (which are hyperlinks in HTML) that has an 'href' (the actual URL destination)
    talk_links = soup.find_all('a', href=True)
    
    # We will store every talk's completed dictionary inside this list before sending to SQL
    all_scraped_data = []

    # Loop through every single link we found on the main page
    for link in talk_links:
        href = link['href'] # Extract just the URL string from the HTML tag
        
        # Filtering logic: We only want actual talks. 
        # If the URL contains the word 'session' (like Saturday Morning Session), skip it.
        # Also ensure the link belongs to the specific conference we are targeting.
        if 'session' in href.lower() or '/study/general-conference/2025/10' not in href:
            continue
            
        # The hrefs are relative (e.g., "/study/general-conference/..."), so we add the domain to make it a full URL
        full_url = f"https://www.churchofjesuschrist.org{href}"
        print(f"trying to scrape url: {full_url}")
        
        # Load the specific page for this individual talk
        talk_response = requests.get(full_url)
        talk_soup = BeautifulSoup(talk_response.content, 'html.parser')
        
        # Find the title of the talk (usually in an <h1> heading tag)
        title_element = talk_soup.find('h1') 
        if title_element:
            talk_title = title_element.text.strip()
            # If the title is the Sustaining of Officers, skip it (as requested by instructions)
            if 'Sustaining' in talk_title:
                continue
        else:
            continue # If there's no title at all, something is wrong with the page, skip it.

        # 4. Create a fresh copy of the base dictionary for THIS specific talk
        current_talk_dict = base_dict.copy()
        current_talk_dict['Talk_Name'] = talk_title
        
        # Find the Speaker Name. We look for a paragraph <p> tag with the class 'author-name'
        speaker_element = talk_soup.find('p', class_='author-name') 
        if speaker_element:
            speaker_text = speaker_element.text.strip()
            # The site usually formats it as "By Elder David A. Bednar". This removes the "By ".
            if speaker_text.startswith("By "):
                speaker_text = speaker_text[3:]
            current_talk_dict['Speaker_Name'] = speaker_text

        # Find the Kicker (the opening quote). Look for a <p> tag with class 'kicker'
        kicker_element = talk_soup.find('p', class_='kicker')
        if kicker_element:
            current_talk_dict['Kicker'] = kicker_element.text.strip()

        # Find footnotes section to count scripture references. We look for a <footer> tag with class 'notes'
        footnotes_section = talk_soup.find('footer', attrs={'class': 'notes'})
        
        # Some talks might not have footnotes. We only proceed if we actually found a footer section.
        if footnotes_section is not None:
            # Grab all the text inside the entire footnote section at once
            footnotes_text = footnotes_section.text
            
            # Loop through all 87 scripture books in our dictionary
            for key in current_talk_dict.keys():
                # We don't want to count occurrences of the Speaker Name or Kicker
                if key not in ['Speaker_Name', 'Talk_Name', 'Kicker']:
                    # .count() simply counts how many times a word (like "Matthew") appears in the footer text
                    count = footnotes_text.count(key)
                    current_talk_dict[key] = count
                    
        # Done scraping this page! Add this talk's data to our master list
        all_scraped_data.append(current_talk_dict)

    # 5. Save all the gathered data to the Postgres database
    # Pandas easily converts a list of dictionaries into a clean data table (DataFrame)
    df = pd.DataFrame(all_scraped_data)
    # Send it to our 'engine' (Postgres connection). if_exists='append' adds rows to the bottom.
    df.to_sql('general_conference', engine, if_exists='append', index=False)
    
    # 6. Print success message
    print("\nYou've saved the scraped data to your postgres database.")


elif user_input == '2':
    # --- PART 2: VIEW SUMMARIES ---
    
    # Sub-menu formatted vertically
    sub_menu = input(
        "\nYou selected to see summaries. Please choose an option:\n"
        "1 - See a summary of all talks\n"
        "2 - Select a specific talk\n"
        "Enter anything else to exit.\n"
        "> "
    )
    
    if sub_menu == '1':
        # Retrieve ALL data from our Postgres table into a Pandas DataFrame
        sql_query = "SELECT * FROM general_conference"
        df_from_postgres = pd.read_sql_query(sql_query, engine)
        
        # .drop() removes the text columns so we are only doing math on the numbers.
        # .sum() adds up the column totals across all the different talks.
        df_sums = df_from_postgres.drop(['Speaker_Name', 'Talk_Name', 'Kicker'], axis=1).sum()
        
        # Filter out books that were referenced 2 or fewer times
        df_sums_filtered = df_sums[df_sums > 2]
        
        # Draw and display the bar chart
        df_sums_filtered.plot(kind='bar')
        plot.title('Standard Works Referenced in General Conference')
        plot.xlabel('Standard Works Books')
        plot.ylabel('# Times Referenced')
        plot.tight_layout() # Prevents the bottom labels from getting cut off by the window border
        plot.show()
        
    elif sub_menu == '2':
        # Retrieve ALL data to build the menu of available talks
        sql_query = "SELECT * FROM general_conference"
        df_from_postgres = pd.read_sql_query(sql_query, engine)
        
        print("\nThe following are the names of speakers and their talks:")
        
        # We need a way to link the number the user types (e.g., "5") to the actual Talk Name.
        talk_lookup = {}
        
        # Loop through our database rows one by one.
        # iterrows() provides an index (0, 1, 2...) and the data for that row.
        for index, row in df_from_postgres.iterrows():
            display_num = index + 1 # Add 1 so the menu starts at 1 instead of 0
            speaker = row["Speaker_Name"]
            talk = row["Talk_Name"]
            
            # Print the menu option
            print(f"{display_num}: {speaker} - {talk}")
            
            # Save it to our lookup dictionary. E.g., {'1': 'In the Path of Their Duty'}
            talk_lookup[str(display_num)] = talk
            
        requested_num = input("\nPlease enter the number of the talk you want to see summarized: ")
        
        # Check if the user typed a valid number that exists in our dictionary
        if requested_num in talk_lookup:
            requested_talk = talk_lookup[requested_num]
            
            # Filter the dataframe to KEEP ONLY the row where Talk_Name matches the requested talk
            df_filtered = df_from_postgres.query("Talk_Name == @requested_talk")
            
            # Drop the text columns and sum the remaining numeric row
            df_filtered_sums = df_filtered.drop(['Speaker_Name', 'Talk_Name', 'Kicker'], axis=1).sum()
            
            # Filter to show ONLY books that have at least 1 reference (no zeros)
            df_filtered_sums = df_filtered_sums[df_filtered_sums > 0]
            
            # Draw and display the specific chart
            df_filtered_sums.plot(kind='bar')
            plot.title(f'Standard Works Referenced in: {requested_talk}')
            plot.xlabel('Standard Works Books')
            plot.ylabel('# Times Referenced')
            plot.tight_layout()
            plot.show()
        else:
             print("Closing the program.")
    else:
        print("Closing the program.")
else:
    print("Closing the program.")