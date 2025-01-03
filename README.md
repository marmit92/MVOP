# MCDA Decision Support System

This project is a **Decision Support System (DSS)** built using **Multiple-Criteria Decision Analysis (MCDA)** methods. It provides users with tools to make informed investment decisions by analyzing and ranking Fortune 500 companies based on user-defined criteria and weights.

## Features

1. **Company Selection**:
   - Choose from subsets of Fortune 500 companies (top 20 companies by revenue).
   - Provides diversity across industries, including tech, retail, and energy.

2. **Criteria Definition**:
   - Analyze companies based on revenue, profit, assets, employee count, and percentage changes in revenue and profit.
   - User-defined weights allow for tailored analyses.

3. **MCDA Methods**:
   - Implements **TOPSIS**, **PROMETHEE**, **WSM**, **VIKOR**, and **MACBETH**.
   - Methods rank companies and provide visual and tabular results.

4. **Comparison Tool**:
   - Compare results across different MCDA methods.
   - Visualize differences in rankings and understand how criteria affect outcomes.

5. **Interactive User Interface**:
   - Intuitive design built with **Bootstrap** for a responsive and user-friendly experience.
   - Features dynamic dropdowns, interactive tables, and customizable options.

## Architecture

### Technologies
- **Frontend**: HTML, CSS, Bootstrap
- **Backend**: Flask (Python)
- **Database**: MongoDB (NoSQL)
- **Visualization**: Chart.js for interactive graphs

### Structure
- **Frontend**: User-friendly interface for selecting companies, criteria, and MCDA methods.
- **Backend**: Handles computations for MCDA methods, manages database queries, and routes.
- **Database**: Stores company data, analysis results, and configurations.

## How to Run

### Prerequisites
- Python 3.8+
- MongoDB installed and running

### Setup Instructions
1. Clone this repository:
   ```bash
   git clone <repository-url>
