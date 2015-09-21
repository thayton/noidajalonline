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

    def get_sector_select(self):
        id = 'ctl00_ContentPlaceHolder1_ddlsector'
        sector_select_elem = self.driver.find_element_by_id(id)
        sector_select = Select(sector_select_elem)
        return sector_select
        
    def select_sector_option(self, index, wait=False):
        id = 'ctl00_ContentPlaceHolder1_ddlblock'
        block_select_elem = self.driver.find_element_by_id(id)

        def block_select_updated(driver):
            try:
                block_select_elem.text
            except StaleElementReferenceException:
                return True
            except:
                pass

            return False

        sector_select = self.get_sector_select()
        sector_select.select_by_index(index)

        if wait:
            # Wait for Block select to load via AJAX
            wait = WebDriverWait(self.driver, 10)
            wait.until(block_select_updated)

        return sector_select

    def get_sector_option_text(self, index):
        sector_select = self.select_sector_option(index)
        return sector_select.first_selected_option.text

    def get_block_select(self):
        id = 'ctl00_ContentPlaceHolder1_ddlblock'
        block_select_elem = self.driver.find_element_by_id(id)
        block_select = Select(block_select_elem)
        return block_select

    def select_block_option(self, index):
        block_select = self.get_block_select()
        block_select.select_by_index(index)
        return block_select

    def get_block_option_text(self, index):
        block_select = self.select_block_option(index)
        return block_select.first_selected_option.text

    def filename(self, sector, block, house):
        filename = \
            self.get_sector_option_text(sector) + '-' \
            + self.get_block_option_text(block) + '-' \
            + house + '.html'

        return filename

    def save_html(self, filename):
        w = open(filename, 'w')
        w.write(self.driver.page_source.encode('utf8'))
        w.close()
        
    def scrape(self):

        def sectors():
            sector_select = self.get_sector_select()
            sector_option_indexes = range(1, len(sector_select.options))

            # Iterate through each sector
            for index in sector_option_indexes:
                self.select_sector_option(index, wait=True)
                yield index

        def blocks():
            block_select = self.get_block_select()
            block_option_indexes = range(1, len(block_select.options))

            # Iterate through each block
            for index in block_option_indexes:
                self.select_block_option(index)

                yield index
            
        def houses():
            for house in range(4, 501):
                yield format(house, '03d')

        # --------------------------------------------------
        self.driver.get(self.url)

        for sector in sectors():
            for block in blocks():
                for house in houses():
                    id = 'ctl00_ContentPlaceHolder1_txtflatno'
                    flatno_input = self.driver.find_element_by_id(id)
                    flatno_input.clear()
                    flatno_input.send_keys(house)

                    # We get the text values for sector, block and 
                    # house from the form elems so we must generate 
                    # the filename before submitting the form
                    filename = self.filename(sector, block, house)

                    id = 'ctl00_ContentPlaceHolder1_btnsave'
                    submit_btn = self.driver.find_element_by_id(id)
                    submit_btn.click()

                    #
                    # If the sector/block/house house exists we'll get
                    # to a page with a logout link. Otherwise we'll 
                    # get an alert box we have to accept
                    #
                    try:
                        id = 'ctl00_linkLogout'
                        logout_elem = self.driver.find_element_by_id(id)
                    except NoSuchElementException:
                        logout_elem = None

                    if logout_elem:
                        self.save_html(filename)
                        logout_elem.click()
                        
                        # We have to reselect these after we logout
                        self.select_sector_option(sector, wait=True)
                        self.select_block_option(block)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint)
    scraper = Scraper()
    scraper.scrape()
