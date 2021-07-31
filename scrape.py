from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import writer
import multiprocessing

options = Options()

options.add_experimental_option('excludeSwitches', ['enable-logging'])
id = 1

class Screenshot:
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=r"C:\Users\Adam\Code\chromedriver.exe", options=options)
        self.driver.set_window_size(1440, 1000)
        self.actions = ActionChains(self.driver)
        self.writer = writer.Writer()
        self.counter = 0;


    def run(self):
        # self.start_search()

    def parse_sqft_string(self, string):
        return int(string.split('sq')[0].replace(',', '').strip())

    def get_roof_sqft(self):
        roof_sqft_elem = self.driver.find_element_by_xpath('/html/body/div[1]/address-view/div[1]/div/div/section[1]/div[2]/md-card[1]/ul/li[2]/div[2]')
        roof_sqft_text = self.parse_sqft_string(roof_sqft_elem.get_attribute('innerText'))

        return roof_sqft_text

    def add_solar_data(self, electric_bill_amount):
        print('Electric bill amount selected', electric_bill_amount)

        try:
            kw_text_elem = self.driver.find_element_by_xpath('/html/body/div[1]/address-view/div[1]/div/div/section[2]/div/md-content[1]/div[2]/md-card/md-card-content/div/div[1]')
            kw_text_value = kw_text_elem.get_attribute('innerText')

            totalSolarPrice = self.calculateSolarPrice(kw_text_value)

            self.writer.insert_solar_data(kw_text_value, totalSolarPrice, electric_bill_amount)

            print('KW Value:', kw_text_value)
            print('Total Price:', totalSolarPrice)
            print('Electric Bill:', electric_bill_amount)
            print('\n\n')
        except NoSuchElementException:
            self.writer.insert_solar_data(0, 0, 0)
            print('Address not detected by project solar.')
    
    def get_basic_data(self):
        self.driver.get('https://jackedupvegan.com')

        random_elem = self.driver.find_element_by_xpath('/html/body/div[3]/div/div/div[1]/div/a/div')
        time.sleep(1)
        print('Value = ', random_elem.text)

        self.driver.close()
        return random_elem.text


    def search_property(self, address):
        self.driver.get("https://www.google.com/get/sunroof")
        WebDriverWait(self.driver, 6).until(EC.element_to_be_clickable((By.ID, 'input-0')))

        input_elem = self.driver.find_element_by_id('input-0')
        input_elem.send_keys(address)
        time.sleep(1)
        input_elem.send_keys(Keys.RETURN)

    def select_dropdown_option(self, amount):
        try:
            self.driver.execute_script("window.scrollTo(0, 500)") 

            # Average Electric Dropdown Menu 
            electric_dropdown = self.driver.find_element_by_xpath('/html/body/div[1]/address-view/div[1]/div/div/section[2]/div/md-content[1]/div[1]/md-card/md-card-content/md-select')
            electric_dropdown.click()

            WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.TAG_NAME, "md-option")))
            dropdown_options = self.driver.find_elements_by_tag_name('md-option')
            # Scroll to dropdown item to make clickable

            for x in dropdown_options:
                electric_bill_amount = int(x.get_attribute('value'))
                if (amount >= 500): amount = 500
                if (electric_bill_amount == amount):
                    time.sleep(0.2)
                    x.click()
        except:
            print('Stale element refrence')

    #  Takes in '10kw' string and multiplies it by 1000 * 5.55
    def calculateSolarPrice(self, str):
        number = float(str.split(' ')[0])

        formula = number * 1000 * 5.55 

        return formula

    def calc_average_electric(self, sqft):
        price = 0

        if (sqft >= 1000):
            price += 150
            sqft -= 1000

        remainder = sqft / 1000 // 1

        if (remainder >= 1):
            price += 100 * remainder

        return price

    def start_next_search(self, address):
        # Scroll Back To Top & Search Again
        self.driver.execute_script("window.scrollTo(0, 0)") 

        # Wait until search bar is loaded.
        
        # search_bar = self.driver.find_element_by_xpath('/html/body/div[1]/address-view/div[1]/div/div/section[1]/div[2]/address-search/div/form/md-autocomplete/md-autocomplete-wrap/input')
        search_bar = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/address-view/div[1]/div/div/section[1]/div[2]/address-search/div/form/md-autocomplete/md-autocomplete-wrap/input")))
        time.sleep(0.2)
        search_bar.send_keys(address)


        search_result_elem = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/md-virtual-repeat-container/div/div[2]/ul")))
        search_result_elem_first = search_result_elem.find_element_by_id('md-option-0-0')

        # self.driver.find_element_by_xpath('//html').click();
        if (search_result_elem):
            search_result_elem_first.click()
        else:
            self.driver.find_elements_by_xpath('/html/body/div[1]/address-view/div[1]/div/div/section[1]/div[2]/address-search/div/form/button').click()

        print('Starting next search for....', address)

    def start_search(self):
        # Start property search
        self.search_property(self.writer.get_current_address())
        print('Starting search for....', self.writer.get_current_address())

        while (self.counter <= (self.writer.get_max_row() - 3)):
            self.counter = self.counter + 1

            try:
                # Using as a way to check if the page is loaded.
                WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/address-view/div[1]/div/div/section[2]/div/md-content[2]/md-card/md-card-content")))
            except TimeoutException:
                print('Address not recognized by project solar.')

                # Start the next search.
                self.writer.next()
                self.writer.insert_solar_data(0, 0, 0)
                self.start_next_search(self.writer.get_current_address())
            else:
                # Get the roof sqFt and calculate electric bill from that
                roof_sq_ft = self.get_roof_sqft()
                electric_price = self.calc_average_electric(roof_sq_ft)
                
                print('Selecting Dropdown\n')

                # # Loop through available options to sleect the right one
                self.select_dropdown_option(electric_price)

                # time.sleep(1)
                # Add the solar data that's been generated
                self.add_solar_data(electric_price)
                self.writer.next()

                time.sleep(0.1)
                # Start the next search.
                self.start_next_search(self.writer.get_current_address())
                
                time.sleep(0.3)
                # # Click out of the search input to select dropdown again
                # self.driver.find_element_by_xpath('//html').click();

        self.writer.save()
    


