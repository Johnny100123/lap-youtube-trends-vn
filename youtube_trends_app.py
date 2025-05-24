import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# --- Giao diện ---
st.set_page_config(page_title="YouTube Keyword Trends VN", layout="wide")
st.title("📈 Phân Tích Từ Khóa YouTube tại Việt Nam (VN) | Keyword Trends Analysis")

st.markdown("**Nhập từ khóa chính / Enter main keyword**")
keyword = st.text_input("🔍 Từ khóa:", value="du lịch")

st.markdown("**Chọn nền tảng tìm kiếm / Platform**")
group = st.selectbox("🔧 Nền tảng", ["YouTube", "Web", "Hình ảnh", "Tin tức"], index=0)
gprop_dict = {"YouTube": "youtube", "Web": "", "Hình ảnh": "images", "Tin tức": "news"}
gprop = gprop_dict[group]

st.markdown("**Chọn quốc gia / Country Code** (ví dụ: VN, US, JP...)")
region = st.text_input("🌍 Quốc gia:", value="VN")

st.markdown("**Chọn khoảng thời gian / Time Range**")
timeframe_label = st.selectbox("🗓️ Khoảng thời gian", ["7 ngày", "30 ngày", "90 ngày", "1 năm", "5 năm"])
tf_dict = {
    "7 ngày": "now 7-d",
    "30 ngày": "today 1-m",
    "90 ngày": "today 3-m",
    "1 năm": "today 12-m",
    "5 năm": "today 5-y"
}
timeframe = tf_dict[timeframe_label]

st.markdown("**Số lượng từ khóa liên quan / Related keywords count**")
num_keywords = st.slider("🔢 Số từ khóa liên quan", 5, 30, 10)

# --- Phân tích dữ liệu ---
if keyword:
    st.divider()
    st.subheader(f"🔎 Đang phân tích từ khóa: {keyword} ({group} - {region})")

    pytrends = TrendReq(hl='vi-VN', tz=420)
    pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=region, gprop=gprop)
    related_queries = pytrends.related_queries()

    top_keywords = related_queries.get(keyword, {}).get("top", pd.DataFrame())
    if top_keywords.empty:
        st.error("⚠️ Không có từ khóa liên quan cho kết quả này.")
    else:
        keywords_to_analyze = top_keywords["query"].head(num_keywords).tolist()
        keywords_to_analyze.insert(0, keyword)

        pytrends.build_payload(keywords_to_analyze, cat=0, timeframe=timeframe, geo=region, gprop=gprop)
        data = pytrends.interest_over_time()
        if data.empty:
            st.error("⚠️ Không thể lấy dữ liệu thời gian.")
        else:
            st.success(f"✅ Lấy dữ liệu thành công cho {len(keywords_to_analyze)} từ khóa.")

            # --- Biểu đồ line ---
            st.markdown("### 📈 Biểu đồ xu hướng tổng hợp (Line Chart)")
            st.line_chart(data[keywords_to_analyze])

            # --- Biểu đồ bar từng từ khóa (chỉ top 10) ---
            st.markdown("### 📊 Biểu đồ mức độ quan tâm trung bình (Bar Chart)")
            avg_interest = data[keywords_to_analyze].mean().sort_values(ascending=False)
            top_avg = avg_interest.head(10)

            fig, ax = plt.subplots(figsize=(10, 5))
            top_avg.plot(kind='bar', color='skyblue', ax=ax)
            ax.set_ylabel("Mức độ quan tâm / Interest")
            ax.set_title("Top 10 từ khóa có mức độ quan tâm trung bình cao nhất")
            st.pyplot(fig)

            # --- Bảng dữ liệu ---
            st.markdown("### 📅 Bảng dữ liệu theo ngày")
            st.dataframe(data[keywords_to_analyze])

            # --- Xuất Excel ---
            st.markdown("### 📥 Tải xuống dữ liệu Excel")
            excel_buffer = BytesIO()
            data.to_excel(excel_buffer, index=True, engine='openpyxl')
            st.download_button("⬇️ Tải Excel", data=excel_buffer.getvalue(), file_name="keyword_trends.xlsx")

    st.info("🚫 Phiên bản hiện tại chưa hỗ trợ CPC / Mức độ cạnh tranh từ Google Ads.")
