"""
Industry 4.0 Multimodal Transportation Optimization Dashboard - Enhanced Version
Complete Streamlit Application with Interactive Maps and Real Transport Data

Run with: streamlit run enhanced_transport_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Optional
import heapq
import math
import json
import itertools

# Page configuration
st.set_page_config(
    page_title="Industry 4.0 Transport Optimizer Pro",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Source+Sans+3:wght@400;500;600;700&display=swap');

    :root {
        --bg-0: #0b1020;
        --bg-1: #111827;
        --bg-2: #1f2937;
        --card: #111827;
        --card-border: rgba(59, 130, 246, 0.45);
        --text-0: #1d201e;
        --text-1: #364fd0;
        --text-2: #cbd5e1;
        --accent: #22d3ee;
        --accent-2: #f97316;
    }

    html, body, [class*="css"]  {
        font-family: "Source Sans 3", system-ui, -apple-system, sans-serif;
        color: var(--text-0);
    }

    h1, h2, h3, h4, h5, h6, .stMetric label {
        font-family: "Space Grotesk", system-ui, -apple-system, sans-serif;
        letter-spacing: 0.2px;
    }

    .main {
        background: radial-gradient(1200px 800px at 10% -10%, rgba(34, 211, 238, 0.12), transparent 60%),
                    radial-gradient(900px 700px at 90% 10%, rgba(249, 115, 22, 0.12), transparent 60%),
                    linear-gradient(180deg, #0b1020 0%, #0f172a 100%);
        color: var(--text-0);
    }
    
    /* Metrics styling */
    .stMetric {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid var(--accent);
        box-shadow: 0 4px 10px rgba(15, 23, 42, 0.12);
    }
    .stMetric label {
        color: #0b1020 !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #0b1020 !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #10b981 !important;
        font-weight: 700 !important;
    }
    
    /* Preference badges */
    .preference-badge {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 800;
        font-size: 1rem;
        margin: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        color: #5541b2!important;
    }
    .very-low { background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); }
    .low { background: linear-gradient(135deg, #f97316 0%, #c2410c 100%); }
    .neutral { background: linear-gradient(135deg, #eab308 0%, #a16207 100%); }
    .high { background: linear-gradient(135deg, #22c55e 0%, #15803d 100%); }
    .very-high { background: linear-gradient(135deg, #10b981 0%, #047857 100%); }
    
    /* Transport mode cards */
    .transport-mode {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: 700;
        color: #ffffff !important;
        font-size: 1.05rem;
    }
    .mode-road { 
        border-left: 5px solid #FF6B35; 
        background: linear-gradient(90deg, rgba(255, 107, 53, 0.3) 0%, rgba(45, 50, 80, 0.8) 100%);
    }
    .mode-rail { 
        border-left: 5px solid #3B82F6; 
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.3) 0%, rgba(45, 50, 80, 0.8) 100%);
    }
    .mode-air { 
        border-left: 5px solid #F59E0B; 
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.3) 0%, rgba(45, 50, 80, 0.8) 100%);
    }
    .mode-sea { 
        border-left: 5px solid #06B6D4; 
        background: linear-gradient(90deg, rgba(6, 182, 212, 0.3) 0%, rgba(45, 50, 80, 0.8) 100%);
    }
    
    /* Route cards */
    .route-card {
        background: linear-gradient(135deg, #e2e8f0 0%, #f8fafc 100%);
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #0ea5e9;
        margin: 15px 0;
        box-shadow: 0 4px 10px rgba(15, 23, 42, 0.12);
        color: #0b1020 !important;
    }
    .route-card h3, .route-card h4 {
        color: #0f172a !important;
        font-size: 1.25rem;
    }
    .route-card p, .route-card li {
        color: #0f172a !important;
        font-size: 1.05rem;
        font-weight: 600;
    }
    .route-card strong {
        color: #0b1020 !important;
    }
    
    /* Segment boxes */
    .segment-box {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid var(--accent);
        margin: 12px 0;
        color: #0b1020 !important;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.12);
    }
    .segment-box h4 {
        color: #0f172a !important;
        margin-bottom: 10px;
        font-size: 1.3rem;
        font-weight: 800;
    }
    .segment-box p {
        color: #0f172a !important;
        margin: 8px 0;
        font-size: 1.05rem;
        font-weight: 600;
    }
    .segment-box strong {
        color: #0b1020 !important;
    }
    
    /* Station info */
    .station-info {
        background: linear-gradient(135deg, #ecfeff 0%, #cffafe 100%);
        padding: 15px;
        border-radius: 8px;
        border: 2px solid rgba(14, 165, 233, 0.35);
        margin: 10px 0;
        font-size: 1rem;
        color: #0b1020 !important;
        font-weight: 700;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 { 
        color: var(--text-0) !important;
        font-weight: 800 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #f1f5f9;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #e2e8f0;
        border-radius: 8px;
        color: #0f172a !important;
        padding: 8px 14px;
        font-weight: 700;
        font-size: 0.95rem;
        border: 2px solid transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #cbd5e1;
        color: #0b1020 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #0b1020 !important;
        border: 2px solid #94a3b8 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    }
    
    /* Labels and text */
    .stSelectbox label, .stSlider label, label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: #ffffff !important;
        font-weight: 800;
        font-size: 1.1rem;
        border: none;
        border-radius: 10px;
        padding: 15px 30px;
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4);
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        box-shadow: 0 6px 16px rgba(249, 115, 22, 0.6);
        transform: translateY(-2px);
    }
    
    /* Expander */
    .stExpander {
        background: #f8fafc;
        border: 2px solid rgba(148, 163, 184, 0.4);
        border-radius: 10px;
    }
    .stExpander label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    
    /* DataFrames */
    .stDataFrame {
        background: rgba(45, 50, 80, 0.9);
    }
    .stDataFrame thead tr th {
        background: #0ea5e9 !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
    }
    .stDataFrame tbody tr td {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0992C2 0%, #63B7D1 100%);
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] li {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }
    
   
    
    /* Success/Warning boxes */
    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(45, 50, 80, 0.9) 100%);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid rgba(16, 185, 129, 0.6);
        margin: 15px 0;
        color: #ffffff !important;
    }
    .success-box h3, .success-box h4 {
        color: #10b981 !important;
    }
    .success-box p, .success-box li {
        color: #e5e7eb !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(45, 50, 80, 0.9) 100%);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid rgba(249, 115, 22, 0.6);
        margin: 15px 0;
        color: #ffffff !important;
    }
    .warning-box h3, .warning-box h4 {
        color: #f97316 !important;
    }
    .warning-box p {
        color: #e5e7eb !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }
    
    .info-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(45, 50, 80, 0.9) 100%);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid rgba(59, 130, 246, 0.6);
        margin: 15px 0;
        color: #ffffff !important;
    }
    .info-box h4 {
        color: #3b82f6 !important;
        margin-bottom: 10px;
    }
    .info-box p, .info-box li {
        color: #e5e7eb !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }
    
    /* Override all paragraph and text colors */
    p, span, div, li {
        color: var(--text-1) !important;
    }
    
    strong {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    
    /* Make sure all text is readable */
    .stMarkdown, .stText {
        color: var(--text-0) !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }
    .stMarkdown p, .stMarkdown li {
        color: var(--text-1) !important;
        font-size: 1.05rem !important;
        line-height: 1.65 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: var(--text-0) !important;
    }

    /* Force labels and sidebar text visibility */
    label, .stSelectbox label, .stSlider label, .stRadio label, .stMultiSelect label {
        color: var(--text-0) !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--text-1) !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--text-0) !important;
    }

    /* Inputs and selectboxes */
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #0b1020 !important;
        border-color: rgba(148, 163, 184, 0.5) !important;
    }
    [data-baseweb="select"] span,
    [data-baseweb="select"] div[role="option"],
    [data-baseweb="select"] div[role="listbox"],
    [data-baseweb="select"] div[role="listbox"] * {
        color: #0b1020 !important;
        font-weight: 600;
    }
    [data-baseweb="select"] input {
        color: #0b1020 !important;
        font-weight: 600;
    }
    [data-baseweb="select"] div[role="listbox"] {
        background: #ffffff !important;
        color: #0b1020 !important;
    }
    [data-baseweb="option"] {
        color: #0b1020 !important;
        font-weight: 600;
    }
    [data-baseweb="option"]:hover {
        background: rgba(59, 130, 246, 0.1) !important;
    }

    /* Slider styling */
    [data-testid="stSlider"] div[role="slider"] {
        background-color: #0ea5e9 !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class TransportMode(Enum):
    """Transport mode enumeration"""
    ROAD = "road"
    RAIL = "rail"
    AIR = "air"
    SEA = "sea"


class PreferenceLevel(Enum):
    """Optimization preference levels"""
    VERY_LOW = ("Very Low", 10)
    LOW = ("Low", 30)
    NEUTRAL = ("Neutral", 50)
    HIGH = ("High", 70)
    VERY_HIGH = ("Very High", 90)
    
    @property
    def label(self):
        return self.value[0]
    
    @property
    def weight(self):
        return self.value[1]


@dataclass
class Location:
    """Represents a geographic location with transport infrastructure"""
    name: str
    latitude: float
    longitude: float
    location_type: str
    has_railway_station: bool = False
    has_airport: bool = False
    has_seaport: bool = False
    railway_station_name: str = ""
    airport_code: str = ""
    seaport_name: str = ""
    
    def distance_to(self, other: 'Location') -> float:
        """Calculate haversine distance to another location (in km)"""
        R = 6371
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c


@dataclass
class RouteSegment:
    """Represents a single segment of a route"""
    mode: TransportMode
    origin: Location
    destination: Location
    distance: float
    duration: float
    cost: float
    emissions: float
    reliability: float
    station_info: str = ""
    
    def __post_init__(self):
        if self.distance == 0:
            self.distance = self.origin.distance_to(self.destination)


@dataclass
class Route:
    """Represents a complete multimodal route"""
    segments: List[RouteSegment]
    total_cost: float
    total_time: float
    total_distance: float
    total_emissions: float
    average_reliability: float
    route_name: str
    optimization_score: float
    mode_percentages: Dict[str, float] = None
    carbon_cost: float = 0.0
    adjusted_total_cost: float = 0.0
    sla_penalty: float = 0.0
    final_total_cost: float = 0.0
    
    def __post_init__(self):
        if self.mode_percentages is None:
            self.calculate_mode_percentages()
    
    def calculate_mode_percentages(self):
        """Calculate percentage of distance covered by each mode"""
        mode_distances = {}
        for segment in self.segments:
            mode = segment.mode.value
            mode_distances[mode] = mode_distances.get(mode, 0) + segment.distance
        
        total_distance = sum(mode_distances.values())
        self.mode_percentages = {
            mode: (dist / total_distance * 100) if total_distance > 0 else 0
            for mode, dist in mode_distances.items()
        }


# ============================================================================
# INDIAN CITIES WITH COMPLETE TRANSPORT INFRASTRUCTURE
# ============================================================================

INDIAN_CITIES_ENHANCED = {
    # Format: (lat, lon, has_railway, has_airport, has_seaport, railway_name, airport_code, seaport_name)
    
    # Major Metros with Full Infrastructure
    "Mumbai, Maharashtra": (19.0760, 72.8777, True, True, True, "Mumbai Central/CSMT", "BOM", "Jawaharlal Nehru Port (JNPT)"),
    "Delhi": (28.7041, 77.1025, True, True, False, "New Delhi Railway Station", "DEL", ""),
    "Bengaluru, Karnataka": (12.9716, 77.5946, True, True, False, "Bengaluru City Junction", "BLR", ""),
    "Kolkata, West Bengal": (22.5726, 88.3639, True, True, True, "Howrah Junction", "CCU", "Kolkata Port"),
    "Chennai, Tamil Nadu": (13.0827, 80.2707, True, True, True, "Chennai Central", "MAA", "Chennai Port"),
    "Hyderabad, Telangana": (17.3850, 78.4867, True, True, False, "Hyderabad Deccan", "HYD", ""),
    
    # Tier 1 Cities
    "Pune, Maharashtra": (18.5204, 73.8567, True, True, False, "Pune Junction", "PNQ", ""),
    "Ahmedabad, Gujarat": (23.0225, 72.5714, True, True, False, "Ahmedabad Junction", "AMD", ""),
    "Jaipur, Rajasthan": (26.9124, 75.7873, True, True, False, "Jaipur Junction", "JAI", ""),
    "Surat, Gujarat": (21.1702, 72.8311, True, True, True, "Surat Railway Station", "STV", "Surat Port (Magdalla)"),
    "Lucknow, Uttar Pradesh": (26.8467, 80.9462, True, True, False, "Lucknow Charbagh", "LKO", ""),
    "Kanpur, Uttar Pradesh": (26.4499, 80.3319, True, False, False, "Kanpur Central", "", ""),
    "Nagpur, Maharashtra": (21.1458, 79.0882, True, True, False, "Nagpur Junction", "NAG", ""),
    "Visakhapatnam, Andhra Pradesh": (17.6869, 83.2185, True, True, True, "Visakhapatnam Junction", "VTZ", "Visakhapatnam Port"),
    "Indore, Madhya Pradesh": (22.7196, 75.8577, True, True, False, "Indore Junction", "IDR", ""),
    "Patna, Bihar": (25.5941, 85.1376, True, True, False, "Patna Junction", "PAT", ""),
    "Bhopal, Madhya Pradesh": (23.2599, 77.4126, True, True, False, "Bhopal Junction", "BHO", ""),
    "Vadodara, Gujarat": (22.3072, 73.1812, True, True, False, "Vadodara Junction", "BDQ", ""),
    "Ludhiana, Punjab": (30.9010, 75.8573, True, False, False, "Ludhiana Junction", "", ""),
    "Agra, Uttar Pradesh": (27.1767, 78.0081, True, True, False, "Agra Cantt", "AGR", ""),
    "Nashik, Maharashtra": (19.9975, 73.7898, True, False, False, "Nashik Road", "", ""),
    "Ranchi, Jharkhand": (23.3441, 85.3096, True, True, False, "Ranchi Junction", "IXR", ""),
    "Rajkot, Gujarat": (22.3039, 70.8022, True, True, False, "Rajkot Junction", "RAJ", ""),
    "Varanasi, Uttar Pradesh": (25.3176, 82.9739, True, True, False, "Varanasi Junction", "VNS", ""),
    "Amritsar, Punjab": (31.6340, 74.8723, True, True, False, "Amritsar Junction", "ATQ", ""),
    "Aurangabad, Maharashtra": (19.8762, 75.3433, True, True, False, "Aurangabad Railway Station", "IXU", ""),
    "Guwahati, Assam": (26.1445, 91.7362, True, True, False, "Guwahati Railway Station", "GAU", ""),
    "Chandigarh": (30.7333, 76.7794, True, True, False, "Chandigarh Railway Station", "IXC", ""),
    "Kochi, Kerala": (9.9312, 76.2673, True, True, True, "Ernakulam Junction", "COK", "Cochin Port"),
    "Coimbatore, Tamil Nadu": (11.0168, 76.9558, True, True, False, "Coimbatore Junction", "CJB", ""),
    "Thiruvananthapuram, Kerala": (8.5241, 76.9366, True, True, True, "Trivandrum Central", "TRV", "Vizhinjam Port"),
    "Goa (Vasco)": (15.3983, 73.8318, True, True, True, "Vasco-da-Gama Railway Station", "GOI", "Mormugao Port"),
    "Mangalore, Karnataka": (12.9141, 74.8560, True, True, True, "Mangalore Central", "IXE", "New Mangalore Port"),
    "Bhubaneswar, Odisha": (20.2961, 85.8245, True, True, False, "Bhubaneswar Railway Station", "BBI", ""),
    "Vijayawada, Andhra Pradesh": (16.5062, 80.6480, True, True, False, "Vijayawada Junction", "VGA", ""),
    "Madurai, Tamil Nadu": (9.9252, 78.1198, True, True, False, "Madurai Junction", "IXM", ""),
    "Jodhpur, Rajasthan": (26.2389, 73.0243, True, True, False, "Jodhpur Junction", "JDH", ""),
    "Raipur, Chhattisgarh": (21.2514, 81.6296, True, True, False, "Raipur Junction", "RPR", ""),
    "Kota, Rajasthan": (25.2138, 75.8648, True, False, False, "Kota Junction", "", ""),
    "Srinagar, Jammu and Kashmir": (34.0837, 74.7973, True, True, False, "Srinagar Railway Station", "SXR", ""),
}


# ============================================================================
# TRANSPORTATION NETWORK
# ============================================================================

class TransportationNetwork:
    """Enhanced transportation network with infrastructure details"""
    
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.connections: Dict[Tuple[str, str, TransportMode], RouteSegment] = {}
        
    def add_location(self, location: Location):
        self.locations[location.name] = location
        
    def add_connection(self, segment: RouteSegment):
        key = (segment.origin.name, segment.destination.name, segment.mode)
        self.connections[key] = segment
        
        reverse_key = (segment.destination.name, segment.origin.name, segment.mode)
        reverse_segment = RouteSegment(
            mode=segment.mode,
            origin=segment.destination,
            destination=segment.origin,
            distance=segment.distance,
            duration=segment.duration,
            cost=segment.cost,
            emissions=segment.emissions,
            reliability=segment.reliability,
            station_info=segment.station_info
        )
        self.connections[reverse_key] = reverse_segment
        
    def get_neighbors(self, location_name: str) -> List[Tuple[str, TransportMode, RouteSegment]]:
        neighbors = []
        for (origin, dest, mode), segment in self.connections.items():
            if origin == location_name:
                neighbors.append((dest, mode, segment))
        return neighbors


# ============================================================================
# MULTIMODAL OPTIMIZER
# ============================================================================

class MultimodalOptimizer:
    """Enhanced AI-powered multimodal transportation optimizer"""
    
    def __init__(self, network: TransportationNetwork):
        self.network = network
        self.cost_weight = 0.33
        self.time_weight = 0.33
        self.emissions_weight = 0.34
        self.reliability_weight = 0.12
        # Typical per-km references for normalization (INR/km, hr/km, kg/km)
        self.cost_ref = {
            TransportMode.ROAD: 150,
            TransportMode.RAIL: 80,
            TransportMode.AIR: 550,
            TransportMode.SEA: 35
        }
        self.time_ref = {
            TransportMode.ROAD: 1 / 65,
            TransportMode.RAIL: 1 / 55,
            TransportMode.AIR: 1 / 750,
            TransportMode.SEA: 1 / 22
        }
        self.emissions_ref = {
            TransportMode.ROAD: 0.35,
            TransportMode.RAIL: 0.09,
            TransportMode.AIR: 1.4,
            TransportMode.SEA: 0.06
        }
        
    def set_optimization_preferences(self, cost_pref: PreferenceLevel, 
                                    time_pref: PreferenceLevel, 
                                    eco_pref: PreferenceLevel):
        """Set optimization preferences using categorical levels"""
        total = cost_pref.weight + time_pref.weight + eco_pref.weight
        base_scale = 0.9
        self.cost_weight = base_scale * (cost_pref.weight / total)
        self.time_weight = base_scale * (time_pref.weight / total)
        self.emissions_weight = base_scale * (eco_pref.weight / total)
        self.reliability_weight = 0.1
        
    def calculate_segment_score(self, segment: RouteSegment, objective: str) -> float:
        if objective == "cost":
            return segment.cost
        elif objective == "time":
            return segment.duration
        elif objective == "emissions":
            return segment.emissions
        else:  # balanced
            distance = max(segment.distance, 1)
            cost_per_km = segment.cost / distance
            time_per_km = segment.duration / distance
            emissions_per_km = segment.emissions / distance

            cost_norm = cost_per_km / self.cost_ref.get(segment.mode, 150)
            time_norm = time_per_km / self.time_ref.get(segment.mode, 1 / 65)
            emissions_norm = emissions_per_km / self.emissions_ref.get(segment.mode, 0.35)
            reliability_penalty = (100 - segment.reliability) / 100
            
            return (
                self.cost_weight * cost_norm +
                self.time_weight * time_norm +
                self.emissions_weight * emissions_norm +
                self.reliability_weight * reliability_penalty
            )

    def build_route_from_segments(self, segments: List[RouteSegment], route_name: str, score: float) -> Route:
        total_cost = sum(s.cost for s in segments)
        total_time = sum(s.duration for s in segments)
        total_distance = sum(s.distance for s in segments)
        total_emissions = sum(s.emissions for s in segments)
        avg_reliability = float(np.mean([s.reliability for s in segments])) if segments else 0.0
        return Route(
            segments=segments,
            total_cost=total_cost,
            total_time=total_time,
            total_distance=total_distance,
            total_emissions=total_emissions,
            average_reliability=avg_reliability,
            route_name=route_name,
            optimization_score=score
        )

    def score_route(self, route: Route, objective: str) -> float:
        if objective == "cost":
            return route.total_cost
        if objective == "time":
            return route.total_time
        if objective == "emissions":
            return route.total_emissions
        # balanced
        score = 0.0
        last_mode = None
        for seg in route.segments:
            score += self.calculate_segment_score(seg, "balanced")
            if last_mode and last_mode != seg.mode:
                score += 0.05
            last_mode = seg.mode
        return score

    def generate_routes(self, origin: str, destination: str, max_segments: int = 4) -> List[Route]:
        routes: List[Route] = []

        def dfs(current: str, segments: List[RouteSegment], visited_nodes: set):
            if len(segments) > max_segments:
                return
            if current == destination and segments:
                tmp_route = self.build_route_from_segments(segments, "candidate", 0.0)
                routes.append(tmp_route)
                return
            for neighbor, mode, segment in self.network.get_neighbors(current):
                if neighbor in visited_nodes:
                    continue
                dfs(neighbor, segments + [segment], visited_nodes | {neighbor})

        dfs(origin, [], {origin})
        return routes
    
    def dijkstra_multimodal(self, origin: str, destination: str, objective: str) -> Optional[Route]:
        counter = itertools.count()
        pq = [(0, next(counter), origin, [], 0, 0, 0, 0, [])]
        visited = set()
        
        while pq:
            score, _tie, current, path, total_cost, total_time, total_emissions, total_distance, segments = heapq.heappop(pq)
            
            last_mode = segments[-1].mode if segments else None
            state = (current, last_mode)
            
            if state in visited:
                continue
                
            visited.add(state)
            
            if current == destination:
                avg_reliability = np.mean([seg.reliability for seg in segments]) if segments else 0
                route = Route(
                    segments=segments,
                    total_cost=total_cost,
                    total_time=total_time,
                    total_distance=total_distance,
                    total_emissions=total_emissions,
                    average_reliability=avg_reliability,
                    route_name=f"{objective}_route",
                    optimization_score=score
                )
                return route
            
            for neighbor, mode, segment in self.network.get_neighbors(current):
                if (neighbor, mode) not in visited:
                    new_cost = total_cost + segment.cost
                    new_time = total_time + segment.duration
                    new_emissions = total_emissions + segment.emissions
                    new_distance = total_distance + segment.distance
                    new_segments = segments + [segment]
                    
                    mode_change_penalty = 0
                    if last_mode and last_mode != mode:
                        mode_change_penalty = 2
                        new_time += mode_change_penalty
                    new_score = score + self.calculate_segment_score(segment, objective)
                    if last_mode and last_mode != mode and objective == "balanced":
                        new_score += 0.05
                    
                    heapq.heappush(pq, (
                        new_score, next(counter), neighbor, path + [current],
                        new_cost, new_time, new_emissions,
                        new_distance, new_segments
                    ))
        
        return None
    
    def find_optimal_routes(self, origin: str, destination: str) -> Dict[str, Route]:
        results: Dict[str, Route] = {}
        candidates = self.generate_routes(origin, destination, max_segments=4)

        def is_multimodal(route: Route) -> bool:
            return len({s.mode for s in route.segments}) >= 2

        def route_signature(route: Route) -> Tuple:
            return tuple((s.mode.value, s.origin.name, s.destination.name) for s in route.segments)

        multimodal_candidates = [r for r in candidates if is_multimodal(r)]
        pool = multimodal_candidates if multimodal_candidates else candidates

        if not pool:
            return results

        used = set()

        def pick_best(objective: str) -> Optional[Route]:
            scored = sorted(pool, key=lambda r: self.score_route(r, objective))
            for r in scored:
                sig = route_signature(r)
                if sig in used:
                    continue
                used.add(sig)
                r.optimization_score = self.score_route(r, objective)
                return r
            return None

        fastest = pick_best("time")
        if fastest:
            fastest.route_name = "Fastest Multimodal Route"
            results["fastest"] = fastest

        cheapest = pick_best("cost")
        if cheapest:
            cheapest.route_name = "Cheapest Multimodal Route"
            results["cheapest"] = cheapest

        balanced = pick_best("balanced")
        if balanced:
            balanced.route_name = "Balanced Multimodal Route (AI Recommended)"
            results["balanced"] = balanced

        eco = pick_best("emissions")
        if eco:
            eco.route_name = "Most Eco-Friendly Multimodal Route"
            results["eco_friendly"] = eco

        return results


# ============================================================================
# DATA INTEGRATOR WITH INDIAN PRICING
# ============================================================================

class DataIntegrator:
    """Enhanced data integrator with real infrastructure information and OpenRouteService API"""
    
    USD_TO_INR = 83.0
    
    # OpenRouteService API key (users can replace with their own)
    ORS_API_KEY = "5b3ce3597851110001cf6248d7c9c6d3e4504c3bb86efef32c62a8a5"  # Free tier key
    ORS_BASE_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
    
    @staticmethod
    def get_real_road_route(origin: Location, destination: Location) -> Dict:
        """Get real road route from OpenRouteService API"""
        try:
            import requests
            
            headers = {
                'Authorization': DataIntegrator.ORS_API_KEY,
                'Content-Type': 'application/json'
            }
            
            body = {
                'coordinates': [
                    [origin.longitude, origin.latitude],
                    [destination.longitude, destination.latitude]
                ]
            }
            
            response = requests.post(
                DataIntegrator.ORS_BASE_URL,
                json=body,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                route_data = data['routes'][0]
                distance_km = route_data['summary']['distance'] / 1000
                duration_hours = route_data['summary']['duration'] / 3600
                
                return {
                    'distance': distance_km,
                    'duration': duration_hours,
                    'geometry': route_data['geometry'],
                    'source': 'OpenRouteService'
                }
            else:
                # Fallback to haversine if API fails
                return None
                
        except Exception as e:
            # Fallback to haversine if API fails
            return None
    
    @staticmethod
    def load_road_data(origin: Location, destination: Location) -> RouteSegment:
        # Try to get real route from OpenRouteService
        real_route = DataIntegrator.get_real_road_route(origin, destination)
        
        if real_route:
            distance = real_route['distance']
            duration = real_route['duration']
            station_info = f"Road transport via National Highways (OpenRouteService API)"
        else:
            # Fallback to haversine calculation
            distance = origin.distance_to(destination)
            avg_speed = 65
            duration = distance / avg_speed
            station_info = f"Road transport via National Highways (Estimated)"
        
        cost_per_km = 1.8 * DataIntegrator.USD_TO_INR
        emissions_per_km = 0.35
        
        return RouteSegment(
            mode=TransportMode.ROAD,
            origin=origin,
            destination=destination,
            distance=distance,
            duration=duration,
            cost=distance * cost_per_km,
            emissions=distance * emissions_per_km,
            reliability=82.0,
            station_info=station_info
        )
    
    @staticmethod
    def load_rail_data(origin: Location, destination: Location) -> RouteSegment:
        distance = origin.distance_to(destination) * 1.1
        avg_speed = 55
        duration = distance / avg_speed
        cost_per_km = 0.9 * DataIntegrator.USD_TO_INR
        emissions_per_km = 0.09
        
        station_info = f"From: {origin.railway_station_name} → To: {destination.railway_station_name}"
        
        return RouteSegment(
            mode=TransportMode.RAIL,
            origin=origin,
            destination=destination,
            distance=distance,
            duration=duration,
            cost=distance * cost_per_km,
            emissions=distance * emissions_per_km,
            reliability=88.0,
            station_info=station_info
        )
    
    @staticmethod
    def load_air_data(origin: Location, destination: Location) -> RouteSegment:
        distance = origin.distance_to(destination) * 1.05
        avg_speed = 750
        duration = distance / avg_speed + 4
        cost_per_km = 6.5 * DataIntegrator.USD_TO_INR
        emissions_per_km = 1.4
        
        station_info = f"From: {origin.airport_code} Airport → To: {destination.airport_code} Airport"
        
        return RouteSegment(
            mode=TransportMode.AIR,
            origin=origin,
            destination=destination,
            distance=distance,
            duration=duration,
            cost=distance * cost_per_km,
            emissions=distance * emissions_per_km,
            reliability=85.0,
            station_info=station_info
        )
    
    @staticmethod
    def load_sea_data(origin: Location, destination: Location) -> RouteSegment:
        distance = origin.distance_to(destination) * 1.35
        avg_speed = 22
        duration = distance / avg_speed
        cost_per_km = 0.35 * DataIntegrator.USD_TO_INR
        emissions_per_km = 0.06
        
        station_info = f"From: {origin.seaport_name} → To: {destination.seaport_name}"
        
        return RouteSegment(
            mode=TransportMode.SEA,
            origin=origin,
            destination=destination,
            distance=distance,
            duration=duration,
            cost=distance * cost_per_km,
            emissions=distance * emissions_per_km,
            reliability=75.0,
            station_info=station_info
        )


# ============================================================================
# NETWORK BUILDER WITH REAL INFRASTRUCTURE
# ============================================================================

def build_enhanced_network(origin_city: str, destination_city: str) -> TransportationNetwork:
    """Build enhanced transportation network with real infrastructure"""
    network = TransportationNetwork()
    integrator = DataIntegrator()
    
    origin_data = INDIAN_CITIES_ENHANCED.get(origin_city)
    dest_data = INDIAN_CITIES_ENHANCED.get(destination_city)
    
    if not origin_data or not dest_data:
        st.error("City not found in database!")
        return network
    
    def make_location(city_name: str, location_type: str) -> Location:
        data = INDIAN_CITIES_ENHANCED[city_name]
        return Location(
            name=city_name,
            latitude=data[0],
            longitude=data[1],
            location_type=location_type,
            has_railway_station=data[2],
            has_airport=data[3],
            has_seaport=data[4],
            railway_station_name=data[5],
            airport_code=data[6],
            seaport_name=data[7]
        )
    
    def add_location_if_missing(loc: Location):
        if loc.name not in network.locations:
            network.add_location(loc)
    
    def find_nearest_seaport_city(from_loc: Location, exclude: Optional[str] = None) -> Optional[str]:
        best_city = None
        best_distance = None
        for city, data in INDIAN_CITIES_ENHANCED.items():
            if not data[4]:
                continue
            if exclude and city == exclude:
                continue
            dist = from_loc.distance_to(Location(
                name=city,
                latitude=data[0],
                longitude=data[1],
                location_type="port"
            ))
            if best_distance is None or dist < best_distance:
                best_distance = dist
                best_city = city
        return best_city
    
    # Create location objects with infrastructure details
    origin = make_location(origin_city, "origin")
    destination = make_location(destination_city, "destination")
    
    network.add_location(origin)
    network.add_location(destination)
    
    distance = origin.distance_to(destination)
    
    # Always add road connection
    network.add_connection(integrator.load_road_data(origin, destination))
    
    # Add rail connection if both have railway stations
    if origin.has_railway_station and destination.has_railway_station:
        network.add_connection(integrator.load_rail_data(origin, destination))
    
    # Add air connection if both have airports and distance > 500 km
    if origin.has_airport and destination.has_airport and distance > 500:
        network.add_connection(integrator.load_air_data(origin, destination))
    
    # Add sea connection if both are coastal
    if origin.has_seaport and destination.has_seaport:
        network.add_connection(integrator.load_sea_data(origin, destination))

    # Add road-sea-road path using nearest seaports for non-coastal cities
    origin_port_city = origin.name if origin.has_seaport else find_nearest_seaport_city(origin)
    destination_port_city = destination.name if destination.has_seaport else find_nearest_seaport_city(destination)

    if origin_port_city and destination_port_city and origin_port_city != destination_port_city:
        origin_port = make_location(origin_port_city, "port")
        destination_port = make_location(destination_port_city, "port")
        add_location_if_missing(origin_port)
        add_location_if_missing(destination_port)

        if origin_port.name != origin.name:
            network.add_connection(integrator.load_road_data(origin, origin_port))
        if destination_port.name != destination.name:
            network.add_connection(integrator.load_road_data(destination_port, destination))

        network.add_connection(integrator.load_sea_data(origin_port, destination_port))
    
    # Add intermediate hubs for long distances
    if distance > 700:
        # Create midway hub
        mid_lat = (origin_data[0] + dest_data[0]) / 2
        mid_lon = (origin_data[1] + dest_data[1]) / 2
        
        hub = Location(
            name=f"Transit Hub (Midway)",
            latitude=mid_lat,
            longitude=mid_lon,
            location_type="hub",
            has_railway_station=True,
            has_airport=False,
            has_seaport=False,
            railway_station_name="Regional Rail Hub"
        )
        
        network.add_location(hub)
        
        # Connect origin to hub
        network.add_connection(integrator.load_road_data(origin, hub))
        if origin.has_railway_station:
            network.add_connection(integrator.load_rail_data(origin, hub))
        
        # Connect hub to destination
        network.add_connection(integrator.load_road_data(hub, destination))
        if destination.has_railway_station:
            network.add_connection(integrator.load_rail_data(hub, destination))

    # Add intermodal hub to encourage multimodal routing
    if distance > 300:
        hub_lat = (origin_data[0] * 0.6 + dest_data[0] * 0.4)
        hub_lon = (origin_data[1] * 0.6 + dest_data[1] * 0.4)
        intermodal_hub = Location(
            name="Intermodal Hub",
            latitude=hub_lat,
            longitude=hub_lon,
            location_type="hub",
            has_railway_station=True,
            has_airport=distance > 500,
            has_seaport=False,
            railway_station_name="Intermodal Rail Hub",
            airport_code="HUB" if distance > 500 else "",
            seaport_name=""
        )
        if intermodal_hub.name not in network.locations:
            network.add_location(intermodal_hub)

        # Origin <-> Hub
        network.add_connection(integrator.load_road_data(origin, intermodal_hub))
        if origin.has_railway_station:
            network.add_connection(integrator.load_rail_data(origin, intermodal_hub))
        if origin.has_airport and intermodal_hub.has_airport and distance > 500:
            network.add_connection(integrator.load_air_data(origin, intermodal_hub))

        # Hub <-> Destination
        network.add_connection(integrator.load_road_data(intermodal_hub, destination))
        if destination.has_railway_station:
            network.add_connection(integrator.load_rail_data(intermodal_hub, destination))
        if destination.has_airport and intermodal_hub.has_airport and distance > 500:
            network.add_connection(integrator.load_air_data(intermodal_hub, destination))
    
    return network


# ============================================================================
# MAP VISUALIZATION
# ============================================================================

def create_route_map(routes: Dict[str, Route], selected_route: str = 'balanced'):
    """Create enhanced interactive map showing the selected route with color-coded transport modes"""
    
    if selected_route not in routes:
        selected_route = list(routes.keys())[0]
    
    if selected_route == "all":
        route_list = list(routes.values())
    else:
        route_list = [routes[selected_route]]
    
    # Mode colors with better contrast
    mode_colors = {
        'road': '#FF6B35',
        'rail': '#3B82F6',
        'air': '#F59E0B',
        'sea': '#06B6D4'
    }
    
    mode_names = {
        'road': '🚚 Road Transport',
        'rail': '🚂 Rail Transport',
        'air': '✈️ Air Cargo',
        'sea': '🚢 Sea Freight'
    }
    
    # Create figure
    fig = go.Figure()

    def sea_path_points(origin: Location, destination: Location):
        mid_lat = (origin.latitude + destination.latitude) / 2
        mid_lon = (origin.longitude + destination.longitude) / 2
        # Heuristic: push sea paths outward from coast
        if origin.longitude < 77 and destination.longitude < 77:
            mid_lon -= 12.0
        elif origin.longitude >= 77 and destination.longitude >= 77:
            mid_lon += 12.0
        else:
            mid_lat -= 12.0
        # Clamp to India bounds
        mid_lat = max(6, min(37, mid_lat))
        mid_lon = max(67, min(98, mid_lon))
        return [origin.latitude, mid_lat, destination.latitude], [origin.longitude, mid_lon, destination.longitude]
    
    # Track which modes are used
    modes_used = set()

    # Add route segments
    for route in route_list:
        for i, segment in enumerate(route.segments):
            color = mode_colors.get(segment.mode.value, '#FFFFFF')
            modes_used.add(segment.mode.value)
            if segment.mode == TransportMode.SEA:
                lat_vals, lon_vals = sea_path_points(segment.origin, segment.destination)
            else:
                lat_vals = [segment.origin.latitude, segment.destination.latitude]
                lon_vals = [segment.origin.longitude, segment.destination.longitude]

            fig.add_trace(go.Scattermapbox(
                lon=lon_vals,
                lat=lat_vals,
                mode='lines+markers',
                line=dict(width=6, color=color),
                marker=dict(size=9, color=color),
                name=mode_names.get(segment.mode.value, segment.mode.value.title()),
                legendgroup=segment.mode.value,
                showlegend=(i == 0 or segment.mode.value not in [s.mode.value for s in route.segments[:i]]),
                opacity=0.85 if selected_route == "all" else 1.0,
                hovertemplate=f"<b>{segment.mode.value.upper()} TRANSPORT</b><br>" +
                             f"<b>From:</b> {segment.origin.name}<br>" +
                             f"<b>To:</b> {segment.destination.name}<br>" +
                             f"<b>Distance:</b> {segment.distance:.2f} km<br>" +
                             f"<b>Duration:</b> {segment.duration:.2f} hrs<br>" +
                             f"<b>Cost:</b> ₹{segment.cost:,.2f}<br>" +
                             f"<b>Emissions:</b> {segment.emissions:.2f} kg CO₂<br>" +
                             f"<extra></extra>"
            ))
    
    # Add markers for all locations with better styling
    all_locations = {}
    for route in route_list:
        for segment in route.segments:
            if segment.origin.name not in all_locations:
                all_locations[segment.origin.name] = (
                    segment.origin.latitude,
                    segment.origin.longitude,
                    segment.origin.location_type
                )
            if segment.destination.name not in all_locations:
                all_locations[segment.destination.name] = (
                    segment.destination.latitude,
                    segment.destination.longitude,
                    segment.destination.location_type
                )
    
    for name, (lat, lon, loc_type) in all_locations.items():
        if loc_type == 'origin':
            marker_color = '#10B981'
            marker_symbol = 'circle'
            marker_size = 20
            marker_text = '🏁 START'
        elif loc_type == 'destination':
            marker_color = '#EF4444'
            marker_symbol = 'star'
            marker_size = 20
            marker_text = '🎯 END'
        elif loc_type == 'port':
            marker_color = '#22D3EE'
            marker_symbol = 'triangle-up'
            marker_size = 17
            marker_text = '⚓ PORT'
        else:
            marker_color = '#F59E0B'
            marker_symbol = 'square'
            marker_size = 15
            marker_text = '⚡ HUB'
        
        fig.add_trace(go.Scattermapbox(
            lon=[lon],
            lat=[lat],
            mode='markers+text',
            marker=dict(
                size=marker_size,
                color=marker_color
            ),
            text=[f"{marker_text}"],
            textposition="top center",
            textfont=dict(size=12, color='#0f172a', family='Arial Black'),
            name=name,
            showlegend=False,
            hovertemplate=f"<b>{name}</b><br>" +
                         f"<b>Type:</b> {loc_type.title()}<br>" +
                         f"<b>Lat:</b> {lat:.4f}<br>" +
                         f"<b>Lon:</b> {lon:.4f}<br>" +
                         f"<extra></extra>"
        ))
    
    try:
        mapbox_token = st.secrets["MAPBOX_TOKEN"]
    except Exception:
        mapbox_token = ""
    map_style = "light" if mapbox_token else "open-street-map"

    @st.cache_data(show_spinner=False)
    def load_india_geojson():
        path = "india-soi.geojson"
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    india_geojson = None
    try:
        india_geojson = load_india_geojson()
    except Exception:
        india_geojson = None
    
    fig.update_layout(
        showlegend=True,
        legend=dict(
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(148, 163, 184, 0.5)',
            borderwidth=2,
            font=dict(color='#0f172a', size=13, family='Arial'),
            title=dict(text='<b>Transport Modes</b>', font=dict(size=14, color='#0f172a')),
            orientation='v',
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=0.01
        ),
        height=520,
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        font=dict(color='#0f172a', family='Arial'),
        margin=dict(l=0, r=0, t=10, b=0),
        hovermode='closest'
    )

    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_token if mapbox_token else None,
            style=map_style,
            center=dict(lat=22.0, lon=82.5),
            zoom=3.6,
            bounds=dict(west=67, east=98, south=6, north=37),
            layers=[
                {
                    "source": india_geojson,
                    "type": "line",
                    "color": "#0f172a",
                    "line": {"width": 2.0}
                }
            ] if india_geojson else []
        )
    )
    
    return fig


def create_mode_percentage_chart(routes: Dict[str, Route]):
    """Create chart showing percentage of transportation by mode"""
    
    # Aggregate data from all routes
    total_mode_distances = {}
    
    for route in routes.values():
        for mode, percentage in route.mode_percentages.items():
            distance = route.total_distance * (percentage / 100)
            total_mode_distances[mode] = total_mode_distances.get(mode, 0) + distance
    
    total_distance = sum(total_mode_distances.values())
    mode_percentages = {
        mode: (dist / total_distance * 100) if total_distance > 0 else 0
        for mode, dist in total_mode_distances.items()
    }
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=[mode.title() for mode in mode_percentages.keys()],
        values=list(mode_percentages.values()),
        hole=0.4,
        marker=dict(colors=['#FF6B35', '#004E89', '#F77F00', '#06AED5']),
        textinfo='label+percent',
        textfont=dict(size=14, color='white')
    )])
    
    fig.update_layout(
        title="Overall Transportation Mode Distribution (%)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e6ed'),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(10, 14, 39, 0.9)',
            bordercolor='rgba(6, 174, 213, 0.3)',
            borderwidth=1
        )
    )
    
    return fig


# ============================================================================
# ENHANCED VISUALIZATION FUNCTIONS
# ============================================================================

def create_cost_comparison_chart(routes: Dict[str, Route]):
    data = []
    for route_type, route in routes.items():
        cost_value = route.final_total_cost if route.final_total_cost > 0 else route.adjusted_total_cost if route.adjusted_total_cost > 0 else route.total_cost
        data.append({
            'Route': route.route_name.replace(' Route', '').replace(' (AI Recommended)', '*'),
            'Cost (₹)': cost_value
        })
    
    df = pd.DataFrame(data)
    fig = px.bar(df, x='Route', y='Cost (₹)', title='Cost Comparison by Route',
                 color='Cost (₹)', color_continuous_scale=['#10b981', '#06AED5', '#F77F00', '#FF6B35'])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e6ed', size=14), showlegend=False
    )
    fig.update_traces(hovertemplate="Route=%{x}<br>Cost=₹%{y:,.2f}<extra></extra>")
    fig.update_layout(hoverlabel=dict(font_size=14))
    return fig


def create_infrastructure_summary(origin: Location, destination: Location):
    """Create infrastructure availability summary"""
    
    st.markdown("### 🏗️ Transport Infrastructure Availability")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### 📍 {origin.name}")
        
        infra_html = "<div style='padding: 15px; background: rgba(10, 14, 39, 0.6); border-radius: 8px;'>"
        
        if origin.has_railway_station:
            infra_html += f"<div class='transport-mode mode-rail'>🚂 {origin.railway_station_name}</div>"
        else:
            infra_html += "<div style='color: #8892ab; padding: 5px;'>❌ No Railway Station</div>"
        
        if origin.has_airport:
            infra_html += f"<div class='transport-mode mode-air'>✈️ {origin.airport_code} Airport</div>"
        else:
            infra_html += "<div style='color: #8892ab; padding: 5px;'>❌ No Airport</div>"
        
        if origin.has_seaport:
            infra_html += f"<div class='transport-mode mode-sea'>🚢 {origin.seaport_name}</div>"
        else:
            infra_html += "<div style='color: #8892ab; padding: 5px;'>❌ No Seaport</div>"
        
        infra_html += "<div class='transport-mode mode-road'>🚚 Road Network Available</div>"
        infra_html += "</div>"
        
        st.markdown(infra_html, unsafe_allow_html=True)

    with col2:
        st.markdown(f"#### 📍 {destination.name}")
        
        infra_html = "<div style='padding: 15px; background: rgba(10, 14, 39, 0.6); border-radius: 8px;'>"
        
        if destination.has_railway_station:
            infra_html += f"<div class='transport-mode mode-rail'>🚂 {destination.railway_station_name}</div>"
        else:
            infra_html += "<div style='color: #8892ab; padding: 5px;'>❌ No Railway Station</div>"
        
        if destination.has_airport:
            infra_html += f"<div class='transport-mode mode-air'>✈️ {destination.airport_code} Airport</div>"
        else:
            infra_html += "<div style='color: #8892ab; padding: 5px;'>❌ No Airport</div>"
        
        if destination.has_seaport:
            infra_html += f"<div class='transport-mode mode-sea'>🚢 {destination.seaport_name}</div>"
        else:
            infra_html += "<div style='color: #8892ab; padding: 5px;'>❌ No Seaport</div>"
        
        infra_html += "<div class='transport-mode mode-road'>🚚 Road Network Available</div>"
        infra_html += "</div>"
        
        st.markdown(infra_html, unsafe_allow_html=True)


# ============================================================================
# COST, SLA, AND SCENARIO HELPERS
# ============================================================================

def apply_carbon_and_sla(routes: Dict[str, Route], carbon_enabled: bool, carbon_price: float,
                         sla_hours: float, sla_penalty_rate: float):
    for route in routes.values():
        route.carbon_cost = route.total_emissions * carbon_price if carbon_enabled else 0.0
        route.adjusted_total_cost = route.total_cost + route.carbon_cost if carbon_enabled else route.total_cost

        if route.total_time > sla_hours:
            delay_hours = route.total_time - sla_hours
            route.sla_penalty = delay_hours * sla_penalty_rate
        else:
            route.sla_penalty = 0.0

        route.final_total_cost = route.adjusted_total_cost + route.sla_penalty


def simulate_routes(routes: Dict[str, Route], simulate_road: bool, simulate_rail: bool, simulate_port: bool) -> Dict[str, Route]:
    simulated = {}
    for key, route in routes.items():
        new_segments = []
        for seg in route.segments:
            new_seg = RouteSegment(
                mode=seg.mode,
                origin=seg.origin,
                destination=seg.destination,
                distance=seg.distance,
                duration=seg.duration,
                cost=seg.cost,
                emissions=seg.emissions,
                reliability=seg.reliability,
                station_info=seg.station_info
            )
            if simulate_road and new_seg.mode == TransportMode.ROAD:
                new_seg.duration *= 1.25
                new_seg.reliability = max(0.0, new_seg.reliability - 10)
            if simulate_rail and new_seg.mode == TransportMode.RAIL:
                new_seg.duration *= 1.15
                new_seg.reliability = max(0.0, new_seg.reliability - 7)
            if simulate_port and new_seg.mode == TransportMode.SEA:
                new_seg.duration *= 1.30
                new_seg.cost *= 1.05
            new_segments.append(new_seg)

        total_cost = sum(s.cost for s in new_segments)
        total_time = sum(s.duration for s in new_segments)
        total_distance = sum(s.distance for s in new_segments)
        total_emissions = sum(s.emissions for s in new_segments)
        avg_reliability = float(np.mean([s.reliability for s in new_segments])) if new_segments else 0.0

        simulated_route = Route(
            segments=new_segments,
            total_cost=total_cost,
            total_time=total_time,
            total_distance=total_distance,
            total_emissions=total_emissions,
            average_reliability=avg_reliability,
            route_name=f"{route.route_name} (Simulated)",
            optimization_score=route.optimization_score
        )
        simulated[key] = simulated_route

    return simulated
    
    with col2:
        st.markdown(f"#### 📍 {destination.name}")
        
        infra_html = "<div style='padding: 15px; background: rgba(10, 14, 39, 0.6); border-radius: 8px;'>"
        
        if destination.has_railway_station:
            infra_html += f"<div class='transport-mode mode-rail'>🚂 {destination.railway_station_name}</div>"
        else:
            infra_html += "<div style='color: #8892ab; padding: 5px;'>❌ No Railway Station</div>"
        
        if destination.has_airport:
            infra_html += f"<div class='transport-mode mode-air'>✈️ {destination.airport_code} Airport</div>"
        else:
            infra_html += "<div style='color: #8892ab; padding: 5px;'>❌ No Airport</div>"
        
        if destination.has_seaport:
            infra_html += f"<div class='transport-mode mode-sea'>🚢 {destination.seaport_name}</div>"
        else:
            infra_html += "<div style='color: #8892ab; padding: 5px;'>❌ No Seaport</div>"
        
        infra_html += "<div class='transport-mode mode-road'>🚚 Road Network Available</div>"
        infra_html += "</div>"
        
        st.markdown(infra_html, unsafe_allow_html=True)


# ============================================================================
# MAIN STREAMLIT APP
# ============================================================================

def main():
    # Header
    st.markdown("""
        <h1 style='text-align: center; background: linear-gradient(135deg, #06AED5 0%, #F77F00 100%); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem;'>
        🚚 Industry 4.0 Transport Optimizer Pro
        </h1>
        <p style='text-align: center; color: #0f172a; font-size: 1.35rem; font-weight: 700; margin-bottom: 2rem;'>
        AI-Powered Multimodal Route Planning with Real Indian Infrastructure Data
        </p>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📍 Route Configuration")
        
        st.markdown("### Origin City")
        origin_city = st.selectbox(
            "Select origin city",
            options=sorted(INDIAN_CITIES_ENHANCED.keys()),
            index=sorted(INDIAN_CITIES_ENHANCED.keys()).index("Mumbai, Maharashtra"),
            label_visibility="collapsed"
        )
        
        st.markdown("### Destination City")
        destination_city = st.selectbox(
            "Select destination city",
            options=sorted(INDIAN_CITIES_ENHANCED.keys()),
            index=sorted(INDIAN_CITIES_ENHANCED.keys()).index("Bengaluru, Karnataka"),
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.markdown("## ⚙️ Optimization Preferences")
        st.markdown("Set your priorities for the optimization:")
        
        preference_options = [
            PreferenceLevel.VERY_LOW,
            PreferenceLevel.LOW,
            PreferenceLevel.NEUTRAL,
            PreferenceLevel.HIGH,
            PreferenceLevel.VERY_HIGH
        ]
        
        cost_pref = st.select_slider(
            "💰 Cost Priority",
            options=preference_options,
            value=PreferenceLevel.NEUTRAL,
            format_func=lambda x: x.label
        )
        
        time_pref = st.select_slider(
            "⚡ Time Priority",
            options=preference_options,
            value=PreferenceLevel.NEUTRAL,
            format_func=lambda x: x.label
        )
        
        eco_pref = st.select_slider(
            "🌱 Environmental Priority",
            options=preference_options,
            value=PreferenceLevel.NEUTRAL,
            format_func=lambda x: x.label
        )
        
        # Show preference badges
        st.markdown("#### Your Preferences:")
        pref_html = f"""
        <span class='preference-badge {cost_pref.label.lower().replace(' ', '-')}'>
            Cost: {cost_pref.label}
        </span>
        <span class='preference-badge {time_pref.label.lower().replace(' ', '-')}'>
            Time: {time_pref.label}
        </span>
        <span class='preference-badge {eco_pref.label.lower().replace(' ', '-')}'>
            Eco: {eco_pref.label}
        </span>
        """
        st.markdown(pref_html, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("## 🌍 Carbon & SLA")
        carbon_enabled = st.toggle("Enable Carbon Pricing", value=False)
        carbon_price = st.number_input("Carbon Price (₹ per kg CO₂)", min_value=0.0, value=0.0, step=0.5)
        sla_hours = st.number_input("SLA Delivery Time (hours)", min_value=1.0, value=48.0, step=1.0)
        sla_penalty_rate = st.number_input("Penalty per Delayed Hour (₹)", min_value=0.0, value=250.0, step=50.0)

        st.markdown("## 🧪 Digital Twin Scenarios")
        simulate_road = st.checkbox("Simulate Road Disruption", value=False)
        simulate_rail = st.checkbox("Simulate Rail Delay", value=False)
        simulate_port = st.checkbox("Simulate Port Congestion", value=False)

        st.markdown("---")
        
        optimize_button = st.button("🚀 Optimize Routes", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📊 Features")
        st.markdown("""
        <div style='font-size: 0.85rem; color: #8892ab;'>
        <ul>
            <li>✅ Real railway stations</li>
            <li>✅ Airport codes</li>
            <li>✅ Coastal seaports</li>
            <li>✅ Interactive maps</li>
            <li>✅ Mode percentages</li>
            <li>✅ Infrastructure data</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    if optimize_button:
        if origin_city == destination_city:
            st.error("⚠️ Origin and destination cities must be different!")
            return
        
        with st.spinner('🤖 AI Optimization in Progress...'):
            network = build_enhanced_network(origin_city, destination_city)
            
            optimizer = MultimodalOptimizer(network)
            optimizer.set_optimization_preferences(cost_pref, time_pref, eco_pref)
            
            routes = optimizer.find_optimal_routes(origin_city, destination_city)
            apply_carbon_and_sla(routes, carbon_enabled, carbon_price, sla_hours, sla_penalty_rate)
            simulated_routes = simulate_routes(routes, simulate_road, simulate_rail, simulate_port)
            apply_carbon_and_sla(simulated_routes, carbon_enabled, carbon_price, sla_hours, sla_penalty_rate)
        
        if not routes:
            st.error("❌ No routes found! Please try different cities.")
            return
        
        st.success("✅ Optimization Complete!")
        
        # Get origin and destination objects
        origin = network.locations[origin_city]
        destination = network.locations[destination_city]
        
        # Infrastructure Summary
        create_infrastructure_summary(origin, destination)
        
        st.markdown("---")
        
        # Create tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Overview", 
            "🗺️ Interactive Map", 
            "🛣️ Route Details", 
            "📈 Analytics", 
            "💡 Insights",
            "🧪 Scenario Simulation",
            "💼 Business Impact"
        ])
        
        # TAB 1: OVERVIEW
        with tab1:
            st.markdown("### 🎯 Key Performance Indicators")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                cheapest = min([r.final_total_cost for r in routes.values()])
                st.metric("Lowest Cost", f"₹{cheapest:,.0f}")
            
            with col2:
                fastest = min([r.total_time for r in routes.values()])
                st.metric("Fastest Time", f"{fastest:.1f} hrs")
            
            with col3:
                most_eco = min([r.total_emissions for r in routes.values()])
                st.metric("Best Eco", f"{most_eco:.0f} kg CO₂")
            
            with col4:
                avg_reliability = np.mean([r.average_reliability for r in routes.values()])
                st.metric("Avg Reliability", f"{avg_reliability:.1f}%")

            st.markdown("---")
            st.markdown("### ⏱️ SLA Status")
            status_html = ""
            for key, route in routes.items():
                on_time = route.total_time <= sla_hours
                color = "#16a34a" if on_time else "#dc2626"
                label = "On-Time" if on_time else "Delayed"
                status_html += f"<div style='margin:6px 0;'><strong>{route.route_name}:</strong> <span style='color:{color}; font-weight:800'>{label}</span></div>"
            st.markdown(f"<div class='info-box'>{status_html}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(create_cost_comparison_chart(routes), use_container_width=True)
            
            with col2:
                st.plotly_chart(create_mode_percentage_chart(routes), use_container_width=True)
        
        # TAB 2: INTERACTIVE MAP
        with tab2:
            st.markdown("### 🗺️ Interactive Route Visualization")
            st.markdown("Explore all four routes side by side with color-coded transport modes.")
            
            route_keys = ["fastest", "cheapest", "balanced", "eco_friendly"]
            route_labels = {
                "fastest": "Fastest Multimodal Route",
                "cheapest": "Cheapest Multimodal Route",
                "balanced": "Balanced Multimodal Route (AI Recommended)",
                "eco_friendly": "Most Eco-Friendly Multimodal Route"
            }

            row1, row2 = st.columns(2)
            for idx, key in enumerate(route_keys):
                if key not in routes:
                    continue
                target_col = row1 if idx < 2 else row2
                with target_col:
                    st.markdown(f"#### {route_labels[key]}")
                    st.markdown('<div class="map-container">', unsafe_allow_html=True)
                    st.plotly_chart(
                        create_route_map(routes, key),
                        use_container_width=True,
                        key=f"route_map_{key}"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Legend and statistics
            st.markdown("---")
            st.markdown("### 🎨 Map Legend & Route Statistics")

            display_route = routes.get("balanced", next(iter(routes.values())))
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style='background: rgba(15, 23, 42, 0.8); padding: 15px; border-radius: 10px; border: 1px solid rgba(148, 163, 184, 0.3);'>
                    <h4 style='color: #F1F5F9; margin-bottom: 10px;'>🚦 Transport Modes</h4>
                    <div class='transport-mode mode-road'>🚚 Road Transport (Orange)</div>
                    <div class='transport-mode mode-rail'>🚂 Rail Transport (Blue)</div>
                    <div class='transport-mode mode-air'>✈️ Air Cargo (Amber)</div>
                    <div class='transport-mode mode-sea'>🚢 Sea Freight (Cyan)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background: rgba(15, 23, 42, 0.8); padding: 15px; border-radius: 10px; border: 1px solid rgba(148, 163, 184, 0.3);'>
                    <h4 style='color: #F1F5F9; margin-bottom: 10px;'>📍 Location Markers</h4>
                    <div style='padding: 8px; margin: 5px 0; color: #10B981; font-weight: 600;'>🏁 START - Origin City (Green)</div>
                    <div style='padding: 8px; margin: 5px 0; color: #EF4444; font-weight: 600;'>🎯 END - Destination City (Red)</div>
                    <div style='padding: 8px; margin: 5px 0; color: #22D3EE; font-weight: 600;'>⚓ PORT - Seaport Nodes (Cyan)</div>
                    <div style='padding: 8px; margin: 5px 0; color: #F59E0B; font-weight: 600;'>⚡ HUB - Transit Points (Amber)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style='background: rgba(15, 23, 42, 0.8); padding: 15px; border-radius: 10px; border: 1px solid rgba(148, 163, 184, 0.3);'>
                    <h4 style='color: #F1F5F9; margin-bottom: 10px;'>📊 Quick Stats</h4>
                    <div style='padding: 5px; color: #CBD5E1;'><strong style='color: #F1F5F9;'>Total Distance:</strong> {display_route.total_distance:,.0f} km</div>
                    <div style='padding: 5px; color: #CBD5E1;'><strong style='color: #F1F5F9;'>Total Duration:</strong> {display_route.total_time:.1f} hrs</div>
                    <div style='padding: 5px; color: #CBD5E1;'><strong style='color: #F1F5F9;'>Total Cost:</strong> ₹{display_route.total_cost:,.0f}</div>
                    <div style='padding: 5px; color: #CBD5E1;'><strong style='color: #F1F5F9;'>CO₂ Emissions:</strong> {display_route.total_emissions:,.0f} kg</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            # Interactive tips
            st.markdown("---")
            st.markdown("""
            <div style='background: linear-gradient(135deg, rgba(6, 174, 213, 0.15) 0%, rgba(15, 23, 42, 0.8) 100%); 
                        padding: 16px; 
                        border-radius: 10px; 
                        border: 2px solid rgba(6, 174, 213, 0.4);'>
                <h4 style='color: #06AED5; margin-bottom: 10px;'>💡 Map Interaction Tips</h4>
                <ul style='color: #CBD5E1; margin-left: 20px;'>
                    <li><strong>Hover</strong> over lines to see detailed segment information</li>
                    <li><strong>Hover</strong> over markers to see location details</li>
                    <li><strong>Click and drag</strong> to pan the map</li>
                    <li><strong>Scroll</strong> to zoom in/out</li>
                    <li><strong>Click legend items</strong> to show/hide specific transport modes</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # TAB 3: ROUTE DETAILS
        with tab3:
            st.markdown("### 🛣️ Detailed Route Breakdown")
            
            # Create two columns for side-by-side route comparison
            num_routes = len(routes)
            if num_routes >= 2:
                col1, col2 = st.columns(2)
                route_items = list(routes.items())
                
                # First column - First two routes
                with col1:
                    for i in range(0, min(2, num_routes)):
                        route_type, route = route_items[i]
                        is_recommended = 'balanced' in route_type
                        
                        with st.expander(f"{'⭐ ' if is_recommended else ''}{route.route_name}", expanded=False):
                            # Summary metrics in a row
                            metric_col1, metric_col2 = st.columns(2)
                            with metric_col1:
                                st.metric("Total Cost", f"₹{route.total_cost:,.0f}")
                                st.metric("Distance", f"{route.total_distance:,.0f} km")
                            with metric_col2:
                                st.metric("Total Time", f"{route.total_time:.1f} hrs")
                                st.metric("Emissions", f"{route.total_emissions:,.0f} kg CO₂")
                            
                            st.markdown("#### 🚦 Route Segments")
                            
                            for j, segment in enumerate(route.segments, 1):
                                mode_emoji = {'road': '🚚', 'rail': '🚂', 'air': '✈️', 'sea': '🚢'}
                                
                                st.markdown(f"""
                                <div class="segment-box">
                                    <h4>{mode_emoji.get(segment.mode.value, '🚚')} Segment {j}: {segment.mode.value.upper()}</h4>
                                    <p><strong>Route:</strong> {segment.origin.name} → {segment.destination.name}</p>
                                    <div class="station-info">
                                        <strong>📍 Infrastructure:</strong> {segment.station_info}
                                    </div>
                                    <p><strong>Duration:</strong> {segment.duration:.1f} hours | 
                                       <strong>Cost:</strong> ₹{segment.cost:,.0f}</p>
                                    <p><strong>Distance:</strong> {segment.distance:.0f} km | 
                                       <strong>Emissions:</strong> {segment.emissions:.0f} kg CO₂</p>
                                    <p><strong>Reliability:</strong> {segment.reliability:.1f}%</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Show mode percentages
                            st.markdown("#### 📊 Mode Distribution")
                            mode_cols = st.columns(len(route.mode_percentages))
                            for k, (mode, percentage) in enumerate(route.mode_percentages.items()):
                                with mode_cols[k]:
                                    mode_emoji = {'road': '🚚', 'rail': '🚂', 'air': '✈️', 'sea': '🚢'}
                                    st.metric(f"{mode_emoji.get(mode, '🚚')} {mode.title()}", f"{percentage:.1f}%")
                
                # Second column - Remaining routes
                with col2:
                    for i in range(2, num_routes):
                        route_type, route = route_items[i]
                        is_recommended = 'balanced' in route_type
                        
                        with st.expander(f"{'⭐ ' if is_recommended else ''}{route.route_name}", expanded=is_recommended):
                            # Summary metrics in a row
                            metric_col1, metric_col2 = st.columns(2)
                            with metric_col1:
                                st.metric("Total Cost", f"₹{route.total_cost:,.0f}")
                                st.metric("Distance", f"{route.total_distance:,.0f} km")
                            with metric_col2:
                                st.metric("Total Time", f"{route.total_time:.1f} hrs")
                                st.metric("Emissions", f"{route.total_emissions:,.0f} kg CO₂")
                            
                            st.markdown("#### 🚦 Route Segments")
                            
                            for j, segment in enumerate(route.segments, 1):
                                mode_emoji = {'road': '🚚', 'rail': '🚂', 'air': '✈️', 'sea': '🚢'}
                                
                                st.markdown(f"""
                                <div class="segment-box">
                                    <h4>{mode_emoji.get(segment.mode.value, '🚚')} Segment {j}: {segment.mode.value.upper()}</h4>
                                    <p><strong>Route:</strong> {segment.origin.name} → {segment.destination.name}</p>
                                    <div class="station-info">
                                        <strong>📍 Infrastructure:</strong> {segment.station_info}
                                    </div>
                                    <p><strong>Duration:</strong> {segment.duration:.1f} hours | 
                                       <strong>Cost:</strong> ₹{segment.cost:,.0f}</p>
                                    <p><strong>Distance:</strong> {segment.distance:.0f} km | 
                                       <strong>Emissions:</strong> {segment.emissions:.0f} kg CO₂</p>
                                    <p><strong>Reliability:</strong> {segment.reliability:.1f}%</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Show mode percentages
                            st.markdown("#### 📊 Mode Distribution")
                            mode_cols = st.columns(len(route.mode_percentages))
                            for k, (mode, percentage) in enumerate(route.mode_percentages.items()):
                                with mode_cols[k]:
                                    mode_emoji = {'road': '🚚', 'rail': '🚂', 'air': '✈️', 'sea': '🚢'}
                                    st.metric(f"{mode_emoji.get(mode, '🚚')} {mode.title()}", f"{percentage:.1f}%")
            else:
                # Single route display
                for route_type, route in routes.items():
                    is_recommended = 'balanced' in route_type
                    
                    with st.expander(f"{'⭐ ' if is_recommended else ''}{route.route_name}", expanded=is_recommended):
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Total Cost", f"₹{route.total_cost:,.2f}")
                        col2.metric("Total Time", f"{route.total_time:.1f} hrs")
                        col3.metric("Distance", f"{route.total_distance:,.0f} km")
                        col4.metric("Emissions", f"{route.total_emissions:,.0f} kg CO₂")
                        
                        st.markdown("#### 🚦 Route Segments")
                        
                        for i, segment in enumerate(route.segments, 1):
                            mode_emoji = {'road': '🚚', 'rail': '🚂', 'air': '✈️', 'sea': '🚢'}
                            
                            st.markdown(f"""
                            <div class="segment-box">
                                <h4>{mode_emoji.get(segment.mode.value, '🚚')} Segment {i}: {segment.mode.value.upper()}</h4>
                                <p><strong>Route:</strong> {segment.origin.name} → {segment.destination.name}</p>
                                <div class="station-info">
                                    <strong>📍 Infrastructure:</strong> {segment.station_info}
                                </div>
                                <p><strong>Duration:</strong> {segment.duration:.1f} hours | 
                                   <strong>Cost:</strong> ₹{segment.cost:,.0f}</p>
                                <p><strong>Distance:</strong> {segment.distance:.0f} km | 
                                   <strong>Emissions:</strong> {segment.emissions:.0f} kg CO₂</p>
                                <p><strong>Reliability:</strong> {segment.reliability:.1f}%</p>
                            </div>
                            """, unsafe_allow_html=True)
        
        # TAB 4: ANALYTICS
        with tab4:
            st.markdown("### 📈 Comprehensive Analytics & Insights")
            
            # Section 1: Route Comparison Matrix
            st.markdown("#### 🔍 Detailed Route Comparison")
            comparison_data = []
            for route_type, route in routes.items():
                modes_used = ', '.join([f"{m.title()} ({p:.0f}%)" for m, p in route.mode_percentages.items()])
                cost_per_km = route.total_cost / route.total_distance if route.total_distance > 0 else 0
                emissions_per_km = route.total_emissions / route.total_distance if route.total_distance > 0 else 0
                avg_speed = route.total_distance / route.total_time if route.total_time > 0 else 0
                
                comparison_data.append({
                    'Route': route.route_name,
                    'Total Cost (₹)': f"₹{route.final_total_cost:,.0f}",
                    'Carbon Cost (₹)': f"₹{route.carbon_cost:,.0f}",
                    'SLA Penalty (₹)': f"₹{route.sla_penalty:,.0f}",
                    'Cost per km (₹)': f"₹{cost_per_km:.2f}",
                    'Time (hrs)': f"{route.total_time:.1f}",
                    'Avg Speed (km/h)': f"{avg_speed:.1f}",
                    'Distance (km)': f"{route.total_distance:,.0f}",
                    'Emissions (kg)': f"{route.total_emissions:,.0f}",
                    'Emissions/km': f"{emissions_per_km:.3f}",
                    'Reliability (%)': f"{route.average_reliability:.1f}",
                    'Segments': len(route.segments),
                    'Modes Used': modes_used
                })
            
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Section 2: Cost Analysis
            st.markdown("#### 💰 Cost Breakdown Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Cost comparison chart
                cost_data = pd.DataFrame([
                    {'Route': routes[k].route_name.replace(' (AI Recommended)', ''), 'Cost': routes[k].final_total_cost}
                    for k in routes.keys()
                ])
                fig_cost = px.bar(
                    cost_data,
                    x='Route',
                    y='Cost',
                    title='Total Cost Comparison (₹)',
                    color='Cost',
                    color_continuous_scale=['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
                )
                fig_cost.update_layout(
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#f8fafc',
                    font=dict(color='#0f172a', size=14),
                    showlegend=False,
                    title_font_size=16
                )
                fig_cost.update_traces(hovertemplate="Route=%{x}<br>Cost=₹%{y:,.2f}<extra></extra>")
                fig_cost.update_layout(hoverlabel=dict(font_size=14))
                st.plotly_chart(fig_cost, use_container_width=True)
            
            with col2:
                # Cost per kilometer analysis
                cost_per_km_data = []
                for k, route in routes.items():
                    cost_per_km = route.final_total_cost / route.total_distance if route.total_distance > 0 else 0
                    cost_per_km_data.append({
                        'Route': route.route_name.replace(' (AI Recommended)', ''),
                        'Cost per km': cost_per_km
                    })
                
                fig_cost_km = px.bar(
                    pd.DataFrame(cost_per_km_data),
                    x='Route',
                    y='Cost per km',
                    title='Cost Efficiency (₹ per km)',
                    color='Cost per km',
                    color_continuous_scale=['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
                )
                fig_cost_km.update_layout(
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#f8fafc',
                    font=dict(color='#0f172a', size=14),
                    showlegend=False,
                    title_font_size=16
                )
                fig_cost_km.update_traces(hovertemplate="Route=%{x}<br>Cost per km=₹%{y:,.2f}<extra></extra>")
                fig_cost_km.update_layout(hoverlabel=dict(font_size=14))
                st.plotly_chart(fig_cost_km, use_container_width=True)
            
            st.markdown("---")
            
            # Section 3: Time and Speed Analysis
            st.markdown("#### ⚡ Time & Speed Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Time comparison
                time_data = pd.DataFrame([
                    {'Route': routes[k].route_name.replace(' (AI Recommended)', ''), 
                     'Time (hours)': routes[k].total_time,
                     'Days': routes[k].total_time / 24}
                    for k in routes.keys()
                ])
                fig_time = px.bar(
                    time_data,
                    x='Route',
                    y='Time (hours)',
                    title='Delivery Time Comparison',
                    color='Time (hours)',
                    color_continuous_scale=['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
                )
                fig_time.update_layout(
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#f8fafc',
                    font=dict(color='#0f172a', size=14),
                    showlegend=False,
                    title_font_size=16
                )
                fig_time.update_traces(hovertemplate="Route=%{x}<br>Time=%{y:.2f} hrs<extra></extra>")
                fig_time.update_layout(hoverlabel=dict(font_size=14))
                st.plotly_chart(fig_time, use_container_width=True)
            
            with col2:
                # Average speed comparison
                speed_data = []
                for k, route in routes.items():
                    avg_speed = route.total_distance / route.total_time if route.total_time > 0 else 0
                    speed_data.append({
                        'Route': route.route_name.replace(' (AI Recommended)', ''),
                        'Avg Speed (km/h)': avg_speed
                    })
                
                fig_speed = px.bar(
                    pd.DataFrame(speed_data),
                    x='Route',
                    y='Avg Speed (km/h)',
                    title='Average Speed Comparison',
                    color='Avg Speed (km/h)',
                    color_continuous_scale=['#ef4444', '#f59e0b', '#3b82f6', '#10b981']
                )
                fig_speed.update_layout(
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#f8fafc',
                    font=dict(color='#0f172a', size=14),
                    showlegend=False,
                    title_font_size=16
                )
                fig_speed.update_traces(hovertemplate="Route=%{x}<br>Avg Speed=%{y:.2f} km/h<extra></extra>")
                fig_speed.update_layout(hoverlabel=dict(font_size=14))
                st.plotly_chart(fig_speed, use_container_width=True)
            
            st.markdown("---")
            
            # Section 4: Environmental Impact
            st.markdown("#### 🌱 Environmental Impact Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Total emissions
                emissions_data = pd.DataFrame([
                    {'Route': routes[k].route_name.replace(' (AI Recommended)', ''), 
                     'CO₂ Emissions (kg)': routes[k].total_emissions}
                    for k in routes.keys()
                ])
                fig_emissions = px.bar(
                    emissions_data,
                    x='Route',
                    y='CO₂ Emissions (kg)',
                    title='Total CO₂ Emissions',
                    color='CO₂ Emissions (kg)',
                    color_continuous_scale=['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
                )
                fig_emissions.update_layout(
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#f8fafc',
                    font=dict(color='#0f172a', size=14),
                    showlegend=False,
                    title_font_size=16
                )
                fig_emissions.update_traces(hovertemplate="Route=%{x}<br>Emissions=%{y:.2f} kg<extra></extra>")
                fig_emissions.update_layout(hoverlabel=dict(font_size=14))
                st.plotly_chart(fig_emissions, use_container_width=True)
            
            with col2:
                # Emissions per kilometer
                emissions_km_data = []
                for k, route in routes.items():
                    emissions_per_km = route.total_emissions / route.total_distance if route.total_distance > 0 else 0
                    emissions_km_data.append({
                        'Route': route.route_name.replace(' (AI Recommended)', ''),
                        'CO₂ per km': emissions_per_km
                    })
                
                fig_emissions_km = px.bar(
                    pd.DataFrame(emissions_km_data),
                    x='Route',
                    y='CO₂ per km',
                    title='Environmental Efficiency (kg CO₂ per km)',
                    color='CO₂ per km',
                    color_continuous_scale=['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
                )
                fig_emissions_km.update_layout(
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#f8fafc',
                    font=dict(color='#0f172a', size=14),
                    showlegend=False,
                    title_font_size=16
                )
                fig_emissions_km.update_traces(hovertemplate="Route=%{x}<br>CO₂ per km=%{y:.2f}<extra></extra>")
                fig_emissions_km.update_layout(hoverlabel=dict(font_size=14))
                st.plotly_chart(fig_emissions_km, use_container_width=True)
            
            st.markdown("---")
            
            # Section 5: Multi-Modal Analysis
            st.markdown("#### 🚦 Transport Mode Utilization")
            
            # Aggregate mode usage across all routes
            mode_distances = {}
            mode_costs = {}
            mode_times = {}
            
            for route in routes.values():
                for segment in route.segments:
                    mode = segment.mode.value
                    mode_distances[mode] = mode_distances.get(mode, 0) + segment.distance
                    mode_costs[mode] = mode_costs.get(mode, 0) + segment.cost
                    mode_times[mode] = mode_times.get(mode, 0) + segment.duration
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Distance by mode
                mode_dist_df = pd.DataFrame([
                    {'Mode': mode.title(), 'Distance (km)': dist}
                    for mode, dist in mode_distances.items()
                ])
                fig_mode_dist = px.pie(
                    mode_dist_df,
                    values='Distance (km)',
                    names='Mode',
                    title='Distance by Mode',
                    color_discrete_sequence=['#FF6B35', '#3B82F6', '#F59E0B', '#06B6D4']
                )
                fig_mode_dist.update_layout(
                    paper_bgcolor='#f8fafc',
                    font=dict(color='#0f172a', size=14),
                    title_font_size=16
                )
                fig_mode_dist.update_traces(hovertemplate="%{label}<br>Distance=%{value:,.2f} km<extra></extra>")
                fig_mode_dist.update_layout(hoverlabel=dict(font_size=14))
                st.plotly_chart(fig_mode_dist, use_container_width=True)
            
            with col2:
                # Cost by mode
                mode_cost_df = pd.DataFrame([
                    {'Mode': mode.title(), 'Cost (₹)': cost}
                    for mode, cost in mode_costs.items()
                ])
                fig_mode_cost = px.pie(
                    mode_cost_df,
                    values='Cost (₹)',
                    names='Mode',
                    title='Cost by Mode',
                    color_discrete_sequence=['#FF6B35', '#3B82F6', '#F59E0B', '#06B6D4']
                )
                fig_mode_cost.update_layout(
                    paper_bgcolor='#f8fafc',
                    font=dict(color='#0f172a', size=14),
                    title_font_size=16
                )
                fig_mode_cost.update_traces(hovertemplate="%{label}<br>Cost=₹%{value:,.2f}<extra></extra>")
                fig_mode_cost.update_layout(hoverlabel=dict(font_size=14))
                st.plotly_chart(fig_mode_cost, use_container_width=True)
            
            with col3:
                # Time by mode
                mode_time_df = pd.DataFrame([
                    {'Mode': mode.title(), 'Time (hours)': time}
                    for mode, time in mode_times.items()
                ])
                fig_mode_time = px.pie(
                    mode_time_df,
                    values='Time (hours)',
                    names='Mode',
                    title='Time by Mode',
                    color_discrete_sequence=['#FF6B35', '#3B82F6', '#F59E0B', '#06B6D4']
                )
                fig_mode_time.update_layout(
                    paper_bgcolor='#f8fafc',
                    font=dict(color='#0f172a', size=14),
                    title_font_size=16
                )
                fig_mode_time.update_traces(hovertemplate="%{label}<br>Time=%{value:.2f} hrs<extra></extra>")
                fig_mode_time.update_layout(hoverlabel=dict(font_size=14))
                st.plotly_chart(fig_mode_time, use_container_width=True)
            
            st.markdown("---")
            
            # Section 6: Key Metrics Summary
            st.markdown("#### 📊 Key Performance Metrics")
            
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            with metrics_col1:
                total_routes = len(routes)
                st.metric("Routes Analyzed", total_routes)
            
            with metrics_col2:
                avg_cost = np.mean([r.final_total_cost for r in routes.values()])
                st.metric("Avg Total Cost", f"₹{avg_cost:,.0f}")
            
            with metrics_col3:
                avg_time = np.mean([r.total_time for r in routes.values()])
                st.metric("Avg Delivery Time", f"{avg_time:.1f} hrs")
            
            with metrics_col4:
                avg_emissions = np.mean([r.total_emissions for r in routes.values()])
                st.metric("Avg Emissions", f"{avg_emissions:,.0f} kg CO₂")
        
        # TAB 5: INSIGHTS
        with tab5:
            st.markdown("### 💡 AI-Generated Insights")
            
            balanced = routes.get('balanced')
            if balanced:
                st.markdown(f"""
                <div class="route-card" style="border-color: #10b981;">
                    <h3>✅ Recommended Route: {balanced.route_name}</h3>
                    <p>Based on your preferences ({cost_pref.label} cost, {time_pref.label} time, {eco_pref.label} eco), 
                    this route offers optimal balance.</p>
                    <ul>
                        <li><strong>Total Cost:</strong> ₹{balanced.total_cost:,.2f}</li>
                        <li><strong>Delivery Time:</strong> {balanced.total_time:.1f} hours ({balanced.total_time/24:.1f} days)</li>
                        <li><strong>Carbon Footprint:</strong> {balanced.total_emissions:,.0f} kg CO₂</li>
                        <li><strong>Reliability Score:</strong> {balanced.average_reliability:.1f}%</li>
                    </ul>
                    <h4>Mode Distribution:</h4>
                    <ul>
                        {''.join([f"<li>{mode.title()}: {percentage:.1f}% of route</li>" for mode, percentage in balanced.mode_percentages.items()])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 📥 Export Results")
            
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'origin': {
                    'city': origin_city,
                    'railway_station': origin.railway_station_name,
                    'airport': origin.airport_code,
                    'seaport': origin.seaport_name
                },
                'destination': {
                    'city': destination_city,
                    'railway_station': destination.railway_station_name,
                    'airport': destination.airport_code,
                    'seaport': destination.seaport_name
                },
                'scenario_flags': {
                    'simulate_road_disruption': simulate_road,
                    'simulate_rail_delay': simulate_rail,
                    'simulate_port_congestion': simulate_port
                },
                'preferences': {
                    'cost': cost_pref.label,
                    'time': time_pref.label,
                    'environmental': eco_pref.label
                },
                'routes': {
                    k: {
                        'name': v.route_name,
                        'cost_inr': v.total_cost,
                        'carbon_cost': v.carbon_cost,
                        'adjusted_total_cost': v.adjusted_total_cost,
                        'sla_penalty': v.sla_penalty,
                        'final_total_cost': v.final_total_cost,
                        'time_hours': v.total_time,
                        'distance_km': v.total_distance,
                        'emissions_kg': v.total_emissions,
                        'reliability': v.average_reliability,
                        'segments': len(v.segments),
                        'mode_percentages': v.mode_percentages
                    } for k, v in routes.items()
                }
            }
            
            st.download_button(
                label="📥 Download Complete Results (JSON)",
                data=json.dumps(export_data, indent=2),
                file_name=f"transport_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

            st.markdown("---")
            with st.expander("📐 Optimization Model Formulation"):
                st.markdown("""
                <div style='background:#f8fafc; border:2px solid #94a3b8; padding:16px; border-radius:10px; color:#0f172a;'>
                    <div style='font-size:1.1rem; font-weight:800; margin-bottom:8px;'>Decision Variable</div>
                    <div style='font-size:1.05rem; font-weight:600; margin-bottom:12px;'>x<sub>ij</sub><sup>m</sup> ∈ {0,1}</div>
                    <div style='font-size:1.1rem; font-weight:800; margin-bottom:8px;'>Objective</div>
                    <div style='font-size:1.05rem; font-weight:600; margin-bottom:12px;'>
                        Minimize Z = TransportCost + CarbonCost + SLAPenalty
                    </div>
                    <div style='font-size:1.1rem; font-weight:800; margin-bottom:8px;'>Subject to</div>
                    <ul style='margin:0 0 0 18px; color:#0f172a; font-weight:600;'>
                        <li>Mode feasibility constraints</li>
                        <li>Infrastructure availability constraints</li>
                        <li>Demand satisfaction</li>
                        <li>SLA constraint</li>
                        <li>Optional emission constraint</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        # TAB 6: SCENARIO SIMULATION
        with tab6:
            st.markdown("### 🧪 Scenario Simulation (Digital Twin)")
            if not (simulate_road or simulate_rail or simulate_port):
                st.info("Enable one or more scenario toggles in the sidebar to simulate disruptions.")
            else:
                rows = []
                for key in routes.keys():
                    base = routes[key]
                    sim = simulated_routes[key]
                    cost_change = ((sim.final_total_cost - base.final_total_cost) / base.final_total_cost * 100) if base.final_total_cost > 0 else 0
                    time_change = ((sim.total_time - base.total_time) / base.total_time * 100) if base.total_time > 0 else 0
                    rows.append({
                        "Route": base.route_name,
                        "Base Cost (₹)": f"₹{base.final_total_cost:,.0f}",
                        "Sim Cost (₹)": f"₹{sim.final_total_cost:,.0f}",
                        "% Cost Change": f"{cost_change:.2f}%",
                        "Base Time (hrs)": f"{base.total_time:.2f}",
                        "Sim Time (hrs)": f"{sim.total_time:.2f}",
                        "% Time Change": f"{time_change:.2f}%"
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # TAB 7: BUSINESS IMPACT
        with tab7:
            st.markdown("### 💼 Business Impact (ROI Calculator)")
            avg_route_cost = float(np.mean([r.final_total_cost for r in routes.values()]))
            st.markdown(f"**Baseline Avg Cost per Shipment:** ₹{avg_route_cost:,.0f}")

            investment = st.number_input("Digital Investment (₹)", min_value=0.0, value=1500000.0, step=50000.0)
            annual_volume = st.number_input("Annual Shipment Volume", min_value=1.0, value=1200.0, step=50.0)
            savings_pct = st.number_input("Expected % Cost Reduction", min_value=0.0, max_value=100.0, value=8.0, step=0.5)
            adoption_rate = st.number_input("Adoption Rate (%)", min_value=0.0, max_value=100.0, value=85.0, step=1.0)
            annual_opex = st.number_input("Annual Operating Cost (₹)", min_value=0.0, value=250000.0, step=25000.0)

            gross_savings = avg_route_cost * annual_volume * (savings_pct / 100) * (adoption_rate / 100)
            net_annual_benefit = gross_savings - annual_opex
            payback_period = (investment / net_annual_benefit) if net_annual_benefit > 0 else 0
            roi_pct = ((net_annual_benefit - investment) / investment * 100) if investment > 0 else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Gross Annual Savings", f"₹{gross_savings:,.0f}")
            col2.metric("Net Annual Benefit", f"₹{net_annual_benefit:,.0f}")
            col3.metric("Payback Period (years)", f"{payback_period:.2f}")
            col4.metric("ROI %", f"{roi_pct:.2f}%")

            roi_df = pd.DataFrame({
                "Metric": ["Investment", "Gross Savings", "Operating Cost", "Net Benefit"],
                "Value": [investment, gross_savings, annual_opex, net_annual_benefit]
            })
            fig_roi = px.bar(roi_df, x="Metric", y="Value", title="Investment vs Annual Savings",
                             color="Value", color_continuous_scale=["#0ea5e9", "#22c55e"])
            fig_roi.update_layout(
                plot_bgcolor='#ffffff',
                paper_bgcolor='#f8fafc',
                font=dict(color='#0f172a', size=14),
                showlegend=False
            )
            fig_roi.update_traces(hovertemplate="%{x}<br>₹%{y:,.2f}<extra></extra>")
            st.plotly_chart(fig_roi, use_container_width=True)


if __name__ == "__main__":
    main()
