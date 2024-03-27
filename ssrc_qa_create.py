# pages/ssrc_qa_create.py
import os
import pandas as pd
import streamlit as st

# スクリプトのあるディレクトリの絶対パスを取得
dir_path = os.path.dirname(__file__)

# CSVファイルの読み込み
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# データの読み込み
st.title('設問フォーマット出力システム')
st.caption('大項目・中項目・小項目・設問を選択すると、設問様式、選択肢、配点を自動で出力してくれます。')
st.caption('大項目・中項目・小項目・設問は3問まで選択できます。')

# ファイルアップローダー
st.markdown('##### 大項目・中項目・小項目・設問の設定（必要な場合にのみ利用）')
# CSVファイルのフォーマット例を表示
example_data = {
    "大項目": ["1サステナビリティ体制", "1サステナビリティ体制"],
    "中項目": ["1.法令等遵守", "1.法令等遵守"],
    "小項目": ["A.法令等遵守に関する方針", "A.法令等遵守に関する方針"],
    "設問": [
        "(1)法令等遵守に関する方針や行動基準を策定していますか",
        "(1)法令等遵守に関する方針や行動基準を策定していますか"
    ],
    "設問様式": ["複数", "複数"],
    "選択肢": ["a.法令等遵守に関する方針はない、もしくは不明", "b.法令等遵守に関する方針がある"],
    "配点": [0, 1]
}
example_df = pd.DataFrame(example_data)
st.markdown("アップロードするCSVのフォーマット例:")
st.dataframe(example_df)
st.text("... (この下にも行が続く)")
st.text("")
uploaded_file = st.file_uploader("設問設定のCSVファイルをアップロードしてください", type=["csv"])
st.divider()

# 初期化
if 'selected_questions' not in st.session_state:
    st.session_state['selected_questions'] = []

# データの読み込み
if uploaded_file is not None:
    data = load_data(uploaded_file)
else:
    data = load_data(os.path.join(dir_path, 'SSRC_qa.csv'))  # デフォルトのCSVファイル

def select_question(prefix, default_values=None):
    if default_values is None:
        default_values = {'major': None, 'mid': None, 'small': None}
    else:
        default_values = {
            'major': default_values.get('大項目'),
            'mid': default_values.get('中項目'),
            'small': default_values.get('小項目')
        }

    major_options = data['大項目'].unique()
    major_index = major_options.tolist().index(default_values['major']) if default_values['major'] in major_options else 0
    selected_major = st.selectbox('大項目を選択してください', options=major_options, index=major_index, key=f'{prefix}_major')

    filtered_mid_options = data[data['大項目'] == selected_major]['中項目'].unique()
    mid_index = filtered_mid_options.tolist().index(default_values['mid']) if default_values['mid'] in filtered_mid_options else 0
    selected_mid = st.selectbox('中項目を選択してください', options=filtered_mid_options, index=mid_index, key=f'{prefix}_mid')

    filtered_small_options = data[(data['大項目'] == selected_major) & (data['中項目'] == selected_mid)]['小項目'].unique()
    small_index = filtered_small_options.tolist().index(default_values['small']) if default_values['small'] in filtered_small_options else 0
    selected_small = st.selectbox('小項目を選択してください', options=filtered_small_options, index=small_index, key=f'{prefix}_small')

    filtered_questions = data[
        (data['大項目'] == selected_major) &
        (data['中項目'] == selected_mid) &
        (data['小項目'] == selected_small)
    ]['設問'].unique()
    selected_question = st.selectbox('設問を選択してください', options=filtered_questions, key=f'{prefix}_question')

    return {
        '大項目': selected_major,
        '中項目': selected_mid,
        '小項目': selected_small,
        '設問': selected_question
    }

def display_questions():
    for i, question in enumerate(st.session_state['selected_questions'], start=1):
        st.markdown(f"問{i}")
        st.markdown(f"- 設問: {question['設問']}")
        question_data = data[
            (data['大項目'] == question['大項目']) &
            (data['中項目'] == question['中項目']) &
            (data['小項目'] == question['小項目']) &
            (data['設問'] == question['設問'])
        ]
        st.markdown(f"- 設問様式: {question_data.iloc[0]['設問様式']}")
        st.markdown("- 選択肢（配点）")
        for _, row in question_data.iterrows():
            st.markdown(f"    - {row['選択肢']}（{row['配点']}）")
        st.markdown("")

# 1問目の選択
st.markdown("")
st.markdown("### 1問目")
question1 = select_question('q1')
if st.button('2問目を選択', key='btn_q1'):
    st.session_state['selected_questions'].append(question1)

# 2問目の選択
if len(st.session_state['selected_questions']) >= 1:
    st.markdown("")
    st.markdown("")
    st.markdown("### 2問目")
    question2 = select_question('q2', st.session_state['selected_questions'][-1])
    if st.button('3問目を選択', key='btn_q2'):
        st.session_state['selected_questions'].append(question2)

# 3問目の選択
if len(st.session_state['selected_questions']) >= 2:
    st.markdown("")
    st.markdown("")
    st.markdown("### 3問目")
    question3 = select_question('q3', st.session_state['selected_questions'][-1])
    if st.button('設問フォーマットで出力', key='btn_q3'):
        # 設問の追加前に、現在の選択内容をリセット
        st.session_state['selected_questions'] = [question1, question2, question3]

# 設問の表示
for i, question in enumerate(st.session_state['selected_questions'], start=1):
    st.markdown("")
    st.markdown(f"問{i}")
    st.markdown(f"- 設問: {question['設問']}")
    question_data = data[
        (data['大項目'] == question['大項目']) &
        (data['中項目'] == question['中項目']) &
        (data['小項目'] == question['小項目']) &
        (data['設問'] == question['設問'])
    ]
    st.markdown(f"- 設問様式: {question_data.iloc[0]['設問様式']}")
    st.markdown("- 選択肢（配点）")
    for _, row in question_data.iterrows():
        st.markdown(f"    - {row['選択肢']}（{row['配点']}）")
    st.markdown("")
# 'Claude用の表記で出力'ボタンをループの外に移動
if 'selected_questions' in st.session_state and st.session_state['selected_questions']:
    if st.button('Claude用の表記で出力', key='btn_claude_output'):
        for i, question in enumerate(st.session_state['selected_questions'], start=1):
            code_content = f"問{i}\n- 設問: {question['設問']}\n"
            question_data = data[
                (data['大項目'] == question['大項目']) &
                (data['中項目'] == question['中項目']) &
                (data['小項目'] == question['小項目']) &
                (data['設問'] == question['設問'])
            ]
            code_content += f"- 設問様式: {question_data.iloc[0]['設問様式']}\n- 選択肢（配点）\n"
            for _, row in question_data.iterrows():
                code_content += f"    - {row['選択肢']}（{row['配点']}）\n"
            st.code(code_content, language='')