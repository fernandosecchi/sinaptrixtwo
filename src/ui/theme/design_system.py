"""
Sinaptrix Design System
A modern, professional design system for the application.
"""

# Color Palette - Modern Tech Company Style
COLORS = {
    # Primary Colors - Professional Blue/Teal
    'primary': '#0891b2',        # Cyan-600 - Main brand color
    'primary_dark': '#0e7490',    # Cyan-700 - Darker shade
    'primary_light': '#06b6d4',   # Cyan-500 - Lighter shade
    'primary_soft': '#ecfeff',    # Cyan-50 - Very light background

    # Secondary Colors - Modern Purple
    'secondary': '#7c3aed',       # Violet-600
    'secondary_dark': '#6d28d9',  # Violet-700
    'secondary_light': '#8b5cf6', # Violet-500
    'secondary_soft': '#f5f3ff',  # Violet-50

    # Accent Colors - Success/Warning/Danger
    'success': '#10b981',         # Emerald-500
    'success_soft': '#ecfdf5',    # Emerald-50
    'warning': '#f59e0b',         # Amber-500
    'warning_soft': '#fffbeb',    # Amber-50
    'danger': '#ef4444',          # Red-500
    'danger_soft': '#fef2f2',     # Red-50

    # Neutral Colors - Grays
    'dark': '#0f172a',            # Slate-900
    'gray_dark': '#334155',       # Slate-700
    'gray': '#64748b',            # Slate-500
    'gray_light': '#94a3b8',      # Slate-400
    'gray_soft': '#f1f5f9',       # Slate-100
    'white': '#ffffff',
    'background': '#f8fafc',      # Slate-50 - Main bg
}

# Typography
TYPOGRAPHY = {
    'font_family': "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    'font_mono': "'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace",

    # Font Sizes
    'text_xs': 'text-xs',         # 12px
    'text_sm': 'text-sm',         # 14px
    'text_base': 'text-base',     # 16px
    'text_lg': 'text-lg',         # 18px
    'text_xl': 'text-xl',         # 20px
    'text_2xl': 'text-2xl',       # 24px
    'text_3xl': 'text-3xl',       # 30px
    'text_4xl': 'text-4xl',       # 36px

    # Font Weights
    'font_normal': 'font-normal',   # 400
    'font_medium': 'font-medium',   # 500
    'font_semibold': 'font-semibold', # 600
    'font_bold': 'font-bold',       # 700
}

# Spacing & Layout
SPACING = {
    'container_max': 'max-w-7xl',
    'card_padding': 'p-6',
    'card_padding_sm': 'p-4',
    'section_gap': 'gap-6',
    'element_gap': 'gap-4',
    'element_gap_sm': 'gap-2',
}

# Component Styles
COMPONENTS = {
    # Cards
    'card': 'bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-200',
    'card_bordered': 'bg-white rounded-xl border-2 border-gray-200',
    'card_elevated': 'bg-white rounded-xl shadow-lg',

    # Buttons
    'btn_primary': 'bg-cyan-600 hover:bg-cyan-700 text-white font-medium rounded-lg px-4 py-2 transition-colors duration-200',
    'btn_secondary': 'bg-violet-600 hover:bg-violet-700 text-white font-medium rounded-lg px-4 py-2 transition-colors duration-200',
    'btn_outline': 'border-2 border-cyan-600 text-cyan-600 hover:bg-cyan-50 font-medium rounded-lg px-4 py-2 transition-colors duration-200',
    'btn_ghost': 'text-gray-700 hover:bg-gray-100 font-medium rounded-lg px-4 py-2 transition-colors duration-200',
    'btn_danger': 'bg-red-500 hover:bg-red-600 text-white font-medium rounded-lg px-4 py-2 transition-colors duration-200',

    # Inputs
    'input': 'border-gray-300 rounded-lg focus:border-cyan-500 focus:ring-cyan-500',
    'input_error': 'border-red-500 rounded-lg focus:border-red-500 focus:ring-red-500',

    # Badges/Chips
    'badge_primary': 'bg-cyan-100 text-cyan-800 rounded-full px-3 py-1 text-sm font-medium',
    'badge_secondary': 'bg-violet-100 text-violet-800 rounded-full px-3 py-1 text-sm font-medium',
    'badge_success': 'bg-emerald-100 text-emerald-800 rounded-full px-3 py-1 text-sm font-medium',
    'badge_warning': 'bg-amber-100 text-amber-800 rounded-full px-3 py-1 text-sm font-medium',
    'badge_danger': 'bg-red-100 text-red-800 rounded-full px-3 py-1 text-sm font-medium',
}

# Navigation Styles
NAVIGATION = {
    'header_bg': 'bg-gradient-to-r from-cyan-600 to-cyan-700',
    'header_height': 'h-16',
    'drawer_bg': 'bg-white',
    'drawer_width': '240px',
    'nav_item': 'text-gray-700 hover:bg-cyan-50 hover:text-cyan-700 rounded-lg px-3 py-2 transition-colors duration-150',
    'nav_item_active': 'bg-cyan-50 text-cyan-700 font-medium rounded-lg px-3 py-2',
}

# Custom CSS for additional styling
CUSTOM_CSS = """
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global styles */
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    min-height: 100vh;
}

/* Smooth animations */
* {
    transition: background-color 0.2s ease, border-color 0.2s ease;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}

/* Card hover effects */
.card-hover {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card-hover:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

/* Button animations */
.btn-scale {
    transition: transform 0.1s ease;
}

.btn-scale:active {
    transform: scale(0.98);
}

/* Modern input focus */
input:focus, textarea:focus, select:focus {
    outline: none;
    ring: 2px;
    ring-color: #0891b2;
    ring-offset: 2px;
}

/* Glass morphism effect */
.glass {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Gradient text */
.gradient-text {
    background: linear-gradient(135deg, #0891b2 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Modern shadows */
.shadow-soft {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
}

.shadow-medium {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
}

.shadow-large {
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
</style>
"""

def get_color_hex(color_name: str) -> str:
    """Get hex color value by name."""
    return COLORS.get(color_name, '#000000')

def apply_custom_styles():
    """Return custom CSS to be injected into the page."""
    return CUSTOM_CSS