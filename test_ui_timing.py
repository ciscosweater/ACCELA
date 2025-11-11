#!/usr/bin/env python3
"""
Test script to verify UI reset timing is reasonable
"""
import sys
import logging

# Add project root to path
sys.path.insert(0, '.')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_ui_reset_timing():
    """Test that UI reset timing is reasonable"""
    
    try:
        with open('/home/gustavof/Projetos/ACCELA-GitHub/ui/main_window.py', 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Find all QTimer.singleShot calls related to UI reset
        ui_timers = []
        
        for i, line in enumerate(lines):
            if 'QTimer.singleShot' in line and 'self._' in line:
                # Extract the time value
                import re
                match = re.search(r'QTimer\.singleShot\((\d+)', line)
                if match:
                    time_ms = int(match.group(1))
                    time_sec = time_ms / 1000
                    
                    # Determine what this timer does
                    context_start = max(0, i - 2)
                    context_end = min(len(lines), i + 2)
                    context = '\n'.join(lines[context_start:context_end])
                    
                    if '_hide_download_controls' in line:
                        purpose = "Hide download controls"
                    elif '_safe_reset_ui_state' in line:
                        purpose = "Reset UI state"
                    elif '_show_download_completion_message' in line:
                        purpose = "Show completion message"
                    else:
                        purpose = "Other UI operation"
                    
                    ui_timers.append({
                        'line': i + 1,
                        'time_ms': time_ms,
                        'time_sec': time_sec,
                        'purpose': purpose,
                        'code': line.strip()
                    })
        
        logger.info("=== UI Reset Timing Analysis ===")
        
        # Check specific timers we care about
        hide_controls_time = None
        reset_ui_time = None
        
        for timer in ui_timers:
            logger.info(f"Line {timer['line']}: {timer['purpose']} - {timer['time_sec']:.1f}s")
            
            if timer['purpose'] == "Hide download controls":
                hide_controls_time = timer['time_sec']
            elif timer['purpose'] == "Reset UI state":
                reset_ui_time = timer['time_sec']
        
        logger.info(f"\n=== Timing Evaluation ===")
        logger.info(f"Hide controls delay: {hide_controls_time}s (should be 1-3s)")
        logger.info(f"Reset UI delay: {reset_ui_time}s (should be 3-8s)")
        
        # Evaluate timing
        timing_good = True
        
        if hide_controls_time and (hide_controls_time < 1 or hide_controls_time > 5):
            logger.warning(f"⚠️ Hide controls timing may be too fast/slow: {hide_controls_time}s")
            timing_good = False
        elif hide_controls_time:
            logger.info(f"✅ Hide controls timing is good: {hide_controls_time}s")
        
        if reset_ui_time and (reset_ui_time < 2 or reset_ui_time > 10):
            logger.warning(f"⚠️ Reset UI timing may be too fast/slow: {reset_ui_time}s")
            timing_good = False
        elif reset_ui_time:
            logger.info(f"✅ Reset UI timing is good: {reset_ui_time}s")
        
        # Specific check for the problematic 15 second timer
        if reset_ui_time and reset_ui_time > 12:
            logger.error(f"❌ Found problematic long timer: {reset_ui_time}s (was probably 15s before)")
            timing_good = False
        elif reset_ui_time and reset_ui_time <= 8:
            logger.info(f"✅ Timer is reasonable (not the old 15s problem)")
        
        return timing_good
        
    except Exception as e:
        logger.error(f"Error testing UI timing: {e}")
        return False

def test_expected_timing():
    """Show what the expected timing should be"""
    logger.info("=== Expected UI Timing ===")
    logger.info("1. Hide download controls: 2-3 seconds (reasonable)")
    logger.info("2. Reset UI state: 4-6 seconds (reasonable)")
    logger.info("3. Total delay before UI reset: ~5-8 seconds (good UX)")
    logger.info("")
    logger.info("❌ BAD: 15 seconds for UI reset (too slow)")
    logger.info("✅ GOOD: 5 seconds for UI reset (responsive)")

if __name__ == "__main__":
    logger.info("=== UI Reset Timing Test ===")
    logger.info("Testing that UI reset timing is reasonable\n")
    
    # Show expected timing
    test_expected_timing()
    
    logger.info("\n" + "="*50)
    
    # Test actual timing
    logger.info("--- Testing Actual Timing ---")
    timing_ok = test_ui_reset_timing()
    
    # Final result
    logger.info("\n=== Final Result ===")
    if timing_ok:
        logger.info("🎉 UI TIMING IS GOOD!")
        logger.info("Interface will reset quickly after download completion!")
        sys.exit(0)
    else:
        logger.error("❌ UI TIMING HAS ISSUES!")
        logger.error("Interface may be too slow to reset!")
        sys.exit(1)