import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. 系统设置与数据加载 ---
FILE_NAME = 'student_scores.csv'

def load_data():
    """加载数据，如果文件不存在则创建一个空的"""
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=["学号", "姓名", "语文", "数学", "英语"])
        df.to_csv(FILE_NAME, index=False)
        return df
    return pd.read_csv(FILE_NAME)

def save_data(df):
    """保存数据到CSV文件"""
    df.to_csv(FILE_NAME, index=False)

# 页面基本设置
st.set_page_config(page_title="小学成绩分析系统", layout="wide")
st.title("🏫 小学学生成绩统计与分析系统")

# 加载现有数据
df = load_data()

# --- 2. 侧边栏：录入成绩 ---
with st.sidebar:
    st.header("📝 成绩录入")
    st.info("在此处添加新同学的成绩")
    
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        new_id = col1.text_input("学号")
        new_name = col2.text_input("姓名")
        
        c_score = st.number_input("语文成绩", 0, 100, step=1)
        m_score = st.number_input("数学成绩", 0, 100, step=1)
        e_score = st.number_input("英语成绩", 0, 100, step=1)
        
        submitted = st.form_submit_button("💾 保存成绩")
        
        if submitted:
            if new_id and new_name:
                new_data = pd.DataFrame({
                    "学号": [new_id], "姓名": [new_name],
                    "语文": [c_score], "数学": [m_score], "英语": [e_score]
                })
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success(f"{new_name} 的成绩已保存！")
                st.rerun() # 刷新页面
            else:
                st.error("请填写学号和姓名！")

# --- 3. 主界面内容 ---
if df.empty:
    st.warning("👈 请在左侧侧边栏录入第一名学生的成绩")
else:
    # 计算总分和平均分
    df['总分'] = df['语文'] + df['数学'] + df['英语']
    
    # 创建两个选项卡：全班分析 vs 个人查询
    tab1, tab2, tab3 = st.tabs(["📊 全班概况", "🔍 个人画像", "📋 数据列表"])

    # === 选项卡 1: 全班概况 ===
    with tab1:
        st.subheader("全班成绩概览")
        
        # 1. 关键指标卡片
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("全班人数", len(df))
        c2.metric("语文平均分", round(df['语文'].mean(), 1))
        c3.metric("数学平均分", round(df['数学'].mean(), 1))
        c4.metric("英语平均分", round(df['英语'].mean(), 1))
        
        st.divider()
        
        # 2. 图表分析区
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("##### 📉 三科平均分对比")
            avg_scores = df[['语文', '数学', '英语']].mean().reset_index()
            avg_scores.columns = ['科目', '平均分']
            fig_bar = px.bar(avg_scores, x='科目', y='平均分', color='科目', text_auto=True)
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_chart2:
            st.markdown("##### 🏆 总分前五名")
            top_5 = df.nlargest(5, '总分')
            fig_top = px.bar(top_5, x='姓名', y='总分', color='总分', text_auto=True)
            st.plotly_chart(fig_top, use_container_width=True)

    # === 选项卡 2: 个人画像 ===
    with tab2:
        st.subheader("学生个人偏科分析")
        
        student_list = df['姓名'].unique()
        selected_student = st.selectbox("请选择一位同学：", student_list)
        
        if selected_student:
            # 获取该学生数据
            student_data = df[df['姓名'] == selected_student].iloc[0]
            
            # 显示基本分
            c1, c2, c3, c4 = st.columns(4)
            c1.info(f"学号: {student_data['学号']}")
            c2.write(f"**语文**: {student_data['语文']}")
            c3.write(f"**数学**: {student_data['数学']}")
            c4.write(f"**英语**: {student_data['英语']}")
            
            # 绘制雷达图
            st.markdown("##### 🕸️ 学科能力雷达图")
            radar_df = pd.DataFrame(dict(
                r=[student_data['语文'], student_data['数学'], student_data['英语'], student_data['语文']], # 最后重复一次闭合
                theta=['语文', '数学', '英语', '语文']
            ))
            fig_radar = px.line_polar(radar_df, r='r', theta='theta', line_close=True, range_r=[0, 100])
            fig_radar.update_traces(fill='toself')
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # 简单的点评逻辑
            weakest = min(student_data['语文'], student_data['数学'], student_data['英语'])
            if weakest < 60:
                st.error("⚠️ 该生存在不及格科目，请重点关注！")
            elif weakest > 90:
                st.success("🌟 该生发展非常均衡且优秀！")

    # === 选项卡 3: 原始数据 ===
    with tab3:
        st.subheader("原始数据表")
        st.dataframe(df, use_container_width=True)
        
        # 允许下载数据
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 导出为 Excel (CSV)", data=csv, file_name="学生成绩单.csv")