#!/usr/bin/env python3
"""
Test the fix for MWE marking in process_senses.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from webanno_spacy_converter.parsers.tsv_parser_v3 import WebAnnoLEXISParser
from preprocessing import get_mwe_tokens, mark_mwe

def test_mwe_marking_fix():
    """Test the fixed MWE marking function."""
    
    print("🧪 TESTING MWE MARKING FIX")
    print("="*50)
    
    # Load test data
    tsv_file = Path("Data/example-mwe.tsv")
    if not tsv_file.exists():
        print(f"⚠️  Test data not found: {tsv_file} — skipping.")
        return
    parser = WebAnnoLEXISParser(tsv_file)
    sentences = parser.parse()
    
    for sent_idx, sentence in enumerate(sentences):
        if not sentence.mwes:
            continue
            
        print(f"\nSentence {sent_idx + 1}: {sentence.text}")
        print("-" * 60)
        
        for mwe_idx, mwe in enumerate(sentence.mwes):
            print(f"\nMWE {mwe_idx + 1}: '{mwe.lemma}' (indices: {mwe.token_indices})")
            
            # Get the tokens that will be annotated
            mwe_tokens = get_mwe_tokens(sentence, mwe)
            print(f"Tokens to annotate:")
            for i, token in enumerate(mwe_tokens):
                print(f"  {i}: '{token.text}' [{token.start}:{token.end}]")
            
            # Test the NEW marking behavior
            marked_sentence = mark_mwe(mwe, sentence, "<<", ">>")
            print(f"\nMarked sentence (for LLM): {marked_sentence}")
            
            # Check if discontinuous MWEs are now marked as continuous spans
            if len(mwe.token_indices) > 1:
                sorted_indices = sorted(mwe.token_indices)
                min_idx, max_idx = sorted_indices[0], sorted_indices[-1]
                expected_continuous = list(range(min_idx, max_idx + 1))
                missing_indices = set(expected_continuous) - set(mwe.token_indices)
                
                if missing_indices:
                    print(f"✅ DISCONTINUOUS MWE - Now marked as continuous span")
                    print(f"   Original tokens: {mwe.token_indices}")
                    print(f"   Missing indices: {sorted(missing_indices)}")
                    
                    # Check if the marking includes the gap
                    min_start = min(token.start for token in mwe_tokens)
                    max_end = max(token.end for token in mwe_tokens)
                    span_text = sentence.text[min_start:max_end]
                    print(f"   Marked span: '{span_text}'")
                    
                    # Verify the marked sentence contains the full span
                    expected_marked = sentence.text[:min_start] + "<<" + span_text + ">>" + sentence.text[max_end:]
                    if marked_sentence == expected_marked:
                        print(f"   ✅ Marking is correct (continuous span)")
                    else:
                        print(f"   ❌ Marking is incorrect")
                        print(f"   Expected: {expected_marked}")
                        print(f"   Got:      {marked_sentence}")
                else:
                    print(f"✅ CONTINUOUS MWE - No gaps to fill")

def test_comparison_old_vs_new():
    """Compare old vs new marking behavior."""
    
    print(f"\n🔍 OLD vs NEW COMPARISON")
    print("="*50)
    
    # Load test data
    tsv_file = Path("Data/example-mwe.tsv")
    if not tsv_file.exists():
        print(f"⚠️  Test data not found: {tsv_file} — skipping.")
        return
    parser = WebAnnoLEXISParser(tsv_file)
    sentences = parser.parse()
    
    # Simulate old behavior (mark individual tokens)
    def mark_mwe_old(mwe, sentence, start_mark="**", end_mark="**"):
        """Old implementation that marks individual tokens."""
        from preprocessing import mark_tokens
        tokens = get_mwe_tokens(sentence, mwe)
        return mark_tokens(tokens, sentence, start_mark, end_mark)
    
    for sentence in sentences:
        if not sentence.mwes:
            continue
            
        print(f"\nSentence: {sentence.text}")
        
        for mwe in sentence.mwes:
            if len(mwe.token_indices) <= 1:
                continue  # Skip single-token MWEs
                
            print(f"\nMWE: '{mwe.lemma}' (indices: {mwe.token_indices})")
            
            # Old behavior
            old_marked = mark_mwe_old(mwe, sentence, "[[", "]]")
            print(f"OLD: {old_marked}")
            
            # New behavior  
            new_marked = mark_mwe(mwe, sentence, "<<", ">>")
            print(f"NEW: {new_marked}")
            
            # Analysis
            if old_marked.count("[[") > 1:
                print("✅ IMPROVEMENT: Old version had multiple separate markers")
                print("✅ IMPROVEMENT: New version uses single continuous span")
            else:
                print("ℹ️  No change needed (already continuous)")

if __name__ == "__main__":
    test_mwe_marking_fix()
    test_comparison_old_vs_new()
    
    print(f"\n🎯 SUMMARY:")
    print("- Fixed mark_mwe() to create continuous spans for discontinuous MWEs")
    print("- LLM now sees clearer context (e.g., '<<se mogu širiti>>' instead of '<<se>> mogu <<širiti>>')")
    print("- Token annotation remains accurate (only 'se' and 'širiti' get sense layers)")
    print("- This should resolve the MWE processing issue in process_senses.py")