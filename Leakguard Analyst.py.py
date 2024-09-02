import os
import sys
import asyncio
import re
import spacy
import requests
import networkx as nx
import matplotlib.pyplot as plt
from telethon import TelegramClient
from telethon.errors import ApiIdInvalidError, FloodWaitError
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress

# Initialize SpaCy model for NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy model 'en_core_web_sm' not found. Downloading...")
    os.system("python3 -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# ASCII Art Banner
ascii_art = """
    __        __                ____                       _       _             
  \\ \\      / /_ _ _ __ _ __  / ___|_ __ __ _  ___ ___  __| |_   _| | ___  _ __  
   \\ \\ /\\ / / _` | '__| '_ \\| |  _| '__/ _` |/ __/ _ \\/ _` | | | | |/ _ \\| '_ \\ 
    \\ V  V / (_| | |  | | | | |_| | | | (_| | (_|  __/ (_| | |_| | | (_) | | | |
     \\_/\\_/ \\__,_|_|  |_| |_|\\____|_|  \\__,_|\\___\\___|\\__,_|\\__,_|_|\\___/|_| |_|


                 __    _             _          _       _           
                / /_ _| |_ _ _ ___  (_)__  __ _| |_ _ _(_)_ _  __ _ 
               / / _` |  _| '_/ _ \\ | / _|/ _` |  _| '_| | ' \\/ _` |
              /_|\\__,_|\\__|_| \\___/ |_|\\__\\__,_|\\__|_| |_|_||_\\__, |
                                                            |___| |___/ 

                  Cyber Intelligence & Data Leak Analysis Tool

    ==============================================
    |            Welcome to LeakGuard Analyst!    |
    |---------------------------------------------|
    | LeakGuard Analyst is a comprehensive tool   |
    | designed for detecting and analyzing data   |
    | leaks, tracking cyber activities, and       |
    | visualizing relationships between entities. |
    |---------------------------------------------|
    | Author: Moataz Younes                       |
    |---------------------------------------------|
    | Key Features:                               |
    | - Data Leak Detection                       |
    | - Social Network Analysis                   |
    | - IP Geolocation                            |
    | - Entity Extraction                         |
    | - Contextual Keyword Search                 |
    |---------------------------------------------|
    | Usage:                                      |
    | - Run the tool with 'leakguard-analyst'     |
    | - Follow the on-screen prompts to configure |
    |   your analysis                             |
    |=============================================|

"""

# Predefined Telegram groups/channels to search
groups_to_search = {
    'world': [
        'https://t.me/breachdetector', 'https://t.me/BreachedMarketplace',
        'https://t.me/leaked_databases', 'https://t.me/leakcheck',
        'https://t.me/data_dumpers', 'https://t.me/BreachedData1',
        'https://t.me/Leaked_dark_DataBase_Group', 'https://t.me/data_leak_breach',
        'https://t.me/hydramarketrebuild', 'https://t.me/SMokerFiles',
        'https://t.me/leakdataprivate', 'https://t.me/UnsafeInternet',
        'https://t.me/leakbasemarket', 'https://t.me/leadsandleaks',
        'https://t.me/Data_Leak1', 'https://t.me/deephackturkiye',
        'https://t.me/deephackers0', 'https://t.me/thehackernews',
        'https://t.me/Leaked_BreachDBS', 'https://t.me/PaluAnonCyber',
        'https://t.me/deepwbmaroc', 'https://t.me/whale_db', 'https://t.me/KromSec404',
        'https://t.me/hackercouncil', 'https://t.me/hak993',
        'https://t.me/fattahh_ir', 'https://t.me/BlackWolves_Tea',
        'https://t.me/GhostSecMafia', 'https://t.me/Anonymous_Guys_313',
        'https://t.me/KMPteam', 'https://t.me/cbcde_2345',
        'https://t.me/Moroccan_Soldiers', 'https://t.me/MoroccanCyberForces',
        'https://t.me/TheDarkWebInformer', 'https://t.me/noname05716eng',
        'https://t.me/dailydarkweb', 'https://t.me/PaluAnonCyber',
        'https://t.me/leakdataprivate', 'https://t.me/blueteamalerts',
        'https://t.me/OffensiveTwitter', 'https://t.me/ALLABOUTHACK',
        'https://t.me/deepweb167', 'https://infranodus.com/', 'https://t.me/dataleaks5', 'https://t.me/data_leak_breach'
    ],
    'egypt': [
        'https://t.me/EgyptHackerTeam', 'https://t.me/AnonymousEgypt',
        'https://t.me/Anonymousegc', 'https://t.me/Anonymousegg'
    ],
    # Add other countries with specific groups here
}

# Predefined keywords to search for
keywords = {
    'world': {
        "data breach": [
            "data breach", "data leak", "information leak", "database dump", "credential dump",
            "account leak", "security breach", "compromised", "hacked", "exposed", "leaked database",
            "data exposure", "dark web dump", "PII leak", "sensitive data"
        ],
        "ransomware": [
            "ransomware", "malware", "phishing", "brute force", "SQL injection", "cross-site scripting",
            "man-in-the-middle", "credential stuffing", "zero-day", "exploit", "social engineering"
        ],
        "personal data": [
            "personal data", "credit card", "social security number", "passport number", "health records",
            "financial data", "bank account", "email addresses", "phone numbers", "ID numbers",
            "user credentials", "account details", "private keys", "encryption keys", "hashed passwords",
            "cleartext passwords"
        ],
        "cybercrime": [
            "APT group", "cybercriminal", "hacktivist", "nation-state", "cyber espionage", "cyber attack",
            "blackhat"
        ]
    },
    'egypt': {
        "data breach": [
            "egy", 'egypt', 'cbe.org.eg', 'cbe', 'alahlybank', 'saudi', 'uae', 'emirates', 'fincirt',
            'egfincirt', '.eg', 'arab', 'central bank of egypt', 'fab', 'qnb', 'bm', 'misr', 'caire',
            'cairo', 'baraka', 'mashreq', 'aaib', 'alahly', 'cib', 'nbe', 'jordan', 'fawry', 'efinance',
            '@cbe', 'ksa', 'faisal', 'egypt', 'jumia', 'aaib.com', 'abe.com.eg', 'adcb.com.eg',
            'ahliunited.com', 'aib.com.eg', 'aibegypt.com', 'alahlynet.com.eg', 'albaraka-bank.com.eg',
            'alexbank.com', 'arabbank.com', 'attijariwafabank.com.eg', 'autodiscover.aib.com.eg',
            'autodiscover.theubeg.com', 'bank-abc.com', 'bankaudi.com.eg', 'bankfab.com',
            'banquemisr.com', 'bdc.com.eg', 'bdconline.com.eg', 'blombankegypt.com',
            'bmonline.banquemisr.com', 'ca-egypt.com', 'cibeg.com', 'citibank.com', 'citidirect.com',
            'cms.aib.com.eg', 'ctxidbapps.idb.com.eg', 'digitalcheck.myegbank.com',
            'dr.i-score.com.eg', 'eal-bank.com', 'ebanking.aib.com.eg', 'ebanking.cibeg.com',
            'ebanking.idb.com.eg', 'ebanking.scbank.com.eg', 'ebebank.com', 'edu.myegbank.com',
            'efinance.com.eg', 'eg-bank.com', 'egfincirt.org.eg', 'egyptianbanks.com',
            'emiratesnbd.com.eg', 'estatement.myegbank.com', 'expe.aib.com.eg', 'faisalbank.com.eg',
            'fawry.com', 'fs.aib.com.eg', 'gas.myegbank.com', 'hdb-egy.com', 'hsbc.com.eg',
            'i-score.com.eg', 'ib.aaib.com', 'idb.com.eg', 'imailsv.i-score.com.eg', 'join.idb.com.eg',
            'mail.aib.com.eg', 'mail.idbe.com.eg', 'mail.myegbank.com', 'mail.scbank.com.eg',
            'mail.theubeg.com', 'mail1.scbank.com.eg', 'mail2.scbank.com.eg', 'mail2.theubeg.com',
            'mailm.scbank.com.eg', 'mam1.idb.com.eg', 'mashreqbank.com', 'mbanking.idb.com.eg',
            'mdm1.idb.com.eg', 'members.i-score.com.eg', 'mint.eg-bank.com', 'mobile.myegbank.com',
            'mx01.aib.com.eg', 'mx02.aib.com.eg', 'mx04.aib.com.eg', 'myegbank.com', 'nbe.com.eg',
            'nbg.com.eg', 'nbk.com', 'owa.i-score.com.eg', 'qnbalahli.com', 'saib.com.eg',
            'scb-exp-e1.scbank.com.eg', 'scbank.com.eg', 'support.i-score.com.eg', 'sv.i-score.com.eg',
            'theubeg.com', 'tubmail.theubeg.com', 'uem.theubeg.com', 'uems.theubeg.com',
            'vpn.i-score.com.eg', 'vpn.scbank.com.eg', 'webmail.aib.com.eg', 'vodafone', 'thailand',
            'fcba.helwan.edu.eg', 'edu.eg', 'moiegy', 'mod.gov.eg', 'mohesr.gov.eg', 'gov.eg'
        ]
    }
    # Add other countries with specific keywords here
}


# Function to load API credentials from an external file (credentials.txt)
def load_telegram_api_credentials():
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            api_id = None
            api_hash = None
            ipinfo_token = None
            for line in lines:
                if line.startswith("api_id="):
                    api_id = line.split("=")[1].strip()
                elif line.startswith("api_hash="):
                    api_hash = line.split("=")[1].strip()
                elif line.startswith("ipinfo_token="):
                    ipinfo_token = line.split("=")[1].strip()

            if not api_id or not api_hash:
                console.print("API ID or API Hash is missing in the credentials file.", style="bold red")
                sys.exit(1)

            return api_id, api_hash, ipinfo_token

    except FileNotFoundError:
        console.print("The credentials.txt file was not found.", style="bold red")
        sys.exit(1)
    except Exception as e:
        console.print(f"An unexpected error occurred: {e}", style="bold red")
        sys.exit(1)


# Function to save results to a file
def save_results_to_file(results, filename="search_results.txt"):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for result in results:
                file.write(result + "\n")
        console.print(f"Results have been saved to {filename}", style="bold green")
    except Exception as e:
        console.print(f"Error saving results to file: {e}", style="bold red")


# Function to geolocate an IP address using ipinfo.io
def geolocate_ip(ip, token=None):
    try:
        if token:
            url = f"https://ipinfo.io/{ip}/json?token={token}"
        else:
            url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "country": data.get("country"),
                "region": data.get("region"),
                "city": data.get("city"),
                "loc": data.get("loc"),  # Latitude and Longitude
                "org": data.get("org")
            }
        else:
            return None
    except requests.RequestException as e:
        console.print(f"Error while geolocating IP {ip}: {e}", style="bold red")
        return None


