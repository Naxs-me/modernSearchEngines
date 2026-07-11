import argparse
from collections import defaultdict

import streamlit as st

from tuebingen_search.search import SearchEngine

def result_card(result: dict) -> None:
    title = result.get("title") or result["url"]
    st.markdown(f"### {result['rank']}. [{title}]({result['url']})")
    st.caption(f"{result['url']}  ·  score={result['score']:.4f}  ·  {result.get('category', 'General')}")
    if result.get("snippet"):
        st.write(result["snippet"])
    with st.expander("Why this result?"):
        st.write(result.get("explanation", "Matched the query."))
        st.write(
            f"BM25: {result.get('bm25_score', 0):.4f} · "
            f"Semantic: {result.get('semantic_score', 0):.4f} · "
            f"Title/heading: {result.get('title_heading_score', 0):.4f}"
        )

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="data/index")
    args, _ = parser.parse_known_args()

    st.set_page_config(page_title="Tübingen Search", page_icon="🔎", layout="wide")
    st.title("🔎 Tübingen Search")
    st.write("BM25 first-stage retrieval with LSA re-ranking, diversity, result explanations, and intent grouping.")

    @st.cache_resource
    def load_engine(index_dir: str):
        return SearchEngine(index_dir)

    engine = load_engine(args.index)

    query = st.text_input("Search query", value="tübingen attractions")
    top_k = st.slider("Number of results", min_value=5, max_value=100, value=20)

    if query:
        results = engine.search(query, top_k=top_k)

        grouped = defaultdict(list)
        for r in results:
            grouped[r.get("category", "General")].append(r)

        tab_names = ["Top results"] + sorted(grouped.keys())
        tabs = st.tabs(tab_names)

        with tabs[0]:
            for r in results:
                result_card(r)
                st.divider()

        for tab, category in zip(tabs[1:], sorted(grouped.keys())):
            with tab:
                for r in grouped[category]:
                    result_card(r)
                    st.divider()

        st.sidebar.header("Query analysis")
        st.sidebar.write(f"Query: `{query}`")
        st.sidebar.write(f"Returned results: {len(results)}")
        st.sidebar.write("Categories:")
        for category, docs in sorted(grouped.items(), key=lambda x: -len(x[1])):
            st.sidebar.write(f"- {category}: {len(docs)}")

if __name__ == "__main__":
    main()
