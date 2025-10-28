#!/usr/bin/env python3
"""
Module: cell_generator.py

WHY: Centralizes the logic for generating notebook cells based on notebook type.
     Separates cell generation concerns from orchestration logic.

RESPONSIBILITY:
- Generate type-specific notebook cells (data analysis, ML, API demo, etc.)
- Build notebook structure using NotebookBuilder pattern
- Extract and parse content requirements from cards
- Apply templates for different notebook types

PATTERNS:
- Strategy Pattern: Different cell generation strategies per notebook type
- Builder Pattern: Uses NotebookBuilder to construct notebooks incrementally
- Dispatch Table: O(1) lookup for generator functions
- Template Method: Common structure with type-specific customization
"""

from typing import Dict, Any, List, Callable, Optional
from jupyter_notebook_handler import NotebookBuilder


class CellGeneratorStrategy:
    """
    Strategy for generating notebook cells based on type

    WHY: Encapsulates cell generation logic for different notebook types
    RESPONSIBILITY: Provide consistent interface for all cell generators
    """

    def __init__(self):
        """Initialize cell generator with dispatch table"""
        # Dispatch table for O(1) generator lookup
        self._generators: Dict[str, Callable] = {
            'data_analysis': self._generate_data_analysis_cells,
            'machine_learning': self._generate_ml_cells,
            'api_demo': self._generate_api_demo_cells,
            'test_visualization': self._generate_test_viz_cells,
            'documentation': self._generate_documentation_cells,
            'general': self._generate_general_cells
        }

    def generate_cells(
        self,
        notebook_type: str,
        card: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate cells for specified notebook type

        Time Complexity: O(n) where n = number of cells
        Space Complexity: O(n) for cell storage

        Args:
            notebook_type: Type of notebook (data_analysis, ml, etc.)
            card: Kanban card with task information
            context: Additional context from pipeline

        Returns:
            Complete notebook dictionary with cells
        """
        # Guard clause: validate notebook type
        if notebook_type not in self._generators:
            return self._generate_general_cells(card, context)

        # Dispatch to type-specific generator (O(1) lookup)
        generator_func = self._generators[notebook_type]
        return generator_func(card, context)

    def _generate_data_analysis_cells(
        self,
        card: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate data analysis notebook cells

        WHY: Data analysis notebooks need data loading, exploration,
             cleaning, analysis, and visualization cells
        """
        title = card.get('title', 'Data Analysis')
        description = card.get('description', '')
        data_source = context.get('data_source', 'data.csv')

        builder = NotebookBuilder(title)

        # Title and overview
        builder.add_markdown(f"# {title}\n\n{description}")

        # Setup section
        builder.add_section("Setup", "Import required libraries")
        builder.add_code(
            "import pandas as pd\n"
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n\n"
            "sns.set_style('whitegrid')\n"
            "%matplotlib inline"
        )

        # Data loading
        builder.add_section("Load Data", f"Load data from {data_source}")
        builder.add_code(
            f"# Load dataset\n"
            f"df = pd.read_csv('{data_source}')\n"
            f"print(f'Shape: {{df.shape}}')\n"
            f"df.head()"
        )

        # Exploration
        builder.add_section("Data Exploration", "Explore dataset structure")
        builder.add_code(
            "# Basic statistics\n"
            "df.describe()\n\n"
            "# Check for missing values\n"
            "df.isnull().sum()"
        )

        # Analysis steps from card
        analysis_steps = self._extract_analysis_steps(description)
        if analysis_steps:
            builder.add_section("Analysis Steps", "Step-by-step analysis")
            for i, step in enumerate(analysis_steps, 1):
                builder.add_markdown(f"### Step {i}: {step}")
                builder.add_code(f"# TODO: Implement {step}\npass")

        # Visualization
        builder.add_section("Visualizations", "Data visualizations")
        builder.add_code(
            "# Create visualizations\n"
            "plt.figure(figsize=(12, 6))\n"
            "# TODO: Add specific visualizations\n"
            "plt.show()"
        )

        # Conclusions
        builder.add_section("Conclusions", "Key findings")
        builder.add_markdown("TODO: Document findings and insights")

        return builder.build()

    def _generate_ml_cells(
        self,
        card: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate machine learning notebook cells

        WHY: ML notebooks need data prep, model training,
             evaluation, and prediction cells
        """
        title = card.get('title', 'Machine Learning Experiment')
        model_type = context.get('model_type', 'classification')
        features = context.get('features', ['feature_1', 'feature_2', 'feature_3'])

        builder = NotebookBuilder(title)

        # Title
        builder.add_markdown(f"# {title}\n\nMachine Learning: {model_type}")

        # Setup
        builder.add_section("Setup", "Import ML libraries")
        builder.add_code(
            "import pandas as pd\n"
            "import numpy as np\n"
            "from sklearn.model_selection import train_test_split\n"
            "from sklearn.preprocessing import StandardScaler\n"
            "from sklearn.metrics import classification_report, confusion_matrix\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns"
        )

        # Data preparation
        builder.add_section("Data Preparation", "Load and prepare data")
        features_str = ', '.join(f"'{f}'" for f in features)
        builder.add_code(
            f"# Load data\n"
            f"df = pd.read_csv('data.csv')\n\n"
            f"# Select features\n"
            f"features = [{features_str}]\n"
            f"X = df[features]\n"
            f"y = df['target']\n\n"
            f"# Train/test split\n"
            f"X_train, X_test, y_train, y_test = train_test_split(\n"
            f"    X, y, test_size=0.2, random_state=42\n"
            f")"
        )

        # Model training
        builder.add_section("Model Training", f"Train {model_type} model")
        builder.add_code(
            "# Scale features\n"
            "scaler = StandardScaler()\n"
            "X_train_scaled = scaler.fit_transform(X_train)\n"
            "X_test_scaled = scaler.transform(X_test)\n\n"
            "# Train model\n"
            "# TODO: Import and configure specific model\n"
            "# model = SomeModel()\n"
            "# model.fit(X_train_scaled, y_train)"
        )

        # Evaluation
        builder.add_section("Model Evaluation", "Evaluate model performance")
        builder.add_code(
            "# Make predictions\n"
            "# y_pred = model.predict(X_test_scaled)\n\n"
            "# Print metrics\n"
            "# print(classification_report(y_test, y_pred))\n\n"
            "# Confusion matrix\n"
            "# cm = confusion_matrix(y_test, y_pred)\n"
            "# sns.heatmap(cm, annot=True, fmt='d')\n"
            "# plt.show()"
        )

        return builder.build()

    def _generate_api_demo_cells(
        self,
        card: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate API demo notebook cells

        WHY: API demos need setup, configuration, and example request cells
        """
        title = card.get('title', 'API Demo')
        description = card.get('description', '')

        builder = NotebookBuilder(title)

        # Title
        builder.add_markdown(f"# {title}\n\n{description}")

        # Setup
        builder.add_section("Setup", "Install and import libraries")
        builder.add_code(
            "# Install requirements\n"
            "# !pip install requests\n\n"
            "import requests\n"
            "import json\n"
            "from typing import Dict, Any"
        )

        # Configuration
        builder.add_section("Configuration", "API credentials and endpoints")
        builder.add_code(
            "# API Configuration\n"
            "BASE_URL = 'https://api.example.com'\n"
            "API_KEY = 'your-api-key-here'\n\n"
            "headers = {\n"
            "    'Authorization': f'Bearer {API_KEY}',\n"
            "    'Content-Type': 'application/json'\n"
            "}"
        )

        # GET example
        builder.add_section("GET Request", "Fetch data from API")
        builder.add_code(
            "# GET request example\n"
            "response = requests.get(f'{BASE_URL}/endpoint', headers=headers)\n"
            "print(f'Status: {response.status_code}')\n"
            "print(json.dumps(response.json(), indent=2))"
        )

        # POST example
        builder.add_section("POST Request", "Submit data to API")
        builder.add_code(
            "# POST request example\n"
            "data = {'key': 'value'}\n"
            "response = requests.post(f'{BASE_URL}/endpoint', headers=headers, json=data)\n"
            "print(f'Status: {response.status_code}')\n"
            "print(json.dumps(response.json(), indent=2))"
        )

        return builder.build()

    def _generate_test_viz_cells(
        self,
        card: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate test visualization notebook cells

        WHY: Test visualization needs data loading, metrics calculation,
             and chart generation cells
        """
        title = card.get('title', 'Test Results Visualization')

        builder = NotebookBuilder(title)

        # Title
        builder.add_markdown(f"# {title}\n\nVisualize test execution results")

        # Setup
        builder.add_section("Setup", "Import visualization libraries")
        builder.add_code(
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "import json\n\n"
            "sns.set_style('whitegrid')\n"
            "%matplotlib inline"
        )

        # Load results
        builder.add_section("Load Test Results", "Read test data")
        builder.add_code(
            "# Load test results\n"
            "with open('test_results.json', 'r') as f:\n"
            "    test_data = json.load(f)\n\n"
            "df = pd.DataFrame(test_data)\n"
            "df.head()"
        )

        # Pass/Fail distribution
        builder.add_section("Pass/Fail Distribution", "Test outcome summary")
        builder.add_code(
            "# Pass/Fail pie chart\n"
            "status_counts = df['status'].value_counts()\n"
            "plt.figure(figsize=(8, 6))\n"
            "plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%')\n"
            "plt.title('Test Results Distribution')\n"
            "plt.show()"
        )

        # Duration analysis
        builder.add_section("Duration Analysis", "Test execution times")
        builder.add_code(
            "# Duration histogram\n"
            "plt.figure(figsize=(10, 6))\n"
            "plt.hist(df['duration'], bins=30, edgecolor='black')\n"
            "plt.xlabel('Duration (seconds)')\n"
            "plt.ylabel('Number of Tests')\n"
            "plt.title('Test Execution Duration')\n"
            "plt.show()"
        )

        return builder.build()

    def _generate_documentation_cells(
        self,
        card: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate documentation notebook cells

        WHY: Documentation notebooks need installation, usage,
             and example cells
        """
        title = card.get('title', 'Documentation')
        description = card.get('description', '')

        builder = NotebookBuilder(title)

        # Title
        builder.add_markdown(f"# {title}\n\n{description}")

        # Overview
        builder.add_section("Overview", "Project documentation")

        # Installation
        builder.add_section("Installation", "Setup instructions")
        builder.add_code(
            "# Install the package\n"
            "# !pip install package-name\n\n"
            "# Verify installation\n"
            "import package_name\n"
            "print(f'Version: {package_name.__version__}')"
        )

        # Basic usage
        builder.add_section("Basic Usage", "Common use cases")
        builder.add_code(
            "# Import library\n"
            "from package_name import MainClass\n\n"
            "# Create instance\n"
            "obj = MainClass()\n\n"
            "# Use functionality\n"
            "result = obj.method()\n"
            "print(result)"
        )

        # Advanced features
        builder.add_section("Advanced Features", "Advanced functionality")
        builder.add_code(
            "# Advanced usage\n"
            "# TODO: Add advanced examples\n"
            "pass"
        )

        return builder.build()

    def _generate_general_cells(
        self,
        card: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate general purpose notebook cells

        WHY: Fallback for notebooks that don't fit specific types
        """
        title = card.get('title', 'Notebook')
        description = card.get('description', '')

        builder = NotebookBuilder(title)

        # Title
        builder.add_markdown(f"# {title}\n\n{description}")

        # Setup
        builder.add_section("Setup", "Import libraries")
        builder.add_code(
            "# Import standard libraries\n"
            "import os\n"
            "import sys\n"
            "from pathlib import Path\n\n"
            "print('Setup complete')"
        )

        # Main content
        builder.add_section("Main Content", "Primary notebook content")
        builder.add_code(
            "# TODO: Add implementation\n"
            "pass"
        )

        # Results
        builder.add_section("Results", "Output and conclusions")
        builder.add_markdown("TODO: Add results and analysis")

        return builder.build()

    def _extract_analysis_steps(self, description: str) -> List[str]:
        """
        Extract analysis steps from description text

        Time Complexity: O(n) where n = description length
        Space Complexity: O(m) where m = number of steps

        Args:
            description: Task description text

        Returns:
            List of extracted analysis steps
        """
        steps: List[str] = []

        # Guard clause: empty description
        if not description:
            return []

        lines = description.split('\n')

        # Single pass through lines
        for line in lines:
            line = line.strip()

            # Guard clause: empty line
            if not line:
                continue

            # Check for numbered or bulleted items
            if line[0].isdigit() or line.startswith('-') or line.startswith('*'):
                # Remove numbering/bullets
                clean_step = line.lstrip('0123456789.-* ')
                if clean_step:
                    steps.append(clean_step)

        return steps
