#!/usr/bin/env python3
"""
Test script to verify MWE processing in process_senses.py
Focuses on checking if only actual MWE tokens are marked and processed.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from webanno_spacy_converter.parsers.tsv_parser_v3 import WebAnnoLEXISParser
from preprocessing import get_mwe_tokens, mark_mwe, get_mwe_filtered_senses
from process_senses import process_senses_with_chain
import pandas as pd

def test_mwe_token_extraction():
    """Test MWE token extraction from example file."""
    
    # Load test data
    tsv_file = Path("Data/example-mwe.tsv")
    if not tsv_file.exists():
        print(f"❌ Test file not found: {tsv_file} — skipping.")
        return
    
    print(f"🔍 Testing MWE processing from: {tsv_file}")
    
    # Parse sentences
    parser = WebAnnoLEXISParser(tsv_file)
    sentences = parser.parse()
    
    print(f"✅ Loaded {len(sentences)} sentences")
    
    # Analyze each sentence
    for sent_idx, sentence in enumerate(sentences):
        print(f"\n{'='*60}")
        print(f"SENTENCE {sent_idx + 1}: {sentence.text}")
        print(f"{'='*60}")
        
        if not sentence.mwes:
            print("No MWEs in this sentence")
            continue
        
        for mwe_idx, mwe in enumerate(sentence.mwes):
            print(f"\n--- MWE {mwe_idx + 1}: '{mwe.lemma}' ---")
            print(f"Type: {mwe.type}")
            print(f"Token indices: {mwe.token_indices}")
            
            # Get MWE tokens (this is what process_senses.py uses)
            mwe_tokens = get_mwe_tokens(sentence, mwe)
            print(f"\n📍 MWE TOKENS (what gets annotated):")
            for i, token in enumerate(mwe_tokens):
                print(f"  {i}: '{token.text}' [{token.start}:{token.end}]")
            
            # Show marked sentence (this is what LLM sees)
            marked_sentence = mark_mwe(mwe, sentence, "<<", ">>")
            print(f"\n📝 MARKED SENTENCE (what LLM sees):")
            print(f"  {marked_sentence}")
            
            # Check for potential issues
            if mwe.token_indices:
                min_idx = min(mwe.token_indices)
                max_idx = max(mwe.token_indices)
                
                # Check if all tokens in range are included
                all_tokens_in_range = list(range(min_idx, max_idx + 1))
                missing_tokens = set(all_tokens_in_range) - set(mwe.token_indices)
                
                if missing_tokens:
                    print(f"\n⚠️  POTENTIAL ISSUE: Missing tokens in MWE range")
                    print(f"   Token indices: {mwe.token_indices}")
                    print(f"   Expected range: {all_tokens_in_range}")
                    print(f"   Missing: {sorted(missing_tokens)}")
                    
                    print(f"\n   Missing tokens that would be skipped:")
                    for idx in sorted(missing_tokens):
                        token = sentence.tokens[idx]
                        print(f"     Token[{idx}]: '{token.text}' [{token.start}:{token.end}]")
                    
                    print(f"\n❌ THIS COULD CAUSE THE ISSUE:")
                    print(f"   - LLM sees marked text that includes non-MWE tokens")
                    print(f"   - But only MWE tokens get annotated with senses")
                    print(f"   - Non-MWE tokens in the middle remain unannotated")
                else:
                    print(f"\n✅ MWE tokens are continuous (no gaps)")
            
            # Reconstruct what the MWE should look like
            if mwe_tokens:
                # Method 1: Join token texts
                reconstructed = ' '.join(token.text for token in mwe_tokens)
                
                # Method 2: Extract span from original text  
                span_start = min(token.start for token in mwe_tokens)
                span_end = max(token.end for token in mwe_tokens)
                span_text = sentence.text[span_start:span_end]
                
                print(f"\n🔧 RECONSTRUCTION CHECK:")
                print(f"  Method 1 (join tokens): '{reconstructed}'")
                print(f"  Method 2 (text span):   '{span_text}'")
                print(f"  MWE lemma:              '{mwe.lemma}'")
                
                if reconstructed != span_text:
                    print(f"  ❌ MISMATCH: Token join vs text span differ!")
                    print(f"  This indicates gaps or overlaps in token coverage")

def test_process_senses_simulation():
    """Simulate what process_senses_with_chain does with MWEs."""
    
    print(f"\n{'='*80}")
    print("SIMULATING PROCESS_SENSES_WITH_CHAIN")
    print(f"{'='*80}")
    
    # Load test data
    tsv_file = Path("Data/example-mwe.tsv")
    parser = WebAnnoLEXISParser(tsv_file)
    sentences = parser.parse()
    
    # Create dummy sense repository
    dummy_senses = pd.DataFrame({
        'senseID': ['CVMWE-0399', 'CVMWE-0292', 'LLM-0287'],
        'lemma': ['širiti se', 'poboljšavati se', 'u roku od'],
        'definition': ['to spread, expand', 'to improve', 'within the period of']
    })
    
    print("Dummy sense repository:")
    print(dummy_senses)
    
    # Simulate processing for each MWE
    for sent_idx, sentence in enumerate(sentences):
        if not sentence.mwes:
            continue
            
        print(f"\n--- Processing Sentence {sent_idx + 1} ---")
        print(f"Text: {sentence.text}")
        
        for mwe_idx, mwe in enumerate(sentence.mwes):
            print(f"\n  MWE {mwe_idx + 1}: '{mwe.lemma}'")
            
            # This is what process_senses_with_chain does:
            
            # 1. Create marked sentence for LLM
            marked_sentence = mark_mwe(mwe, sentence, "**", "**")
            print(f"  LLM input: {marked_sentence}")
            
            # 2. Get MWE tokens that will receive annotations
            mwe_tokens = get_mwe_tokens(sentence, mwe)
            print(f"  Tokens to annotate ({len(mwe_tokens)}):")
            for i, token in enumerate(mwe_tokens):
                print(f"    {i}: '{token.text}' at position [{token.start}:{token.end}]")
            
            # 3. Check if lemma matches any senses
            matching_senses = dummy_senses[dummy_senses['lemma'] == mwe.lemma]
            if len(matching_senses) > 0:
                print(f"  Found {len(matching_senses)} matching senses")
                print(f"  These tokens would get sense annotations: ✅")
            else:
                print(f"  No matching senses found")
                print(f"  These tokens would get NEW_SENSE: ❌")
            
            print(f"  ---")

if __name__ == "__main__":
    print("🚀 TESTING MWE PROCESSING PIPELINE")
    print("="*50)
    
    test_mwe_token_extraction()
    test_process_senses_simulation()
    
    print(f"\n✅ TEST COMPLETE")
    print("\nTo run this test:")
    print("python test_mwe_processing.py")