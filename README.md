# PROJECT TITLE: Virtualizer
## Video Demo:  https://youtu.be/u9B9cV6Rk1k
## Github Repo: https://github.com/ApostolosVarvatis/CS50-Final-Project
## Description
My final project for CS50x is a web-based virtual wallet application (developed locally in vs code and saved in the cloud using git and GitHub) using JavaScript, Python, and SQL as well as
with the bootstrap 5.2.3 framework, the jinja 3.1 templating engine, and the flask micro-framework!

## Disclaimer: The application uses a free API (from rapidapi.com), so it has a few limitations due to the free subscription plan. Sadly you have 5 requests per minute for crypto-currencies and 5 for currencies. This means that if the history page or the homepage contains a lot of elements, the page cannot load..

## Usage

- My software is a virtual wallet that gathers real-time information on currencies/cryptocurrencies such as exchange rates and currency names/symbols.
  It supports many features such as a transactions history tab, real-time exchange rate displaying, safe password hashing, password changing, user error explaining, and cash adding in any currency!

- When you first open the page you are introduced to the login tab. But you don't have an account! Probably. So you can go to the register tab from the navigation bar and register.
  If you want to change your password you can also do that by clicking on the Change Password prompt on the login page!

- When you enter, you are presented with the homepage where your currencies and cryptos are displayed.
  Next to any currency, you can see a real-time calculation based on the current exchange rate of the currency displayed!
  Within your virtual wallet, you begin with 100,000.00 EUR and you can start trading into other currencies like USD, and AUD.

- How do you do that? Well, firstly you have to check the current exchange rate from one currency to another in the Currency tab on the navigation bar.
  After that, you can advance to the Exchange Currency tab, where you can exchange with real-time rates.

- Your transaction will be instantly added to the History tab and the Homepage will add that new currency to the table.
  The same goes for the crypto-currencies, with the Exchange Crypto and Crypto tab respectively.

- If you are not satisfied with the currencies in your wallet you can add some via the Add to Wallet form on the homepage. Any existing currency is accepted.

- Once you add one the transaction will be logged into the history page.
  Now onto the history tab, every transaction is logged and is displayed extensively.
  More notably the exchange rate of when a transaction was made is shown next to the current rate of the same transaction so you can compare and analyze your choices!
  That's it! You can now track any currency or cryptocurrency and start making smart investments!


## Contents

To begin with, my project contains multiple files and folders:
- The templates folder contains all the HTML files as well as the "layout.html" file, which is the template for all the other pages.

- The static folder stores the CSS stylesheet as well as a .svg icon file used as the logo of the navbar.

- The flask_session file keeps track of the current user. Instead of cookies, the data is stored locally.

- The requirements file lists all the modules that need to be downloaded for the application to function correctly.

- The database.db file stores all the data accumulated such as usernames, hashed passwords, transactions, currencies, dates/times, and much more.

- The helpers.py file contains additional functions which are used in app.py (the .py main file). Most noticeable are the API lookup functions, which take as arguments two currency symbols and output a dictionary containing information about them.

- Then the app.py file which is the main file of the project. It contains all the routes for the HTML to be rendered as well as all the logic and functionality behind the web application.

- And lastly, this README.md file tries to best explain the project!

## The Debate
The only change I debate making is the use of the API so extensively as it limits the usage of the history and home page, but I think the trade is worth it as it doesn't focus on a large audience.
I implemented a feature that disables the Rate Now and does not call the API so you can use the page more often but this is not how the site is meant to be used AT ALL.
At the end of the app.py file, there are two more routes called HistoryNonRate and IndexNonRate which do not provide real-time data and are based on database data only.
You can only access the pages by manually typing historynonrate and indexnonrate on the URL of your browser.
I repeat this is not how the site is meant to be used only to understand its functionality!
    

All in all, I am proud of my final project and my determination, despite the deadlines and my full schedule.

# THANK YOU CS50!