#!/usr/bin/env python3
"""
Debug script to trace exactly how MWE sense annotations are applied.
This will help identify where the "whole span" issue occurs.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from webanno_spacy_converter.parsers.tsv_parser_v3 import WebAnnoLEXISParser
from preprocessing import get_mwe_tokens, mark_mwe, get_mwe_filtered_senses
from process_senses import process_senses_with_chain, parse_model_output
from config import SENSE_ID_FIELD, SENSE_AINOTES_FIELD, SENSE_COUNT_FIELD, SENSE_LIST_FIELD, SENSE_ORIGIN
import pandas as pd

def mock_llm_chain(input_dict):
    """Mock LLM that always returns a simple JSON response."""
    return '{"sense_id": "TEST_SENSE", "explanation": "Mock LLM explanation"}'

def test_mwe_annotation_application():
    """Test how MWE annotations are applied to tokens."""
    
    print("🔍 DEBUGGING MWE ANNOTATION APPLICATION")
    print("="*60)
    
    # Load test data
    tsv_file = Path("Data/example-mwe.tsv")
    parser = WebAnnoLEXISParser(tsv_file)
    sentences = parser.parse()
    
    # Create dummy sense repository
    dummy_senses = pd.DataFrame({
        'senseID': ['CVMWE-0399', 'TEST_SENSE'],
        'lemma': ['širiti se', 'poboljšavati se'],
        'definition': ['to spread, expand', 'to improve'],
        'type': ['IRV', 'IRV'],
        'upos': ['V', 'V']
    })
    
    for sent_idx, sentence in enumerate(sentences):
        if not sentence.mwes:
            continue
            
        print(f"\n{'='*50}")
        print(f"SENTENCE {sent_idx + 1}: {sentence.text}")
        print(f"{'='*50}")
        
        for mwe_idx, mwe in enumerate(sentence.mwes):
            print(f"\n--- MWE {mwe_idx + 1}: '{mwe.lemma}' ---")
            print(f"Token indices: {mwe.token_indices}")
            
            # Show all tokens in the sentence with their current annotation state
            print(f"\nBEFORE PROCESSING - All sentence tokens:")
            for i, token in enumerate(sentence.tokens):
                sense_id = token.layers.get(SENSE_ID_FIELD, "NONE")
                is_mwe_token = i in mwe.token_indices
                marker = "🎯" if is_mwe_token else "  "
                print(f"{marker} Token[{i}]: '{token.text}' [{token.start}:{token.end}] sense={sense_id}")
            
            # Get MWE tokens that should receive annotations
            mwe_tokens = get_mwe_tokens(sentence, mwe)
            print(f"\nMWE TOKENS to annotate:")
            for i, token in enumerate(mwe_tokens):
                print(f"  {i}: '{token.text}' [{token.start}:{token.end}]")
            
            # Show what the LLM sees
            marked_sentence = mark_mwe(mwe, sentence, "**", "**")
            print(f"\nLLM INPUT: {marked_sentence}")
            
            # Simulate what process_senses_with_chain does
            print(f"\nSIMULATING ANNOTATION APPLICATION...")
            
            # Mock the LLM response
            sense_id = "TEST_SENSE"
            notes = "Mock explanation for testing"
            n = 2000 + mwe_idx
            
            # This is exactly what process_senses_with_chain does (lines 189-194)
            for token in mwe_tokens:
                print(f"  Adding sense layers to token: '{token.text}'")
                token.add_layer(SENSE_ID_FIELD, f"{sense_id}[{n}]")
                token.add_layer(SENSE_COUNT_FIELD, f"1[{n}]")
                token.add_layer(SENSE_LIST_FIELD, f"TEST_SENSE[{n}]")
                token.add_layer(SENSE_AINOTES_FIELD, f"{notes}[{n}]")
                token.add_layer(SENSE_ORIGIN, "TEST")
            
            # Show all tokens AFTER processing
            print(f"\nAFTER PROCESSING - All sentence tokens:")
            for i, token in enumerate(sentence.tokens):
                sense_id_layer = token.layers.get(SENSE_ID_FIELD, "NONE")
                is_mwe_token = i in mwe.token_indices
                marker = "✅" if is_mwe_token else "  "
                print(f"{marker} Token[{i}]: '{token.text}' [{token.start}:{token.end}] sense={sense_id_layer}")
            
            # Check if any non-MWE tokens got annotations
            print(f"\nCHECKING FOR INCORRECT ANNOTATIONS:")
            incorrect_annotations = []
            for i, token in enumerate(sentence.tokens):
                has_sense = SENSE_ID_FIELD in token.layers and token.layers[SENSE_ID_FIELD] != "NONE"
                should_have_sense = i in mwe.token_indices
                
                if has_sense and not should_have_sense:
                    incorrect_annotations.append(i)
                    print(f"  ❌ Token[{i}] '{token.text}' has sense but shouldn't!")
                elif not has_sense and should_have_sense:
                    print(f"  ⚠️  Token[{i}] '{token.text}' should have sense but doesn't!")
            
            if not incorrect_annotations:
                print(f"  ✅ All annotations applied correctly!")
            else:
                print(f"  🚨 Found {len(incorrect_annotations)} incorrect annotations!")

def test_output_verification():
    """Test what gets written to the output TSV."""
    
    print(f"\n{'='*60}")
    print("TESTING OUTPUT VERIFICATION")
    print(f"{'='*60}")
    
    # Load and process one sentence
    tsv_file = Path("Data/example-mwe.tsv")
    parser = WebAnnoLEXISParser(tsv_file)
    sentences = parser.parse()
    
    if not sentences or not sentences[0].mwes:
        print("No MWEs to test")
        return
    
    sentence = sentences[0]
    mwe = sentence.mwes[0]
    
    # Manually add some sense annotations like process_senses_with_chain would
    mwe_tokens = get_mwe_tokens(sentence, mwe)
    for i, token in enumerate(mwe_tokens):
        token.add_layer(SENSE_ID_FIELD, f"TEST_SENSE[2000]")
        token.add_layer(SENSE_AINOTES_FIELD, f"Test annotation {i}[2000]")
    
    # Show what would be written to TSV
    print(f"\nTSV OUTPUT PREVIEW:")
    print(f"Sentence: {sentence.text}")
    print(f"MWE: '{mwe.lemma}' (indices: {mwe.token_indices})")
    print()
    
    for i, token in enumerate(sentence.tokens):
        sense_id = token.layers.get(SENSE_ID_FIELD, "*")
        sense_notes = token.layers.get(SENSE_AINOTES_FIELD, "_")
        is_mwe_token = i in mwe.token_indices
        
        # Simulate TSV output format
        tsv_line = f"{i+1}\t{token.start}-{token.end}\t{token.text}\t...\t{sense_id}\t{sense_notes}"
        
        if is_mwe_token:
            print(f"✅ {tsv_line}")
        else:
            if sense_id != "*" and sense_id != "_":
                print(f"❌ {tsv_line}  <-- WRONG! Non-MWE token has sense annotation")
            else:
                print(f"   {tsv_line}")

if __name__ == "__main__":
    test_mwe_annotation_application()
    test_output_verification()
    
    print(f"\n🎯 ANALYSIS:")
    print("This test shows exactly which tokens get sense annotations.")
    print("If non-MWE tokens are getting annotations, the issue is in process_senses_with_chain.")
    print("If the annotations are correct but the TSV output looks wrong, the issue is in the writers.")