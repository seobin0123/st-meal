
    if filtered.empty:
        st.info("선택한 조건에 해당하는 규칙이 없습니다.")
    else:
        st.dataframe(
            filtered.style.format({
                "지지도": "{:.3f}",
                "신뢰도": "{:.3f}",
                "향상도": "{:.3f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    # 함께 나온 적 없는 메뉴 쌍 찾기
    st.divider()
    st.subheader("🔎 함께 나온 적 없는 짝")
    st.write(
        "기준 메뉴와 같은 날 한 번도 함께 나오지 않았고, "
        "혼자서는 10일 이상 나온 메뉴를 찾습니다."
    )

    selected_absent_menu = st.selectbox(
        "함께 나온 적 없는 짝 찾기 - 기준 메뉴",
        menu_options,
        index=0,
        key="absent_pair_menu",
    )

    selected_menu_days = item_counts[selected_absent_menu]
    st.write(
        f"**선택한 메뉴 '{selected_absent_menu}'의 출현 일수: "
        f"{selected_menu_days:,}일**"
    )

    absent_rows = []
    for other_menu, other_days in item_counts.items():
        if other_menu == selected_absent_menu:
            continue

        pair_key = tuple(sorted((selected_absent_menu, other_menu)))
        together_days = pair_counts.get(pair_key, 0)

        if together_days == 0 and other_days >= 10:
            absent_rows.append({
                "메뉴": other_menu,
                "나온 날 수": other_days,
            })

    absent_df = pd.DataFrame(absent_rows, columns=["메뉴", "나온 날 수"])
    if absent_df.empty:
        st.info(
            "이 메뉴와 한 번도 함께 나오지 않았고, "
            "혼자서는 10일 이상 나온 메뉴가 없습니다."
        )
    else:
        absent_df = absent_df.sort_values(
            by=["나온 날 수", "메뉴"],
            ascending=[False, True],
        ).reset_index(drop=True)

        st.write(f"**조건에 맞는 메뉴: {len(absent_df):,}개**")
        st.dataframe(
            absent_df,
            use_container_width=True,
            hide_index=True,
        )

    # 현재 연관 규칙 필터가 적용된 결과 중 향상도 상위 10개
    st.divider()
    st.subheader("📊 향상도 상위 10개 규칙")

    top10 = filtered.sort_values(
        by=["향상도", "신뢰도", "동시"],
        ascending=[False, False, False],
    ).head(10).copy()

    if top10.empty:
        st.info("그래프로 표시할 규칙이 없습니다.")
    else:
        top10["규칙"] = top10["조건"] + " → " + top10["결과"]
        top10 = top10.sort_values("향상도", ascending=True)

        fig = px.bar(
            top10,
            x="향상도",
            y="규칙",
            orientation="h",
            text="향상도",
            labels={
                "향상도": "향상도",
                "규칙": "연관 규칙",
            },
            title="향상도 기준 상위 10개",
        )
        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            cliponaxis=False,
        )
        fig.update_layout(
            yaxis_title="",
            xaxis_title="향상도",
            height=max(400, 42 * len(top10) + 130),
            margin=dict(l=20, r=70, t=65, b=35),
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("분석 지표 읽는 방법"):
        st.markdown(
            """
            - **동시**: 조건 메뉴와 결과 메뉴가 같은 날 함께 나온 횟수
            - **지지도**: 전체 급식일 중 두 메뉴가 함께 나온 비율
            - **신뢰도**: 조건 메뉴가 나온 날 중 결과 메뉴도 함께 나온 비율
            - **향상도**: 조건 메뉴와 결과 메뉴의 동시 출현이 우연히 독립적으로 나타나는 경우보다 얼마나 높은지 나타내는 값
              - 1보다 크면 함께 나오는 경향이 있고, 1이면 독립적인 수준이며, 1보다 작으면 함께 나오는 경향이 낮습니다.
            """
        )

    st.caption(
        "※ 메뉴 이름은 괄호와 괄호 안의 내용을 제거한 뒤 비교합니다. "
        "한 날짜 안에서 같은 메뉴가 중복되면 한 번만 계산합니다."
    )


if __name__ == "__main__":
    main()

