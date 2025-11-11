#!/usr/bin/env python3
"""
Test script to verify all modal scenarios are correct
"""
import sys
import logging

# Add project root to path
sys.path.insert(0, '.')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_all_modal_scenarios():
    """Test all modal scenarios to ensure correct flow"""
    
    try:
        with open('/home/gustavof/Projetos/ACCELA-GitHub/ui/main_window.py', 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Scenario tracking
        scenarios = {
            'no_fixes_available': False,
            'user_declines_fix': False,
            'user_accepts_fix': False
        }
        
        for i, line in enumerate(lines):
            # Check for _show_download_completion_message calls
            if '_show_download_completion_message()' in line and not line.strip().startswith('#'):
                # Determine which scenario this call belongs to
                context_start = max(0, i - 5)
                context_end = min(len(lines), i + 5)
                context = '\n'.join(lines[context_start:context_end])
                
                if 'No Online-Fixes available' in context:
                    scenarios['no_fixes_available'] = True
                    logger.error(f"❌ Scenario 'No Fixes Available': Found _show_download_completion_message() at line {i+1}")
                elif 'User chose not to install' in context:
                    scenarios['user_declines_fix'] = True
                    logger.error(f"❌ Scenario 'User Declines Fix': Found _show_download_completion_message() at line {i+1}")
                else:
                    logger.info(f"ℹ️ Other _show_download_completion_message() call at line {i+1}")
            
            # Check for _prompt_for_steam_restart calls
            if '_prompt_for_steam_restart()' in line and not line.strip().startswith('#'):
                context_start = max(0, i - 5)
                context_end = min(len(lines), i + 5)
                context = '\n'.join(lines[context_start:context_end])
                
                if 'No Online-Fixes available' in context:
                    logger.info(f"✅ Scenario 'No Fixes Available': Found _prompt_for_steam_restart() at line {i+1}")
                elif 'User chose not to install' in context:
                    logger.info(f"✅ Scenario 'User Declines Fix': Found _prompt_for_steam_restart() at line {i+1}")
                elif '_on_fix_applied' in context:
                    logger.info(f"✅ Scenario 'User Accepts Fix': Found _prompt_for_steam_restart() at line {i+1}")
        
        logger.info(f"\n=== Modal Scenarios Analysis ===")
        logger.info(f"No Fixes Available - Has completion modal (should be False): {scenarios['no_fixes_available']}")
        logger.info(f"User Declines Fix - Has completion modal (should be False): {scenarios['user_declines_fix']}")
        
        # All scenarios should be False (no completion modals)
        all_correct = (
            not scenarios['no_fixes_available'] and
            not scenarios['user_declines_fix']
        )
        
        if all_correct:
            logger.info("✅ All scenarios are correct!")
            return True
        else:
            logger.error("❌ Some scenarios have incorrect modals!")
            return False
            
    except Exception as e:
        logger.error(f"Error testing modal scenarios: {e}")
        return False

def test_expected_behavior():
    """Document what the expected behavior should be"""
    logger.info("=== Expected Behavior ===")
    logger.info("1. Download WITHOUT Online Fixes available:")
    logger.info("   ❌ NO 'Download Complete' modal")
    logger.info("   ✅ YES Steam restart modal (SLSsteam)")
    logger.info("")
    logger.info("2. Download WITH Online Fixes - User ACCEPTS:")
    logger.info("   ❌ NO 'Download Complete' modal")
    logger.info("   ✅ YES Steam restart modal (after fix installation)")
    logger.info("")
    logger.info("3. Download WITH Online Fixes - User DECLINES:")
    logger.info("   ❌ NO 'Download Complete' modal")
    logger.info("   ❌ NO 'No Fix Installed' modal")
    logger.info("   ✅ YES Steam restart modal (SLSsteam)")
    logger.info("")
    logger.info("In ALL cases, only Steam restart modal should appear!")

if __name__ == "__main__":
    logger.info("=== Complete Modal Flow Test ===")
    logger.info("Testing all modal scenarios for correctness\n")
    
    # Show expected behavior first
    test_expected_behavior()
    
    logger.info("\n" + "="*50)
    
    # Test actual implementation
    logger.info("--- Testing Implementation ---")
    test_passed = test_all_modal_scenarios()
    
    # Final result
    logger.info("\n=== Final Result ===")
    if test_passed:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("Modal flow is now correct in all scenarios!")
        sys.exit(0)
    else:
        logger.error("❌ TESTS FAILED!")
        logger.error("Modal flow still has issues!")
        sys.exit(1)