# Function to visualize the relationships using NetworkX
def visualize_relationships(graph):
    try:
        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(graph, k=0.5)
        nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='gray', linewidths=1,
                font_size=15)
        plt.title("Entity Relationship Graph")
        plt.show()
    except Exception as e:
        console.print(f"Error visualizing relationships: {e}", style="bold red")


# Function to perform the search with detailed output including NER, IP Geolocation, and Link Analysis
async def search_in_groups(client, selected_groups, selected_keywords, ipinfo_token=None):
    results = []  # List to store search results
    graph = nx.Graph()  # Create a graph for relationship visualization

    async with client:
        with Progress() as progress:
            task = progress.add_task("[cyan]Searching...", total=len(selected_groups))
            for group_url in selected_groups:
                try:
                    group = await client.get_entity(group_url)
                    async for message in client.iter_messages(group, limit=100):
                        message_text = message.message
                        if message_text:
                            # Named Entity Recognition (NER)
                            doc = nlp(message_text)
                            entities = [(ent.text, ent.label_) for ent in doc.ents]

                            # Add entities to the graph
                            sender_node = f"User_{message.sender_id}"
                            graph.add_node(sender_node)

                            # Contextual Keyword Search and NER
                            for category, words in selected_keywords.items():
                                for word in words:
                                    match = re.search(r'\b' + re.escape(word) + r'\b', message_text, re.IGNORECASE)
                                    if match:
                                        # Extract context around the keyword (e.g., 30 characters before and after)
                                        start_idx = max(match.start() - 30, 0)
                                        end_idx = min(match.end() + 30, len(message_text))
                                        context = message_text[start_idx:end_idx]

                                        # Highlight detected entities
                                        highlighted_text = message_text
                                        for ent in entities:
                                            highlighted_text = highlighted_text.replace(ent[0],
                                                                                        f"[bold red]{ent[0]}[/bold red]")

                                        # Geolocate IP addresses in the message (if any)
                                        geolocated_ips = []
                                        ip_pattern = re.compile(
                                            r'(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)'
                                        )
                                        ips_found = ip_pattern.findall(message_text)
                                        for ip in ips_found:
                                            geo_info = geolocate_ip(ip, ipinfo_token)
                                            if geo_info:
                                                ip_node = f"IP_{ip}"
                                                graph.add_edge(sender_node, ip_node)
                                                geolocated_ips.append((ip, geo_info))

                                        # Add keyword nodes and edges
                                        keyword_node = f"Keyword_{word}"
                                        graph.add_edge(sender_node, keyword_node)

                                        for ent in entities:
                                            entity_node = f"{ent[1]}_{ent[0]}"
                                            graph.add_edge(sender_node, entity_node)

                                        # Formatting the result
                                        result = (
                                            f"Keyword: {word}\n"
                                            f"Context: {context}\n"
                                            f"Group: {group.title}\n"
                                            f"Date: {message.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                            f"Sender ID: {message.sender_id}\n"
                                            f"Message: {highlighted_text}\n"
                                            f"Entities: {entities}\n"
                                            f"Geolocated IPs: {geolocated_ips}\n"
                                            f"{'-' * 50}\n"
                                        )
                                        results.append(result)
                                        console.print(f"[yellow]{result}[/yellow]")
                except FloodWaitError as e:
                    console.print(f"Rate limit exceeded, waiting for {e.seconds} seconds", style="bold red")
                    await asyncio.sleep(e.seconds)
                except (ApiIdInvalidError, Exception) as e:
                    error_message = f"An error occurred while searching {group_url}: {e}"
                    results.append(error_message)
                    console.print(f"[red]{error_message}[/red]")
                progress.update(task, advance=1)

    # Visualize the relationships after processing all messages
    visualize_relationships(graph)
    return results  # Return the list of results


