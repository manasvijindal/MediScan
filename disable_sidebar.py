import streamlit as st

def disable_sidebar():
    """Completely disable and remove the sidebar."""
    # Inject JavaScript to remove sidebar elements
    st.markdown("""
    <script>
    // Function to completely remove sidebar elements
    function removeSidebarElements() {
        // Remove sidebar elements
        const elements = document.querySelectorAll('[data-testid="stSidebar"], [data-testid="collapsedControl"], button[kind="header"], button[kind="headerNoPadding"]');
        elements.forEach(el => {
            if (el && el.parentNode) {
                el.parentNode.removeChild(el);
            }
        });
        
        // Remove by class names
        const classNames = [
            'st-emotion-cache-h5rgaw', 
            'st-emotion-cache-1egp7i3', 
            'st-emotion-cache-1okhd5e',
            'st-emotion-cache-z5fcl4',
            'st-emotion-cache-1dp5vir',
            'st-emotion-cache-r421ms',
            'st-emotion-cache-10pw50'
        ];
        
        classNames.forEach(className => {
            const elements = document.getElementsByClassName(className);
            while(elements.length > 0) {
                if (elements[0] && elements[0].parentNode) {
                    elements[0].parentNode.removeChild(elements[0]);
                }
            }
        });
    }
    
    // Run immediately
    removeSidebarElements();
    
    // Run again after DOM is fully loaded
    document.addEventListener('DOMContentLoaded', removeSidebarElements);
    
    // Run periodically to catch any dynamically added elements
    setInterval(removeSidebarElements, 50);
    
    // Run when page visibility changes
    document.addEventListener('visibilitychange', removeSidebarElements);
    </script>
    
    <style>
    /* Completely hide sidebar and related elements */
    [data-testid="stSidebar"] {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important; opacity: 0 !important; pointer-events: none !important;}
    [data-testid="collapsedControl"] {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important; opacity: 0 !important; pointer-events: none !important;}
    button[kind="header"] {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important; opacity: 0 !important; pointer-events: none !important;}
    button[kind="headerNoPadding"] {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important; opacity: 0 !important; pointer-events: none !important;}
    
    /* Hide by class names */
    .st-emotion-cache-h5rgaw {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important; opacity: 0 !important; pointer-events: none !important;}
    .st-emotion-cache-1egp7i3 {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important; opacity: 0 !important; pointer-events: none !important;}
    .st-emotion-cache-1okhd5e {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important; opacity: 0 !important; pointer-events: none !important;}
    .st-emotion-cache-z5fcl4 {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important; opacity: 0 !important; pointer-events: none !important;}
    .st-emotion-cache-1dp5vir {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important; opacity: 0 !important; pointer-events: none !important;}
    .st-emotion-cache-r421ms {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important; opacity: 0 !important; pointer-events: none !important;}
    .st-emotion-cache-10pw50 {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important; opacity: 0 !important; pointer-events: none !important;}
    
    /* Ensure main content takes full width */
    .main .block-container {
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
        margin-left: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True) 