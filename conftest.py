# conftest.py
import os
import pytest 

TESTRAIL_URL = os.getenv("TESTRAIL_URL")
TESTRAIL_USER = os.getenv("TESTRAIL_USER")
TESTRAIL_KEY = os.getenv("TESTRAIL_KEY")
TESTRAIL_PROJECT_ID = os.getenv("TESTRAIL_PROJECT_ID")
TESTRAIL_SUITE_ID = os.getenv("TESTRAIL_SUITE_ID")
TESTRAIL_RUN_ID = os.getenv("TESTRAIL_RUN_ID")

