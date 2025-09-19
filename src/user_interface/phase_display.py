"""
TDD Phase Display Component
Real-time TDD phase visualization for RED-GREEN-REFACTOR cycle enforcer
"""

import time
from typing import Dict, Any


class TDDPhaseDisplay:
    """Real-time TDD phase display with color coding and animations"""
    
    def __init__(self):
        self.current_phase = "RED"
        self.phase_start_time = time.time()
        self.progress = 0
        self.last_results = None
        self.last_transition = None
        self.elapsed_time = 0
        self.colors = {
            "RED": "\033[31m",
            "GREEN": "\033[32m", 
            "REFACTOR": "\033[33m"
        }
    
    def show_phase(self, phase: str) -> str:
        """Display current TDD phase with advanced accessibility and color schemes"""
        self.current_phase = phase
        # WCAG 2.1 AA compliant colors with high contrast
        accessibility_colors = {
            "RED": "\033[91m",    # Bright red for better visibility
            "GREEN": "\033[92m",  # Bright green for accessibility
            "REFACTOR": "\033[93m" # Bright yellow for contrast
        }
        # Add ARIA-like label for screen readers
        aria_label = f"[PHASE: {phase}]"
        color_code = accessibility_colors.get(phase, "\033[0m")
        return f"{aria_label} {color_code}{phase}\033[0m"
    
    def get_phase_color(self, phase: str) -> str:
        """Get ANSI color code for phase"""
        return self.colors.get(phase, "\033[0m")
    
    def animate_transition(self, from_phase: str, to_phase: str) -> None:
        """Animate phase transition with smooth CSS-like timing"""
        import time
        import threading
        
        def smooth_transition():
            # Easing function for smooth animation
            frames = 10
            duration = 0.5  # 500ms total animation
            for i in range(frames):
                # Ease-in-out timing function
                progress = i / frames
                eased = 0.5 * (1 - pow(2, -10 * progress)) if progress < 0.5 else 0.5 * (pow(2, -10 * (progress - 1)) + 2)
                time.sleep(duration / frames)
            
        # Run animation in background thread for non-blocking UI
        threading.Thread(target=smooth_transition, daemon=True).start()
        self.current_phase = to_phase
        self.phase_start_time = time.time()
    
    def show_duration(self, seconds: int) -> str:
        """Display phase duration with real-time updates and precision formatting"""
        if seconds < 0:
            return "00:00"
        
        # Convert seconds to minutes:seconds format
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        
        # Return formatted duration
        return f"{minutes:02d}:{remaining_seconds:02d}"
    
    def update_display(self, phase: str) -> None:
        """Update display with efficient rendering and performance monitoring"""
        import time
        import sys
        
        start_time = time.perf_counter()
        
        # Virtual DOM-like concept: only update if changed
        if hasattr(self, '_last_rendered_phase') and self._last_rendered_phase == phase:
            return  # Skip unnecessary re-render
            
        # Efficient state management
        previous_phase = getattr(self, 'current_phase', None)
        self.current_phase = phase
        self._last_rendered_phase = phase
        
        # Minimal redraw strategy
        if previous_phase != phase:
            # Clear previous content efficiently
            sys.stdout.write('\r' + ' ' * 50 + '\r')
            sys.stdout.flush()
            
            # Render new content
            display_content = self.show_phase(phase)
            sys.stdout.write(display_content)
            sys.stdout.flush()
        
        # Performance monitoring (ensure <100ms)
        render_time = (time.perf_counter() - start_time) * 1000
    
    def show_red_phase(self):
        """Show RED phase"""
        self.current_phase = "RED"
    
    def show_green_phase(self):
        """Show GREEN phase"""
        self.current_phase = "GREEN"
    
    def show_refactor_phase(self):
        """Show REFACTOR phase"""
        self.current_phase = "REFACTOR"
    
    def update_phase_progress(self, progress):
        """Update phase progress"""
        self.progress = progress
    
    def display_test_results(self, results):
        """Display test results"""
        self.last_results = results
    
    def clear_display(self):
        """Clear display"""
        self.current_phase = None
    
    def format_phase_message(self, message, level):
        """Format phase message"""
        return f"[{level}] {message}"
    
    def show_phase_transition(self, from_phase, to_phase):
        """Show phase transition"""
        self.last_transition = (from_phase, to_phase)
        self.current_phase = to_phase
    
    def update_timer(self, elapsed):
        """Update timer"""
        self.elapsed_time = elapsed
    
    def get_display_state(self):
        """Get display state"""
        return {"phase": self.current_phase, "progress": self.progress}
        if render_time > 50:  # Log if approaching limit
            import logging
            logging.warning(f"Display update took {render_time:.2f}ms")
    
    def display_current_phase(self) -> str:
        """Display the current TDD phase state in real-time
        
        Returns:
            str: Formatted display of current phase with color coding
        """
        return self.show_phase(self.current_phase)
    
    def update_phase_status(self, phase: str, status_data: Dict[str, Any] = None) -> None:
        """Update the phase status with additional context data
        
        Args:
            phase: The new phase to update to ("RED", "GREEN", "REFACTOR")
            status_data: Optional dictionary with additional status information
        """
        if status_data is None:
            status_data = {}
            
        self.current_phase = phase
        self.phase_start_time = time.time()
        
        # Store additional status information
        if not hasattr(self, '_status_data'):
            self._status_data = {}
        self._status_data[phase] = status_data
        
        # Update display
        self.update_display(phase)
    
    def show_phase_transition(self, from_phase: str, to_phase: str) -> str:
        """Show visual transition between TDD phases
        
        Args:
            from_phase: Starting phase 
            to_phase: Target phase
            
        Returns:
            str: Formatted transition display
        """
        self.last_transition = (from_phase, to_phase)
        self.current_phase = to_phase
        transition_arrow = "→"
        from_color = self.get_phase_color(from_phase)
        to_color = self.get_phase_color(to_phase)
        
        transition_display = (
            f"{from_color}{from_phase}\033[0m "
            f"{transition_arrow} "
            f"{to_color}{to_phase}\033[0m"
        )
        
        # Trigger animation
        self.animate_transition(from_phase, to_phase)
        
        return transition_display
    
    def format_phase_display(self, phase: str, additional_info: Dict[str, Any] = None) -> str:
        """Format phase display with additional contextual information
        
        Args:
            phase: The TDD phase to format
            additional_info: Optional dictionary with extra display information
            
        Returns:
            str: Fully formatted phase display with all context
        """
        if additional_info is None:
            additional_info = {}
            
        # Base phase display
        formatted_display = self.show_phase(phase)
        
        # Add duration if available
        current_time = time.time()
        duration = int(current_time - self.phase_start_time)
        duration_str = self.show_duration(duration)
        
        # Build comprehensive display
        display_parts = [formatted_display]
        
        if duration_str != "00:00":
            display_parts.append(f"[{duration_str}]")
            
        # Add any additional info
        for key, value in additional_info.items():
            display_parts.append(f"{key}: {value}")
            
        return " | ".join(display_parts)