# Initialize console for rich output
console = Console()

# Print ASCII Art
console.print(ascii_art, style="bold cyan")

# Load the API credentials from the credentials.txt file
api_id, api_hash, ipinfo_token = load_telegram_api_credentials()

# Setup Telegram client
client = TelegramClient('my_session', api_id, api_hash)


# Main loop
async def main():
    console.print("Welcome to the Detect.Leaked tool!", style="bold cyan")
    while True:
        console.print("Would you like to perform another search task? (yes to continue / exit to stop)",
                      style="bold green")
        user_input = Prompt.ask("(exit)").strip().lower()
        if user_input == 'exit':
            break

        # Ask user to choose a country or global search
        available_countries = list(groups_to_search.keys()) + ['world']
        console.print(
            f"Enter a country to search for leaks or type 'world' for a global search. Available countries: {', '.join(available_countries)}",
            style="bold green")
        selected_country = Prompt.ask("(world)").strip().lower()

        if selected_country in groups_to_search:
            selected_groups = groups_to_search[selected_country]
            selected_keywords = keywords.get(selected_country, keywords['world'])
        else:
            selected_groups = groups_to_search['world']
            selected_keywords = keywords['world']

        # Allow user to add additional channels
        console.print("Would you like to add additional Telegram channels to search? (yes/no)", style="bold green")
        add_channels = Prompt.ask("(no)").strip().lower()
        if add_channels == 'yes':
            new_channels = Prompt.ask("Enter the Telegram channels/groups to search (comma-separated)").strip()
            # Validate and clean the input channels
            new_channels = [channel.strip() for channel in new_channels.split(',') if channel.strip()]
            selected_groups.extend(new_channels)

        # Allow user to add additional keywords
        console.print("Would you like to add additional keywords? (yes/no)", style="bold green")
        add_keywords = Prompt.ask("(no)").strip().lower()
        if add_keywords == 'yes':
            new_keywords = Prompt.ask("Enter the keywords to search for (comma-separated)").strip()
            if "custom_keywords" not in selected_keywords:
                selected_keywords["custom_keywords"] = []
            # Clean and add new keywords
            selected_keywords["custom_keywords"].extend([kw.strip() for kw in new_keywords.split(',') if kw.strip()])

        results = await search_in_groups(client, selected_groups, selected_keywords, ipinfo_token)

        # Ask the user if they want to save the results
        save_results = Prompt.ask("Do you want to save the results? (S to save / N to skip)").strip().lower()
        if save_results == 's':
            save_results_to_file(results)

    console.print("Thank you for using Detect.Leaked!", style="bold cyan")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\nProcess interrupted by user. Exiting...", style="bold red")
        sys.exit(0)
