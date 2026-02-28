from webanno_spacy_converter.writers.webanno_writer import BaseWebAnnoTSVWriter
from webanno_spacy_converter.models.annotation_token import AnnotationToken
from config import (
    L_LEMMA, L_POS, L_UPOS, L_NAMED_ENT, L_NE_ID,
    L_MWE_ID, L_MWE_LEMMA, L_MWE_TYPE,
    SENSE_ID_FIELD, SENSE_COUNT_FIELD, SENSE_LIST_FIELD,
    SENSE_AINOTES_FIELD, SENSE_ORIGIN, SENSE_COMMENT_FIELD
)
from typing import List

class CustomWebAnnoTSVWriter(BaseWebAnnoTSVWriter):
    def _build_layer_header(self) -> str:
        """
        Constructs the layer header string used by WebAnno.
        Returns:
            str: Header line describing the annotation layers.
        """
        header = """
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS|PosValue|coarseValue
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity|identifier|value
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma|value
#T_SP=webanno.custom.MWE|MWEid|MWElemma|MWEtype
#T_SP=webanno.custom.sense|SenseID|Number_of_candidate_senses|List_of_candidate_senses|Comment|Ainotes
"""
        return header.strip()

    def _format_token_layers(self, token: AnnotationToken) -> List[str]:
        """
        Formats the annotation layers for a single token.
        Args:
            token (AnnotationToken): Token with annotation data.
        Returns:
            List[str]: List of string fields representing layers.
        """
        pos = token.layers.get(L_POS, "_")
        upos = token.layers.get(L_UPOS, "_")
        lemma = token.layers.get(L_LEMMA, "_")
        identifier = token.layers.get(L_NE_ID, "_")
        ne_type = token.layers.get(L_NAMED_ENT, "_")
        mwe_id = token.layers.get(L_MWE_ID, "_")
        mwe_lemma = token.layers.get(L_MWE_LEMMA, "_")
        mwe_type = token.layers.get(L_MWE_TYPE, "_")
        sense_id = token.layers.get(SENSE_ID_FIELD, "_")
        sense_count = token.layers.get(SENSE_COUNT_FIELD, "_")
        sense_list = token.layers.get(SENSE_LIST_FIELD, "_")
        sense_comment = token.layers.get(SENSE_COMMENT_FIELD, "_")
        sense_ainotes = token.layers.get(SENSE_AINOTES_FIELD, "_")

        if identifier not in ("*", "_") and not identifier.startswith("http"):
            identifier = f"http://www.wikidata.org/entity/{identifier}"
        return [
            pos, upos, identifier, ne_type, lemma, mwe_id, mwe_lemma, mwe_type,
            sense_id, sense_count, sense_list, sense_comment, sense_ainotes
        ]

class IncetprionWebAnnoTSVWriter(BaseWebAnnoTSVWriter):
    def _build_layer_header(self) -> str:
        """
        Constructs the layer header string used by WebAnno.
        Returns:
            str: Header line describing the annotation layers.
        """
        header = """
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS|PosValue|coarseValue
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity|identifier|value
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma|value
#T_SP=webanno.custom.MWE|MWEid|MWElemma|MWEtype
#T_SP=webanno.custom.WSD|Comment|Explanation|KBid|NumberOfSenses|Origine|Possible
"""
        return header.strip()

    def _format_token_layers(self, token: AnnotationToken) -> List[str]:
        """
        Formats the annotation layers for a single token.
        Args:
            token (AnnotationToken): Token with annotation data.
        Returns:
            List[str]: List of string fields representing layers.
        """
        def convert_expression(expr):
            base_url = "http://llod.jerteh.rs/WSD/se"
            code = expr.replace('-', '')
            code = code.replace('/', '_')
            code = code.replace('\\', '_')
            return f"{base_url}{code}"
        pos = token.layers.get(L_POS, "_")
        upos = token.layers.get(L_UPOS, "_")
        lemma = token.layers.get(L_LEMMA, "_")
        identifier = token.layers.get(L_NE_ID, "_")
        ne_type = token.layers.get(L_NAMED_ENT, "_")
        mwe_id = token.layers.get(L_MWE_ID, "_")
        mwe_lemma = token.layers.get(L_MWE_LEMMA, "_")
        mwe_type = token.layers.get(L_MWE_TYPE, "_")
        sense_id = token.layers.get(SENSE_ID_FIELD, "_")
        sense_count = token.layers.get(SENSE_COUNT_FIELD, "_")
        sense_list = token.layers.get(SENSE_LIST_FIELD, "_")
        sense_comment = token.layers.get(SENSE_COMMENT_FIELD, "_")
        sense_ainotes = token.layers.get(SENSE_AINOTES_FIELD, "_")
        sense_origine = token.layers.get(SENSE_ORIGIN, "_")

        if sense_id not in ("_", "*") and not sense_id.startswith("http"):
            sense_id = convert_expression(sense_id)
        if identifier not in ("_", "*") and not identifier.startswith("http"):
            identifier = f"http://www.wikidata.org/entity/{identifier}"
        return [
            pos, upos, identifier, ne_type, lemma, mwe_id, mwe_lemma, mwe_type,
            sense_comment, sense_ainotes, sense_id, sense_count, sense_origine, sense_list
        ]
