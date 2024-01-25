import streamlit as st
import pandas as pd
import sqlite3
import os
import folium
from streamlit_folium import folium_static

# データベースからデータを読み込む関数
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'fudosan2.db')
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM property_data", conn)
    df['Rent'] = pd.to_numeric(df['Rent'], errors='coerce')
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    df['Size'] = pd.to_numeric(df['Size'], errors='coerce')
    conn.close()
    return df


# メインアプリケーション
def main():
    st.sidebar.title("検索条件")

    # サイドバーでのフィルタリング
    price = st.sidebar.slider("賃料 (万円)", 0, 100, (10, 50))
    age = st.sidebar.slider("築年数", 0, 30, (0, 10))
    size = st.sidebar.slider("面積 (m²)", 0, 100, (10, 50))
    

    # 間取りのチェックボックスを設定
    st.sidebar.markdown("間取り")
    layouts = ["1R", "1K", "1DK", "1LDK", "2K", "2DK", "2LDK"]
    selected_layouts = []
    col1, col2, col3 = st.sidebar.columns(3)  # 3列に分割

    for i, layout in enumerate(layouts):
        if i % 3 == 0:
            with col1:
                if st.checkbox(layout, key=layout):
                    selected_layouts.append(layout)
        elif i % 3 == 1:
            with col2:
                if st.checkbox(layout, key=layout):
                    selected_layouts.append(layout)
        else:
            with col3:
                if st.checkbox(layout, key=layout):
                    selected_layouts.append(layout)

    # 検索ボタン
    if st.sidebar.button('検索'):
        # データベースからデータを読み込む
        df = load_data()
        
        df_loc = df[['lat', 'lon']].dropna()
        # 地図の表示
        st.write('▼ マップ：')
        st.map(df_loc)
        
        # フィルタリングされたデータを表示
        if selected_layouts:  # 選択された間取りがある場合のみフィルタリングを適用
            filtered_df = df[
                (df['Rent'] >= price[0]) & (df['Rent'] <= price[1]) &
                (df['Age'] >= age[0]) & (df['Age'] <= age[1]) &
                (df['Size'] >= size[0]) & (df['Size'] <= size[1]) &
                (df['Layout'].isin(selected_layouts))
            ]
        else:  # 間取りが選択されていない場合はフィルタリングしない
            filtered_df = df

        # ヒット件数の計算
        num_hits = len(filtered_df)

        # ヒット件数の表示
        st.markdown(f"<h1 style='text-align: center; color: white; font-size: 48px;'>{num_hits}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: white; font-size: 24px;'>件がヒットしました！</p>", unsafe_allow_html=True)

        # カラムの順序を設定
        column_order = [
        'Name', 'Address', 'Access1', 'Access1_Walk', 'Access2', 'Access2_Walk', 'Access3', 'Access3_Walk',
        'Age', 'Max_Floor', 'Floor', 'Rent', 'Layout', 'Size', 'Image_URL'
        ]

        # カラムの順序を変更
        filtered_df = filtered_df[column_order]

        # 結果の表示
        st.dataframe(filtered_df.T)



# アプリケーションの実行
if __name__ == "__main__":
    main()