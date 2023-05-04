import time
import pandas as pd
from pandas.tseries.offsets import *
import datetime as dt

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.maximize_window()
driver.get('https://kalimatimarket.gov.np/price')
driver.implicitly_wait(5)

# select english language
language_xpath = '/html/body/header/div[3]/div/div/nav/ul/li[7]/a'
language_select = driver.find_element(By.XPATH, language_xpath)
language_select.click()
time.sleep(2)
country_xpath = '/html/body/header/div[3]/div/div/nav/ul/li[7]/ul'
country_select = driver.find_element(By.XPATH, country_xpath)
country_select.click()
time.sleep(2)





# price information of all the data
def price_information(driver):
    number_of_record_xpath = '//*[@id="commodityPriceParticular_info"]'
    number_of_record = driver.find_element(By.XPATH, number_of_record_xpath).text
    #print(number_of_record)
    record_numbers = number_of_record.split()  # Split the text into a list of words
    record_number = int(record_numbers[-2])

    datas = []
    for record in range(1, record_number+1):
        #print(record)
        price_information_xpath = '//*[@id="commodityPriceParticular"]/tbody/tr[' + str(record) + ']'
        price_informations = driver.find_element(By.XPATH, price_information_xpath).text
        #print(type(price_informations))
        datas.append(price_informations)
    return datas


def made_dataframe(driver):
    product_information = price_information(driver)
    #print(product_information)
    data_new = [row.split('Rs') for row in product_information]
    #print(data_new)

    daily_df = pd.DataFrame(data_new, columns=['Product', 'Minimum', 'Maximum', 'Average'])
    # Remove whitespace from the columns
    daily_df.columns = daily_df.columns.str.strip()
    # Remove whitespace from the product names
    daily_df['Product'] = daily_df['Product'].str.strip()
    # Convert prices to numeric values
    daily_df['Minimum'] = pd.to_numeric(daily_df['Minimum'].str.strip())
    daily_df['Maximum'] = pd.to_numeric(daily_df['Maximum'].str.strip())
    daily_df['Average'] = pd.to_numeric(daily_df['Average'].str.strip())
    #print(daily_df)
    return daily_df

#made_dataframe(driver)


#to calculate the date range
def daterange(initial_date, end_date):
    dates = []
    while (initial_date != end_date):
        initial_date = initial_date + DateOffset(days=1)
        dates.append(initial_date.date())
    return dates
initial_date = pd.to_datetime('2022-12-31')
# end_date = pd.to_datetime(dt.date.today())
end_date = pd.to_datetime('2023-04-15')
date_range = daterange(initial_date, end_date)

def selectdate(date_range, driver):
    final_df = pd.DataFrame()
    for date_input in date_range:
        date_id = 'datePricing'
        date_to_find = driver.find_element(By.ID, date_id)
        submit_button_xpath = '//*[@id="queryFormDues"]/div/div[2]/button'
        submit_button = driver.find_element(By.XPATH, submit_button_xpath)

        date_formatted = date_input.strftime('%m/%d/%Y') # convert into string
        # print(date_formatted)
        # print(type(date_formatted))
        date_to_find.send_keys(date_formatted)
        time.sleep(15)
        submit_button.click()
        # all_information = price_information(driver)
        # print(all_information)
        daily_dataframe = made_dataframe(driver)
        # print(date_input)
        # print(daily_dataframe)
        daily_dataframe['Date'] = date_input
        #print(daily_dataframe)
        final_df = pd.concat([final_df, daily_dataframe], axis=0)

    return final_df
final_price_info = selectdate(date_range, driver)
# conver to csv file
final_price_info.to_csv('tarkari2023.csv')
#print(final_price_info)


driver.close()

