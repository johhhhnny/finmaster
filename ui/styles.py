"""
FinMaster UI 全局样式模块 (Professional Financial Workstation Theme)
集中管理全局 CSS 注入、响应式布局、三级字体层级体系与专业卡片样式。
"""
import streamlit as st

def inject_custom_css():
    """注入 FinMaster 专业金融终端定制样式"""
    st.markdown("""
<style>
/* 1. 彻底消除主内容区域顶部巨大空白 (默认 6rem 留白) 并保留侧边栏展开按钮 */
header[data-testid="stHeader"],
[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
}
/* 隐藏 Streamlit 自带的部署与三点菜单，消除顶部干扰 */
[data-testid="stAppDeployButton"],
[data-testid="stMainMenuButton"] {
    display: none !important;
}
/* 侧边栏折叠后页面左上角的展开浮动按钮 */
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    position: fixed !important;
    top: 0.6rem !important;
    left: 0.6rem !important;
    z-index: 999999 !important;
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    padding: 2px !important;
    transition: all 0.15s ease !important;
}
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover {
    background: #f1f5f9 !important;
    border-color: #94a3b8 !important;
}
[data-testid="stExpandSidebarButton"] button,
[data-testid="stSidebarCollapsedControl"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #1e293b !important;
    padding: 4px 6px !important;
}

.block-container,
div[data-testid="stMainBlockContainer"],
div[data-testid="stAppViewBlockContainer"],
.main .block-container,
.stMain .block-container,
section.main .block-container,
section.stMain .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.8rem !important;
    padding-right: 1.8rem !important;
    max-width: 100% !important;
    margin-top: 0 !important;
}
[data-testid="stAppViewContainer"] > .main,
[data-testid="stAppViewContainer"] > .stMain,
section[data-testid="stMain"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* 2. 侧边栏整体与折叠收起按钮 (紧凑微顶栏，允许一键隐藏与收起) */
[data-testid="stSidebarHeader"] {
    display: flex !important;
    visibility: visible !important;
    justify-content: flex-end !important;
    align-items: center !important;
    height: 2rem !important;
    min-height: 2rem !important;
    padding: 0.2rem 0.6rem 0 0.6rem !important;
    background: transparent !important;
}
[data-testid="stSidebarCollapseButton"] {
    display: inline-flex !important;
    visibility: visible !important;
}
[data-testid="stSidebarCollapseButton"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 6px !important;
    padding: 4px !important;
    cursor: pointer !important;
    color: #64748b !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebarCollapseButton"] button:hover {
    background: #e2e8f0 !important;
    color: #0f172a !important;
}

[data-testid="stSidebar"] {
    background-color: #f8fafc !important;
    border-right: 1px solid #e2e8f0 !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebar"] [data-testid="stSidebarContent"],
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebar"] .block-container,
[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
    padding-top: 0.5rem !important;
    margin-top: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-bottom: 1.5rem !important;
    padding-left: 0.95rem !important;
    padding-right: 0.95rem !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.55rem !important; /* 平衡的垂直呼吸间距 */
}
/* 移除侧边栏所有粗硬分割线 */
[data-testid="stSidebar"] hr {
    display: none !important;
}

/* 3. 侧边栏品牌区域 */
.sidebar-header-box {
    padding-top: 0 !important;
    margin-top: 0 !important;
    padding-bottom: 8px;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 10px;
}
.sidebar-main-title {
    font-size: 1.42rem !important; /* 第一层级：最大 */
    font-weight: 800 !important;
    color: #0f172a !important;
    letter-spacing: -0.015em !important;
    margin: 0 !important;
    display: flex;
    align-items: center;
    gap: 0.45rem;
}
.sidebar-sub-caption {
    font-size: 0.72rem !important;
    color: #64748b !important;
    line-height: 1.3 !important;
    margin-top: 0.25rem !important;
}

/* 4. 分组小节标题 (第二层级：次之，清晰稳重) */
.sidebar-section-title {
    font-size: 0.98rem !important; /* 第二层级：次之，明确小节归属 */
    font-weight: 700 !important;
    color: #1e293b !important;
    letter-spacing: -0.01em !important;
    margin-top: 14px !important;
    margin-bottom: 6px !important;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}

/* 5. 现代化无圆点色块卡片 (工作台导航 + 技能工具直选) */
/* 彻底隐藏 Streamlit 1.40 react-aria 默认单选圆点及 input 控件 */
[data-testid="stSidebar"] [data-testid="stRadioOption"] input,
[data-testid="stSidebar"] [data-testid="stRadioOption"] span:has(input),
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child,
[data-testid="stSidebar"] [data-testid="stRadioOption"] div[class*="ex50key4"],
[data-testid="stSidebar"] [data-testid="stRadioOption"] div[class*="ex50key5"],
[data-testid="stSidebar"] [data-testid="stRadioOption"] svg {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}
[data-testid="stSidebar"] div.react-aria-RadioField,
[data-testid="stSidebar"] [data-testid="stRadio"] div[data-selected],
[data-testid="stSidebar"] [data-testid="stRadioGroup"] {
    width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="stRadioGroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 0.28rem !important;
}
[data-testid="stSidebar"] label[data-testid="stRadioOption"] {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    padding: 0.46rem 0.68rem !important;
    margin: 0 !important;
    border-radius: 8px !important;
    border: 1px solid #e2e8f0 !important;
    background: #ffffff !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    cursor: pointer !important;
    transition: all 0.15s ease-in-out !important;
    box-sizing: border-box !important;
}
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover {
    background-color: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04) !important;
}
/* 浅蓝高光现代色块卡片激活态 (匹配 react-aria data-selected 及 :has(input:checked)) */
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected],
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked) {
    background: #eff6ff !important; /* 浅蓝底色 */
    border: 1.5px solid #3b82f6 !important;
    border-left: 4.5px solid #1d4ed8 !important; /* 经典深蓝侧标 */
    box-shadow: 0 2px 5px rgba(37, 99, 235, 0.10) !important;
}
[data-testid="stSidebar"] label[data-testid="stRadioOption"] p {
    font-size: 0.81rem !important;
    font-weight: 500 !important;
    color: #334155 !important;
    margin: 0 !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    line-height: 1.35 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    transition: color 0.15s ease !important;
}
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected] p,
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked) p {
    color: #1d4ed8 !important; /* 激活文字深蓝 */
    font-weight: 700 !important;
}

/* 5.1 投研阶段横向微胶囊卡片栏 (st.pills) */
[data-testid="stSidebar"] [data-testid="stButtonGroup"] {
    width: 100% !important;
    margin-bottom: 4px !important;
}
/* 强制内部胶囊容器采用 Flex 自动折行，紧密网格排列 */
[data-testid="stSidebar"] [data-testid="stButtonGroup"] > div,
[data-testid="stSidebar"] [data-testid="stButtonGroup"] > div:last-child {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 4px !important;
    width: 100% !important;
    justify-content: flex-start !important;
}
[data-testid="stSidebar"] button[data-variant="pills"],
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 1.75rem !important;
    height: 1.75rem !important;
    padding: 0 0.52rem !important;
    font-size: 0.74rem !important;
    font-weight: 500 !important;
    border-radius: 9999px !important;
    border: 1px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #475569 !important;
    line-height: 1 !important;
    white-space: nowrap !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    transition: all 0.15s ease !important;
    flex: 0 0 auto !important; /* 自适应紧凑胶囊宽度，绝不独占单行 */
}
[data-testid="stSidebar"] button[data-variant="pills"]:hover,
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button:hover {
    background: #f1f5f9 !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
}
/* 激活态：深蓝高光微胶囊 (精确匹配 react-aria data-selected 属性) */
[data-testid="stSidebar"] button[data-variant="pills"][data-selected],
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[data-selected] {
    background: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 4px rgba(29, 78, 216, 0.25) !important;
}
[data-testid="stSidebar"] button[data-variant="pills"][data-selected] *,
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[data-selected] * {
    color: #ffffff !important;
}

/* 6. 表单输入与下拉框微调 (第三层级：小巧精致) */
/* 6. 表单输入与下拉框微调 (第三层级：小巧精致 0.78rem ~ 0.80rem) */
[data-testid="stSidebar"] label p {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    margin-bottom: 3px !important;
    margin-top: 5px !important;
}
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    min-height: 2.1rem !important;
    height: 2.1rem !important;
    padding: 0 0.5rem !important;
    font-size: 0.8rem !important;
    border-radius: 6px !important;
    border: 1px solid #cbd5e1 !important;
    background-color: #ffffff !important;
}
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {
    font-size: 0.8rem !important;
    line-height: 1.3 !important;
}
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] input[type="password"] {
    height: 2.1rem !important;
    min-height: 2.1rem !important;
    font-size: 0.8rem !important;
    padding: 0.2rem 0.6rem !important;
    border-radius: 6px !important;
    border: 1px solid #cbd5e1 !important;
    background-color: #ffffff !important;
}

/* 6.1 全局下拉菜单浮层项 (BaseWeb Portal 弹出菜单：收敛为协调的 0.8rem 精致字号与行高) */
div[data-baseweb="popover"],
div[data-baseweb="popover"] ul,
div[data-baseweb="menu"],
ul[role="listbox"],
ul[data-testid="stSelectboxVirtualDropdown"] {
    border-radius: 8px !important;
    padding: 3px !important;
}
div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li,
ul[role="listbox"] li,
ul[role="listbox"] li[role="option"],
ul[data-testid="stSelectboxVirtualDropdown"] li {
    font-size: 0.8rem !important;
    min-height: 2.05rem !important;
    height: 2.05rem !important;
    padding: 0.25rem 0.55rem !important;
    line-height: 1.3 !important;
    border-radius: 5px !important;
}
div[data-baseweb="popover"] li *,
div[data-baseweb="menu"] li *,
ul[role="listbox"] li *,
ul[role="listbox"] li[role="option"] *,
ul[data-testid="stSelectboxVirtualDropdown"] li * {
    font-size: 0.8rem !important;
    line-height: 1.3 !important;
}

/* 7. 彻底解决按钮文字过大与粗笨外观问题 */
[data-testid="stSidebar"] .stButton {
    margin-top: 4px !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] .stButton button {
    padding: 0.25rem 0.4rem !important;
    min-height: 2.05rem !important;
    height: 2.05rem !important;
    border-radius: 6px !important;
    border: 1px solid #cbd5e1 !important;
    background-color: #ffffff !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.15s ease-in-out !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    border-color: #94a3b8 !important;
    background-color: #f1f5f9 !important;
}
/* 核心穿透选择器：强制将侧边栏按钮内所有内部标签字体收敛至 0.74rem 精致大小 */
[data-testid="stSidebar"] .stButton button * {
    font-size: 0.74rem !important;
    font-weight: 600 !important;
    line-height: 1 !important;
}

/* 快捷标的填选按钮精致化 (仅作用于非 primary 按钮，绝对不污染主行动按钮) */
div[data-testid="stHorizontalBlock"] .stButton button:not([kind="primary"]),
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    font-size: 0.74rem !important;
    height: 2.05rem !important;
    min-height: 2.05rem !important;
    padding: 0.15rem 0.45rem !important;
    border-radius: 6px !important;
    border: 1px solid #e2e8f0 !important;
    background: #f8fafc !important;
    background-color: #f8fafc !important;
    color: #334155 !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stHorizontalBlock"] .stButton button:not([kind="primary"]):hover,
div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    border-color: #94a3b8 !important;
    background: #f1f5f9 !important;
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
}
div[data-testid="stHorizontalBlock"] .stButton button:not([kind="primary"]) *,
div[data-testid="stHorizontalBlock"] button[kind="secondary"] * {
    font-size: 0.74rem !important;
    font-weight: 500 !important;
    color: #334155 !important;
    line-height: 1 !important;
}

/* 核心：启动投研分析主行动按钮 (Primary Action Button) 强对比度科技蓝鲜明配色 */
button[kind="primary"],
.stButton button[kind="primary"],
div[data-testid="stHorizontalBlock"] button[kind="primary"],
div[data-testid="stHorizontalBlock"] .stButton button[kind="primary"],
[data-testid="stVerticalBlock"] button[kind="primary"],
[data-testid="stVerticalBlock"] .stButton button[kind="primary"],
.main button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
    background-color: #1d4ed8 !important;
    color: #ffffff !important;
    border: 1px solid #1e40af !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    height: 2.4rem !important;
    min-height: 2.4rem !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 6px rgba(29, 78, 216, 0.35) !important;
    transition: all 0.15s ease-in-out !important;
    cursor: pointer !important;
}
button[kind="primary"]:hover,
.stButton button[kind="primary"]:hover,
div[data-testid="stHorizontalBlock"] button[kind="primary"]:hover,
div[data-testid="stHorizontalBlock"] .stButton button[kind="primary"]:hover,
[data-testid="stVerticalBlock"] button[kind="primary"]:hover,
[data-testid="stVerticalBlock"] .stButton button[kind="primary"]:hover,
.main button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%) !important;
    background-color: #1e40af !important;
    border-color: #172554 !important;
    box-shadow: 0 4px 12px rgba(29, 78, 216, 0.5) !important;
    transform: translateY(-1px);
}
button[kind="primary"] *,
.stButton button[kind="primary"] *,
div[data-testid="stHorizontalBlock"] button[kind="primary"] *,
div[data-testid="stHorizontalBlock"] .stButton button[kind="primary"] *,
[data-testid="stVerticalBlock"] button[kind="primary"] *,
[data-testid="stVerticalBlock"] .stButton button[kind="primary"] *,
.main button[kind="primary"] * {
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    line-height: 1 !important;
}

/* 8. Slider 紧凑平衡 */
[data-testid="stSidebar"] .stSlider {
    padding-top: 0 !important;
    margin-top: -0.1rem !important;
    margin-bottom: 0.1rem !important;
}
[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {
    font-size: 0.7rem !important;
}

/* 9. Toggle 开关精致化 */
[data-testid="stSidebar"] .stToggle {
    margin-top: 0.35rem !important;
    margin-bottom: 0.15rem !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] .stToggle label span {
    font-size: 0.77rem !important;
    color: #334155 !important;
    font-weight: 500 !important;
}

/* 10. 折叠卡片面板 (Expander) 优雅卡片化美化 */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    overflow: hidden !important;
    margin-top: 4px !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] details summary {
    padding: 0.35rem 0.55rem !important;
    min-height: 1.95rem !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] details summary p,
[data-testid="stSidebar"] [data-testid="stExpander"] details summary span {
    font-size: 0.74rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
    line-height: 1.25 !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    padding: 0.4rem 0.6rem !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"] * {
    font-size: 0.72rem !important;
    line-height: 1.35 !important;
}

/* 10.1 侧边栏状态提示框 (st.success, st.error, st.warning, st.info) 彻底精致微型化 */
[data-testid="stSidebar"] div[data-testid="stAlert"],
[data-testid="stSidebar"] .stAlert {
    padding: 0.3rem 0.55rem !important;
    min-height: auto !important;
    margin-top: 3px !important;
    margin-bottom: 3px !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] div[data-testid="stAlert"] [data-testid="stAlertContent"],
[data-testid="stSidebar"] .stAlert [data-testid="stAlertContent"] {
    padding: 0 !important;
    margin: 0 !important;
}
[data-testid="stSidebar"] div[data-testid="stAlert"] *,
[data-testid="stSidebar"] .stAlert *,
[data-testid="stSidebar"] div[data-testid="stAlert"] p,
[data-testid="stSidebar"] .stAlert p {
    font-size: 0.74rem !important;
    line-height: 1.3 !important;
    margin: 0 !important;
}
[data-testid="stSidebar"] div[data-testid="stAlert"] svg,
[data-testid="stSidebar"] .stAlert svg {
    width: 0.85rem !important;
    height: 0.85rem !important;
    min-width: 0.85rem !important;
    min-height: 0.85rem !important;
}

/* 10.2 侧边栏专业紧凑状态徽章 (Sidebar Compact Status Cards) */
.sidebar-status-badge {
    border-radius: 6px;
    padding: 5px 9px;
    font-size: 0.74rem;
    line-height: 1.35;
    margin: 4px 0;
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
}
.sidebar-status-success {
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
}
.sidebar-status-error {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;
}
.sidebar-status-warning {
    background-color: #fffbeb;
    border: 1px solid #fde68a;
    color: #92400e;
}


/* 11. 彻底隐藏 Streamlit 默认顶部杂项 (Deploy 按钮、页眉、汉堡菜单、顶部彩色条) */
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton,
.stAppToolbar,
#MainMenu,
footer {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

/* 12. Tabs 现代化分段卡片控制台 (Segmented Pill Card Tabs for React-Aria & Standard) */
[data-testid="stTabs"] {
    margin-top: 10px !important;
    margin-bottom: 14px !important;
}

/* 彻底隐藏 Streamlit / React-Aria 默认的下划线指示器与底边滑动条 */
[data-testid="stTabs"] .react-aria-SelectionIndicator,
[data-testid="stTabs"] [class*="SelectionIndicator"],
[data-testid="stTabs"] div[data-baseweb="tab-highlight"],
[data-testid="stTabs"] div[data-baseweb="tab-border"],
[data-testid="stTabs"] [data-testid="stTab"] [class*="SelectionIndicator"] {
    display: none !important;
    height: 0 !important;
    width: 0 !important;
    visibility: hidden !important;
    opacity: 0 !important;
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
}
[data-testid="stTabs"] [role="tablist"]::after,
[data-testid="stTabs"] .react-aria-TabList::after,
[data-testid="stTabs"] [data-testid="stTab"]::after,
[data-testid="stTabs"] [role="tab"]::after {
    display: none !important;
    content: none !important;
    height: 0 !important;
}

/* 标签栏滑轨底座：优雅的中性灰浅槽容器 (仅作用于 TabList，绝不污染面板外层) */
[data-testid="stTabs"] [role="tablist"],
[data-testid="stTabs"] .react-aria-TabList,
[data-testid="stTabs"] div[data-baseweb="tab-list"] {
    background-color: #f1f5f9 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 6px !important;
    gap: 8px !important;
    display: flex !important;
    flex-direction: row !important;
    width: 100% !important;
    min-width: 100% !important;
    align-items: stretch !important;
    box-sizing: border-box !important;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    overflow: visible !important;
}

/* 核心：确保外层 Tab 容器与面板保持纵向列流，让内容面板正常处于下方 */
[data-testid="stTabs"],
[data-testid="stTabs"] > div {
    display: flex !important;
    flex-direction: column !important;
    width: 100% !important;
}
/* 确保 Tab 内容面板为 100% 满宽，且仅在激活态显示，未激活态严格隐藏 */
[data-testid="stTabs"] [data-testid="stTabPanel"],
[data-testid="stTabs"] [role="tabpanel"] {
    width: 100% !important;
    margin-top: 10px !important;
}
[data-testid="stTabs"] [data-testid="stTabPanel"][hidden],
[data-testid="stTabs"] [data-testid="stTabPanel"][data-st-inactive],
[data-testid="stTabs"] [role="tabpanel"][hidden],
[data-testid="stTabs"] [role="tabpanel"][data-st-inactive] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

/* 单个 Tab 按钮基类：独立等宽 25% 实体卡片 (支持所有 div/button/react-aria 渲染) */
[data-testid="stTabs"] [data-testid="stTab"],
[data-testid="stTabs"] .react-aria-Tab,
[data-testid="stTabs"] [role="tab"],
[data-testid="stTabs"] button[role="tab"] {
    flex: 1 1 calc(25% - 8px) !important;
    width: calc(25% - 8px) !important;
    min-width: calc(25% - 8px) !important;
    max-width: calc(25% - 8px) !important;
    box-sizing: border-box !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 8px 10px !important;
    margin: 0 !important;
    min-height: 2.45rem !important;
    height: 2.45rem !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.15s ease-in-out !important;
    cursor: pointer !important;
    outline: none !important;
    position: relative !important;
}

/* 未激活状态的文字与图标 */
[data-testid="stTabs"] [data-testid="stTab"] *,
[data-testid="stTabs"] .react-aria-Tab *,
[data-testid="stTabs"] [role="tab"] * {
    font-size: 0.81rem !important;
    font-weight: 500 !important;
    color: #475569 !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
}

/* 悬停状态：高亮浮起与边框加深 */
[data-testid="stTabs"] [data-testid="stTab"]:hover,
[data-testid="stTabs"] .react-aria-Tab:hover,
[data-testid="stTabs"] [role="tab"]:hover,
[data-testid="stTabs"] [data-testid="stTab"][data-hovered] {
    background-color: #f8fafc !important;
    border-color: #94a3b8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.06) !important;
}
[data-testid="stTabs"] [data-testid="stTab"]:hover *,
[data-testid="stTabs"] .react-aria-Tab:hover *,
[data-testid="stTabs"] [role="tab"]:hover * {
    color: #0f172a !important;
}

/* 激活选中状态：明亮微蓝卡片底色 + 品牌科技蓝边框 + 蓝字加粗 + 醒目投影 */
[data-testid="stTabs"] [data-testid="stTab"][data-selected],
[data-testid="stTabs"] [data-testid="stTab"][data-selected="true"],
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"],
[data-testid="stTabs"] .react-aria-Tab[data-selected],
[data-testid="stTabs"] [role="tab"][data-selected],
[data-testid="stTabs"] [role="tab"][aria-selected="true"],
[data-testid="stTab"][data-selected] {
    background-color: #eff6ff !important;
    background: #eff6ff !important;
    border: 1.5px solid #2563eb !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.18) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stTabs"] [data-testid="stTab"][data-selected] *,
[data-testid="stTabs"] [data-testid="stTab"][data-selected="true"] *,
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] *,
[data-testid="stTabs"] .react-aria-Tab[data-selected] *,
[data-testid="stTabs"] [role="tab"][data-selected] *,
[data-testid="stTabs"] [role="tab"][aria-selected="true"] * {
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    color: #1d4ed8 !important;
}

/* Tab 下方面板内容与卡片间距舒适化 */
[data-testid="stTabContent"] {
    padding-top: 8px !important;
}

/* 13. 主工作区卡片容器规范 (Modern Workspace Card Components) */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    margin-bottom: 14px !important;
}
.skill-hero-card {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    margin-bottom: 14px;
}
.master-preview-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px 18px 16px 18px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    height: 100%;
    min-height: 220px;
    transition: all 0.2s ease;
}
.master-preview-card:hover {
    border-color: #cbd5e1;
    box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.05);
    transform: translateY(-2px);
}

/* 预设标的轻量药丸按钮 */
div[data-testid="stColumn"] div.stButton > button:not([kind="primary"]) {
    border-radius: 9999px !important;
    font-size: 0.74rem !important;
    font-weight: 500 !important;
    padding: 4px 12px !important;
    min-height: 30px !important;
    line-height: 1.2 !important;
    border: 1px solid #e2e8f0 !important;
    background-color: #f8fafc !important;
    color: #475569 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stColumn"] div.stButton > button:not([kind="primary"]):hover {
    border-color: #0284c7 !important;
    background-color: #f0f9ff !important;
    color: #0284c7 !important;
    transform: translateY(-1px) !important;
}

/* 主工作区水平单选组微胶囊卡片美化 */
.main div[data-testid="stRadio"] div[role="radiogroup"] {
    gap: 0.75rem !important;
    padding: 2px 0 !important;
}
.main div[data-testid="stRadio"] div[role="radiogroup"] label {
    padding: 0.28rem 0.7rem !important;
    border-radius: 8px !important;
    background-color: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.15s ease !important;
}
.main div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
    border-color: #38bdf8 !important;
    background-color: #f0f9ff !important;
}
.main div[data-testid="stRadio"] div[role="radiogroup"] label p {
    font-size: 0.79rem !important;
    font-weight: 500 !important;
    color: #334155 !important;
}

/* 14. 知识库研报阅读器与 KPI 视觉卡片 */
.report-reading-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}
.metric-kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 14px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    text-align: center;
}
.audit-safety-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px 18px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}
</style>
""", unsafe_allow_html=True)
