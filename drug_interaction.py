# filename: drug_interaction_app.py
import streamlit as st
import pandas as pd
import os
import re

# --- Page Setup ---
st.set_page_config(page_title="Drug Interaction Checker", layout="centered")

# --- Light blue background & text/input styles ---
st.markdown(
    """
    <style>
    .stApp { background-color: #d0e7ff; font-size: 20px; color: #222222; }
    label, .stSelectbox label, .stNumberInput label, .stTextInput label, .stTextArea label {
        font-size: 28px !important; color: #000000 !important; font-weight: 600 !important;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > textarea,
    .stSelectbox > div > div {
        background-color: #000000 !important; color: #ffffff !important;
        font-size: 18px !important; border-radius: 8px; border: 1px solid #888;
    }
    .result-text {
        font-size: 22px !important; color: #000000;
        background-color: rgba(255,255,255,0.85); padding: 15px; border-radius: 10px;
    }
    .subtitle {
        font-size: 35px !important; font-weight: 600; color: #023047 !important; margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Title ---
st.markdown(
    """
    <div style="font-size:50px; font-weight:bold; color:#006d77; text-align:center; line-height:1.2; margin-bottom:20px;">
        💊 Drug Interaction Detection System 💊
    </div>
    """, unsafe_allow_html=True
)

# --- Excel Paths ---
original_excel_path = r"C:\Users\Nichitha Reddy\Desktop\drug_interaction_xlsheet.xlsx"
updated_excel_path = r"C:\Users\Nichitha Reddy\Downloads\drug_interaction_updated.xlsx"

# --- Interaction Dictionary ---
interaction_dict = {}

# --- Load Excel Data ---
try:
    df = pd.read_excel(original_excel_path)

    # Use lowercase consistent column names
    df.columns = df.columns.str.strip().str.lower()

    drug_list = sorted(df['drug1'].dropna().unique().tolist() + df['drug2'].dropna().unique().tolist())
    drug_list = sorted(list(set(drug_list)))  # unique sorted list

    for _, row in df.iterrows():
        d1, d2, inter, sev, dose, alt, age_val = (
            row["drug1"], row["drug2"], row["interaction"],
            row.get("severity", ""), row.get("dosage_recommendation", ""),
            row.get("alternative", ""), row.get("age", "")
        )
        key = tuple(sorted([str(d1).strip().lower(), str(d2).strip().lower()]))
        if key not in interaction_dict:
            interaction_dict[key] = []
        interaction_dict[key].append((inter, sev, dose, alt, age_val))

    st.success("✅ Excel data loaded successfully!")
except Exception as e:
    st.error(f"⚠️ Failed to load Excel: {e}")
    drug_list = []

# --- Helper function: Match Age ---
def age_match(row_age, input_age):
    try:
        if isinstance(row_age, str) and '-' in row_age:
            start, end = map(int, row_age.split('-'))
            return start <= input_age <= end
        else:
            return int(row_age) == int(input_age)
    except:
        return False

# --- Function to Check Interaction ---
def check_interaction(drug1, drug2, age):
    key = tuple(sorted([drug1.strip().lower(), drug2.strip().lower()]))
    if key in interaction_dict:
        results = interaction_dict[key]
        for inter, sev, dose, alt, a in results:
            if age_match(a, age):
                return f"⚠️ **Interaction Found:**\n\n👉 {drug1} + {drug2} → {inter}\n📌 Severity: **{sev}**\n💊 Dosage Recommendation (age {age}): **{dose}**\n🔄 Alternative: {alt}"
        inter, sev, dose, alt, a = results[0]
        return f"⚠️ **Interaction Found:**\n\n👉 {drug1} + {drug2} → {inter}\n📌 Severity: **{sev}**\n💊 Dosage Recommendation (age {age}): **{dose}**\n🔄 Alternative: {alt}"
    else:
        return "✅ No harmful interaction found."

# --- Dropdown Menu instead of Tabs ---
menu = st.selectbox("📌 Choose an Option", ["🔍 Check Interaction", "➕ Add Interaction", "🧠 NLP Prescription Check"])

# --- Menu 1: Check Interaction ---
if menu == "🔍 Check Interaction":
    st.markdown('<div class="subtitle">Check Drug Interaction</div>', unsafe_allow_html=True)
    drug1_check = st.selectbox("Drug 1:", options=drug_list, key="check_d1")
    drug2_check = st.selectbox("Drug 2:", options=drug_list, key="check_d2")
    age_check = st.number_input("Enter Age:", min_value=0, max_value=120, step=1, key="check_age")

    if st.button("Check Interaction", key="btn_check"):
        if drug1_check.strip() == "" or drug2_check.strip() == "":
            st.error("Please select both drugs.")
        else:
            result = check_interaction(drug1_check, drug2_check, age_check)
            st.markdown(f'<div class="result-text">{result}</div>', unsafe_allow_html=True)

# --- Menu 2: Add Interaction ---
elif menu == "➕ Add Interaction":
    st.markdown('<div class="subtitle">Add a New Interaction</div>', unsafe_allow_html=True)
    new_d1 = st.text_input("Drug 1 (new)", key="add_d1")
    new_d2 = st.text_input("Drug 2 (new)", key="add_d2")
    new_interaction = st.text_input("Interaction", key="add_inter")
    new_severity = st.selectbox("Severity", ["Mild", "Moderate", "Severe"], key="add_sev")
    new_age = st.number_input("Age for this interaction", min_value=0, max_value=120, step=1, key="add_age")
    new_dose = st.text_input("Dosage Recommendation", key="add_dose")
    new_alt = st.text_input("Alternative Drug", key="add_alt")

    if st.button("Add Interaction", key="btn_add"):
        if not all([new_d1.strip(), new_d2.strip(), new_interaction.strip(), new_dose.strip(), new_alt.strip()]):
            st.error("Please fill in all fields.")
        else:
            key = tuple(sorted([new_d1.strip().lower(), new_d2.strip().lower()]))
            if key not in interaction_dict:
                interaction_dict[key] = []
            interaction_dict[key].append((new_interaction, new_severity, new_dose, new_alt, new_age))

            try:
                if os.path.exists(updated_excel_path):
                    df_updated = pd.read_excel(updated_excel_path)
                else:
                    df_updated = df.copy()

                new_row = pd.DataFrame([{
                    "drug1": new_d1.strip(),
                    "drug2": new_d2.strip(),
                    "interaction": new_interaction,
                    "severity": new_severity,
                    "dosage_recommendation": new_dose,
                    "alternative": new_alt,
                    "age": new_age
                }])
                df_updated = pd.concat([df_updated, new_row], ignore_index=True)
                df_updated.to_excel(updated_excel_path, index=False)
                st.success(f"✅ Added: {new_d1} + {new_d2} → {new_interaction} (Severity: {new_severity}, Age {new_age}, Dose {new_dose}, Alt {new_alt})")
            except Exception as e:
                st.error(f"⚠️ Failed to save: {e}")

# --- Menu 3: NLP Prescription Extraction ---
elif menu == "🧠 NLP Prescription Check":
    st.markdown('<div class="subtitle">Check Interaction from Prescription Text</div>', unsafe_allow_html=True)
    prescription_text = st.text_area("Paste prescription text here:")

    if st.button("Extract and Check Interaction from Text", key="btn_nlp"):
        if prescription_text.strip() == "":
            st.error("Please enter prescription text.")
        else:
            # 1. Try to capture "DrugName + mg"
            pattern = r"\b([A-Z][a-zA-Z0-9-]+)\s*(?:\d+)?\s*mg\b"
            matches = re.findall(pattern, prescription_text)

            extracted_drugs = []

            # If regex found matches, use them
            if matches:
                extracted_drugs = list(dict.fromkeys(matches))  # unique preserve order

            # 2. Fallback: match against known drug list from Excel
            if len(extracted_drugs) < 2:
                for drug in drug_list:
                    if re.search(rf"\b{re.escape(drug)}\b", prescription_text, re.IGNORECASE):
                        extracted_drugs.append(drug)
                extracted_drugs = list(dict.fromkeys(extracted_drugs))  # unique

            # 3. Check if at least 2 drugs found
            if len(extracted_drugs) >= 2:
                drug1_extracted, drug2_extracted = extracted_drugs[0], extracted_drugs[1]
                default_age = 25  # can enhance later with age detection
                result = check_interaction(drug1_extracted, drug2_extracted, default_age)

                st.markdown(
                    f'<div class="result-text">'
                    f'<b>Extracted Drugs:</b> {drug1_extracted} + {drug2_extracted}<br>'
                    f'👤 Age considered: {default_age}<br>{result}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.warning("⚠️ Could not extract at least two drugs from the text. Please check input.")
