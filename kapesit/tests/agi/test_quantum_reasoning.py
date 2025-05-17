import numpy as np
import pytest
from kapesit.agi.quantum_reasoning import QuantumReasoning

def test_quantum_reasoning():
    reasoning = QuantumReasoning(num_qubits=4)
    
    reasoning.add_knowledge("A", 0.8)
    reasoning.add_knowledge("B", 0.6)
    reasoning.add_inference_rule("A", "B", 0.9)
    
    result = reasoning.reason("A")
    assert "probability" in result
    assert "confidence" in result
    assert "query" in result
    assert isinstance(result["probability"], float)
    assert 0 <= result["probability"] <= 1
    assert 0 <= result["confidence"] <= 1
    
    inference = reasoning.infer(["A"])
    assert "conclusions" in inference
    assert "confidence" in inference
    assert isinstance(inference["conclusions"], list)
    assert 0 <= inference["confidence"] <= 1
    
    reasoning.update_knowledge("A", 0.9)
    assert reasoning.knowledge_base["A"] == 0.85
    
    example = {"C": 0.7, "D": 0.5}
    reasoning.learn_from_example(example)
    assert "C" in reasoning.knowledge_base
    assert "D" in reasoning.knowledge_base
    
    hypothesis = reasoning.generate_hypothesis(["A", "B"])
    assert "hypotheses" in hypothesis
    assert "confidence" in hypothesis
    assert isinstance(hypothesis["hypotheses"], list)
    assert 0 <= hypothesis["confidence"] <= 1
    
    contradiction = reasoning.resolve_contradiction("A", "B")
    assert "resolution" in contradiction
    assert "confidence" in contradiction
    assert isinstance(contradiction["resolution"], (str, type(None)))
    assert 0 <= contradiction["confidence"] <= 1

def test_error_handling():
    reasoning = QuantumReasoning(num_qubits=4)
    
    with pytest.raises(ValueError):
        reasoning.add_knowledge("A", 1.5)
    
    with pytest.raises(ValueError):
        reasoning.add_inference_rule("A", "B", 1.5)
    
    with pytest.raises(ValueError):
        reasoning.update_knowledge("A", 1.5)
    
    result = reasoning.reason("X")
    assert result["probability"] == 0.0
    assert result["confidence"] == 0.0
    
    inference = reasoning.infer(["X"])
    assert inference["conclusions"] == []
    assert inference["confidence"] == 0.0
    
    hypothesis = reasoning.generate_hypothesis(["X"])
    assert hypothesis["hypotheses"] == []
    assert hypothesis["confidence"] == 0.0
    
    contradiction = reasoning.resolve_contradiction("X", "Y")
    assert contradiction["resolution"] is None
    assert contradiction["confidence"] == 0.0

def test_integration():
    reasoning = QuantumReasoning(num_qubits=4)
    
    reasoning.add_knowledge("A", 0.8)
    reasoning.add_knowledge("B", 0.6)
    reasoning.add_inference_rule("A", "B", 0.9)
    
    result = reasoning.reason("A")
    inference = reasoning.infer(["A"])
    
    assert isinstance(result["probability"], float)
    assert isinstance(inference["confidence"], float)
    
    reasoning.update_knowledge("A", 0.9)
    example = {"C": 0.7, "D": 0.5}
    reasoning.learn_from_example(example)
    
    hypothesis = reasoning.generate_hypothesis(["A", "B"])
    contradiction = reasoning.resolve_contradiction("A", "B")
    
    assert isinstance(hypothesis["confidence"], float)
    assert isinstance(contradiction["confidence"], float)
    
    reasoning.add_knowledge("E", 0.4)
    reasoning.add_inference_rule("B", "E", 0.8)
    
    chain_inference = reasoning.infer(["A"])
    assert len(chain_inference["conclusions"]) > 0
    assert 0 <= chain_inference["confidence"] <= 1 