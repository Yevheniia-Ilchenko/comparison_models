import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3

st.title("Multi-Example Model Comparison (From Directory)")

MODEL_DIRS = {
    "Model 1": "./comparison_models/model_1/",
    "Model 2": "./comparison_models/model_2/",
    "Model 3": "./comparison_models/model_3/"
}

def load_json_files_from_dir(directory):
    files = [f for f in os.listdir(directory) if f.endswith(".json")]
    results = []
    for file in files:
        path = os.path.join(directory, file)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            results.append(parse_file(data, file))
    return results

def parse_file(data, file_name):
    model_name = data.get("message", {}).get("model_info", {}).get("name", "NA")
    tokens = data.get("message", {}).get("model_info", {}).get("tokens", {}).get("total", 0)
    cost = data.get("message", {}).get("model_info", {}).get("cost", 0)
    knots = set([item for sublist in data["message"].get("knots_from_section", []) for item in sublist])
    entities = set(data["message"].get("keywords_named_entities", []))
    return {
        "model": model_name,
        "tokens": tokens,
        "cost": cost,
        "knots": knots,
        "entities": entities,
        "file_name": file_name
    }

def aggregate_metrics(model_results):
    total_tokens = sum(r["tokens"] for r in model_results)
    total_cost = sum(r["cost"] for r in model_results)
    avg_tokens = total_tokens / len(model_results) if model_results else 0
    avg_cost = total_cost / len(model_results) if model_results else 0
    all_knots = set().union(*[r["knots"] for r in model_results])
    all_entities = set().union(*[r["entities"] for r in model_results])
    return {
        "Total Tokens": total_tokens,
        "Avg Tokens": avg_tokens,
        "Total Cost": total_cost,
        "Avg Cost": avg_cost,
        # "Entities_list": all_entities,
        "Unique Knots": len(all_knots),
        "Unique Entities": len(all_entities)
    }

model1_data = load_json_files_from_dir(MODEL_DIRS["Model 1"])
model2_data = load_json_files_from_dir(MODEL_DIRS["Model 2"])
model3_data = load_json_files_from_dir(MODEL_DIRS["Model 3"])

if model1_data and model2_data and model3_data:
    agg1 = aggregate_metrics(model1_data)
    agg2 = aggregate_metrics(model2_data)
    agg3 = aggregate_metrics(model3_data)

    df = pd.DataFrame([
        {"Model": model1_data[0]["model"], **agg1},
        {"Model": model2_data[0]["model"], **agg2},
        {"Model": model3_data[0]["model"], **agg3},
    ])

    st.subheader("Summary Table")
    st.dataframe(df)

    st.subheader("Unique Knots Count (Aggregated Across Examples)")
    fig_bar, ax_bar = plt.subplots()
    ax_bar.bar(df["Model"], df["Unique Knots"])
    ax_bar.set_ylabel("Unique Knots")
    ax_bar.set_xlabel("Model")
    ax_bar.set_title("Unique Knots per Model")
    st.pyplot(fig_bar)


    st.subheader("Venn Diagram of Knots (Aggregated Across Examples)")
    knots1 = set.union(*[r["knots"] for r in model1_data])
    knots2 = set.union(*[r["knots"] for r in model2_data])
    knots3 = set.union(*[r["knots"] for r in model3_data])

    fig_venn, ax_venn = plt.subplots()
    venn3([knots1, knots2, knots3],
          (model1_data[0]["model"], model2_data[0]["model"], model3_data[0]["model"]))
    st.pyplot(fig_venn)

    st.subheader("Detailed Per File and Top Entities Per File")

    num_examples = min(len(model1_data), len(model2_data), len(model3_data))

    for i in range(num_examples):
        st.markdown(f"### Example {i+1}")

        col1, col2, col3 = st.columns(3)

        with col1:
            m1 = model1_data[i]
            st.markdown(f"**{m1['model']} — {m1['file_name']}**")
            st.write(f"Tokens: {m1['tokens']}, Cost: ${m1['cost']:.6f}")
            st.write(f"Knots: {len(m1['knots'])}")
            st.write(f"Entities count: {len(m1['entities'])}")
            entities_list = ', '.join(list(m1['entities'])[:3])
            st.markdown(f"Top 3 entities: <span style='color:red; font-weight:bold;'>{entities_list}</span>", unsafe_allow_html=True)

        with col2:
            m2 = model2_data[i]
            st.markdown(f"**{m2['model']} — {m2['file_name']}**")
            st.write(f"Tokens: {m2['tokens']}, Cost: ${m2['cost']:.6f}")
            st.write(f"Knots: {len(m2['knots'])}")
            st.write(f"Entities count: {len(m2['entities'])}")
            entities_list = ', '.join(list(m2['entities'])[:3])
            st.markdown(f"Top 3 entities: <span style='color:red; font-weight:bold;'>{entities_list}</span>", unsafe_allow_html=True)

        with col3:
            m3 = model3_data[i]
            st.markdown(f"**{m3['model']} — {m3['file_name']}**")
            st.write(f"Tokens: {m3['tokens']}, Cost: ${m3['cost']:.6f}")
            st.write(f"Knots: {len(m3['knots'])}")
            st.write(f"Entities count: {len(m3['entities'])}")
            entities_list = ', '.join(list(m3['entities'])[:3])
            st.markdown(f"Top 3 entities: <span style='color:red; font-weight:bold;'>{entities_list}</span>", unsafe_allow_html=True)


else:
    st.warning("No data found in one or more model directories!")

