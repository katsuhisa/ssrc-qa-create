import os
import pandas as pd
import streamlit as st

# スクリプトのあるディレクトリの絶対パスを取得
dir_path = os.path.dirname(__file__)

# CSVファイルの読み込み
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

def select_question(prefix, data, default_values=None):
    if default_values is None:
        default_values = {'大項目': None, '中項目': None, '小項目': None}
    
    major_options = data['大項目'].unique()
    major_index = major_options.tolist().index(default_values['大項目']) if default_values and default_values['大項目'] in major_options else 0
    selected_major = st.selectbox(f'{prefix} 大項目を選択してください', options=major_options, index=major_index, key=f'{prefix}_major')

    filtered_mid_options = data[data['大項目'] == selected_major]['中項目'].unique()
    mid_index = filtered_mid_options.tolist().index(default_values['中項目']) if default_values and default_values['中項目'] in filtered_mid_options else 0
    selected_mid = st.selectbox(f'{prefix} 中項目を選択してください', options=filtered_mid_options, index=mid_index, key=f'{prefix}_mid')

    filtered_small_options = data[(data['大項目'] == selected_major) & (data['中項目'] == selected_mid)]['小項目'].unique()
    small_index = filtered_small_options.tolist().index(default_values['小項目']) if default_values and default_values['小項目'] in filtered_small_options else 0
    selected_small = st.selectbox(f'{prefix} 小項目を選択してください', options=filtered_small_options, index=small_index, key=f'{prefix}_small')

    filtered_questions = data[
        (data['大項目'] == selected_major) &
        (data['中項目'] == selected_mid) &
        (data['小項目'] == selected_small)
    ]['設問'].unique()
    selected_question = st.selectbox(f'{prefix} 設問を選択してください', options=filtered_questions, key=f'{prefix}_question')

    return {
        '大項目': selected_major,
        '中項目': selected_mid,
        '小項目': selected_small,
        '設問': selected_question
    }

def display_questions(questions, data):
    if questions:
        st.markdown("### 選択された設問")
        for i, question in enumerate(questions, start=1):
            question_data = data[
                (data['大項目'] == question['大項目']) &
                (data['中項目'] == question['中項目']) &
                (data['小項目'] == question['小項目']) &
                (data['設問'] == question['設問'])
            ]
            choices = '\n'.join([f"    - {row['選択肢']}（{row['配点']}）" for _, row in question_data.iterrows()])
            st.markdown(f"""
            **問{i}**
            - 設問: {question['設問']}
            - 設問様式: {question_data.iloc[0]['設問様式']}
            - 選択肢（配点）:
                {choices}
            """)

def app():
    st.title('設問フォーマット出力システム')
    st.caption('大項目・中項目・小項目・設問を選択すると、設問様式、選択肢、配点を自動で出力してくれます。')
    st.caption('大項目・中項目・小項目・設問は3問まで選択できます。')

    uploaded_file = st.file_uploader("設問設定のCSVファイルをアップロードしてください", type=["csv"])
    if uploaded_file is not None:
        data = load_data(uploaded_file)
    else:
        dir_path = os.path.dirname(__file__)
        default_file_path = '../SSRC_qa.csv'
        data = load_data(os.path.join(dir_path, default_file_path))

    st.title('設問フォーマット出力システム')

    # 初期化
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = []

    # 1問目の選択
    st.markdown("### 1問目")
    question1 = select_question('1問目', data)
    if st.button('1問目を確定'):
        st.session_state.selected_questions.append(question1)
        st.session_state['q1_completed'] = True

    # 2問目の選択
    if 'q1_completed' in st.session_state:
        st.markdown("### 2問目")
        question2 = select_question('2問目', data, st.session_state.selected_questions[-1] if st.session_state.selected_questions else None)
        if st.button('2問目を確定'):
            st.session_state.selected_questions.append(question2)
            st.session_state['q2_completed'] = True

    # 3問目の選択
    if 'q2_completed' in st.session_state:
        st.markdown("### 3問目")
        question3 = select_question('3問目', data, st.session_state.selected_questions[-1])
        if st.button('3問目を確定'):
            st.session_state.selected_questions.append(question3)

    # 選択された設問の表示
    display_questions(st.session_state.selected_questions, data)

    # 選択された設問の表示
    for i, question in enumerate(st.session_state.selected_questions, start=1):
        st.write(f"問{i}: {question}")


if __name__ == "__main__":
    app()

