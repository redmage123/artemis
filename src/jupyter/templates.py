#!/usr/bin/env python3
"""
WHY: Provide pre-built notebook templates for common use cases
RESPONSIBILITY: Generate data analysis and ML notebook templates
PATTERNS:
- Template method pattern for notebook structure
- Factory functions for different notebook types
- Composition of NotebookBuilder

This module provides convenience functions for creating common notebook
types without boilerplate code.
"""

from typing import Dict, List, Any

from .notebook_builder import NotebookBuilder


def create_data_analysis_notebook(
    title: str,
    data_source: str,
    analysis_steps: List[str]
) -> Dict[str, Any]:
    """
    WHY: Create data analysis notebook template quickly
    RESPONSIBILITY: Generate notebook with common data analysis structure

    Args:
        title: Notebook title
        data_source: Description of data source
        analysis_steps: List of analysis step descriptions

    Returns:
        Complete notebook ready to save
    """
    builder = NotebookBuilder(title)

    # Add data loading section
    builder.add_section("Data Loading", f"Load data from: {data_source}")
    builder.add_code(
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n\n"
        "# Set plotting style\n"
        "sns.set_style('whitegrid')\n"
        "plt.rcParams['figure.figsize'] = (12, 6)"
    )

    # Add analysis sections
    for i, step in enumerate(analysis_steps, 1):
        builder.add_section(f"Step {i}: {step}")
        builder.add_code(f"# TODO: Implement {step}\npass")

    # Add conclusion section
    builder.add_section(
        "Conclusions",
        "Summary of findings and next steps"
    )

    return builder.build()


def create_ml_notebook(
    title: str,
    model_type: str,
    features: List[str]
) -> Dict[str, Any]:
    """
    WHY: Create machine learning notebook template quickly
    RESPONSIBILITY: Generate notebook with ML workflow structure

    Args:
        title: Notebook title
        model_type: Type of ML model (classification, regression, clustering)
        features: List of feature names

    Returns:
        Complete notebook ready to save
    """
    builder = NotebookBuilder(title)

    # Import libraries
    builder.add_section("Setup", "Import required libraries")
    builder.add_code(
        "import pandas as pd\n"
        "import numpy as np\n"
        "from sklearn.model_selection import train_test_split\n"
        "from sklearn.preprocessing import StandardScaler\n"
        "from sklearn.metrics import classification_report, confusion_matrix\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns"
    )

    # Data loading
    builder.add_section("Data Loading")
    builder.add_code(
        "# Load dataset\n"
        "df = pd.read_csv('data.csv')\n"
        "df.head()"
    )

    # Feature engineering
    feature_list = ', '.join(features)
    builder.add_section(
        "Feature Engineering",
        f"Selected features: {feature_list}"
    )

    features_str = ', '.join([f"'{f}'" for f in features])
    builder.add_code(
        f"features = [{features_str}]\n"
        "X = df[features]\n"
        "y = df['target']\n\n"
        "# Split data\n"
        "X_train, X_test, y_train, y_test = train_test_split("
        "X, y, test_size=0.2, random_state=42)"
    )

    # Model training
    builder.add_section("Model Training", f"Train {model_type} model")
    builder.add_code(
        "# Initialize and train model\n"
        f"# TODO: Select appropriate model for {model_type}\n"
        "model = None  # Replace with actual model\n"
        "# model.fit(X_train, y_train)"
    )

    # Evaluation
    builder.add_section("Model Evaluation")
    builder.add_code(
        "# Make predictions\n"
        "# y_pred = model.predict(X_test)\n\n"
        "# Evaluate model\n"
        "# TODO: Add evaluation metrics"
    )

    return builder.build()


def create_exploratory_notebook(title: str) -> Dict[str, Any]:
    """
    WHY: Create exploratory data analysis notebook template
    RESPONSIBILITY: Generate notebook with EDA structure

    Args:
        title: Notebook title

    Returns:
        Complete notebook ready to save
    """
    builder = NotebookBuilder(title)

    # Setup
    builder.add_section("Setup", "Import libraries and configure environment")
    builder.add_code(
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n\n"
        "# Configure display options\n"
        "pd.set_option('display.max_columns', None)\n"
        "pd.set_option('display.max_rows', 100)\n"
        "sns.set_style('whitegrid')"
    )

    # Data loading
    builder.add_section("Data Loading", "Load and inspect dataset")
    builder.add_code(
        "# Load data\n"
        "df = pd.read_csv('data.csv')\n\n"
        "# Basic info\n"
        "print(f'Shape: {df.shape}')\n"
        "df.head()"
    )

    # Data overview
    builder.add_section("Data Overview", "Understanding the dataset")
    builder.add_code(
        "# Data types and missing values\n"
        "df.info()\n\n"
        "# Summary statistics\n"
        "df.describe()"
    )

    # Missing values
    builder.add_section("Missing Values Analysis")
    builder.add_code(
        "# Check for missing values\n"
        "missing = df.isnull().sum()\n"
        "missing[missing > 0].sort_values(ascending=False)"
    )

    # Distribution analysis
    builder.add_section("Distribution Analysis")
    builder.add_code(
        "# Plot distributions\n"
        "# TODO: Add distribution plots for key variables"
    )

    # Correlation analysis
    builder.add_section("Correlation Analysis")
    builder.add_code(
        "# Correlation matrix\n"
        "plt.figure(figsize=(12, 8))\n"
        "sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0)\n"
        "plt.title('Correlation Matrix')\n"
        "plt.show()"
    )

    # Key findings
    builder.add_section("Key Findings", "Summary of insights")

    return builder.build()
