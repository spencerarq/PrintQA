# conftest.py
import os
# ... (outras importações) ...

# Estas variáveis serão lidas pelo pytest-testrail (se ele conseguir usá-las)
# ou pelo seu script trcli se você usar variáveis de ambiente para ele.
TESTRAIL_URL = os.getenv("TESTRAIL_URL")
TESTRAIL_USER = os.getenv("TESTRAIL_USER")
TESTRAIL_KEY = os.getenv("TESTRAIL_KEY")
TESTRAIL_PROJECT_ID = os.getenv("TESTRAIL_PROJECT_ID")
TESTRAIL_SUITE_ID = os.getenv("TESTRAIL_SUITE_ID")
TESTRAIL_RUN_ID = os.getenv("TESTRAIL_RUN_ID")

# Remova ou comente completamente qualquer HOOK ou FIXTURE que tente criar/publicar no TestRail
# Ex:
# @pytest.hookimpl(...)
# def pytest_runtest_makereport(...):
#     pass
# @pytest.fixture(...)
# def testrail_client():
#     pass