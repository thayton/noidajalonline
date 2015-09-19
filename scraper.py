#!/usr/bin/env python

import os, re, sys, signal
import urlparse

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from bs4 import BeautifulSoup

def sigint(signal, frame):
    sys.stderr.write('Exiting...\n')
    sys.exit(0)    

class Scraper(object):
    def __init__(self):
        self.url = 'http://www.noidajalonline.com/NOIDAJAL/Consumer.aspx'
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)

    def scrape(self):
        self.driver.get(self.url)

        block_select_elem = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_ddlblock')

        sector_select_elem = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_ddlsector')
        sector_select = Select(sector_select_elem)
        sector_option_indexes = range(1, len(sector_select.options))

        # Iterate through each sector
        for sector_index in sector_option_indexes:
            sector_select.select_by_index(sector_index)

            def block_select_updated(driver):
                try:
                    block_select_elem.text
                except StaleElementReferenceException:
                    return True
                except:
                    pass

                return False

            # Wait for Block select to load via AJAX
            wait = WebDriverWait(self.driver, 10)
            wait.until(block_select_updated)

            block_select_elem = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_ddlblock')
            block_select = Select(block_select_elem)
            block_option_indexes = range(1, len(block_select.options))

            # Iterate through each block
            for block_index in block_option_indexes:
                block_select.select_by_index(block_index)

                flatno_input = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_txtflatno')
                flatno_input.send_keys('004')

                submit_btn = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnsave')
                submit_btn.click()

                s = BeautifulSoup(self.driver.page_source, 'html.parser')            

                print s.prettify()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint)
    scraper = Scraper()
    scraper.scrape()
