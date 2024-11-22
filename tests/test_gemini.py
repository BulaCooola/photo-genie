import pytest
from unittest.mock import patch
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "modules"))
)


print(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "modules")))

from gemini import Gemini


# Test for initialization
# @pytest.fixture
def gemini():
    return Gemini()


geminiF = gemini()


def test_initialization(gemini):
    assert gemini._env_file == ".env"
    assert gemini._model1 is None
    assert gemini._model2 is None


test_initialization(geminiF)
