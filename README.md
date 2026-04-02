# PashuScore – Cattle Credit Intelligence System

**Developed by Mohan | NSTI Chennai**

PashuScore is a personal project built to explore how technology can support **rural finance**, **livestock-based credit evaluation**, and **data-driven decision making**.

Many small farmers may own valuable cattle assets but often lack formal credit history. This can make loan access difficult.  
PashuScore addresses this by evaluating a farmer’s **loan eligibility** based on cattle-related data such as herd size, breed quality, vaccination status, health condition, and milk yield.

The system calculates a **credit score out of 100**, assigns a **grade**, and estimates the **maximum eligible loan amount**.

---

## Features

- Dashboard overview for all registered farmers
- Individual farmer credit score calculation
- Village batch scoring
- Cattle registry management
- Vaccination overdue alerts
- Loan application submission and status tracking
- Farmer and cattle registration

---

## Credit Scoring Logic

The credit score is calculated using the following factors:

- **Herd Size** → Maximum 20 points
- **Breed Quality** → Maximum 30 points
- **Vaccination Status** → Maximum 25 points
- **Animal Health** → Maximum 15 points
- **Milk Yield** → Maximum 10 points

### Grade Mapping
- **A+** → 80 and above
- **A** → 65 to 79
- **B** → 50 to 64
- **C** → 35 to 49
- **D** → Below 35

### Loan Eligibility Mapping
- **A+** → ₹2,00,000
- **A** → ₹1,50,000
- **B** → ₹75,000
- **C** → ₹25,000
- **D** → Not eligible

---

## Tech Stack

- Python
- Streamlit
- MySQL
- Pandas
- Plotly

---

## Project Structure

```bash
PashuScore/
│
├── app.py
├── pashuscore.sql
├── requirements.txt
├── README.md
└── screenshots/
