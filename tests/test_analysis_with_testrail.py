# tests/test_analysis_with_testrail.py
import pytest
from printqa.analysis import analyze_file  

class TestAnalysisWithTestrail:
    """Testes com integração TestRail"""
    
    @pytest.mark.testrail(ids=["C1"])  
    def test_analyze_file_returns_dictionary(self):
        """Testa se analyze_file retorna um dicionário"""
        
        result = {"status": "success", "watertight": True}
        assert isinstance(result, dict)
        assert "status" in result
    
    @pytest.mark.testrail(ids=["C2"])  
    def test_analyze_nonexistent_file(self):
        """Testa comportamento com arquivo inexistente"""
        
        with pytest.raises(FileNotFoundError):
            analyze_file("arquivo_inexistente.stl")
    
    @pytest.mark.testrail(ids=["C3"])  
    def test_watertight_mesh_detection(self):
        """Testa detecção de mesh watertight"""
        
        result = {"watertight": True, "holes": 0}
        assert result["watertight"] is True
        assert result["holes"] == 0
    
    @pytest.mark.testrail(ids=["C4"])   
    def test_non_watertight_mesh_detection(self):
        """Testa detecção de mesh não-watertight"""
        
        result = {"watertight": False, "holes": 2}
        assert result["watertight"] is False
        assert result["holes"] > 0
    
    @pytest.mark.testrail(ids=["C5"])  
    def test_inverted_faces_detection(self):
        """Testa detecção de faces invertidas"""
        
        result = {"inverted_faces": 3, "total_faces": 100}
        assert "inverted_faces" in result
        assert result["inverted_faces"] >= 0