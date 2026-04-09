#Tye Buckley, Kyle Pinkney

# =======================
# Libraries
# =======================
from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plot

# Standard Works Dictionary
standard_works_dict = {'Speaker_Name' : '', 'Talk_Name' : '', 'Kicker' : '', 
                       'Matthew': 0, 'Mark': 0, 'Luke': 0, 'John': 0, 'Acts': 0, 
                       'Romans': 0, '1 Corinthians': 0, '2 Corinthians': 0, 'Galatians': 0, 
                       'Ephesians': 0, 'Philippians': 0, 'Colossians': 0, '1 Thessalonians': 0, 
                       '2 Thessalonians': 0, '1 Timothy': 0, '2 Timothy': 0, 'Titus': 0, 
                       'Philemon': 0, 'Hebrews': 0, 'James': 0, '1 Peter': 0, '2 Peter': 0, 
                       '1 John': 0, '2 John': 0, '3 John': 0, 'Jude': 0, 'Revelation': 0, 
                       'Genesis': 0, 'Exodus': 0, 'Leviticus': 0, 'Numbers': 0,
                         'Deuteronomy': 0, 'Joshua': 0, 'Judges': 0, 'Ruth': 0, '1 Samuel': 0, 
                         '2 Samuel': 0, '1 Kings': 0, '2 Kings': 0, '1 Chronicles': 0, 
                         '2 Chronicles': 0, 'Ezra': 0, 'Nehemiah': 0, 'Esther': 0, 'Job': 0, 
                         'Psalm': 0, 'Proverbs': 0, 'Ecclesiastes': 0, 'Song of Solomon': 0,
                           'Isaiah': 0, 'Jeremiah': 0, 'Lamentations': 0, 'Ezekiel': 0, 
                           'Daniel': 0, 'Hosea': 0, 'Joel': 0, 'Amos': 0, 'Obadiah': 0, 
                           'Jonah': 0, 'Micah': 0, 'Nahum': 0, 'Habakkuk': 0, 'Zephaniah': 0, 
                           'Haggai': 0, 'Zechariah': 0, 'Malachi': 0, '1 Nephi': 0, '2 Nephi': 0, 
                           'Jacob': 0, 'Enos': 0, 'Jarom': 0, 'Omni': 0, 'Words of Mormon': 0, 
                           'Mosiah': 0, 'Alma': 0, 'Helaman': 0, '3 Nephi': 0, '4 Nephi': 0, 
                           'Mormon': 0, 'Ether': 0, 'Moroni': 0, 'Doctrine and Covenants': 0,
                             'Moses': 0, 'Abraham': 0, 'Joseph Smith—Matthew': 0, 
                             'Joseph Smith—History': 0, 'Articles of Faith': 0}

# Menu
def menu():
    print("++General Conference Webscraping Menu++")
    print("1.See a summary of all talks")
    print("2.See a specific talk")
    print("Anything else will exit the program")
    return input("Enter your choice: ")

