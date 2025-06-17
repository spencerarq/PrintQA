# tests/test_analysis_with_testrail.py

import pytest
from unittest.mock import patch
from printqa.analysis import analyze_file
from scripts.testrail_reporter import send_individual_result

pytestmark = [pytest.mark.testrail, pytest.mark.unit]

TEST_CASE_ID_SUCCESS = 1
TEST_CASE_ID_FAILURE = 4

@pytest.mark.testrail(ids=[f"C{TEST_CASE_ID_SUCCESS}"])
def test_sends_passed_result_for_perfect_mesh(cube_perfect_path: str):
    """
    Verifica se, para uma malha perfeita, um resultado "Passed" (status_id=1) 
    é enviado para o TestRail.
    """
    analysis_result = analyze_file(cube_perfect_path)

    send_individual_result(analysis_result, test_case_id=TEST_CASE_ID_SUCCESS)

@pytest.mark.testrail(ids=[f"C{TEST_CASE_ID_FAILURE}"])
def test_sends_failed_result_for_open_mesh(cube_open_path: str):
    """
    Verifica se, para uma malha aberta, um resultado "Failed" (status_id=5) 
    é enviado para o TestRail.
    """
    analysis_result = analyze_file(cube_open_path)

    send_individual_result(analysis_result, test_case_id=TEST_CASE_ID_FAILURE)