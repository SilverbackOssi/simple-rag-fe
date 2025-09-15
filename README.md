# RAG Search Platform Frontend

A modular Streamlit frontend for a RAG-based People and Business Intelligence Search Platform. This Stage 2 implementation provides core components for search, results display, and interactive graph visualization.

## 🚀 Features

### Search Interface
- **Smart Search Input**: Text-based queries with real-time validation
- **Search Modes**: Fast Retrieval vs Enhanced Generation with AI summaries
- **Entity Filters**: Filter by People, Business, or Assets
- **Autocomplete**: Dynamic suggestions via `/suggest` API
- **Advanced Options**: Configurable result limits and parameters

### Results Display
- **Tabbed Sections**: Organized display of Business, People, Social Profiles, and AI Summaries
- **Interactive Data**: Sortable tables with CSV export functionality
- **Metrics Dashboard**: Real-time result counts and statistics
- **Error Handling**: Graceful degradation with retry mechanisms

### Graph Visualization
- **Interactive Networks**: PyVis-powered relationship graphs
- **Multiple Layouts**: Hierarchical, Physics-based, and Circular arrangements
- **Depth Control**: 1-3 level relationship traversals
- **Color Coding**: Entity type-based node coloring
- **Performance Optimized**: <50 node limit for responsive rendering

## 🏗️ Architecture

### Project Structure
```
simple-rag-fe/
├── app.py                 # Main Streamlit application
├── components/            # Modular UI components
│   ├── __init__.py
│   ├── search.py         # Search interface
│   ├── results.py        # Results display
│   └── graph.py          # Graph visualization
├── utils/                # Utility functions
│   ├── __init__.py
│   └── api.py            # Backend API integration
├── requirements.txt      # Dependencies
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

### Backend Integration
The frontend integrates with these FastAPI endpoints:

- **POST /search**: Main search functionality
  ```json
  {
    "q": "query string",
    "mode": "fast|enhanced", 
    "filters": {"entity_type": ["people", "business", "assets"]}
  }
  ```

- **GET /graph**: Relationship traversal
  ```
  ?entity_id=123&depth=2
  ```

- **POST /generate**: AI summary generation
  ```json
  {"context": {...}}
  ```

- **GET /suggest**: Query autocomplete
  ```
  ?q=partial_query
  ```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.12+
- Backend API server (optional for frontend testing)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Configuration
Set backend URL via Streamlit secrets in `.streamlit/secrets.toml`:
```toml
BACKEND_URL = "http://your-backend-url:8000"
```

## 📊 Usage

1. **Start a Search**: Enter your query in the sidebar search box
2. **Select Mode**: Choose Fast Retrieval or Enhanced Generation
3. **Apply Filters**: Optionally filter by entity types
4. **View Results**: Browse tabbed sections for different data types
5. **Explore Relationships**: Use the interactive graph to visualize connections
6. **Export Data**: Download results as CSV files

### Example Queries
- **People**: "John Smith CEO", "Tech startup founders"
- **Business**: "AI companies San Francisco", "Fortune 500"  
- **Relationships**: "Board member connections", "Investment networks"

## 🎨 UI Features

- **Responsive Design**: Wide layout optimized for data visualization
- **Custom Styling**: Professional CSS theming
- **Intuitive Navigation**: Sidebar inputs, main content area
- **Progress Indicators**: Loading states and status messages
- **Error Recovery**: Retry buttons and helpful error messages

## 🔧 Technical Specifications

- **Framework**: Streamlit 1.38.0
- **Data Handling**: pandas 2.2.2
- **Graph Visualization**: pyvis 0.3.2
- **HTTP Client**: requests 2.32.3
- **Performance**: Sub-1s rendering target
- **State Management**: Streamlit session state
- **Modularity**: Component-based architecture

## 🌐 Browser Compatibility

Tested and optimized for modern web browsers including Chrome, Firefox, Safari, and Edge.

## 🚦 Status

**Stage 2: Core Component Development** ✅ Complete

All functional and non-functional requirements met:
- ✅ User-friendly search interface
- ✅ Aggregated response handling  
- ✅ Interactive graph visualization
- ✅ Backend API integration
- ✅ Error handling and validation
- ✅ Responsive design
- ✅ Performance optimization

## 📄 License

This project is part of a POC implementation for RAG-based business intelligence search.