"""
Project: P4 - Webscraping General Conference
Description: Scrapes talk data and scripture references from the October 2025 General Conference 
and stores it in a PostgreSQL database. Allows users to view summary charts of the data.
Authors: Tye, Kyle, and Tanner
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plot

# --- DATABASE CONNECTION ---
# UPDATE THIS STRING with your postgres username, password, and port
# Format: 'postgresql://username:password@localhost:5432/is303'
engine = sqlalchemy.create_engine('postgresql://postgres:password@localhost:5432/is303')

# Base dictionary provided in instructions
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
user_input = input("If you want to scrape data, enter 1. If you want to see summaries of stored data, enter 2. Enter any other value to exit the program: ")

if user_input == '1':
    # 1. Drop table if it exists to prevent duplicate data
    drop_table_query = sqlalchemy.text("drop table if exists general_conference;")
    with engine.connect() as conn:
        conn.execute(drop_table_query)
        conn.commit()

    # 2. Load the main conference page
    main_url = 'https://www.churchofjesuschrist.org/study/general-conference/2025/10?lang=eng'
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all links to the talks
    # (Assuming links are inside an 'a' tag with a specific class or within a specific section)
    # The actual finding logic might need adjustment based on the live website's structure
    talk_links = soup.find_all('a', href=True)
    
    all_scraped_data = []

    # 3. Access individual talk pages
    for link in talk_links:
        href = link['href']
        
        # Filter out pages that are just entire sessions
        if 'session' in href.lower() or '/study/general-conference/2025/10' not in href:
            continue
            
        full_url = f"https://www.churchofjesuschrist.org{href}"
        print(f"trying to scrape url: {full_url}")
        
        # Load specific talk page
        talk_response = requests.get(full_url)
        talk_soup = BeautifulSoup(talk_response.content, 'html.parser')
        
        # Find the talk title to filter out Sustaining of General Authorities
        title_element = talk_soup.find('h1') # Typically titles are in h1 tags
        if title_element:
            talk_title = title_element.text.strip()
            if 'Sustaining' in talk_title:
                continue
        else:
            continue

        # Create a fresh copy of the dictionary for this specific talk
        current_talk_dict = base_dict.copy()
        current_talk_dict['Talk_Name'] = talk_title
        
        # 4. Extract Speaker, Kicker, and Footnotes
        speaker_element = talk_soup.find('p', class_='author-name') # Update class based on actual HTML
        if speaker_element:
            speaker_text = speaker_element.text.strip()
            # Remove "By " from the beginning if it exists
            if speaker_text.startswith("By "):
                speaker_text = speaker_text[3:]
            current_talk_dict['Speaker_Name'] = speaker_text

        kicker_element = talk_soup.find('p', class_='kicker') # Update class based on actual HTML
        if kicker_element:
            current_talk_dict['Kicker'] = kicker_element.text.strip()

        # Find footnotes section
        footnotes_section = talk_soup.find('footer', attrs={'class': 'notes'})
        
        if footnotes_section is not None:
            footnotes_text = footnotes_section.text
            # Loop through the dictionary keys to count scripture references
            for key in current_talk_dict.keys():
                # Skip the non-scripture keys
                if key not in ['Speaker_Name', 'Talk_Name', 'Kicker']:
                    # Count occurrences of the book name in the footnotes text
                    count = footnotes_text.count(key)
                    current_talk_dict[key] = count
                    
        # Add this talk's dictionary to our master list
        all_scraped_data.append(current_talk_dict)

    # 5. Save data to Postgres
    df = pd.DataFrame(all_scraped_data)
    df.to_sql('general_conference', engine, if_exists='append', index=False)
    
    # 6. Success message
    print("You've saved the scraped data to your postgres database.")

elif user_input == '2':
    # --- PART 2: VIEW SUMMARIES ---
    sub_menu = input("You selected to see summaries. Enter 1 to see a summary of all talks. Enter 2 to select a specific talk. Enter anything else to exit: ")
    
    if sub_menu == '1':
        # Retrieve all data
        sql_query = "SELECT * FROM general_conference"
        df_from_postgres = pd.read_sql_query(sql_query, engine)
        
        # Drop text columns, sum the numeric columns, filter > 2, and plot
        df_sums = df_from_postgres.drop(['Speaker_Name', 'Talk_Name', 'Kicker'], axis=1).sum()
        df_sums_filtered = df_sums[df_sums > 2]
        
        df_sums_filtered.plot(kind='bar')
        plot.title('Standard Works Referenced in General Conference')
        plot.xlabel('Standard Works Books')
        plot.ylabel('# Times Referenced')
        plot.tight_layout() # Helps prevent labels from being cut off
        plot.show()
        
    elif sub_menu == '2':
        # Retrieve all data to build the menu
        sql_query = "SELECT * FROM general_conference"
        df_from_postgres = pd.read_sql_query(sql_query, engine)
        
        print("The following are the names of speakers and their talks:")
        
        # Create a dictionary to map the input number to the Talk_Name
        talk_lookup = {}
        
        # Loop through dataframe to display options
        # Note: iterrows index starts at 0, so we add 1 for the display number
        for index, row in df_from_postgres.iterrows():
            display_num = index + 1
            speaker = row["Speaker_Name"]
            talk = row["Talk_Name"]
            print(f"{display_num}: {speaker} - {talk}")
            talk_lookup[str(display_num)] = talk
            
        requested_num = input("Please enter the number of the talk you want to see summarized: ")
        
        # Check if they entered a valid number
        if requested_num in talk_lookup:
            requested_talk = talk_lookup[requested_num]
            
            # Filter the dataframe to only have rows from the selected talk
            df_filtered = df_from_postgres.query("Talk_Name == @requested_talk")
            
            # Drop text columns, sum the remaining numeric columns
            df_filtered_sums = df_filtered.drop(['Speaker_Name', 'Talk_Name', 'Kicker'], axis=1).sum()
            
            # Filter for books with at least 1 reference
            df_filtered_sums = df_filtered_sums[df_filtered_sums > 0]
            
            # Generate the chart
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