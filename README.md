# Assessor
A tool for analyzing the quality of human-AI interactions using the Cognitive Resonance & Alignment (CR&A) Framework.

## **Quick Start**

### **1. Installation**
**Clone the repository:**
  ``` bash
   git clone https://github.com/Research-FormianLabs/assessor.git
   cd assessor
```

### **2. Install Dependencies**

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

### **3. Run the Application**

Start the web server:

```bash
python3 app.py
```

### **4. Open Your Browser**

Go to: `http://127.0.0.1:5000`

### **5. Analyze an Interaction**

1. Paste a **User Prompt** (what the human said to the AI)
2. Paste the **AI Response** (what the AI replied)
3. Click "Analyze Interaction"
4. View the Resonance Index and dimension scores

## **What It Measures**

The Assessor evaluates interactions across six dimensions:
- **IAI** - Input Alignment (quality of the user's prompt)
- **CAI** - Conceptual Anchoring (structure in AI's response)
- **PAS** - Process Alignment (naturalness of conversation)
- **SAS** - Synchronization (style matching)
- **CPS** - Cognitive Progression (depth of collaboration)
- **CSS** - Cognitive Safety (user comfort level)

## **For Developers**

### **Project Structure**
```
assessor/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── dimensions/         # Individual analyzers
│   ├── iai.py         # Input Alignment analyzer
│   ├── cai.py         # Conceptual Anchoring analyzer
│   └── ...            # Other dimension analyzers
├── templates/          # Web page templates
│   ├── base.html      # Main layout
│   └── index.html     # Analysis form
└── static/            # CSS and JavaScript
    ├── css/
    └── js/
```

### **Contributing to Individual Dimensions**

Each dimension analyzer is independent. To improve one:

1. **Pick a dimension** (e.g., `sas.py` for Synchronization Alignment)
2. **Study the existing code** - each file has simple scoring rules
3. **Make improvements** without changing other files
4. **Test your changes** and submit improvements

## **About the CR&A Framework**

This tool implements the Cognitive Resonance & Alignment Framework, which provides scientific metrics for measuring the quality of human-AI collaboration beyond just factual accuracy.

## **Support**

For questions or contributions, please open an issue or discussion in this repository.
