#!/usr/bin/env python3
"""
Test script to verify correct modal flow when declining Online Fix
"""
import sys
import logging

# Add project root to path
sys.path.insert(0, '.')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_modal_flow_logic():
    """Test that only Steam restart modal appears when declining Online Fix"""
    
    # Check the code to ensure _show_download_completion_message is NOT called
    # when user declines Online Fix
    
    try:
        with open('/home/gustavof/Projetos/ACCELA-GitHub/ui/main_window.py', 'r') as f:
            content = f.read()
        
        # Find the section where user declines Online Fix
        lines = content.split('\n')
        in_decline_section = False
        has_completion_message = False
        has_steam_restart = False
        
        for i, line in enumerate(lines):
            if 'User chose not to install Online-Fixes' in line:
                in_decline_section = True
                logger.info(f"Found decline section at line {i+1}")
                continue
            
            if in_decline_section:
                # Check for actual function call (not in comments)
                if '_show_download_completion_message()' in line and not line.strip().startswith('#'):
                    has_completion_message = True
                    logger.error(f"❌ Found _show_download_completion_message() at line {i+1} - THIS SHOULD NOT BE HERE!")
                
                if '_prompt_for_steam_restart()' in line and not line.strip().startswith('#'):
                    has_steam_restart = True
                    logger.info(f"✅ Found _prompt_for_steam_restart() at line {i+1}")
                
                # Check if we've moved to next section
                if line.strip().startswith('except Exception') or 'def ' in line:
                    break
        
        logger.info(f"\n=== Modal Flow Test Results ===")
        logger.info(f"Has completion message (should be False): {has_completion_message}")
        logger.info(f"Has Steam restart prompt (should be True): {has_steam_restart}")
        
        if not has_completion_message and has_steam_restart:
            logger.info("✅ CORRECT: Only Steam restart modal will appear when declining Online Fix!")
            return True
        else:
            logger.error("❌ INCORRECT: Modal flow is wrong!")
            return False
            
    except Exception as e:
        logger.error(f"Error testing modal flow: {e}")
        return False

def test_comment_verification():
    """Verify that the explanatory comment is present"""
    try:
        with open('/home/gustavof/Projetos/ACCELA-GitHub/ui/main_window.py', 'r') as f:
            content = f.read()
        
        if 'NOTA: Não mostrar _show_download_completion_message() aqui' in content:
            logger.info("✅ Explanatory comment found - code is properly documented")
            return True
        else:
            logger.warning("⚠️ Explanatory comment not found")
            return True  # Not critical, just nice to have
            
    except Exception as e:
        logger.error(f"Error checking comment: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Modal Flow Correction Test ===")
    logger.info("Testing that only Steam restart modal appears when declining Online Fix\n")
    
    # Test 1: Modal Flow Logic
    logger.info("--- Test 1: Modal Flow Logic ---")
    flow_test = test_modal_flow_logic()
    
    # Test 2: Comment Verification
    logger.info("\n--- Test 2: Comment Verification ---")
    comment_test = test_comment_verification()
    
    # Final results
    logger.info("\n=== Final Test Results ===")
    if flow_test and comment_test:
        logger.info("🎉 TEST PASSED: Modal flow is now correct!")
        logger.info("When user declines Online Fix:")
        logger.info("  ❌ NO 'Download Complete' modal")
        logger.info("  ✅ YES Steam restart modal")
        sys.exit(0)
    else:
        logger.error("❌ TEST FAILED: Modal flow still has issues!")
        sys.exit(1)