import streamlit as st

def show_navigation():
    """Display the top navigation bar."""
    st.markdown("""
        <script>
        // Function to remove sidebar elements
        function removeSidebar() {
            // Find all sidebar elements
            const sidebarElements = document.querySelectorAll('[data-testid="stSidebar"], [data-testid="collapsedControl"], button[kind="header"], button[kind="headerNoPadding"]');
            
            // Remove them from the DOM completely
            sidebarElements.forEach(el => {
                if (el && el.parentNode) {
                    el.parentNode.removeChild(el);
                }
            });
            
            // Also remove by class names
            const sidebarClasses = [
                'st-emotion-cache-h5rgaw', 
                'st-emotion-cache-1egp7i3', 
                'st-emotion-cache-1okhd5e',
                'st-emotion-cache-z5fcl4',
                'st-emotion-cache-1dp5vir',
                'st-emotion-cache-r421ms'
            ];
            
            sidebarClasses.forEach(className => {
                const elements = document.getElementsByClassName(className);
                while(elements.length > 0){
                    if (elements[0] && elements[0].parentNode) {
                        elements[0].parentNode.removeChild(elements[0]);
                    }
                }
            });
        }
        
        // Run immediately
        removeSidebar();
        
        // Run again after DOM is fully loaded
        document.addEventListener('DOMContentLoaded', removeSidebar);
        
        // Run periodically to catch any dynamically added elements
        setInterval(removeSidebar, 100);
        </script>
        
        <style>
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 70px;
            background-color: #52b788;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 999;
            display: flex;
            align-items: center;
            padding: 0 20px;
            justify-content: flex-start;
        }
        .nav-brand {
            font-size: 5px;
            font-weight: bold;
            font-family: 'Gafata', sans-serif;
            color: white !important;
            text-decoration: none !important;
            margin-right: 100px;
        }
        .nav-links {
            display: flex;
            justify-content: flex-start;
            gap: 200px;
            margin-left: 200px;
        }
        .nav-link {
            color: white !important;
            text-decoration: none !important;
            font-size: 15px;
            padding: 8px 20px;
            border-radius: 5px;
            transition: all 0.3s;
            text-align: center;
            font-weight: 500;
        }
        .nav-link:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        .nav-link.active {
            background-color: rgba(255, 255, 255, 0.2);
            
        }
        /* Add padding to content to prevent overlap with fixed navbar */
        .main-content {
            margin-top: 80px;
        }
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] {display: none !important; width: 0 !important;}
        [data-testid="collapsedControl"] {display: none !important; width: 0 !important;}
        footer {visibility: hidden;}
        .stDeployButton {display: none !important;}
        section[data-testid="stSidebar"] {display: none !important; width: 0 !important;}
        button[kind="header"] {display: none !important;}
        .st-emotion-cache-1dp5vir {display: none !important;}
        .st-emotion-cache-79elbk {display: none !important;}
        /* Additional rules to completely remove sidebar */
        .st-emotion-cache-r421ms {display: none !important;}
        .st-emotion-cache-10pw50 {display: none !important;}
        .st-emotion-cache-z5fcl4 {width: 0 !important; margin: 0 !important; padding: 0 !important;}
        div[data-testid="stSidebarNav"] {display: none !important;}
        div[data-testid="stSidebarContent"] {display: none !important;}
        div[data-testid="collapsedControl-container"] {display: none !important;}
        /* Ensure main content takes full width */
        .main .block-container {
            max-width: 100%;
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1rem;
        }
        /* Remove any transitions that might show the sidebar */
        .st-emotion-cache-z5fcl4 {
            transition: none !important;
        }
        .st-emotion-cache-ue6h4q {
            transition: none !important;
        }
        /* Hide all sidebar elements completely */
        [data-testid="collapsedControl"] {display: none !important;}
        section[data-testid="stSidebar"][aria-expanded="true"] {display: none !important;}
        section[data-testid="stSidebar"][aria-expanded="false"] {display: none !important;}
        div[data-testid="stToolbar"] {display: none !important;}
        button[kind="header"] {display: none !important;}
        button[kind="headerNoPadding"] {display: none !important;}
        button[data-testid="baseButton-headerNoPadding"] {display: none !important;}
        
        /* Target the specific arrow button and container */
        div.st-emotion-cache-h5rgaw.ea3mdgi1 {display: none !important;}
        div.st-emotion-cache-1egp7i3.e1nzilvr5 {display: none !important;}
        div.st-emotion-cache-1okhd5e.e1nzilvr5 {display: none !important;}
        
        /* Target all possible sidebar-related classes */
        .st-emotion-cache-h5rgaw {display: none !important;}
        .st-emotion-cache-1egp7i3 {display: none !important;}
        .st-emotion-cache-1okhd5e {display: none !important;}
        .st-emotion-cache-z5fcl4 {width: 0 !important; margin: 0 !important; padding: 0 !important;}
        
        /* Target the arrow icon specifically */
        svg[data-icon="chevron-right"] {display: none !important;}
        svg[data-icon="chevron-left"] {display: none !important;}
        
        /* Hide any element with a chevron icon */
        *:has(> svg[data-icon="chevron-right"]) {display: none !important;}
        *:has(> svg[data-icon="chevron-left"]) {display: none !important;}
        
        /* Aggressive CSS to hide sidebar */
        [data-testid="stSidebar"] {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important;}
        [data-testid="collapsedControl"] {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important;}
        button[kind="header"] {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important;}
        button[kind="headerNoPadding"] {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important;}
        
        /* Hide by class names */
        .st-emotion-cache-h5rgaw {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important;}
        .st-emotion-cache-1egp7i3 {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important;}
        .st-emotion-cache-1okhd5e {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important;}
        .st-emotion-cache-z5fcl4 {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important;}
        .st-emotion-cache-1dp5vir {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important;}
        .st-emotion-cache-r421ms {display: none !important; width: 0 !important; height: 0 !important; position: absolute !important; top: -9999px !important; left: -9999px !important;}
        
        /* Remove underlines from all links globally */
        a {
            text-decoration: none !important;
        }
        a:hover {
            text-decoration: none !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Get current page name
    current_page = st.session_state.get('current_page', '')

    # Create navigation HTML with onclick events that use Streamlit's page navigation
    nav_html = """
    <div class="navbar">
        <a href="/" class="nav-brand" target="_self" style="font-family: 'Gerogia', serif; font-size: 2.5rem;" >MediScan</a>
        <div class="nav-links">
            <a href="/1_Prescription" class="nav-link {rx_active}" target="_self" style="font-family: 'Actor', sans-serif; font-size: 1.5rem; margin: auto 0;">Process Rx</a>
            <a href="/2_Inventory" class="nav-link {mgmt_active}" target="_self" style="font-family: 'Actor', sans-serif; font-size: 1.5rem; margin: auto 0;">Inventory</a>
            <a href="/3_Notifications" class="nav-link {notif_active}" target="_self" style="font-family: 'Actor', sans-serif; font-size: 1.5rem; margin: auto 0;">Notifications</a>
        </div>
    </div>
    <div class="main-content"></div>
    """.format(
        rx_active='active' if current_page == '1_Prescription' else '',
        mgmt_active='active' if current_page == '2_Inventory' else '',
        notif_active='active' if current_page == '3_Notifications' else ''
    )

    st.markdown(nav_html, unsafe_allow_html=True) 