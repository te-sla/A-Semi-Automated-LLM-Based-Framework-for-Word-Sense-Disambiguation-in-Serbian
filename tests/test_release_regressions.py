import importlib
import sys
import types
from pathlib import Path


class FakeSimilarity:
    def squeeze(self, dim):
        assert dim == 0
        return self

    def tolist(self):
        return [0.0, 1.0]


class RecordingSentenceTransformer:
    def __init__(self):
        self.calls = []

    def encode(self, texts, **kwargs):
        self.calls.append((texts, kwargs))
        return texts


class FakeToken:
    def __init__(self, text, start, end, layers=None):
        self.text = text
        self.start = start
        self.end = end
        self.layers = dict(layers or {})

    def add_layer(self, name, value):
        self.layers[name] = value


class FakeMwe:
    def __init__(self, lemma, token_indices):
        self.lemma = lemma
        self.token_indices = token_indices


class FakeSentence:
    def __init__(self):
        self.text = "u skladu"
        self.tokens = [
            FakeToken("u", 0, 1, {"coarseValue": "ADP", "value_4": "u", "MWEid": "1"}),
            FakeToken("skladu", 2, 8, {"coarseValue": "NOUN", "value_4": "sklad", "MWEid": "1"}),
        ]
        self.mwes = [FakeMwe("*", [0, 1])]


class UnusedChain:
    def invoke(self, _payload):
        raise AssertionError("placeholder MWEs must not call the model chain")


def _install_lightweight_import_stubs(monkeypatch):
    fake_dotenv = types.ModuleType("dotenv")
    fake_dotenv.load_dotenv = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "dotenv", fake_dotenv)

    fake_sentence_transformers = types.ModuleType("sentence_transformers")
    fake_sentence_transformers.SentenceTransformer = RecordingSentenceTransformer
    fake_sentence_transformers.util = types.SimpleNamespace(cos_sim=lambda *_args: FakeSimilarity())
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_sentence_transformers)

    fake_webanno_root = types.ModuleType("webanno_spacy_converter")
    fake_models = types.ModuleType("webanno_spacy_converter.models")
    fake_annotation_token = types.ModuleType("webanno_spacy_converter.models.annotation_token")
    fake_annotation_token.AnnotationToken = FakeToken
    fake_sentence_module = types.ModuleType("webanno_spacy_converter.models.sentence_with_mwes")
    fake_sentence_module.AnnotatedSentenceWithMWEs = FakeSentence
    fake_sentence_module.MultiWordExpression = FakeMwe
    fake_writers = types.ModuleType("webanno_spacy_converter.writers")
    fake_writer_module = types.ModuleType("webanno_spacy_converter.writers.webanno_writer")
    fake_writer_module.BaseWebAnnoTSVWriter = object

    monkeypatch.setitem(sys.modules, "webanno_spacy_converter", fake_webanno_root)
    monkeypatch.setitem(sys.modules, "webanno_spacy_converter.models", fake_models)
    monkeypatch.setitem(sys.modules, "webanno_spacy_converter.models.annotation_token", fake_annotation_token)
    monkeypatch.setitem(sys.modules, "webanno_spacy_converter.models.sentence_with_mwes", fake_sentence_module)
    monkeypatch.setitem(sys.modules, "webanno_spacy_converter.writers", fake_writers)
    monkeypatch.setitem(sys.modules, "webanno_spacy_converter.writers.webanno_writer", fake_writer_module)


def _fresh_import(module_name):
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def test_placeholder_mwe_is_marked_new_sense_without_chain_call(monkeypatch):
    _install_lightweight_import_stubs(monkeypatch)
    process_senses = _fresh_import("process_senses")
    config = _fresh_import("config")

    sentence = FakeSentence()
    result = process_senses.process_senses_with_chain(
        [sentence],
        senses_df=object(),
        chain=UnusedChain(),
        origin_model="test-model",
        time_delay=0,
    )

    assert result == [sentence]
    for token in sentence.tokens:
        assert token.layers[config.SENSE_ID_FIELD] == "NEW_SENSE[2000]"
        assert token.layers[config.SENSE_COUNT_FIELD] == "0[2000]"
        assert token.layers[config.SENSE_ORIGIN] == "None"


def test_simple_wsd_presets_include_paper_baselines(monkeypatch):
    _install_lightweight_import_stubs(monkeypatch)
    config = _fresh_import("config")

    assert set(config.SIMPLE_WSD_MODEL_PRESETS) == {"simple", "tesla", "mling"}
    assert config.SIMPLE_WSD_MODEL_PRESETS["simple"]["model_name"] == config.SWD_MODEL
    assert config.SIMPLE_WSD_MODEL_PRESETS["tesla"]["model_name"] == config.TESLA_SWD_MODEL
    assert config.SIMPLE_WSD_MODEL_PRESETS["mling"]["model_name"] == config.MLING_SWD_MODEL
    assert config.SIMPLE_WSD_MODEL_PRESETS["mling"]["text_prefix"] == "query: "
    assert config.SIMPLE_WSD_MODEL_PRESETS["mling"]["normalize_embeddings"] is True


def test_simple_wsd_applies_e5_prefix_and_normalization(monkeypatch):
    _install_lightweight_import_stubs(monkeypatch)
    simple_wsd = _fresh_import("simple_wsd")
    model = RecordingSentenceTransformer()

    scores = simple_wsd._compute_similarity_scores(
        model,
        "Marked Serbian context",
        ["first gloss", "query: already prefixed gloss"],
        text_prefix="query: ",
        normalize_embeddings=True,
    )

    assert model.calls[0] == (
        "query: Marked Serbian context",
        {"convert_to_tensor": True, "normalize_embeddings": True},
    )
    assert model.calls[1] == (
        ["query: first gloss", "query: already prefixed gloss"],
        {"convert_to_tensor": True, "normalize_embeddings": True},
    )
    assert scores == [(0, 0.0), (1, 1.0)]


def test_range_runner_uses_public_repo_preprocessing_imports():
    script = Path("tools/run_simple_wsd_range.py").read_text(encoding="utf-8")

    assert "lexisense_wsd_agent" not in script
    assert "from preprocessing import" in script
