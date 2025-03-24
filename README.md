# MaLDReTH Research Data Lifecycle Visualization

This Streamlit application visualizes the MaLDReTH Research Data Lifecycle with tool exemplars, implemented in a style similar to the Harvard RDM visualization.

![MaLDReTH Research Data Lifecycle](https://raw.githubusercontent.com/adammoore/maldreth-visualization/main/utils/preview.png)

## Features

- Interactive circular visualization of the Research Data Lifecycle
- Three view modes: Complete Lifecycle, Focus on Stage, and Compare Tools
- Display tool exemplars for each lifecycle stage
- Filter connections by type (normal, alternative)
- Detailed information panel for selected stages
- Responsive design that works on desktop and mobile devices
- Data automatically loaded from JSON file

## Live Demo

You can access the live demo here: [MaLDReTH Visualization on Streamlit Cloud](https://maldreth-arcs.streamlit.app/)

## Local Development

### Prerequisites

- Python 3.8 or higher
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/adammoore/maldreth-visualization.git
   cd maldreth-visualization
   ```

2. Create and activate a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```

5. Open your browser and navigate to http://localhost:8501

## Project Structure
```text
maldreth-visualization/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration settings
├── utils/
│   ├── __init__.py        # Make utils a package
│   ├── data_loader.py     # Data loading utilities
│   ├── visualization.py   # Visualization functions
│   └── styles.css         # Custom CSS styling
├── data/
│   └── lifecycle_data.json # Data for visualization
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Actions workflow for deployment
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── requirements.txt       # Dependencies
└── README.md              # Project documentation
```

### Customizing the Data
The visualization uses data from data/lifecycle_data.json. You can customize this file to add, remove, or modify stages, connections, and tool exemplars.
If the file doesn't exist, the application will create it with sample data. The data structure is as follows:
```json{
  "stages": [
    {
      "name": "StageName",
      "description": "Stage description",
      "color": "#hexcolor"
    },
    ...
  ],
  "connections": [
    {
      "from": "SourceStage",
      "to": "DestinationStage",
      "type": "normal|alternative"
    },
    ...
  ],
  "exemplars": [
    {
      "stage": "StageName",
      "category": "ToolCategory",
      "name": "ToolName",
      "description": "Tool description"
    },
    ...
  ]
}
```

## Deployment
### Deploying to Streamlit Cloud

Fork this repository to your GitHub account.
Go to Streamlit Cloud and sign in with your GitHub account.
Click "New app" and select your forked repository.
Choose the app.py file as the main file and click "Deploy".
Your app will be deployed and automatically updated whenever you push changes to your GitHub repository.

### Adding a Custom Domain
If you want to use a custom domain with your Streamlit app:

In the Streamlit Cloud dashboard, go to your app settings.
Under "Custom domain", enter your domain name.
Follow the instructions to configure DNS settings for your domain.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

### Fork the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
## Acknowledgments

This visualization is based on the MaLDReTH Research Data Lifecycle model.
Data sourced from the RDA-OfR Mapping the Landscape of Digital Research Tools Working Group.
